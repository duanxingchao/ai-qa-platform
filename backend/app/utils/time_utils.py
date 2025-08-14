"""
时间范围工具类
"""

from datetime import datetime, timedelta
from typing import Tuple
import calendar
from app.utils.datetime_helper import get_current_beijing_time, BEIJING_TZ


class TimeRangeUtils:
    """时间范围工具类"""
    
    @staticmethod
    def get_time_range(range_type: str) -> Tuple[datetime, datetime]:
        """
        获取时间范围
        :param range_type: 'today', 'week', 'month', 'year', 'all'
        :return: (start_time, end_time)
        """
        now = get_current_beijing_time().replace(tzinfo=None)  # 获取北京时间但移除时区信息以便与数据库比较
        
        if range_type == 'today':
            # 本日：今天 00:00:00 - 23:59:59
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
        elif range_type == 'week':
            # 本周：本周一 00:00:00 - 本周日 23:59:59
            start_time = now - timedelta(days=now.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
            
        elif range_type == 'month':
            # 本月：本月1日 00:00:00 - 本月最后一天 23:59:59
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # 获取本月最后一天
            last_day = calendar.monthrange(now.year, now.month)[1]
            end_time = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
            
        elif range_type == 'year':
            # 本年：今年1月1日 00:00:00 - 今年12月31日 23:59:59
            start_time = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_time = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            
        elif range_type == 'all':
            # 累计：所有数据（设置一个足够大的时间范围）
            start_time = datetime(2020, 1, 1, 0, 0, 0)
            end_time = datetime(2099, 12, 31, 23, 59, 59, 999999)
            
        else:
            # 默认本周
            start_time = now - timedelta(days=now.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
        
        return start_time, end_time
    
    @staticmethod
    def get_range_display_text(range_type: str) -> str:
        """获取时间范围的显示文本"""
        start_time, end_time = TimeRangeUtils.get_time_range(range_type)
        
        if range_type == 'all':
            return "累计数据"
        elif range_type == 'today':
            return f"今日 ({start_time.strftime('%Y-%m-%d')})"
        elif range_type == 'week':
            return f"本周 ({start_time.strftime('%m-%d')} 至 {end_time.strftime('%m-%d')})"
        elif range_type == 'month':
            return f"本月 ({start_time.strftime('%Y-%m')})"
        elif range_type == 'year':
            return f"本年 ({start_time.strftime('%Y')})"
        else:
            return f"{start_time.strftime('%Y-%m-%d')} 至 {end_time.strftime('%Y-%m-%d')}"
    
    @staticmethod
    def validate_range_type(range_type: str) -> bool:
        """验证时间范围类型是否有效"""
        valid_ranges = ['today', 'week', 'month', 'year', 'all']
        return range_type in valid_ranges
    
    @staticmethod
    def get_valid_range_types() -> list:
        """获取所有有效的时间范围类型"""
        return ['today', 'week', 'month', 'year', 'all']

    @staticmethod
    def get_next_week_start() -> datetime:
        """获取下周一的开始时间"""
        now = datetime.now()
        days_until_next_monday = 7 - now.weekday()
        next_monday = now + timedelta(days=days_until_next_monday)
        return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_next_period_start(period_type: str = 'week') -> datetime:
        """获取下个周期的开始时间"""
        if period_type == 'week':
            return TimeRangeUtils.get_next_week_start()
        elif period_type == 'month':
            now = datetime.now()
            if now.month == 12:
                return datetime(now.year + 1, 1, 1, 0, 0, 0)
            else:
                return datetime(now.year, now.month + 1, 1, 0, 0, 0)
        else:
            return datetime.now() + timedelta(days=1)
    
    @staticmethod
    def get_range_type_display_name(range_type: str) -> str:
        """获取时间范围类型的显示名称"""
        display_names = {
            'today': '本日',
            'week': '本周',
            'month': '本月',
            'year': '本年',
            'all': '累计'
        }
        return display_names.get(range_type, range_type)
    
    @staticmethod
    def is_same_period(date1: datetime, date2: datetime, range_type: str) -> bool:
        """判断两个日期是否在同一个时间周期内"""
        if range_type == 'today':
            return date1.date() == date2.date()
        elif range_type == 'week':
            # 计算周一的日期
            monday1 = date1 - timedelta(days=date1.weekday())
            monday2 = date2 - timedelta(days=date2.weekday())
            return monday1.date() == monday2.date()
        elif range_type == 'month':
            return date1.year == date2.year and date1.month == date2.month
        elif range_type == 'year':
            return date1.year == date2.year
        elif range_type == 'all':
            return True
        else:
            return False
    
    @staticmethod
    def get_previous_period_range(range_type: str) -> Tuple[datetime, datetime]:
        """获取上一个周期的时间范围"""
        now = datetime.now()
        
        if range_type == 'today':
            # 昨天
            yesterday = now - timedelta(days=1)
            start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            
        elif range_type == 'week':
            # 上周
            last_week_start = now - timedelta(days=now.weekday() + 7)
            start_time = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
            
        elif range_type == 'month':
            # 上个月
            if now.month == 1:
                last_month = now.replace(year=now.year - 1, month=12, day=1)
            else:
                last_month = now.replace(month=now.month - 1, day=1)
            
            start_time = last_month.replace(hour=0, minute=0, second=0, microsecond=0)
            last_day = calendar.monthrange(last_month.year, last_month.month)[1]
            end_time = last_month.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
            
        elif range_type == 'year':
            # 去年
            last_year = now.replace(year=now.year - 1, month=1, day=1)
            start_time = last_year.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = last_year.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            
        else:
            # 默认返回当前周期
            return TimeRangeUtils.get_time_range(range_type)
        
        return start_time, end_time
