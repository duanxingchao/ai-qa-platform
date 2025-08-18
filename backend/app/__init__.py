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
    from app.api import sync_bp, question_bp, process_bp, review_bp, dashboard_bp, analysis_bp
    from app.api.scheduler_api import scheduler_bp
    from app.api.mock_api import mock_bp
    from app.api.display_api import display_bp
    from app.api.config_api import config_bp
    from app.api.classification_api import classification_bp
    from app.api.answer_generation_api import answer_generation_bp
    from app.api.answer_api import answer_bp
    from app.api.scores_api import scores_bp as scores_api_bp

    # 注释掉缺失的API模块，待后续添加
    from app.api.badcase_api import badcase_bp
    from app.api.auth_api import auth_bp
    from app.api.admin_api import admin_bp
    from app.api.stats_api import stats_bp

    app.register_blueprint(sync_bp, url_prefix='/api/sync')
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    app.register_blueprint(process_bp, url_prefix='/api/process')
    app.register_blueprint(review_bp, url_prefix='/api/review')
    app.register_blueprint(scheduler_bp, url_prefix='/api/scheduler')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')  # 启用热词分析API
    app.register_blueprint(mock_bp, url_prefix='/api/mock')
    app.register_blueprint(display_bp, url_prefix='/api/display')
    app.register_blueprint(badcase_bp)  # badcase API (已在蓝图中定义了url_prefix)
    app.register_blueprint(config_bp, url_prefix='/api/config')   # 系统配置API
    app.register_blueprint(classification_bp)  # 分类管理API
    app.register_blueprint(answer_generation_bp)  # 答案生成管理API
    app.register_blueprint(answer_bp, url_prefix='/api/answers')  # 答案管理API
    app.register_blueprint(scores_api_bp, url_prefix='/api/scores')  # 评分管理API

    # 注册认证API
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # 注册用户管理API
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')


def configure_logging(app):
    """配置日志"""
    from app.utils.logging_helper import setup_beijing_logging
    setup_beijing_logging(app)


def init_scheduler(app):
    """初始化定时任务调度器"""
    try:
        # 检查是否启用调度器
        if not app.config.get('SCHEDULER_ENABLED', True):
            app.logger.info("调度器已被配置禁用，跳过初始化")
            return

        from app.services.scheduler_service import scheduler_service
        scheduler_service.initialize(app)
        app.logger.info("定时任务调度器初始化完成")
    except Exception as e:
        app.logger.error(f"定时任务调度器初始化失败: {str(e)}")
        # 不抛出异常，允许应用继续运行