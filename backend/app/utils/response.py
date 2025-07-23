"""
API响应工具模块
"""
from flask import jsonify
from typing import Any, Dict, Optional


def api_response(data: Any = None, message: str = "操作成功", code: int = 200) -> Dict:
    """
    标准API成功响应格式
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 响应状态码
    
    Returns:
        标准化的响应格式
    """
    response = {
        "success": True,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": int(__import__('time').time())
    }
    return jsonify(response)


def error_response(message: str = "操作失败", code: int = 400, error_code: Optional[str] = None) -> Dict:
    """
    标准API错误响应格式
    
    Args:
        message: 错误消息
        code: HTTP状态码
        error_code: 业务错误代码
    
    Returns:
        标准化的错误响应格式
    """
    response = {
        "success": False,
        "code": code,
        "message": message,
        "error_code": error_code,
        "timestamp": int(__import__('time').time())
    }
    return jsonify(response), code


def paginated_response(items: list, total: int, page: int = 1, page_size: int = 20, message: str = "获取成功") -> Dict:
    """
    分页响应格式
    
    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
    
    Returns:
        包含分页信息的响应格式
    """
    total_pages = (total + page_size - 1) // page_size
    
    pagination_data = {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return api_response(data=pagination_data, message=message) 