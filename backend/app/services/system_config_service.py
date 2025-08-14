"""
系统配置服务
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.database import db
from app.models.system_config import SystemConfig
from app.models.config_change_history import ConfigChangeHistory
from app.utils.time_utils import TimeRangeUtils


class SystemConfigService:
    """系统配置服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_config(self, key: str, default_value: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default_value: 默认值
            
        Returns:
            配置值
        """
        try:
            return SystemConfig.get_config(key, default_value)
        except Exception as e:
            self.logger.error(f"获取配置失败 {key}: {str(e)}")
            return default_value
    
    def update_config(self, key: str, value: Any, config_type: str = None, description: str = None) -> bool:
        """
        更新配置值
        
        Args:
            key: 配置键名
            value: 配置值
            config_type: 配置类型
            description: 配置描述
            
        Returns:
            bool: 更新是否成功
        """
        try:
            config = db.session.query(SystemConfig).filter_by(config_key=key).first()
            
            if config:
                # 更新现有配置
                config.set_typed_value(value)
                if description:
                    config.description = description
                config.updated_at = datetime.utcnow()
            else:
                # 创建新配置
                if not config_type:
                    # 根据值类型推断配置类型
                    if isinstance(value, bool):
                        config_type = 'boolean'
                    elif isinstance(value, (int, float)):
                        config_type = 'number'
                    elif isinstance(value, (dict, list)):
                        config_type = 'json'
                    else:
                        config_type = 'string'
                
                config = SystemConfig(
                    config_key=key,
                    config_type=config_type,
                    description=description
                )
                config.set_typed_value(value)
                db.session.add(config)
            
            db.session.commit()
            self.logger.info(f"更新配置成功: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新配置失败 {key}: {str(e)}")
            db.session.rollback()
            return False
    
    def get_all_configs(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            dict: 所有配置的键值对
        """
        try:
            return SystemConfig.get_all_configs()
        except Exception as e:
            self.logger.error(f"获取所有配置失败: {str(e)}")
            return {}
    
    def get_configs_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """
        根据前缀获取配置
        
        Args:
            prefix: 配置键前缀
            
        Returns:
            dict: 匹配前缀的配置
        """
        try:
            return SystemConfig.get_configs_by_prefix(prefix)
        except Exception as e:
            self.logger.error(f"根据前缀获取配置失败 {prefix}: {str(e)}")
            return {}
    
    def get_config_list(self, prefix: str = None) -> List[Dict[str, Any]]:
        """
        获取配置列表（包含详细信息）
        
        Args:
            prefix: 配置键前缀（可选）
            
        Returns:
            list: 配置详细信息列表
        """
        try:
            query = db.session.query(SystemConfig)
            
            if prefix:
                query = query.filter(SystemConfig.config_key.like(f'{prefix}%'))
            
            configs = query.order_by(SystemConfig.config_key).all()
            
            return [config.to_dict() for config in configs]
            
        except Exception as e:
            self.logger.error(f"获取配置列表失败: {str(e)}")
            return []
    
    def delete_config(self, key: str) -> bool:
        """
        删除配置
        
        Args:
            key: 配置键名
            
        Returns:
            bool: 删除是否成功
        """
        try:
            config = db.session.query(SystemConfig).filter_by(config_key=key).first()
            
            if not config:
                self.logger.warning(f"配置不存在: {key}")
                return False
            
            db.session.delete(config)
            db.session.commit()
            
            self.logger.info(f"删除配置成功: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除配置失败 {key}: {str(e)}")
            db.session.rollback()
            return False
    
    def get_monitor_configs(self) -> Dict[str, Any]:
        """
        获取监控相关配置
        
        Returns:
            dict: 监控配置
        """
        try:
            monitor_configs = self.get_configs_by_prefix('badcase_')
            
            # 添加默认配置（如果不存在）
            default_configs = {
                'badcase_score_threshold': 2.5
            }
            
            for key, default_value in default_configs.items():
                if key not in monitor_configs:
                    monitor_configs[key] = default_value
            
            return monitor_configs
            
        except Exception as e:
            self.logger.error(f"获取监控配置失败: {str(e)}")
            return {'badcase_score_threshold': 2.5}
    
    def update_monitor_config(self, key: str, value: Any) -> bool:
        """
        更新监控配置
        
        Args:
            key: 配置键名
            value: 配置值
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证监控配置键名
            valid_keys = ['badcase_score_threshold']
            if key not in valid_keys:
                self.logger.error(f"无效的监控配置键名: {key}")
                return False
            
            # 验证配置值
            if key == 'badcase_score_threshold':
                try:
                    new_threshold = float(value)
                    if new_threshold < 0 or new_threshold > 5:
                        self.logger.error(f"badcase阈值必须在0-5之间: {value}")
                        return False

                    # 获取当前有效阈值
                    current_threshold = self.get_config('badcase_score_threshold', 2.5)
                    current_threshold = float(current_threshold)

                    # 如果值没有变化，直接返回成功
                    if current_threshold == new_threshold:
                        self.logger.info(f"badcase阈值未发生变化: {new_threshold}")
                        return True

                    # 延迟生效：安排到下周一生效
                    next_week_start = TimeRangeUtils.get_next_week_start()
                    return self.schedule_config_change(
                        key=key,
                        new_value=new_threshold,
                        effective_time=next_week_start,
                        reason=f"用户手动调整badcase检测阈值从 {current_threshold} 到 {new_threshold}",
                        changed_by='admin'
                    )

                except (ValueError, TypeError):
                    self.logger.error(f"badcase阈值必须是数字: {value}")
                    return False

            # 其他配置立即生效
            description_map = {
                'badcase_score_threshold': 'Badcase评分阈值，当yoyo模型任一评分维度低于此阈值时标记为badcase'
            }

            return self.update_config(
                key=key,
                value=value,
                config_type='number',
                description=description_map.get(key)
            )
            
        except Exception as e:
            self.logger.error(f"更新监控配置失败 {key}: {str(e)}")
            return False
    
    def reset_config_to_default(self, key: str) -> bool:
        """
        重置配置为默认值
        
        Args:
            key: 配置键名
            
        Returns:
            bool: 重置是否成功
        """
        try:
            default_values = {
                'badcase_score_threshold': 2.5
            }
            
            if key not in default_values:
                self.logger.error(f"没有默认值的配置: {key}")
                return False
            
            return self.update_config(key, default_values[key])
            
        except Exception as e:
            self.logger.error(f"重置配置失败 {key}: {str(e)}")
            return False

    def schedule_config_change(self, key: str, new_value: Any, effective_time: datetime, reason: str = None, changed_by: str = None) -> bool:
        """
        安排配置变更（延迟生效）

        Args:
            key: 配置键
            new_value: 新值
            effective_time: 生效时间
            reason: 变更原因
            changed_by: 变更人

        Returns:
            bool: 安排是否成功
        """
        try:
            config = db.session.query(SystemConfig).filter_by(config_key=key).first()

            if not config:
                self.logger.error(f"配置不存在: {key}")
                return False

            # 保存当前值作为previous_value
            current_effective_value = config.get_effective_value()
            config.previous_value = str(current_effective_value) if current_effective_value is not None else None
            config.config_value = str(new_value)
            config.effective_time = effective_time
            config.status = 'pending'
            config.updated_at = datetime.utcnow()

            # 记录变更历史
            change_record = ConfigChangeHistory(
                config_key=key,
                old_value=config.previous_value,
                new_value=str(new_value),
                scheduled_time=datetime.utcnow(),
                effective_time=effective_time,
                changed_by=changed_by,
                change_reason=reason,
                status='pending'
            )

            db.session.add(change_record)
            db.session.commit()

            self.logger.info(f"配置变更已安排: {key} = {new_value}, 生效时间: {effective_time}")
            return True

        except Exception as e:
            self.logger.error(f"安排配置变更失败: {str(e)}")
            db.session.rollback()
            return False

    def get_pending_changes(self) -> List[Dict]:
        """获取所有待生效的配置变更"""
        try:
            configs = db.session.query(SystemConfig).filter(
                SystemConfig.status == 'pending',
                SystemConfig.effective_time > datetime.utcnow()
            ).all()

            return [
                {
                    'config_key': config.config_key,
                    'current_value': config.get_effective_value(),
                    'new_value': config.get_typed_value(),
                    'effective_time': config.effective_time.isoformat() if config.effective_time else None,
                    'description': config.description
                }
                for config in configs
            ]

        except Exception as e:
            self.logger.error(f"获取待生效变更失败: {str(e)}")
            return []

    def cancel_scheduled_change(self, key: str) -> bool:
        """取消待生效的配置变更"""
        try:
            config = db.session.query(SystemConfig).filter_by(
                config_key=key,
                status='pending'
            ).first()

            if not config:
                self.logger.warning(f"没有找到待生效的配置变更: {key}")
                return False

            # 恢复到之前的值
            if config.previous_value is not None:
                config.config_value = config.previous_value

            config.previous_value = None
            config.effective_time = None
            config.status = 'active'
            config.updated_at = datetime.utcnow()

            # 更新历史记录
            history = db.session.query(ConfigChangeHistory).filter_by(
                config_key=key,
                status='pending'
            ).first()

            if history:
                history.status = 'cancelled'
                history.effective_time = datetime.utcnow()

            db.session.commit()

            self.logger.info(f"已取消配置变更: {key}")
            return True

        except Exception as e:
            self.logger.error(f"取消配置变更失败: {str(e)}")
            db.session.rollback()
            return False

    def apply_scheduled_changes(self) -> int:
        """应用已到生效时间的配置变更"""
        try:
            now = datetime.utcnow()

            # 查找需要生效的配置
            pending_configs = db.session.query(SystemConfig).filter(
                SystemConfig.status == 'pending',
                SystemConfig.effective_time <= now
            ).all()

            applied_count = 0
            for config in pending_configs:
                try:
                    # 应用变更
                    config.previous_value = None
                    config.effective_time = None
                    config.status = 'active'
                    config.updated_at = now

                    # 更新历史记录
                    history = db.session.query(ConfigChangeHistory).filter_by(
                        config_key=config.config_key,
                        status='pending'
                    ).first()

                    if history:
                        history.status = 'active'
                        history.effective_time = now

                    applied_count += 1
                    self.logger.info(f"配置变更已生效: {config.config_key} = {config.config_value}")

                except Exception as e:
                    self.logger.error(f"应用配置变更失败 {config.config_key}: {str(e)}")
                    continue

            if applied_count > 0:
                db.session.commit()
                self.logger.info(f"成功应用 {applied_count} 个配置变更")

            return applied_count

        except Exception as e:
            self.logger.error(f"应用配置变更失败: {str(e)}")
            db.session.rollback()
            return 0
