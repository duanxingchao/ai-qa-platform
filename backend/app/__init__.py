"""
Flask应用初始化模块
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import config
from app.utils.database import db, init_db


def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 配置日志
    configure_logging(app)
    
    # 初始化数据库
    with app.app_context():
        init_db(app)
    
    # 启动定时任务
    if not app.testing:
        init_scheduler(app)
    
    return app


def init_extensions(app):
    """初始化Flask扩展"""
    # 数据库已在utils中初始化
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # JWT
    JWTManager(app)


def register_blueprints(app):
    """注册蓝图"""
    from app.api import sync_bp, question_bp, process_bp, review_bp
    
    app.register_blueprint(sync_bp, url_prefix='/api/sync')
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    app.register_blueprint(process_bp, url_prefix='/api/process')
    app.register_blueprint(review_bp, url_prefix='/api/review')


def configure_logging(app):
    """配置日志"""
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format=app.config['LOG_FORMAT'],
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)


def init_scheduler(app):
    """初始化定时任务"""
    scheduler = BackgroundScheduler()
    
    # 导入任务
    from app.services.sync_service import sync_data_task
    
    # 添加定时任务
    scheduler.add_job(
        func=lambda: sync_data_task(app),
        trigger='interval',
        minutes=app.config['SYNC_INTERVAL_MINUTES'],
        id='sync_data_job',
        replace_existing=True
    )
    
    scheduler.start()
    
    # 确保程序退出时关闭调度器
    import atexit
    atexit.register(lambda: scheduler.shutdown()) 