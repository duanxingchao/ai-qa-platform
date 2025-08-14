"""
数据库工具模块
提供数据库连接、初始化等功能
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# 创建全局数据库实例
db = SQLAlchemy()

logger = logging.getLogger(__name__)

def init_db(app):
    """初始化数据库并根据方言补充外部源表等结构"""
    db.init_app(app)

    with app.app_context():
        # 创建模型声明的所有表
        db.create_all()
        logger.info("数据库表创建完成")

        # 根据数据库方言创建/补充外部表（如 table1）与索引
        try:
            dialect_name = db.session.bind.dialect.name if db.session.bind else ""
            if dialect_name == "sqlite":
                # SQLite 版本的 table1 与必要索引/约束（尽量使用通用语法）
                sqlite_sql = text(
                    """
                    CREATE TABLE IF NOT EXISTS table1 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pageid VARCHAR(100),
                        devicetypename VARCHAR(50),
                        sendmessagetime TIMESTAMP,
                        query TEXT,
                        answer TEXT,
                        serviceid VARCHAR(50),
                        qatype VARCHAR(50),
                        intent VARCHAR(100),
                        classification VARCHAR(50),
                        iskeyboardinput BOOLEAN,
                        isstopanswer BOOLEAN
                    );
                    """
                )
                db.session.execute(sqlite_sql)
                db.session.commit()
                logger.info("SQLite 方言下已确保创建 table1 表")
            else:
                # 其他方言（PostgreSQL 等）执行预置的建表与索引 SQL
                sql_statements = create_tables_sql().split(';')
                for sql in sql_statements:
                    stmt = sql.strip()
                    if not stmt:
                        continue
                    try:
                        db.session.execute(text(stmt))
                        db.session.commit()
                    except Exception as exec_err:
                        # 多次运行可能触发对象已存在等非致命错误
                        db.session.rollback()
                        logger.debug(f"忽略可预期建表/索引错误: {exec_err}")
                logger.info("已执行方言通用建表与索引 SQL")
        except Exception as e:
            logger.error(f"补充外部表/索引失败: {e}")

def get_db_session(database_uri):
    """获取独立的数据库会话（用于定时任务等场景）"""
    engine = create_engine(database_uri)
    Session = sessionmaker(bind=engine)
    return Session()

def execute_sql(sql, params=None):
    """执行原始SQL语句"""
    try:
        result = db.session.execute(text(sql), params or {})
        db.session.commit()
        return result
    except Exception as e:
        db.session.rollback()
        logger.error(f"SQL执行失败: {str(e)}")
        raise

def create_tables_sql():
    """返回创建表的SQL语句"""
    return """
    -- 创建源表（如果不存在）
    CREATE TABLE IF NOT EXISTS table1 (
        id SERIAL PRIMARY KEY,
        pageid VARCHAR(100),
        devicetypename VARCHAR(50),
        sendmessagetime TIMESTAMP,
        query TEXT,
        answer TEXT,
        serviceid VARCHAR(50),
        qatype VARCHAR(50),
        intent VARCHAR(100),
        classification VARCHAR(50),
        iskeyboardinput BOOLEAN,
        isstopanswer BOOLEAN
    );
    
    -- 创建questions表
    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        business_id VARCHAR(64) UNIQUE NOT NULL,
        pageid VARCHAR(100),
        devicetypename VARCHAR(50),
        query TEXT NOT NULL,
        sendmessagetime TIMESTAMP,
        classification VARCHAR(50),
        serviceid VARCHAR(50),
        qatype VARCHAR(50),
        intent VARCHAR(100),
        iskeyboardinput BOOLEAN,
        isstopanswer BOOLEAN,
        is_deleted BOOLEAN DEFAULT FALSE,
        processing_status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 创建answers表
    CREATE TABLE IF NOT EXISTS answers (
        id SERIAL PRIMARY KEY,
        question_business_id VARCHAR(64) NOT NULL,
        answer_text TEXT,
        assistant_type VARCHAR(50) NOT NULL,
        is_scored BOOLEAN DEFAULT FALSE,
        answer_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_business_id) REFERENCES questions(business_id)
    );
    
    -- 创建scores表
    CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        answer_id INTEGER NOT NULL,
        score_1 INTEGER CHECK (score_1 >= 1 AND score_1 <= 5),
        score_2 INTEGER CHECK (score_2 >= 1 AND score_2 <= 5),
        score_3 INTEGER CHECK (score_3 >= 1 AND score_3 <= 5),
        score_4 INTEGER CHECK (score_4 >= 1 AND score_4 <= 5),
        score_5 INTEGER CHECK (score_5 >= 1 AND score_5 <= 5),
        dimension_1_name VARCHAR(50),
        dimension_2_name VARCHAR(50),
        dimension_3_name VARCHAR(50),
        dimension_4_name VARCHAR(50),
        dimension_5_name VARCHAR(50),
        average_score DECIMAL(3,2),
        comment TEXT,
        rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (answer_id) REFERENCES answers(id)
    );
    
    -- 创建review_status表
    CREATE TABLE IF NOT EXISTS review_status (
        id SERIAL PRIMARY KEY,
        question_business_id VARCHAR(64) UNIQUE NOT NULL,
        is_reviewed BOOLEAN DEFAULT FALSE,
        reviewer_id VARCHAR(50),
        review_comment TEXT,
        reviewed_at TIMESTAMP,
        FOREIGN KEY (question_business_id) REFERENCES questions(business_id)
    );
    
    -- 创建索引以提高查询性能
    CREATE INDEX IF NOT EXISTS idx_questions_sendmessagetime ON questions(sendmessagetime);
    CREATE INDEX IF NOT EXISTS idx_questions_classification ON questions(classification);
    CREATE INDEX IF NOT EXISTS idx_questions_processing_status ON questions(processing_status);
    CREATE INDEX IF NOT EXISTS idx_answers_question_business_id ON answers(question_business_id);
    CREATE INDEX IF NOT EXISTS idx_answers_assistant_type ON answers(assistant_type);
    """ 