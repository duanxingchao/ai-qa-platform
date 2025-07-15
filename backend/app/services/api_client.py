"""
API客户端基类模块
提供统一的外部API调用基础设施，包含HTTP请求处理、重试机制、错误处理等
"""
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

import requests
from requests.adapters import HTTPAdapter

from app.config import Config
from app.exceptions import (
    APIException,
    APITimeoutException,
    APIConnectionException,
    APIRateLimitException,
    APIAuthenticationException,
    APIValidationException,
    APIServerException,
    APIResponseException
)


class BaseAPIClient(ABC):
    """
    API客户端基类
    
    提供统一的外部API调用基础设施，包含：
    - HTTP请求处理
    - 自动重试机制
    - 超时控制
    - 错误处理
    - 请求/响应日志记录
    - 性能监控
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        retry_delay: Optional[float] = None,
        backoff_factor: Optional[float] = None
    ):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
            retry_times: 重试次数
            retry_delay: 重试延迟（秒）
            backoff_factor: 退避因子
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout or Config.API_TIMEOUT
        self.retry_times = retry_times or Config.API_RETRY_TIMES
        self.retry_delay = retry_delay or Config.API_RETRY_DELAY
        self.backoff_factor = backoff_factor or Config.API_RETRY_BACKOFF_FACTOR
        
        # 配置日志记录器
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 创建HTTP会话
        self.session = self._create_session()
        
        # 请求统计
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0
        }
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        
        # 设置默认请求头
        session.headers.update(Config.API_REQUEST_HEADERS)
        session.headers.update(self._get_auth_headers())
        
        return session
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        获取认证请求头
        
        Returns:
            包含认证信息的请求头字典
        """
        pass
    
    def _generate_request_id(self) -> str:
        """生成唯一的请求ID"""
        return str(uuid.uuid4())
    
    def _log_request(
        self, 
        request_id: str, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录请求日志"""
        self.logger.info(
            f"[{request_id}] API请求开始 - {method} {url}",
            extra={
                'request_id': request_id,
                'method': method,
                'url': url,
                'headers': {k: v for k, v in headers.items() if k.lower() not in ['authorization', 'x-api-key']},
                'data_size': len(json.dumps(data)) if data else 0
            }
        )
    
    def _log_response(
        self, 
        request_id: str, 
        response: requests.Response, 
        duration: float
    ) -> None:
        """记录响应日志"""
        self.logger.info(
            f"[{request_id}] API响应完成 - {response.status_code} ({duration:.3f}s)",
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': duration,
                'response_size': len(response.text),
                'content_type': response.headers.get('content-type', 'unknown')
            }
        )
    
    def _handle_response_error(self, response: requests.Response) -> None:
        """处理HTTP响应错误"""
        status_code = response.status_code
        
        try:
            error_data = response.json()
        except (json.JSONDecodeError, ValueError):
            error_data = {'error': response.text}
        
        if status_code == 401:
            raise APIAuthenticationException(
                f"API认证失败: {error_data.get('error', 'Unauthorized')}"
            )
        elif status_code == 400:
            raise APIValidationException(
                f"请求参数无效: {error_data.get('error', 'Bad Request')}",
                validation_errors=error_data
            )
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise APIRateLimitException(
                f"API调用频率超限: {error_data.get('error', 'Rate limit exceeded')}",
                retry_after=int(retry_after) if retry_after else None
            )
        elif 500 <= status_code < 600:
            raise APIServerException(
                f"API服务器错误: {error_data.get('error', 'Internal Server Error')}",
                status_code=status_code
            )
        else:
            raise APIException(
                f"API请求失败: {error_data.get('error', 'Unknown error')}",
                status_code=status_code,
                response_data=error_data
            )
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """解析API响应"""
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise APIResponseException(
                f"API响应格式错误: {str(e)}",
                response_text=response.text[:500]  # 限制日志长度
            )
    
    def _should_retry(self, exception: Exception, status_code: Optional[int] = None) -> bool:
        """判断是否应该重试"""
        # 网络异常应该重试
        if isinstance(exception, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            return True
        
        # 服务器错误应该重试
        if status_code and status_code >= 500:
            return True
        
        # 速率限制应该重试
        if status_code == 429:
            return True
        
        return False
    
    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """执行带重试的HTTP请求"""
        last_exception = None
        
        for attempt in range(self.retry_times + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # 如果是可重试的错误状态码，抛出异常进入重试逻辑
                if response.status_code >= 500 or response.status_code == 429:
                    if attempt < self.retry_times:
                        time.sleep(self.retry_delay * (self.backoff_factor ** attempt))
                        continue
                
                return response
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exception = e
                if attempt < self.retry_times:
                    self.logger.warning(f"请求失败，{self.retry_delay * (self.backoff_factor ** attempt):.1f}秒后重试 (尝试 {attempt + 1}/{self.retry_times + 1}): {str(e)}")
                    time.sleep(self.retry_delay * (self.backoff_factor ** attempt))
                    continue
                else:
                    raise e
            except requests.exceptions.RequestException as e:
                # 其他请求异常不重试
                raise e
        
        # 如果所有重试都失败了，抛出最后一个异常
        if last_exception:
            raise last_exception
            
        # 理论上不会到达这里
        raise APIException("所有重试均失败")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求体数据
            params: URL参数
            headers: 额外的请求头
            
        Returns:
            API响应数据
            
        Raises:
            APIException: API调用相关异常
        """
        request_id = self._generate_request_id()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # 合并请求头
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        # 更新统计信息
        self.request_stats['total_requests'] += 1
        
        # 记录请求日志（确保headers都是字符串类型）
        log_headers = {k: str(v) for k, v in request_headers.items()}
        self._log_request(request_id, method, url, log_headers, data)
        
        start_time = time.time()
        
        try:
            response = self._make_request_with_retry(
                method=method,
                url=url,
                data=data,
                params=params,
                headers=headers
            )
            
            duration = time.time() - start_time
            self.request_stats['total_response_time'] += duration
            
            # 记录响应日志
            self._log_response(request_id, response, duration)
            
            # 检查响应状态
            if not response.ok:
                self.request_stats['failed_requests'] += 1
                self._handle_response_error(response)
            
            self.request_stats['successful_requests'] += 1
            return self._parse_response(response)
            
        except requests.exceptions.Timeout as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] API请求超时: {str(e)}")
            raise APITimeoutException(f"API请求超时: {str(e)}", timeout=self.timeout)
            
        except requests.exceptions.ConnectionError as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] API连接失败: {str(e)}")
            raise APIConnectionException(f"API连接失败: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] API请求异常: {str(e)}")
            raise APIException(f"API请求异常: {str(e)}")
    
    def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """执行GET请求"""
        return self._make_request('GET', endpoint, params=params, headers=headers)
    
    def post(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """执行POST请求"""
        return self._make_request('POST', endpoint, data=data, params=params, headers=headers)
    
    def put(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """执行PUT请求"""
        return self._make_request('PUT', endpoint, data=data, headers=headers)
    
    def delete(
        self, 
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """执行DELETE请求"""
        return self._make_request('DELETE', endpoint, headers=headers)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取客户端统计信息
        
        Returns:
            包含请求统计信息的字典
        """
        total_requests = self.request_stats['total_requests']
        if total_requests > 0:
            success_rate = (self.request_stats['successful_requests'] / total_requests) * 100
            avg_response_time = self.request_stats['total_response_time'] / total_requests
        else:
            success_rate = 0.0
            avg_response_time = 0.0
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.request_stats['successful_requests'],
            'failed_requests': self.request_stats['failed_requests'],
            'success_rate': round(success_rate, 2),
            'average_response_time': round(avg_response_time, 3),
            'total_response_time': round(self.request_stats['total_response_time'], 3)
        }
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0
        }
    
    def __del__(self):
        """析构函数，清理资源"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# 具体API客户端实现
# ============================================================================

class ClassificationAPIClient(BaseAPIClient):
    """
    问题分类API客户端
    
    负责调用外部分类API，实现问题领域分类功能
    """
    
    def __init__(self):
        super().__init__(
            base_url=Config.CLASSIFY_API_URL,
            api_key=Config.CLASSIFY_API_KEY
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取分类API认证头"""
        return {
            'X-API-Key': self.api_key,
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def classify_question(
        self, 
        question: str, 
        answer: Optional[str] = None,
        user_id: str = "00031559"
    ) -> str:
        """
        对问题进行分类 - 符合用户的外部API格式
        
        Args:
            question: 要分类的问题文本
            answer: AI回答内容（可选）
            user_id: 用户ID（默认: 00031559）
            
        Returns:
            str: 分类结果文本
        """
        # 按照用户的API格式构建请求体
        body = {
            "inputs": {
                "QUERY": question,
                "ANSWER": answer or ""
            },
            "response_mode": "blocking",
            "user": user_id
        }
        
        self.logger.info(f"开始问题分类: {question[:50]}...")
        
        try:
            # 直接使用requests.post调用，符合用户的方式
            response = self._make_classification_request(body)
            
            if response.status_code == 200:
                response_json = response.json()
                res = response_json["data"]["outputs"]["text"]
                
                self.logger.info(f"分类完成: {res}")
                return res
            else:
                raise APIException(
                    f"分类API请求失败，状态码: {response.status_code}",
                    status_code=response.status_code
                )
            
        except APIException as e:
            self.logger.error(f"问题分类失败: {str(e)}")
            raise
    
    def _make_classification_request(self, body: Dict[str, Any]) -> requests.Response:
        """
        执行分类API请求 - 完全按照用户的格式
        """
        request_id = self._generate_request_id()
        
        # 构建请求头
        headers = self._get_auth_headers()
        headers.update({
            'Content-Type': 'application/json'
        })
        
        # 更新统计
        self.request_stats['total_requests'] += 1
        
        # 记录请求日志
        self.logger.info(f"[{request_id}] 发起分类API请求")
        self.logger.debug(f"[{request_id}] 请求体: {body}")
        
        start_time = time.time()
        
        try:
            # 完全按照用户的方式调用
            response = requests.post(
                f"{self.base_url}/classify",
                json=body,
                headers=headers,
                timeout=15
            )
            
            duration = time.time() - start_time
            self.request_stats['total_response_time'] += duration
            
            # 记录响应日志
            self.logger.info(
                f"[{request_id}] 分类API响应: {response.status_code} "
                f"({duration:.3f}s)"
            )
            
            if response.status_code == 200:
                self.request_stats['successful_requests'] += 1
            else:
                self.request_stats['failed_requests'] += 1
            
            return response
            
        except requests.exceptions.Timeout as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] 分类API请求超时: {str(e)}")
            raise APITimeoutException(f"分类API请求超时: {str(e)}", timeout=15)
            
        except requests.exceptions.ConnectionError as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] 分类API连接失败: {str(e)}")
            raise APIConnectionException(f"分类API连接失败: {str(e)}")
            
        except Exception as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] 分类API请求异常: {str(e)}")
            raise APIException(f"分类API请求异常: {str(e)}")


class DoubaoAPIClient(BaseAPIClient):
    """
    豆包AI API客户端
    
    负责调用豆包API生成回答
    """
    
    def __init__(self):
        super().__init__(
            base_url=Config.DOUBAO_API_URL,
            api_key=Config.DOUBAO_API_KEY
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取豆包API认证头"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'X-API-Key': self.api_key
        }
    
    def generate_answer(
        self,
        question: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成问题回答
        
        Args:
            question: 问题文本
            context: 上下文信息
            max_tokens: 最大生成token数
            temperature: 生成温度 (0-1)
            model: 使用的模型名称
            
        Returns:
            包含生成结果的字典
            {
                'answer': str,             # 生成的回答
                'confidence': float,       # 置信度
                'tokens_used': int,        # 使用的token数
                'model': str,              # 使用的模型
                'processing_time': float   # 处理时间（毫秒）
            }
        """
        payload = {
            'question': question,
            'context': context,
            'max_tokens': max_tokens or 1000,
            'temperature': temperature or 0.7,
            'model': model or 'doubao-default'
        }
        
        self.logger.info(f"开始豆包答案生成: {question[:50]}...")
        
        try:
            result = self.post('/generate', data=payload)
            
            self.logger.info(
                f"豆包生成完成: 生成{result.get('tokens_used', 0)}个token"
            )
            
            return result
            
        except APIException as e:
            self.logger.error(f"豆包答案生成失败: {str(e)}")
            raise


class XiaotianAPIClient(BaseAPIClient):
    """
    小天AI API客户端
    
    负责调用小天API生成回答
    """
    
    def __init__(self):
        super().__init__(
            base_url=Config.XIAOTIAN_API_URL,
            api_key=Config.XIAOTIAN_API_KEY
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取小天API认证头"""
        return {
            'X-Auth-Token': self.api_key,
            'Authorization': f'ApiKey {self.api_key}'
        }
    
    def generate_answer(
        self,
        question: str,
        context: Optional[str] = None,
        style: Optional[str] = None,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成问题回答
        
        Args:
            question: 问题文本
            context: 上下文信息
            style: 回答风格 (formal, casual, professional)
            max_length: 最大回答长度
            
        Returns:
            包含生成结果的字典
            {
                'answer': str,             # 生成的回答
                'confidence': float,       # 置信度
                'style': str,              # 使用的风格
                'length': int,             # 回答长度
                'processing_time': float   # 处理时间（毫秒）
            }
        """
        payload = {
            'question': question,
            'context': context,
            'style': style or 'professional',
            'max_length': max_length or 500
        }
        
        self.logger.info(f"开始小天答案生成: {question[:50]}...")
        
        try:
            result = self.post('/answer', data=payload)
            
            self.logger.info(
                f"小天生成完成: 回答长度{result.get('length', 0)}字符"
            )
            
            return result
            
        except APIException as e:
            self.logger.error(f"小天答案生成失败: {str(e)}")
            raise


class ScoreAPIClient(BaseAPIClient):
    """
    评分系统API客户端
    
    负责调用评分API实现五维评分
    """
    
    def __init__(self):
        super().__init__(
            base_url=Config.SCORE_API_URL,
            api_key=Config.SCORE_API_KEY
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取评分API认证头"""
        return {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def score_multiple_answers(
        self,
        question: str,
        our_answer: str,
        doubao_answer: str,
        xiaotian_answer: str,
        classification: str
    ) -> List[Dict[str, Any]]:
        """
        对多个AI模型的答案进行评分 - 符合用户的API格式
        
        Args:
            question: 原始问题
            our_answer: 原始模型答案
            doubao_answer: 豆包模型答案  
            xiaotian_answer: 小天模型答案
            classification: 问题分类
            
        Returns:
            List[Dict]: 包含3个模型评分结果的列表
            [
                {
                    "模型名称": "原始模型",
                    "准确性": 4,
                    "完整性": 3,
                    "清晰度": 4,
                    "相关性": 3,
                    "有用性": 4,
                    "理由": "评分理由"
                },
                ...
            ]
        """
        # 按照用户的API格式构建请求体
        inputs = {
            'question': question,
            'our_answer': our_answer,
            'doubao_answer': doubao_answer,
            'xiaotian_answer': xiaotian_answer,
            'classification': classification
        }
        
        self.logger.info(f"开始多模型答案评分: {question[:50]}...")
        
        try:
            # 直接使用requests.post调用，符合用户的方式
            response = self._make_score_request(inputs)
            
            if response.status_code == 200:
                response_json = response.json()
                # 按照用户指定的格式解析
                text_result = response_json["data"]["outputs"]["text"]
                
                # 解析JSON格式的评分结果
                import json
                score_results = json.loads(text_result)
                
                self.logger.info(f"多模型评分完成: 获得{len(score_results)}个模型的评分")
                return score_results
            else:
                raise APIException(
                    f"评分API请求失败，状态码: {response.status_code}",
                    status_code=response.status_code
                )
            
        except APIException as e:
            self.logger.error(f"多模型答案评分失败: {str(e)}")
            raise
    
    def _make_score_request(self, inputs: Dict[str, Any]) -> requests.Response:
        """
        执行评分API请求 - 完全按照用户的格式
        """
        request_id = self._generate_request_id()
        
        # 构建请求体
        body = {
            'inputs': inputs
        }
        
        # 构建请求头
        headers = self._get_auth_headers()
        headers.update({
            'Content-Type': 'application/json'
        })
        
        # 更新统计
        self.request_stats['total_requests'] += 1
        
        # 记录请求日志
        self.logger.info(f"[{request_id}] 发起评分API请求")
        self.logger.debug(f"[{request_id}] 请求体: {body}")
        
        start_time = time.time()
        
        try:
            # 完全按照用户的方式调用
            response = requests.post(
                f"{self.base_url}/score",
                json=body,
                headers=headers,
                timeout=30
            )
            
            duration = time.time() - start_time
            self.request_stats['total_response_time'] += duration
            
            # 记录响应日志
            self.logger.info(
                f"[{request_id}] 评分API响应: {response.status_code} "
                f"({duration:.3f}s)"
            )
            
            if response.status_code == 200:
                self.request_stats['successful_requests'] += 1
            else:
                self.request_stats['failed_requests'] += 1
            
            return response
            
        except requests.exceptions.Timeout as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] 评分API请求超时: {str(e)}")
            raise APITimeoutException(f"评分API请求超时: {str(e)}", timeout=30)
            
        except requests.exceptions.ConnectionError as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] 评分API连接失败: {str(e)}")
            raise APIConnectionException(f"评分API连接失败: {str(e)}")
            
        except Exception as e:
            self.request_stats['failed_requests'] += 1
            self.logger.error(f"[{request_id}] 评分API请求异常: {str(e)}")
            raise APIException(f"评分API请求异常: {str(e)}")


# ============================================================================
# API客户端工厂类
# ============================================================================

class APIClientFactory:
    """
    API客户端工厂类
    
    负责创建和管理各种API客户端实例
    """
    
    _instances: Dict[str, BaseAPIClient] = {}
    
    @classmethod
    def get_classification_client(cls) -> ClassificationAPIClient:
        """获取分类API客户端（单例）"""
        if 'classification' not in cls._instances:
            cls._instances['classification'] = ClassificationAPIClient()
        return cls._instances['classification']
    
    @classmethod
    def get_doubao_client(cls) -> DoubaoAPIClient:
        """获取豆包API客户端（单例）"""
        if 'doubao' not in cls._instances:
            cls._instances['doubao'] = DoubaoAPIClient()
        return cls._instances['doubao']
    
    @classmethod
    def get_xiaotian_client(cls) -> XiaotianAPIClient:
        """获取小天API客户端（单例）"""
        if 'xiaotian' not in cls._instances:
            cls._instances['xiaotian'] = XiaotianAPIClient()
        return cls._instances['xiaotian']
    
    @classmethod
    def get_score_client(cls) -> ScoreAPIClient:
        """获取评分API客户端（单例）"""
        if 'score' not in cls._instances:
            cls._instances['score'] = ScoreAPIClient()
        return cls._instances['score']
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有客户端的统计信息"""
        stats = {}
        for name, client in cls._instances.items():
            stats[name] = client.get_stats()
        return stats
    
    @classmethod
    def reset_all_stats(cls) -> None:
        """重置所有客户端的统计信息"""
        for client in cls._instances.values():
            client.reset_stats()
    
    @classmethod
    def close_all(cls) -> None:
        """关闭所有客户端连接"""
        for client in cls._instances.values():
            if hasattr(client, 'session'):
                client.session.close()
        cls._instances.clear() 