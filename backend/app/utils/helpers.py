"""
辅助工具函数
包含业务主键生成、数据验证等通用函数
"""
import hashlib
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_business_id(pageid, sendmessagetime, query):
    """
    生成业务主键：基于关键字段的MD5哈希值
    确保相同问题的唯一性和稳定性
    
    Args:
        pageid: 页面ID
        sendmessagetime: 发送时间
        query: 查询内容
    
    Returns:
        str: 32位的MD5哈希值
    """
    # 标准化数据
    pageid_str = str(pageid) if pageid else ''
    time_str = sendmessagetime.isoformat() if isinstance(sendmessagetime, datetime) else str(sendmessagetime)
    query_str = query.strip() if query else ''
    
    # 组合字段
    data_str = f"{pageid_str}_{time_str}_{query_str}"
    
    # 生成MD5哈希
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def is_valid_query(query):
    """
    验证查询内容是否有效
    
    Args:
        query: 查询内容
    
    Returns:
        bool: 是否有效
    """
    if not query or not isinstance(query, str):
        return False
    
    # 去除空白字符后检查
    cleaned_query = query.strip()
    
    # 检查是否为空
    if not cleaned_query:
        return False
    
    # 检查是否只包含特殊字符
    if re.match(r'^[^\w\u4e00-\u9fa5]+$', cleaned_query):
        return False
    
    # 检查最小长度（至少2个字符）
    if len(cleaned_query) < 2:
        return False
    
    return True

def clean_text(text):
    """
    清理文本内容
    
    Args:
        text: 原始文本
    
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ''
    
    # 去除首尾空白
    text = text.strip()
    
    # 替换多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除控制字符
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    return text

def calculate_average_score(scores):
    """
    计算平均分
    
    Args:
        scores: 分数列表或字典
    
    Returns:
        float: 平均分（保留2位小数）
    """
    if isinstance(scores, dict):
        # 从字典中提取分数
        score_values = [v for k, v in scores.items() if k.startswith('score_') and v is not None]
    else:
        score_values = [s for s in scores if s is not None]
    
    if not score_values:
        return 0.0
    
    avg = sum(score_values) / len(score_values)
    return round(avg, 2)

def format_datetime(dt):
    """
    格式化日期时间
    
    Args:
        dt: datetime对象或字符串
    
    Returns:
        str: 格式化后的日期时间字符串
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    
    if not isinstance(dt, datetime):
        return str(dt)
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def paginate_query(query, page, page_size, max_page_size=100):
    """
    分页查询辅助函数
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码（从1开始）
        page_size: 每页大小
        max_page_size: 最大每页大小
    
    Returns:
        dict: 包含分页信息和数据的字典
    """
    # 验证参数
    page = max(1, int(page))
    page_size = min(max(1, int(page_size)), max_page_size)
    
    # 执行分页查询
    paginated = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return {
        'items': paginated.items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page,
        'has_prev': paginated.has_prev,
        'has_next': paginated.has_next
    }

def get_processing_status_display(status):
    """
    获取处理状态的显示文本
    
    Args:
        status: 状态代码
    
    Returns:
        str: 状态显示文本
    """
    status_map = {
        'pending': '待处理',
        'cleaning': '清洗中',
        'classifying': '分类中',
        'generating': '生成答案中',
        'scoring': '评分中',
        'completed': '已完成',
        'failed': '处理失败'
    }
    return status_map.get(status, status)

def batch_process(items, batch_size, process_func):
    """
    批量处理数据
    
    Args:
        items: 待处理的数据列表
        batch_size: 批次大小
        process_func: 处理函数
    
    Returns:
        list: 处理结果
    """
    results = []
    total = len(items)
    
    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        try:
            batch_results = process_func(batch)
            results.extend(batch_results)
            logger.info(f"批处理进度: {min(i + batch_size, total)}/{total}")
        except Exception as e:
            logger.error(f"批处理失败: {str(e)}")
            # 继续处理下一批
            continue
    
    return results 