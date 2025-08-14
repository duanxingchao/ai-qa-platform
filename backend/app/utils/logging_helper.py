"""
日志配置辅助工具
"""

import logging
import logging.handlers
import os
from datetime import datetime
from app.utils.datetime_helper import get_current_beijing_time


class BeijingTimeFormatter(logging.Formatter):
    """北京时间格式化器"""
    
    def formatTime(self, record, datefmt=None):
        """使用北京时间格式化时间"""
        beijing_time = get_current_beijing_time()
        if datefmt:
            return beijing_time.strftime(datefmt)
        else:
            return beijing_time.strftime('%Y-%m-%d %H:%M:%S')


def setup_beijing_logging(app):
    """设置使用北京时间的日志配置"""
    
    # 获取日志级别
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = app.config.get('LOG_FILE', 'app.log')
    
    # 创建北京时间格式化器
    formatter = BeijingTimeFormatter(log_format)
    
    # 设置根日志器级别
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # 文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 使用RotatingFileHandler进行日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # 添加处理器到根日志器
        logging.getLogger().addHandler(file_handler)
    
    # 添加控制台处理器到根日志器
    logging.getLogger().addHandler(console_handler)
    
    # 设置Flask应用的日志器
    app.logger.handlers.clear()  # 清除默认处理器
    app.logger.addHandler(console_handler)
    if log_file:
        app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # 设置第三方库的日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    app.logger.info(f"日志系统初始化完成，级别: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """获取配置好的日志器"""
    return logging.getLogger(name)
