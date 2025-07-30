"""
配置文件
包含数据库连接、API配置、定时任务配置等
"""
import os
from datetime import timedelta

class Config:
    """基础配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # API配置
    API_TITLE = 'AI问答回流数据处理平台 API'
    API_VERSION = 'v1.0'
    API_DESCRIPTION = '提供数据同步、处理、分析和评估等功能的RESTful API'
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:5173', 'http://127.0.0.1:3000', 'http://localhost:5174', 'http://127.0.0.1:5174']
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 外部API配置
    CLASSIFY_API_URL = os.environ.get('CLASSIFY_API_URL') or 'http://localhost:8001'
    DOUBAO_API_URL = os.environ.get('DOUBAO_API_URL') or 'http://localhost:8002'  # Mock豆包API
    XIAOTIAN_API_URL = os.environ.get('XIAOTIAN_API_URL') or 'http://localhost:8003'  # Mock小天API
    SCORE_API_URL = os.environ.get('SCORE_API_URL') or 'http://localhost:8004'

    # API密钥配置
    CLASSIFY_API_KEY = os.environ.get('CLASSIFY_API_KEY') or 'classify-dev-key'
    DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY') or 'doubao-dev-key'
    XIAOTIAN_API_KEY = os.environ.get('XIAOTIAN_API_KEY') or 'xiaotian-dev-key'
    SCORE_API_KEY = os.environ.get('SCORE_API_KEY') or 'score-dev-key'

    # API超时配置（秒）
    API_TIMEOUT = 30
    API_RETRY_TIMES = 3

    # API请求配置
    API_RETRY_DELAY = 1.0  # 重试延迟（秒）
    API_RETRY_BACKOFF_FACTOR = 2.0  # 退避因子
    API_REQUEST_HEADERS = {
        'Content-Type': 'application/json',
        'User-Agent': 'AI-QA-Platform/1.0'
    }
    
    # 自动化工作流配置（统一调度）
    AUTO_PROCESS_ON_STARTUP = False  # 启动时立即处理已有数据 - 已禁用以避免自动处理
    SCHEDULER_ENABLED = False  # 完全禁用调度器 - 防止自动启动任何任务
    WORKFLOW_INTERVAL_MINUTES = int(os.environ.get('WORKFLOW_INTERVAL_MINUTES', 3))  # 工作流执行间隔（分钟）
    DATA_CHECK_ENABLED = True  # 是否启用数据检测
    AUTO_SUSPEND_WHEN_NO_DATA = True  # 无数据时自动挂起
    MIN_BATCH_SIZE = 1  # 最小批处理大小，小于此数量时挂起
    
    # Mock服务自动启动配置
    AUTO_START_MOCK_SERVICES = True  # 是否自动启动Mock服务
    MOCK_SERVICES_ENABLED = True  # Mock服务是否启用
    
    # 批处理配置
    BATCH_SIZE = 100  # 批处理大小
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'app.log'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class LocalTestConfig(Config):
    """本地测试配置（使用SQLite）"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ai_qa_platform.db'
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'local': LocalTestConfig,  # 新增本地测试配置
    'default': DevelopmentConfig
} 