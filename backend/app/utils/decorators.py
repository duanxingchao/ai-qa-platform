"""
装饰器工具模块
"""
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """
    登录验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 对于大屏展示等公开API，暂时跳过认证
            if request.endpoint and ('display' in request.endpoint or 'analysis' in request.endpoint):
                return f(*args, **kwargs)
            
            # 其他API需要JWT验证
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"认证失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': '认证失败，请重新登录',
                'error_code': 'AUTH_FAILED'
            }), 401
    
    return decorated_function

def admin_required(f):
    """
    管理员权限验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 对于大屏展示等公开API，暂时跳过权限检查
            if request.endpoint and ('display' in request.endpoint or 'analysis' in request.endpoint):
                return f(*args, **kwargs)
            
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', 'user')
            
            if user_role != 'admin':
                return jsonify({
                    'success': False,
                    'message': '权限不足，需要管理员权限',
                    'error_code': 'PERMISSION_DENIED'
                }), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"权限验证失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': '权限验证失败',
                'error_code': 'PERMISSION_CHECK_FAILED'
            }), 401
    
    return decorated_function

def rate_limit(max_requests=100, per_seconds=3600):
    """
    简单的速率限制装饰器
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 暂时不实现速率限制，直接通过
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json(required_fields=None):
    """
    JSON数据验证装饰器
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': '请求必须是JSON格式',
                    'error_code': 'INVALID_JSON'
                }), 400
            
            data = request.get_json()
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'message': f'缺少必需字段: {", ".join(missing_fields)}',
                        'error_code': 'MISSING_FIELDS'
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
