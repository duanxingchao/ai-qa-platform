"""
API客户端测试模块
测试API客户端基类和具体实现的功能
"""
import json
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import requests
from requests import Response

from app.services.api_client import (
    BaseAPIClient,
    ClassificationAPIClient,
    DoubaoAPIClient,
    XiaotianAPIClient,
    ScoreAPIClient,
    APIClientFactory
)
from app.exceptions import (
    APIException,
    APITimeoutException,
    APIConnectionException,
    APIRateLimitException,
    APIAuthenticationException,
    APIValidationException,
    APIServerException
)


class MockAPIClient(BaseAPIClient):
    """用于测试的模拟API客户端"""
    
    def _get_auth_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.api_key}'}


class TestBaseAPIClient(unittest.TestCase):
    """基础API客户端测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = MockAPIClient(
            base_url='https://api.example.com',
            api_key='test-key',
            timeout=5.0,
            retry_times=2
        )
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self.client, 'session'):
            self.client.session.close()
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        self.assertEqual(self.client.base_url, 'https://api.example.com')
        self.assertEqual(self.client.api_key, 'test-key')
        self.assertEqual(self.client.timeout, 5.0)
        self.assertEqual(self.client.retry_times, 2)
        self.assertIsNotNone(self.client.session)
        self.assertIsNotNone(self.client.logger)
    
    def test_generate_request_id(self):
        """测试请求ID生成"""
        request_id = self.client._generate_request_id()
        self.assertIsInstance(request_id, str)
        self.assertEqual(len(request_id), 36)  # UUID长度
        
        # 确保生成的ID是唯一的
        another_id = self.client._generate_request_id()
        self.assertNotEqual(request_id, another_id)
    
    @patch('requests.Session.request')
    def test_successful_request(self, mock_request):
        """测试成功的API请求"""
        # 模拟成功响应
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'data': 'test'}
        mock_response.text = '{"status": "success", "data": "test"}'
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response
        
        # 执行请求
        result = self.client.get('/test')
        
        # 验证结果
        self.assertEqual(result, {'status': 'success', 'data': 'test'})
        self.assertEqual(self.client.request_stats['total_requests'], 1)
        self.assertEqual(self.client.request_stats['successful_requests'], 1)
        self.assertEqual(self.client.request_stats['failed_requests'], 0)
    
    @patch('requests.Session.request')
    def test_request_timeout(self, mock_request):
        """测试请求超时"""
        mock_request.side_effect = requests.exceptions.Timeout('Request timeout')
        
        with self.assertRaises(APITimeoutException):
            self.client.get('/test')
        
        self.assertEqual(self.client.request_stats['failed_requests'], 1)
    
    @patch('requests.Session.request')
    def test_connection_error(self, mock_request):
        """测试连接错误"""
        mock_request.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with self.assertRaises(APIConnectionException):
            self.client.get('/test')
        
        self.assertEqual(self.client.request_stats['failed_requests'], 1)
    
    @patch('requests.Session.request')
    def test_authentication_error(self, mock_request):
        """测试认证错误"""
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        mock_request.return_value = mock_response
        
        with self.assertRaises(APIAuthenticationException):
            self.client.get('/test')
    
    @patch('requests.Session.request')
    def test_validation_error(self, mock_request):
        """测试请求参数验证错误"""
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Bad Request', 'field': 'invalid'}
        mock_request.return_value = mock_response
        
        with self.assertRaises(APIValidationException) as cm:
            self.client.post('/test', data={'invalid': 'data'})
        
        self.assertIn('Bad Request', str(cm.exception))
    
    @patch('requests.Session.request')
    def test_rate_limit_error(self, mock_request):
        """测试速率限制错误"""
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.json.return_value = {'error': 'Rate limit exceeded'}
        mock_request.return_value = mock_response
        
        with self.assertRaises(APIRateLimitException) as cm:
            self.client.get('/test')
        
        self.assertEqual(cm.exception.retry_after, 60)
    
    @patch('requests.Session.request')
    def test_server_error(self, mock_request):
        """测试服务器错误"""
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {'error': 'Internal Server Error'}
        mock_request.return_value = mock_response
        
        with self.assertRaises(APIServerException):
            self.client.get('/test')
    
    @patch('requests.Session.request')
    def test_retry_mechanism(self, mock_request):
        """测试重试机制"""
        # 模拟前两次请求失败，第三次成功
        mock_response_fail = Mock(spec=Response)
        mock_response_fail.ok = False
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock(spec=Response)
        mock_response_success.ok = True
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'status': 'success'}
        mock_response_success.text = '{"status": "success"}'
        mock_response_success.headers = {'content-type': 'application/json'}
        
        mock_request.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]
        
        # 执行请求
        result = self.client.get('/test')
        
        # 验证结果
        self.assertEqual(result, {'status': 'success'})
        self.assertEqual(mock_request.call_count, 3)  # 重试了2次
    
    def test_stats_tracking(self):
        """测试统计信息跟踪"""
        initial_stats = self.client.get_stats()
        self.assertEqual(initial_stats['total_requests'], 0)
        self.assertEqual(initial_stats['success_rate'], 0.0)
        
        # 重置统计
        self.client.reset_stats()
        stats = self.client.get_stats()
        self.assertEqual(stats['total_requests'], 0)


class TestClassificationAPIClient(unittest.TestCase):
    """分类API客户端测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = ClassificationAPIClient()
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self.client, 'session'):
            self.client.session.close()
    
    def test_auth_headers(self):
        """测试认证头设置"""
        headers = self.client._get_auth_headers()
        self.assertIn('X-API-Key', headers)
        self.assertIn('Authorization', headers)
        self.assertTrue(headers['Authorization'].startswith('Bearer'))
    
    @patch('requests.Session.request')
    def test_classify_question(self, mock_request):
        """测试问题分类功能"""
        # 模拟成功响应
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'category': 'technology',
            'confidence': 0.95,
            'subcategory': 'programming',
            'tags': ['python', 'api'],
            'processing_time': 150.5
        }
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response
        
        # 执行分类
        result = self.client.classify_question(
            question="How to use Python API?",
            context="Programming tutorial",
            categories=['technology', 'education']
        )
        
        # 验证结果
        self.assertEqual(result['category'], 'technology')
        self.assertEqual(result['confidence'], 0.95)
        self.assertIn('python', result['tags'])


class TestDoubaoAPIClient(unittest.TestCase):
    """豆包API客户端测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = DoubaoAPIClient()
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self.client, 'session'):
            self.client.session.close()
    
    @patch('requests.Session.request')
    def test_generate_answer(self, mock_request):
        """测试答案生成功能"""
        # 模拟成功响应
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'answer': 'Python is a programming language...',
            'confidence': 0.88,
            'tokens_used': 156,
            'model': 'doubao-pro',
            'processing_time': 2500.0
        }
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response
        
        # 执行生成
        result = self.client.generate_answer(
            question="What is Python?",
            context="Programming education",
            max_tokens=200,
            temperature=0.7
        )
        
        # 验证结果
        self.assertIn('Python', result['answer'])
        self.assertEqual(result['tokens_used'], 156)
        self.assertEqual(result['model'], 'doubao-pro')


class TestScoreAPIClient(unittest.TestCase):
    """评分API客户端测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = ScoreAPIClient()
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self.client, 'session'):
            self.client.session.close()
    
    @patch('requests.Session.request')
    def test_score_answer(self, mock_request):
        """测试答案评分功能"""
        # 模拟成功响应
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'overall_score': 85.5,
            'dimension_scores': {
                'accuracy': 90.0,
                'completeness': 80.0,
                'clarity': 88.0,
                'relevance': 92.0,
                'helpfulness': 85.0
            },
            'feedback': 'Good answer with minor improvements needed',
            'suggestions': ['Add more examples', 'Clarify terminology'],
            'processing_time': 1800.0
        }
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_response.headers = {'content-type': 'application/json'}
        mock_request.return_value = mock_response
        
        # 执行评分
        result = self.client.score_answer(
            question="What is Python?",
            answer="Python is a high-level programming language...",
            reference_answer="Python is a versatile programming language..."
        )
        
        # 验证结果
        self.assertEqual(result['overall_score'], 85.5)
        self.assertIn('accuracy', result['dimension_scores'])
        self.assertEqual(result['dimension_scores']['accuracy'], 90.0)


class TestAPIClientFactory(unittest.TestCase):
    """API客户端工厂测试类"""
    
    def setUp(self):
        """测试前置设置"""
        # 清理工厂实例
        APIClientFactory._instances.clear()
    
    def tearDown(self):
        """测试后清理"""
        APIClientFactory.close_all()
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        # 获取同一类型的客户端实例
        client1 = APIClientFactory.get_classification_client()
        client2 = APIClientFactory.get_classification_client()
        
        # 验证是同一个实例
        self.assertIs(client1, client2)
    
    def test_different_client_types(self):
        """测试不同类型的客户端"""
        classification_client = APIClientFactory.get_classification_client()
        doubao_client = APIClientFactory.get_doubao_client()
        xiaotian_client = APIClientFactory.get_xiaotian_client()
        score_client = APIClientFactory.get_score_client()
        
        # 验证类型
        self.assertIsInstance(classification_client, ClassificationAPIClient)
        self.assertIsInstance(doubao_client, DoubaoAPIClient)
        self.assertIsInstance(xiaotian_client, XiaotianAPIClient)
        self.assertIsInstance(score_client, ScoreAPIClient)
        
        # 验证是不同的实例
        self.assertIsNot(classification_client, doubao_client)
    
    def test_get_all_stats(self):
        """测试获取所有统计信息"""
        # 创建一些客户端实例
        APIClientFactory.get_classification_client()
        APIClientFactory.get_doubao_client()
        
        # 获取统计信息
        stats = APIClientFactory.get_all_stats()
        
        # 验证结果
        self.assertIn('classification', stats)
        self.assertIn('doubao', stats)
        self.assertIsInstance(stats['classification'], dict)
    
    def test_reset_all_stats(self):
        """测试重置所有统计信息"""
        # 创建客户端并模拟一些请求统计
        client = APIClientFactory.get_classification_client()
        client.request_stats['total_requests'] = 5
        
        # 重置统计
        APIClientFactory.reset_all_stats()
        
        # 验证重置成功
        self.assertEqual(client.request_stats['total_requests'], 0)
    
    def test_close_all(self):
        """测试关闭所有客户端"""
        # 创建一些客户端
        APIClientFactory.get_classification_client()
        APIClientFactory.get_doubao_client()
        
        # 关闭所有客户端
        APIClientFactory.close_all()
        
        # 验证实例已清空
        self.assertEqual(len(APIClientFactory._instances), 0)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 