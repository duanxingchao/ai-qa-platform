"""
Flask应用初始化模块
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

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
    
    # 启动定时任务调度器
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
    from app.api.scheduler_api import scheduler_bp
    
    app.register_blueprint(sync_bp, url_prefix='/api/sync')
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    app.register_blueprint(process_bp, url_prefix='/api/process')
    app.register_blueprint(review_bp, url_prefix='/api/review')
    app.register_blueprint(scheduler_bp, url_prefix='/api/scheduler')


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
    """初始化定时任务调度器"""
    try:
        from app.services.scheduler_service import scheduler_service
        scheduler_service.initialize(app)
        app.logger.info("定时任务调度器初始化完成")
    except Exception as e:
        app.logger.error(f"定时任务调度器初始化失败: {str(e)}")
        # 不抛出异常，允许应用继续运行 