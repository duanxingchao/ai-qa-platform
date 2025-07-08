"""
数据同步服务
负责从table1增量同步数据到questions表
"""
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError

from app.utils.database import db
from app.models.question import Question

class SyncService:
    """数据同步服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sync_status = {
            'last_sync_time': None,
            'total_synced': 0,
            'status': 'idle',  # idle, running, error
            'error_message': None
        }
    
    def get_sync_status(self) -> Dict:
        """获取同步状态"""
        # 获取最后同步时间（从数据库中获取）
        try:
            last_question = db.session.query(Question).order_by(Question.created_at.desc()).first()
            if last_question:
                self.sync_status['last_sync_time'] = last_question.created_at.isoformat()
            
            # 获取总同步数量
            total_count = db.session.query(func.count(Question.id)).scalar()
            self.sync_status['total_synced'] = total_count
            
        except Exception as e:
            self.logger.error(f"获取同步状态失败: {str(e)}")
        
        return self.sync_status.copy()
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """获取最后同步时间"""
        try:
            last_question = db.session.query(Question).order_by(Question.sendmessagetime.desc()).first()
            return last_question.sendmessagetime if last_question else None
        except Exception as e:
            self.logger.error(f"获取最后同步时间失败: {str(e)}")
            return None
    
    def fetch_new_data_from_table1(self, since_time: Optional[datetime] = None) -> List[Dict]:
        """从table1获取新数据并生成business_id"""
        try:
            # 构建查询SQL - 根据table1的实际字段结构
            base_sql = """
                SELECT 
                    pageid,
                    devicetypename,
                    sendmessagetime,
                    query,
                    serviceid,
                    qatype,
                    intent,
                    classification,
                    iskeyboardinput,
                    isstopanswer
                FROM table1
                {where}
                ORDER BY sendmessagetime ASC
            """
            
            where_clause = "WHERE sendmessagetime > :since_time" if since_time else ""
            sql = text(base_sql.format(where=where_clause))
            result = db.session.execute(sql, {'since_time': since_time} if since_time else {})
            
            # 转换为字典列表并生成business_id
            data = []
            for row in result:
                (
                    pageid,
                    devicetypename,
                    send_time,
                    query_text,
                    serviceid,
                    qatype,
                    intent,
                    classification,
                    iskeyboardinput,
                    isstopanswer
                ) = row

                # 生成business_id = MD5(pageid + sendmessagetime + query)
                raw_str = f"{pageid}{send_time.isoformat() if send_time else ''}{query_text}"
                business_id = hashlib.md5(raw_str.encode('utf-8')).hexdigest()

                data.append({
                    'business_id': business_id,
                    'pageid': pageid,
                    'devicetypename': devicetypename,
                    'query': query_text,
                    'sendmessagetime': send_time,
                    'classification': classification,
                    'serviceid': serviceid,
                    'qatype': qatype,
                    'intent': intent,
                    'iskeyboardinput': iskeyboardinput,
                    'isstopanswer': isstopanswer
                })
            
            self.logger.info(f"从table1获取到 {len(data)} 条新数据")
            return data
            
        except Exception as e:
            self.logger.error(f"从table1获取数据失败: {str(e)}")
            raise
    
    def sync_to_questions(self, data: List[Dict]) -> int:
        """将数据同步到questions表"""
        synced_count = 0
        
        try:
            for item in data:
                # 检查是否已存在（基于business_id）
                existing = db.session.query(Question).filter_by(
                    business_id=item['business_id']
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in item.items():
                        if hasattr(existing, key) and key != 'business_id':
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    # 创建新记录 - 字段映射到Question模型
                    question = Question(
                        business_id=item['business_id'],
                        pageid=item['pageid'],
                        devicetypename=item['devicetypename'],
                        query=item['query'],
                        sendmessagetime=item['sendmessagetime'],
                        classification=item['classification'],
                        serviceid=item['serviceid'],
                        qatype=item['qatype'],
                        intent=item['intent'],
                        iskeyboardinput=item['iskeyboardinput'],
                        isstopanswer=item['isstopanswer']
                    )
                    db.session.add(question)
                
                synced_count += 1
            
            # 提交事务
            db.session.commit()
            self.logger.info(f"成功同步 {synced_count} 条数据到questions表")
            return synced_count
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"同步数据到questions表失败: {str(e)}")
            raise
    
    def perform_sync(self, force_full_sync: bool = False) -> Dict:
        """执行数据同步"""
        try:
            self.sync_status['status'] = 'running'
            self.sync_status['error_message'] = None
            
            # 获取最后同步时间
            last_sync_time = None if force_full_sync else self.get_last_sync_time()
            
            self.logger.info(f"开始数据同步，最后同步时间: {last_sync_time}")
            
            # 获取新数据
            new_data = self.fetch_new_data_from_table1(last_sync_time)
            
            if not new_data:
                self.logger.info("没有新数据需要同步")
                self.sync_status['status'] = 'idle'
                return {
                    'success': True,
                    'message': '没有新数据需要同步',
                    'synced_count': 0
                }
            
            # 同步数据
            synced_count = self.sync_to_questions(new_data)
            
            # 更新状态
            self.sync_status['status'] = 'idle'
            self.sync_status['total_synced'] += synced_count
            
            result = {
                'success': True,
                'message': f'成功同步 {synced_count} 条数据',
                'synced_count': synced_count,
                'total_synced': self.sync_status['total_synced']
            }
            
            self.logger.info(f"数据同步完成: {result}")
            return result
            
        except Exception as e:
            self.sync_status['status'] = 'error'
            self.sync_status['error_message'] = str(e)
            
            error_msg = f"数据同步失败: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'synced_count': 0
            }
    
    def get_sync_statistics(self) -> Dict:
        """获取同步统计信息"""
        try:
            # 获取questions表统计
            questions_count = db.session.query(func.count(Question.id)).scalar()
            
            # 获取table1表统计
            table1_query = text("SELECT COUNT(*) FROM table1")
            table1_count = db.session.execute(table1_query).scalar()
            
            # 获取最新记录时间
            latest_question = db.session.query(Question).order_by(
                Question.sendmessagetime.desc()
            ).first()
            
            latest_table1_query = text("SELECT MAX(sendmessagetime) FROM table1")
            latest_table1_time = db.session.execute(latest_table1_query).scalar()
            
            return {
                'questions_count': questions_count,
                'table1_count': table1_count,
                'sync_rate': f"{(questions_count/table1_count*100):.1f}%" if table1_count > 0 else "0%",
                'latest_question_time': latest_question.sendmessagetime.isoformat() if latest_question else None,
                'latest_table1_time': latest_table1_time.isoformat() if latest_table1_time else None,
                'sync_status': self.sync_status['status']
            }
            
        except Exception as e:
            self.logger.error(f"获取同步统计失败: {str(e)}")
            return {
                'error': str(e)
            }
    

# 创建全局同步服务实例
sync_service = SyncService()

def sync_data_task(app):
    """定时任务：数据同步"""
    with app.app_context():
        try:
            result = sync_service.perform_sync()
            if result['success']:
                app.logger.info(f"定时同步完成: {result['message']}")
            else:
                app.logger.error(f"定时同步失败: {result['message']}")
        except Exception as e:
            app.logger.error(f"定时同步任务异常: {str(e)}")