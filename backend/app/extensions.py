"""
Flask扩展初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db) 