"""
API异常处理模块
定义API客户端调用过程中可能遇到的各种异常类型
"""
from typing import Optional, Dict, Any


class APIException(Exception):
    """API调用基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class APITimeoutException(APIException):
    """API请求超时异常"""
    
    def __init__(self, message: str = "API请求超时", timeout: Optional[float] = None):
        super().__init__(message)
        self.timeout = timeout


class APIConnectionException(APIException):
    """API连接异常"""
    
    def __init__(self, message: str = "API连接失败"):
        super().__init__(message)


class APIRateLimitException(APIException):
    """API速率限制异常"""
    
    def __init__(self, message: str = "API调用频率超限", retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class APIAuthenticationException(APIException):
    """API认证异常"""
    
    def __init__(self, message: str = "API认证失败"):
        super().__init__(message, status_code=401)


class APIValidationException(APIException):
    """API请求参数验证异常"""
    
    def __init__(
        self, 
        message: str = "API请求参数无效", 
        validation_errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=400)
        self.validation_errors = validation_errors or {}


class APIServerException(APIException):
    """API服务器异常"""
    
    def __init__(self, message: str = "API服务器内部错误", status_code: int = 500):
        super().__init__(message, status_code=status_code)


class APIResponseException(APIException):
    """API响应格式异常"""
    
    def __init__(self, message: str = "API响应格式错误", response_text: Optional[str] = None):
        super().__init__(message)
        self.response_text = response_text 