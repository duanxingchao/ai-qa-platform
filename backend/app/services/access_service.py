"""
访问统计服务
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from app.models.user import AccessLog
from app.utils.database import db
from app.utils.datetime_helper import utc_to_beijing_str

class AccessService:
    """访问统计服务类"""
    
    @staticmethod
    def get_access_stats():
        """获取访问统计数据"""
        today = date.today()

        # 系统总登录次数
        total_logins = AccessLog.query.filter_by(action='login').count()

        # 今日登录次数
        today_logins = AccessLog.query.filter(
            AccessLog.action == 'login',
            func.date(AccessLog.created_at) == today
        ).count()

        # 活跃用户数（最近30天内有登录记录的用户）
        thirty_days_ago = today - timedelta(days=30)
        active_users = AccessLog.query.filter(
            AccessLog.action == 'login',
            func.date(AccessLog.created_at) >= thirty_days_ago
        ).distinct(AccessLog.user_id).count()

        # 在线用户数：以“每个用户的最近一次访问行为”为准
        # 规则：最近一次行为为 login 且发生在窗口期内（默认12小时）即视为在线
        # 说明：避免“登录超过1小时未登出”的用户被错误判定为离线
        window_hours = 12
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)

        # 获取每个用户的最后一次访问时间
        last_actions_subq = db.session.query(
            AccessLog.user_id,
            func.max(AccessLog.created_at).label('last_time')
        ).group_by(AccessLog.user_id).subquery()

        # 关联取出该最后一次访问记录，并判断是否为 login
        last_actions = db.session.query(AccessLog).join(
            last_actions_subq,
            (AccessLog.user_id == last_actions_subq.c.user_id) &
            (AccessLog.created_at == last_actions_subq.c.last_time)
        ).filter(
            AccessLog.created_at >= cutoff_time
        ).all()

        online_users = sum(1 for a in last_actions if a.action == 'login')

        return {
            'total_logins': total_logins,
            'today_logins': today_logins,
            'active_users': active_users,
            'online_users': online_users
        }
    
    @staticmethod
    def get_access_logs_with_duration(page=1, page_size=20, action=''):
        """获取带时长的访问日志"""
        # 构建查询条件
        query = AccessLog.query

        if action:
            query = query.filter_by(action=action)

        # 分页查询
        pagination = query.order_by(AccessLog.created_at.desc())\
            .paginate(page=page, per_page=page_size, error_out=False)

        access_logs = pagination.items

        result = []
        for log in access_logs:
            # 如果是登录记录，计算时长
            if log.action == 'login':
                # 查找对应的登出记录
                logout_log = AccessLog.query.filter(
                    and_(
                        AccessLog.user_id == log.user_id,
                        AccessLog.action == 'logout',
                        AccessLog.created_at > log.created_at
                    )
                ).order_by(AccessLog.created_at.asc()).first()

                # 计算在线时长
                duration_text = '计算中'

                if logout_log:
                    duration_seconds = (logout_log.created_at - log.created_at).total_seconds()
                    duration = int(duration_seconds / 60)  # 转换为分钟

                    # 格式化时长显示
                    if duration >= 60:
                        hours = duration // 60
                        minutes = duration % 60
                        duration_text = f"{hours}小时{minutes}分钟"
                    else:
                        duration_text = f"{duration}分钟"

                result.append({
                    'username': log.username,
                    'action': log.action,
                    'created_at': utc_to_beijing_str(log.created_at),
                    'ip_address': log.ip_address,
                    'duration': duration_text
                })
            else:
                # 登出记录不需要计算时长
                result.append({
                    'username': log.username,
                    'action': log.action,
                    'created_at': utc_to_beijing_str(log.created_at),
                    'ip_address': log.ip_address,
                    'duration': '-'
                })

        return {
            'logs': result,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        }
