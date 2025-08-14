"""
日期时间辅助工具
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# 北京时区常量
BEIJING_TZ = timezone(timedelta(hours=8))


def get_current_beijing_time() -> datetime:
    """
    获取当前北京时间

    Returns:
        datetime: 当前北京时间
    """
    return datetime.now(BEIJING_TZ)


def utc_to_beijing_str(utc_time: Optional[datetime]) -> Optional[str]:
    """
    将UTC时间转换为北京时间字符串
    
    Args:
        utc_time: UTC时间对象
        
    Returns:
        str: 北京时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
    """
    if not utc_time:
        return None
    
    try:
        # 如果输入时间没有时区信息，假设它是UTC时间
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=timezone.utc)
        
        # 转换为北京时间 (UTC+8)
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = utc_time.astimezone(beijing_tz)
        
        # 格式化为字符串
        return beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception as e:
        # 如果转换失败，返回原始时间的字符串表示
        return str(utc_time)


def beijing_to_utc(beijing_time: Optional[datetime]) -> Optional[datetime]:
    """
    将北京时间转换为UTC时间
    
    Args:
        beijing_time: 北京时间对象
        
    Returns:
        datetime: UTC时间对象
    """
    if not beijing_time:
        return None
    
    try:
        # 如果输入时间没有时区信息，假设它是北京时间
        if beijing_time.tzinfo is None:
            beijing_tz = timezone(timedelta(hours=8))
            beijing_time = beijing_time.replace(tzinfo=beijing_tz)
        
        # 转换为UTC时间
        utc_time = beijing_time.astimezone(timezone.utc)
        
        return utc_time
    
    except Exception as e:
        # 如果转换失败，返回原始时间
        return beijing_time


def format_datetime(dt: Optional[datetime], format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[str]:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        str: 格式化后的时间字符串
    """
    if not dt:
        return None
    
    try:
        return dt.strftime(format_str)
    except Exception:
        return str(dt)


def parse_datetime(date_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        datetime: 解析后的日期时间对象
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, format_str)
    except Exception:
        return None
