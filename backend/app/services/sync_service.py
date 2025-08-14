"""
数据同步服务（支持questions和answers表分离同步）
负责从table1同步数据到questions表和answers表，在SQL查询阶段过滤掉query为空的记录
"""
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError

from app.utils.database import db
from app.models.question import Question
from app.models.answer import Answer

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
        try:
            last_question = db.session.query(Question).order_by(Question.created_at.desc()).first()
            if last_question:
                self.sync_status['last_sync_time'] = last_question.created_at.isoformat()
            
            # 获取总同步数量
            questions_count = db.session.query(func.count(Question.id)).scalar()
            answers_count = db.session.query(func.count(Answer.id)).scalar()
            self.sync_status['total_synced'] = questions_count
            self.sync_status['questions_count'] = questions_count
            self.sync_status['answers_count'] = answers_count
            
        except Exception as e:
            self.logger.error(f"获取同步状态失败: {str(e)}")
        
        return self.sync_status.copy()
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """获取最后同步时间（排除未来时间的数据）"""
        try:
            # 只查询当前时间之前的数据，避免未来时间数据干扰
            last_question = db.session.query(Question).filter(
                Question.sendmessagetime <= datetime.utcnow()
            ).order_by(Question.sendmessagetime.desc()).first()
            
            last_sync_time = last_question.sendmessagetime if last_question else None
            self.logger.debug(f"获取最后同步时间: {last_sync_time}")
            return last_sync_time
        except Exception as e:
            self.logger.error(f"获取最后同步时间失败: {str(e)}")
            return None
    
    def get_week_start(self) -> datetime:
        """获取本周开始时间（周一00:00:00）"""
        today = datetime.utcnow()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)



    def fetch_new_data_from_table1(self, since_time: Optional[datetime] = None) -> List[Dict]:
        """从table1获取新数据，包括answer字段，限制只同步本周数据，并避免重复同步"""
        try:
            # 获取本周开始时间
            week_start = self.get_week_start()

            # 确保since_time不早于本周开始时间，防止同步过多历史数据
            if since_time and since_time < week_start:
                self.logger.info(f"最后同步时间({since_time})早于本周开始时间({week_start})，调整为本周开始时间")
                since_time = week_start
            elif not since_time:
                # 如果没有since_time，默认只同步本周数据
                since_time = week_start
                self.logger.info(f"没有最后同步时间，默认只同步本周数据，开始时间: {week_start}")

            # 构建查询SQL - 适配不同方言，避免使用 Postgres 专有函数
            dialect_name = db.session.bind.dialect.name if db.session.bind else ""
            if dialect_name == 'sqlite':
                base_sql = """
                    SELECT
                        t1.pageid,
                        t1.devicetypename,
                        t1.sendmessagetime,
                        t1.query,
                        t1.answer,
                        t1.serviceid,
                        t1.qatype,
                        t1.intent,
                        t1.iskeyboardinput,
                        t1.isstopanswer
                    FROM table1 t1
                    WHERE t1.query IS NOT NULL
                    AND t1.query != ''
                    AND TRIM(t1.query) != ''
                    AND datetime(t1.sendmessagetime) >= datetime(:week_start)
                    ORDER BY t1.sendmessagetime ASC
                """
                sql = text(base_sql)
                result = db.session.execute(sql, {'week_start': week_start})
            else:
                # Postgres 版本：保留去重避免重复同步到 questions（基于 business_id）
                base_sql = """
                    SELECT
                        t1.pageid,
                        t1.devicetypename,
                        t1.sendmessagetime,
                        t1.query,
                        t1.answer,
                        t1.serviceid,
                        t1.qatype,
                        t1.intent,
                        t1.iskeyboardinput,
                        t1.isstopanswer
                    FROM table1 t1
                    WHERE t1.query IS NOT NULL
                    AND t1.query != ''
                    AND TRIM(t1.query) != ''
                    AND t1.sendmessagetime >= :week_start
                    AND NOT EXISTS (
                        SELECT 1 FROM questions q
                        WHERE q.business_id = MD5(CONCAT(
                            t1.pageid,
                            COALESCE(to_char(t1.sendmessagetime, 'YYYY-MM-DD"T"HH24:MI:SS.US'), ''),
                            t1.query
                        ))
                    )
                    ORDER BY t1.sendmessagetime ASC
                """
                sql = text(base_sql)
                result = db.session.execute(sql, {'week_start': week_start})
            
            # 转换为字典列表并生成business_id
            data = []
            for row in result:
                (
                    pageid,
                    devicetypename,
                    send_time,
                    query_text,
                    answer_text,
                    serviceid,
                    qatype,
                    intent,
                    classification,
                    iskeyboardinput,
                    isstopanswer
                ) = row

                # 生成business_id = MD5(pageid + sendmessagetime + query)
                # 统一使用 Python 端生成，避免不同方言函数差异
                raw_str = f"{pageid}{send_time.isoformat() if send_time else ''}{query_text}"
                business_id = hashlib.md5(raw_str.encode('utf-8')).hexdigest()

                data.append({
                    'business_id': business_id,
                    'pageid': pageid,
                    'devicetypename': devicetypename,
                    'query': query_text,
                    'answer': answer_text,
                    'sendmessagetime': send_time,
                    'classification': classification,
                    'serviceid': serviceid,
                    'qatype': qatype,
                    'intent': intent,
                    'iskeyboardinput': iskeyboardinput,
                    'isstopanswer': isstopanswer
                })
            
            self.logger.info(f"从table1获取到 {len(data)} 条有效数据（已过滤空query记录）")
            return data
            
        except Exception as e:
            self.logger.error(f"从table1获取数据失败: {str(e)}")
            raise
    
    def sync_to_questions(self, data: List[Dict]) -> int:
        """将问题相关数据同步到questions表（不包含分类，分类将由AI处理服务后续填充）"""
        synced_count = 0

        try:
            for item in data:
                # 检查是否已存在（基于business_id）
                existing = db.session.query(Question).filter_by(
                    business_id=item['business_id']
                ).first()

                if existing:
                    # 更新现有记录（不更新classification字段，保留现有分类）
                    existing.pageid = item['pageid']
                    existing.devicetypename = item['devicetypename']
                    existing.query = item['query']
                    existing.sendmessagetime = item['sendmessagetime']
                    # 注意：不更新classification字段，保留AI处理的结果
                    existing.serviceid = item['serviceid']
                    existing.qatype = item['qatype']
                    existing.intent = item['intent']
                    existing.iskeyboardinput = item['iskeyboardinput']
                    existing.isstopanswer = item['isstopanswer']
                    existing.updated_at = datetime.utcnow()
                else:
                    # 创建新记录 - classification字段初始为None，等待AI处理
                    question = Question(
                        business_id=item['business_id'],
                        pageid=item['pageid'],
                        devicetypename=item['devicetypename'],
                        query=item['query'],
                        sendmessagetime=item['sendmessagetime'],
                        classification=None,  # 初始为None，等待AI分类处理
                        serviceid=item['serviceid'],
                        qatype=item['qatype'],
                        intent=item['intent'],
                        iskeyboardinput=item['iskeyboardinput'],
                        isstopanswer=item['isstopanswer']
                    )
                    db.session.add(question)

                synced_count += 1

            self.logger.info(f"准备同步 {synced_count} 条数据到questions表（classification字段将由AI处理服务填充）")
            return synced_count

        except Exception as e:
            self.logger.error(f"同步数据到questions表失败: {str(e)}")
            raise
    
    def sync_to_answers(self, data: List[Dict]) -> int:
        """将答案数据同步到answers表"""
        synced_count = 0
        
        try:
            for item in data:
                # 检查answer字段是否有内容
                answer_text = item.get('answer')
                if not answer_text or answer_text.strip() == '':
                    continue
                
                # 检查是否已存在（基于business_id和assistant_type）
                existing = db.session.query(Answer).filter_by(
                    question_business_id=item['business_id'],
                    assistant_type='yoyo'
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.answer_text = answer_text
                    existing.answer_time = item['sendmessagetime']
                    existing.updated_at = datetime.utcnow()
                else:
                    # 创建新记录
                    answer = Answer(
                        question_business_id=item['business_id'],
                        answer_text=answer_text,
                        assistant_type='yoyo',  # 标识为yoyo答案
                        answer_time=item['sendmessagetime']
                    )
                    db.session.add(answer)
                
                synced_count += 1
            
            self.logger.info(f"准备同步 {synced_count} 条答案到answers表")
            return synced_count
            
        except Exception as e:
            self.logger.error(f"同步数据到answers表失败: {str(e)}")
            raise
    
    def perform_sync(self, force_full_sync: bool = False) -> Dict:
        """执行数据同步（同时处理questions和answers表）"""
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
                    'synced_questions': 0,
                    'synced_answers': 0
                }
            
            # 同步数据到questions表
            questions_count = self.sync_to_questions(new_data)
            
            # 同步数据到answers表
            answers_count = self.sync_to_answers(new_data)
            
            # 提交事务
            db.session.commit()
            
            # 更新状态
            self.sync_status['status'] = 'idle'
            self.sync_status['total_synced'] += questions_count
            
            result = {
                'success': True,
                'message': f'成功同步 {questions_count} 条问题和 {answers_count} 条答案',
                'synced_questions': questions_count,
                'synced_answers': answers_count,
                'total_synced': self.sync_status['total_synced']
            }
            
            self.logger.info(f"数据同步完成: {result}")
            return result
            
        except Exception as e:
            db.session.rollback()
            self.sync_status['status'] = 'error'
            self.sync_status['error_message'] = str(e)
            
            error_msg = f"数据同步失败: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'synced_questions': 0,
                'synced_answers': 0
            }
    
    def get_sync_statistics(self) -> Dict:
        """获取同步统计信息"""
        try:
            # 获取questions表统计
            questions_count = db.session.query(func.count(Question.id)).scalar()
            
            # 获取answers表统计
            answers_count = db.session.query(func.count(Answer.id)).scalar()
            yoyo_answers_count = db.session.query(func.count(Answer.id)).filter_by(assistant_type='yoyo').scalar()
            
            # 获取table1表统计
            table1_total_query = text("SELECT COUNT(*) FROM table1")
            table1_total_count = db.session.execute(table1_total_query).scalar()
            
            table1_with_answer_query = text("SELECT COUNT(*) FROM table1 WHERE answer IS NOT NULL AND answer != '' AND TRIM(answer) != ''")
            table1_with_answer_count = db.session.execute(table1_with_answer_query).scalar()
            
            # 获取最新记录时间
            latest_question = db.session.query(Question).order_by(
                Question.sendmessagetime.desc()
            ).first()
            
            latest_table1_query = text("SELECT MAX(sendmessagetime) FROM table1")
            latest_table1_time = db.session.execute(latest_table1_query).scalar()
            
            return {
                'questions_count': questions_count,
                'answers_count': answers_count,
                'yoyo_answers_count': yoyo_answers_count,
                'table1_total_count': table1_total_count,
                'table1_with_answer_count': table1_with_answer_count,
                'questions_sync_rate': f"{(questions_count/table1_total_count*100):.1f}%" if table1_total_count > 0 else "0%",
                'answers_sync_rate': f"{(yoyo_answers_count/table1_with_answer_count*100):.1f}%" if table1_with_answer_count > 0 else "0%",
                'latest_question_time': latest_question.sendmessagetime.isoformat() if latest_question else None,
                'latest_table1_time': latest_table1_time.isoformat() if latest_table1_time else None,
                'sync_status': self.sync_status['status']
            }
            
        except Exception as e:
            self.logger.error(f"获取同步统计失败: {str(e)}")
            return {'error': str(e)}


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