"""
认证相关API接口
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.user import User, UserApplication, AccessLog
from app.utils.database import db
from app.utils.response import api_response, error_response
from app.utils.datetime_helper import utc_to_beijing_str

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return error_response('用户名和密码不能为空', 400)
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return error_response('用户名或密码错误', 401)
        
        # 验证密码
        if not user.check_password(password):
            return error_response('用户名或密码错误', 401)
        
        # 检查用户状态
        if user.status != 'active':
            return error_response('账户已被禁用，请联系管理员', 403)
        
        # 创建访问令牌，包含用户角色信息
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7),
            additional_claims={'role': user.role}
        )
        
        # 更新登录信息
        user.last_login_at = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        
        # 记录访问日志
        access_log = AccessLog(
            user_id=user.id,
            username=user.username,
            action='login',
            ip_address=request.remote_addr
        )
        
        db.session.add(access_log)
        db.session.commit()
        
        return api_response({
            'token': access_token,
            'user': user.to_dict()
        }, '登录成功')
        
    except Exception as e:
        current_app.logger.error(f"登录失败: {str(e)}")
        return error_response('登录失败，请稍后重试', 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user:
            # 记录访问日志
            access_log = AccessLog(
                user_id=user.id,
                username=user.username,
                action='logout',
                ip_address=request.remote_addr
            )
            db.session.add(access_log)
            db.session.commit()
        
        return api_response(None, '登出成功')
        
    except Exception as e:
        current_app.logger.error(f"登出失败: {str(e)}")
        return error_response('登出失败', 500)

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """验证token有效性"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.status != 'active':
            return error_response('用户不存在或已被禁用', 401)
        
        return api_response({
            'user': user.to_dict()
        }, 'Token有效')
        
    except Exception as e:
        current_app.logger.error(f"Token验证失败: {str(e)}")
        return error_response('Token验证失败', 401)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 404)
        
        return api_response({
            'user': user.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取用户信息失败: {str(e)}")
        return error_response('获取用户信息失败', 500)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册申请"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        apply_role = data.get('apply_role', 'user').strip()
        
        if not username or not password:
            return error_response('用户名和密码不能为空', 400)
        
        if apply_role not in ['admin', 'user']:
            return error_response('申请角色无效', 400)
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return error_response('用户名已存在', 400)
        
        # 检查是否已有待审核的申请
        existing_application = UserApplication.query.filter_by(
            username=username, 
            status='pending'
        ).first()
        if existing_application:
            return error_response('您已有待审核的申请，请耐心等待', 400)
        
        # 创建申请记录
        from werkzeug.security import generate_password_hash
        application = UserApplication(
            username=username,
            password_hash=generate_password_hash(password),
            apply_role=apply_role
        )
        
        db.session.add(application)
        db.session.commit()
        
        return api_response({
            'application_id': application.id
        }, '注册申请已提交，请等待管理员审核')
        
    except Exception as e:
        current_app.logger.error(f"注册申请失败: {str(e)}")
        return error_response('注册申请失败，请稍后重试', 500)

@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    """检查用户名是否可用"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        username = data.get('username', '').strip()
        if not username:
            return error_response('用户名不能为空', 400)
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return api_response({
                'available': False
            }, '用户名已存在')
        
        # 检查是否有待审核的申请
        existing_application = UserApplication.query.filter_by(
            username=username, 
            status='pending'
        ).first()
        if existing_application:
            return api_response({
                'available': False
            }, '用户名已有待审核申请')
        
        return api_response({
            'available': True
        }, '用户名可用')
        
    except Exception as e:
        current_app.logger.error(f"检查用户名失败: {str(e)}")
        return error_response('检查用户名失败', 500)
