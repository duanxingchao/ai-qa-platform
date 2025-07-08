"""
数据库初始化脚本
用于创建数据库表和初始数据
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.database import db, create_tables_sql, execute_sql
# 导入所有模型以确保表被创建
from app.models import Question, Answer, Score, ReviewStatus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # 创建表
            logger.info("开始创建数据库表...")
            
            # 使用SQLAlchemy创建表
            db.create_all()
            logger.info("SQLAlchemy表创建完成")
            
            # 执行额外的SQL（索引等）
            sql_statements = create_tables_sql().split(';')
            for sql in sql_statements:
                sql = sql.strip()
                if sql and 'CREATE INDEX' in sql:
                    try:
                        execute_sql(sql)
                        logger.info(f"执行SQL成功: {sql[:50]}...")
                    except Exception as e:
                        # 索引可能已存在，忽略错误
                        logger.warning(f"SQL执行警告: {str(e)}")
            
            logger.info("数据库初始化完成！")
            
            # 打印表信息
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"已创建的表: {', '.join(tables)}")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    init_database() 