"""
管理员API接口
"""
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.user import User, UserApplication
from app.utils.database import db
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        role = request.args.get('role', '')
        
        # 构建查询
        query = db.session.query(User)
        
        # 关键词搜索
        if keyword:
            query = query.filter(User.username.ilike(f'%{keyword}%'))
        
        # 状态筛选
        if status:
            query = query.filter(User.status == status)
        
        # 角色筛选
        if role:
            query = query.filter(User.role == role)
        
        # 排序和分页
        query = query.order_by(desc(User.created_at))
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()
        
        # 序列化数据
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'role': user.role,
                'status': user.status,
                'login_count': user.login_count,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return success_response('获取用户列表成功', {
            'users': data,
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        current_app.logger.error(f"获取用户列表失败: {str(e)}")
        return error_response(f'获取用户列表失败: {str(e)}')

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """更新用户信息"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据为空')
        
        user = db.session.get(User, user_id)
        if not user:
            return error_response('用户不存在')
        
        # 更新用户信息
        if 'status' in data:
            user.status = data['status']
        if 'role' in data:
            user.role = data['role']
        db.session.commit()
        
        return success_response('用户信息更新成功')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新用户信息失败: {str(e)}")
        return error_response(f'更新用户信息失败: {str(e)}')

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return error_response('用户不存在')
        
        db.session.delete(user)
        db.session.commit()
        
        return success_response('用户删除成功')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除用户失败: {str(e)}")
        return error_response(f'删除用户失败: {str(e)}')

@admin_bp.route('/applications', methods=['GET'])
@login_required
@admin_required
def get_applications():
    """获取申请列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        status = request.args.get('status', 'pending')

        # 构建查询 - 查找用户申请表
        query = db.session.query(UserApplication)

        # 状态筛选
        if status:
            query = query.filter(UserApplication.status == status)

        # 排序和分页
        query = query.order_by(desc(UserApplication.created_at))

        # 获取总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * page_size
        applications = query.offset(offset).limit(page_size).all()

        # 序列化数据
        data = []
        for app in applications:
            data.append({
                'id': app.id,
                'username': app.username,
                'display_name': app.display_name,
                'apply_role': app.apply_role,
                'status': app.status,
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'reviewed_at': app.reviewed_at.isoformat() if app.reviewed_at else None,
                'reviewer': app.reviewer.username if app.reviewer else None
            })

        return success_response('获取申请列表成功', {
            'applications': data,
            'total': total,
            'page': page,
            'page_size': page_size
        })

    except Exception as e:
        current_app.logger.error(f"获取申请列表失败: {str(e)}")
        return error_response(f'获取申请列表失败: {str(e)}')

@admin_bp.route('/applications/<int:app_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_application(app_id):
    """批准申请"""
    try:
        application = db.session.get(UserApplication, app_id)
        if not application:
            return error_response('申请不存在')

        # 创建新用户
        new_user = User(
            username=application.username,
            display_name=application.display_name,
            password_hash=application.password_hash,
            role=application.apply_role,
            status='active'
        )

        # 更新申请状态
        application.status = 'approved'
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = 1  # 当前管理员ID，应该从JWT中获取

        db.session.add(new_user)
        db.session.commit()

        return success_response('申请已批准')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"批准申请失败: {str(e)}")
        return error_response(f'批准申请失败: {str(e)}')

@admin_bp.route('/applications/<int:app_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_application(app_id):
    """拒绝申请"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', '未通过审核')

        application = db.session.get(UserApplication, app_id)
        if not application:
            return error_response('申请不存在')

        application.status = 'rejected'
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = 1  # 当前管理员ID，应该从JWT中获取

        db.session.commit()

        return success_response('申请已拒绝')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"拒绝申请失败: {str(e)}")
        return error_response(f'拒绝申请失败: {str(e)}')

@admin_bp.route('/statistics', methods=['GET'])
@login_required
@admin_required
def get_admin_statistics():
    """获取管理统计数据"""
    try:
        # 用户统计
        total_users = db.session.query(User).count()
        active_users = db.session.query(User).filter(User.status == 'active').count()
        pending_users = db.session.query(User).filter(User.status == 'pending').count()
        
        # 最近7天新用户
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = db.session.query(User).filter(User.created_at >= week_ago).count()
        
        data = {
            'total_users': total_users,
            'active_users': active_users,
            'pending_applications': pending_users,
            'new_users_this_week': new_users_week,
            'user_status_distribution': {
                'active': active_users,
                'pending': pending_users,
                'inactive': total_users - active_users - pending_users
            }
        }
        
        return success_response('获取统计数据成功', data)
        
    except Exception as e:
        current_app.logger.error(f"获取统计数据失败: {str(e)}")
        return error_response(f'获取统计数据失败: {str(e)}')
