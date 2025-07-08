"""
API蓝图模块
"""
from flask import Blueprint

# 创建蓝图
sync_bp = Blueprint('sync', __name__)
question_bp = Blueprint('question', __name__)
process_bp = Blueprint('process', __name__)
review_bp = Blueprint('review', __name__)

# 导入路由
from . import sync_api, question_api, process_api, review_api 