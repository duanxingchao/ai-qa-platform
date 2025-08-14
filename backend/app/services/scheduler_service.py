"""
定时任务调度管理服务
提供工作流式的定时任务管理，支持自动化和手动控制
"""
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
except ImportError:
    # APScheduler未安装时的备用处理
    BackgroundScheduler = None
    IntervalTrigger = None
    CronTrigger = None
    EVENT_JOB_EXECUTED = None
    EVENT_JOB_ERROR = None

from app.config import Config


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    SUCCESS = "success"      # 执行成功
    FAILED = "failed"        # 执行失败
    DISABLED = "disabled"    # 已禁用


class WorkflowPhase(Enum):
    """工作流阶段枚举"""
    DATA_SYNC = "data_sync"              # 数据同步阶段
    CLASSIFICATION = "classification"     # 分类处理阶段
    ANSWER_GENERATION = "answer_generation"  # 答案生成阶段
    SCORING = "scoring"                  # 评分处理阶段
    REVIEW = "review"                    # 审核阶段


class SchedulerService:
    """定时任务调度服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scheduler = None
        self.tasks_status: Dict[str, Any] = {}
        self.workflow_status: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history_size = 200
        self._lock = threading.Lock()
        
        # 工作流配置
        self.workflow_config = {
            WorkflowPhase.DATA_SYNC: {
                'name': '数据同步',
                'description': '从table1同步最新数据到questions和answers表',
                'depends_on': [],
                'auto_next': True
            },
            WorkflowPhase.CLASSIFICATION: {
                'name': '问题分类',
                'description': '调用分类API对新问题进行分类',
                'depends_on': [WorkflowPhase.DATA_SYNC],
                'auto_next': True
            },
            WorkflowPhase.ANSWER_GENERATION: {
                'name': '答案生成',
                'description': '调用AI API生成问题答案',
                'depends_on': [WorkflowPhase.CLASSIFICATION],
                'auto_next': True
            },
            WorkflowPhase.SCORING: {
                'name': '答案评分',
                'description': '对生成的答案进行质量评分',
                'depends_on': [WorkflowPhase.ANSWER_GENERATION],
                'auto_next': False
            },
            WorkflowPhase.REVIEW: {
                'name': '人工审核',
                'description': '人工审核处理结果',
                'depends_on': [WorkflowPhase.SCORING],
                'auto_next': False
            }
        }
        
    def initialize(self, app):
        """初始化调度器"""
        try:
            # 检查是否启用调度器
            if not app.config.get('SCHEDULER_ENABLED', True):
                self.logger.info("调度器已被配置禁用，跳过初始化")
                return

            if BackgroundScheduler is None:
                self.logger.error("APScheduler未安装，无法启动定时任务调度器")
                return

            if self.scheduler is not None:
                self.logger.warning("调度器已经初始化，跳过重复初始化")
                return
            
            self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
            
            # 添加事件监听器
            if EVENT_JOB_EXECUTED and EVENT_JOB_ERROR:
                self.scheduler.add_listener(
                    self._job_executed_listener, 
                    EVENT_JOB_EXECUTED
                )
                self.scheduler.add_listener(
                    self._job_error_listener, 
                    EVENT_JOB_ERROR
                )
            
            # 启动调度器
            self.scheduler.start()
            self.logger.info("定时任务调度器启动成功")
            
            # 注册默认任务
            self._register_default_jobs(app)
            
            # 初始化工作流状态
            self._initialize_workflow_status()
            
            # 启动时立即处理已有数据
            if app.config.get('AUTO_PROCESS_ON_STARTUP', True):
                self.logger.info("配置启用启动时立即处理，开始处理已有数据")
                self._startup_immediate_process(app)
            
            # 注册关闭回调 (注释掉避免开发模式下过早关闭)
            # import atexit
            # atexit.register(self.shutdown)
            
        except Exception as e:
            self.logger.error(f"定时任务调度器初始化失败: {str(e)}")
            raise
    
    def _startup_immediate_process(self, app):
        """启动时立即处理已有数据"""
        # 防止重复执行：检查是否已经执行过
        if hasattr(app, '_startup_process_executed'):
            self.logger.info("启动时处理已执行过，跳过重复执行")
            return
            
        def immediate_process():
            try:
                with app.app_context():
                    # 标记已执行，防止重复
                    app._startup_process_executed = True
                    self.logger.info("🚀 开始启动时立即处理已有数据")
                    result = self.execute_full_workflow_with_suspend_check(app)
                    if result.get('success'):
                        self.logger.info(f"✅ 启动时数据处理完成: {result.get('message')}")
                    else:
                        self.logger.error(f"❌ 启动时数据处理失败: {result.get('message')}")
            except Exception as e:
                self.logger.error(f"启动时数据处理异常: {str(e)}")
        
        # 延迟3秒执行，确保应用完全启动
        import threading
        timer = threading.Timer(3.0, immediate_process)
        timer.start()
    
    def _register_default_jobs(self, app):
        """注册默认的定时任务"""
        # 获取可配置的间隔时间
        interval_minutes = app.config.get('WORKFLOW_INTERVAL_MINUTES', 3)
        self.logger.info(f"配置的工作流间隔时间: {interval_minutes} 分钟，类型: {type(interval_minutes)}")
        
        # 确保间隔时间是整数且大于0
        if not isinstance(interval_minutes, int) or interval_minutes <= 0:
            interval_minutes = 3
            self.logger.warning(f"工作流间隔时间无效，使用默认值: {interval_minutes} 分钟")
        
        # 主工作流任务 - 可配置间隔执行
        self.add_interval_job(
            job_id='configurable_workflow',
            job_name='可配置间隔AI处理工作流',
            func=lambda: self.execute_full_workflow_with_suspend_check(app),
            minutes=interval_minutes,
            description=f'每{interval_minutes}分钟自动执行完整的AI数据处理工作流（支持无数据挂起）',
            enabled=True
        )
        
        # 数据同步任务 - 可独立执行
        self.add_interval_job(
            job_id='frequent_data_sync',
            job_name='频繁数据同步',
            func=lambda: self.execute_workflow_phase(app, WorkflowPhase.DATA_SYNC),
            minutes=interval_minutes,
            description=f'每{interval_minutes}分钟自动同步数据（可独立执行）',
            enabled=False  # 默认禁用，由主工作流控制
        )
    
    def _initialize_workflow_status(self):
        """初始化工作流状态"""
        with self._lock:
            for phase in WorkflowPhase:
                self.workflow_status[phase.value] = {
                    'phase': phase.value,
                    'name': self.workflow_config[phase]['name'],
                    'description': self.workflow_config[phase]['description'],
                    'status': TaskStatus.PENDING.value,
                    'last_execution': None,
                    'execution_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'current_batch_id': None,
                    'progress': 0,
                    'message': '',
                    'can_execute': self._can_execute_phase(phase)
                }
    
    def execute_full_workflow(self, app) -> Dict[str, Any]:
        """执行完整工作流"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.logger.info(f"开始执行完整工作流: {workflow_id}")
            
            results = {}
            
            # 按顺序执行各个阶段
            phases = [
                WorkflowPhase.DATA_SYNC,
                WorkflowPhase.CLASSIFICATION,
                WorkflowPhase.ANSWER_GENERATION,
                WorkflowPhase.SCORING
            ]
            
            for phase in phases:
                self.logger.info(f"执行工作流阶段: {phase.value}")
                
                result = self.execute_workflow_phase(app, phase, workflow_id)
                results[phase.value] = result
                
                if not result.get('success', False):
                    self.logger.error(f"工作流阶段失败: {phase.value}, 停止后续执行")
                    break
                
                # 检查是否自动进入下一阶段
                if not self.workflow_config[phase]['auto_next']:
                    self.logger.info(f"阶段 {phase.value} 不自动进入下一阶段，工作流暂停")
                    break
            
            # 记录工作流执行结果
            self._record_workflow_execution(workflow_id, results)
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'message': '工作流执行完成',
                'results': results
            }
            
        except Exception as e:
            error_msg = f"工作流执行异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'workflow_id': workflow_id,
                'message': error_msg,
                'results': {}
            }
    
    def execute_full_workflow_with_suspend_check(self, app) -> Dict[str, Any]:
        """执行完整工作流（带无数据挂起检查）"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 检查是否启用数据检测
            if not app.config.get('DATA_CHECK_ENABLED', True):
                return self.execute_full_workflow(app)
            
            # 检查是否有可处理的数据
            has_data_to_process = self._check_if_has_data_to_process(app)
            
            if not has_data_to_process:
                if app.config.get('AUTO_SUSPEND_WHEN_NO_DATA', True):
                    self.logger.info("💤 没有检测到可处理的数据，工作流挂起等待")
                    return {
                        'success': True,
                        'workflow_id': workflow_id,
                        'message': '没有可处理的数据，工作流挂起等待',
                        'suspended': True,
                        'results': {}
                    }
            
            self.logger.info(f"检测到可处理数据，开始执行完整工作流: {workflow_id}")
            
            # 执行正常的工作流
            result = self.execute_full_workflow(app)
            result['suspended'] = False
            return result
            
        except Exception as e:
            error_msg = f"带挂起检查的工作流执行异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'workflow_id': workflow_id,
                'message': error_msg,
                'suspended': False,
                'results': {}
            }
    
    def _check_if_has_data_to_process(self, app) -> bool:
        """检查是否有可处理的数据"""
        try:
            with app.app_context():
                from app.models.question import Question
                from app.models.answer import Answer
                from app.utils.database import db
                from sqlalchemy import func, and_, or_
                
                min_batch_size = app.config.get('MIN_BATCH_SIZE', 1)
                
                # 检查数据同步阶段：是否有新数据需要同步（限制本周数据，避免重复同步）
                from app.services.sync_service import sync_service
                from datetime import datetime, timedelta

                # 获取本周开始时间
                today = datetime.utcnow()
                days_since_monday = today.weekday()
                week_start = today - timedelta(days=days_since_monday)
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

                from sqlalchemy import text
                # 检查本周未同步的数据量（排除已存在的business_id）
                new_data_query = text("""
                    SELECT COUNT(*) FROM table1 t1
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
                """)
                new_data_count = db.session.execute(new_data_query, {
                    'week_start': week_start
                }).scalar()
                
                if new_data_count >= min_batch_size:
                    self.logger.info(f"🔍 检测到 {new_data_count} 条新数据需要同步")
                    return True
                
                # 检查分类阶段：是否有未分类的问题
                unclassified_count = db.session.query(Question).filter(
                    or_(Question.classification.is_(None), Question.classification == '')
                ).count()
                
                if unclassified_count >= min_batch_size:
                    self.logger.info(f"🔍 检测到 {unclassified_count} 条问题需要分类")
                    return True
                
                # 检查答案生成阶段：是否有已分类但未生成答案的问题
                # 查找有分类但缺少豆包或小天答案的问题
                questions_needing_answers = db.session.query(Question).filter(
                    and_(
                        Question.classification.isnot(None),
                        Question.classification != '',
                        Question.processing_status.in_(['classified', 'generating', 'answers_generated'])
                    )
                ).count()

                if questions_needing_answers >= min_batch_size:
                    self.logger.info(f"🔍 检测到 {questions_needing_answers} 条问题需要生成答案")
                    return True

                # 检查评分阶段：是否有未评分的答案
                # 优化：检查有完整答案但未完成评分的问题
                unscored_questions = db.session.query(Question).filter(
                    and_(
                        Question.processing_status.in_(['answers_generated', 'scoring']),
                        Question.classification.isnot(None),
                        Question.classification != ''
                    )
                ).count()

                if unscored_questions >= min_batch_size:
                    self.logger.info(f"🔍 检测到 {unscored_questions} 条问题需要评分")
                    return True
                
                self.logger.info("🔍 没有检测到足够的待处理数据")
                return False
                
        except Exception as e:
            self.logger.error(f"检查待处理数据时出错: {str(e)}")
            # 出错时默认返回True，避免阻塞正常流程
            return True
    
    def execute_workflow_phase(
        self, 
        app, 
        phase: WorkflowPhase, 
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行工作流的特定阶段"""
        
        if workflow_id is None:
            workflow_id = f"manual_{phase.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 检查依赖
        if not self._check_phase_dependencies(phase):
            return {
                'success': False,
                'message': f'阶段 {phase.value} 的依赖条件未满足',
                'phase': phase.value
            }
        
        # 更新阶段状态
        self._update_phase_status(phase, TaskStatus.RUNNING, workflow_id)
        
        try:
            with app.app_context():
                if phase == WorkflowPhase.DATA_SYNC:
                    result = self._execute_data_sync_phase(app, workflow_id)
                elif phase == WorkflowPhase.CLASSIFICATION:
                    result = self._execute_classification_phase(app, workflow_id)
                elif phase == WorkflowPhase.ANSWER_GENERATION:
                    result = self._execute_answer_generation_phase(app, workflow_id)
                elif phase == WorkflowPhase.SCORING:
                    result = self._execute_scoring_phase(app, workflow_id)
                elif phase == WorkflowPhase.REVIEW:
                    result = self._execute_review_phase(app, workflow_id)
                else:
                    result = {'success': False, 'message': f'未知阶段: {phase.value}'}
                
                # 更新阶段状态
                status = TaskStatus.SUCCESS if result.get('success', False) else TaskStatus.FAILED
                self._update_phase_status(
                    phase, 
                    status, 
                    workflow_id, 
                    message=result.get('message', ''),
                    progress=100 if status == TaskStatus.SUCCESS else 0
                )
                
                return result
                
        except Exception as e:
            error_msg = f"阶段 {phase.value} 执行异常: {str(e)}"
            self.logger.error(error_msg)
            
            self._update_phase_status(
                phase, 
                TaskStatus.FAILED, 
                workflow_id, 
                message=error_msg
            )
            
            return {
                'success': False,
                'message': error_msg,
                'phase': phase.value
            }
    
    def _execute_data_sync_phase(self, app, workflow_id: str) -> Dict[str, Any]:
        """执行数据同步阶段"""
        from app.services.sync_service import sync_service
        
        self.logger.info(f"开始执行数据同步阶段 [workflow: {workflow_id}]")
        
        try:
            result = sync_service.perform_sync()
            
            if result['success']:
                self.logger.info(f"数据同步阶段完成: {result['message']}")
            else:
                self.logger.error(f"数据同步阶段失败: {result['message']}")
                
            return result
            
        except Exception as e:
            error_msg = f"数据同步阶段异常: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _execute_classification_phase(self, app, workflow_id: str) -> Dict[str, Any]:
        """执行分类处理阶段"""
        self.logger.info(f"开始执行分类处理阶段 [workflow: {workflow_id}]")
        
        try:
            # TODO: 创建AI处理服务后取消注释
            # from app.services.ai_processing_service import ai_processing_service
            # result = ai_processing_service.process_classification_batch()
            
            # 临时返回成功结果
            result = {
                'success': True, 
                'message': '分类处理阶段完成（待实现具体逻辑）',
                'processed_count': 0
            }
            return result
            
        except Exception as e:
            error_msg = f"分类处理阶段异常: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _execute_answer_generation_phase(self, app, workflow_id: str) -> Dict[str, Any]:
        """执行答案生成阶段（支持手动模式和API模式切换）"""
        self.logger.info(f"开始执行答案生成阶段 [workflow: {workflow_id}]")

        try:
            with app.app_context():
                from app.services.system_config_service import SystemConfigService
                from app.services.answer_generation_service import AnswerGenerationService

                # 获取答案生成模式配置
                config_service = SystemConfigService()
                answer_generation_mode = config_service.get_config('workflow.answer_generation_mode', 'manual')

                self.logger.info(f"当前答案生成模式: {answer_generation_mode}")

                if answer_generation_mode == 'manual':
                    # 手动模式：检查是否有待导出的问题
                    answer_service = AnswerGenerationService()
                    pending_count = answer_service.get_export_questions_count()

                    if pending_count > 0:
                        return {
                            'success': True,
                            'message': f'手动模式：有{pending_count}个问题待导出Excel进行答案生成',
                            'pending_count': pending_count,
                            'mode': 'manual',
                            'action_required': 'export_excel'
                        }
                    else:
                        return {
                            'success': True,
                            'message': '手动模式：无待处理问题',
                            'pending_count': 0,
                            'mode': 'manual',
                            'action_required': 'none'
                        }

                elif answer_generation_mode == 'api':
                    # API模式：调用原有的API生成逻辑
                    from app.services.ai_processing_service import ai_processing_service
                    result = ai_processing_service.process_answer_generation_batch()
                    result['mode'] = 'api'
                    return result

                else:
                    return {
                        'success': False,
                        'message': f'未知的答案生成模式: {answer_generation_mode}',
                        'mode': answer_generation_mode
                    }

        except Exception as e:
            error_msg = f"答案生成阶段异常: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _execute_scoring_phase(self, app, workflow_id: str) -> Dict[str, Any]:
        """执行评分处理阶段"""
        self.logger.info(f"开始执行评分处理阶段 [workflow: {workflow_id}]")
        
        try:
            from app.services.ai_processing_service import AIProcessingService
            ai_service = AIProcessingService()
            result = ai_service.process_scoring_batch()
            return result
            
        except Exception as e:
            error_msg = f"评分处理阶段异常: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _execute_review_phase(self, app, workflow_id: str) -> Dict[str, Any]:
        """执行审核阶段（通常是人工操作）"""
        self.logger.info(f"开始执行审核阶段 [workflow: {workflow_id}]")
        
        # 审核阶段通常是人工操作，这里只是标记为可审核状态
        return {
            'success': True,
            'message': '审核阶段已准备就绪，等待人工操作',
            'requires_manual_action': True
        }
    
    def _check_phase_dependencies(self, phase: WorkflowPhase) -> bool:
        """检查阶段依赖是否满足"""
        dependencies = self.workflow_config[phase]['depends_on']
        
        for dep_phase in dependencies:
            if dep_phase.value not in self.workflow_status:
                return False
            
            dep_status = self.workflow_status[dep_phase.value]['status']
            if dep_status != TaskStatus.SUCCESS.value:
                return False
        
        return True
    
    def _can_execute_phase(self, phase: WorkflowPhase) -> bool:
        """检查阶段是否可以执行"""
        return self._check_phase_dependencies(phase)
    
    def _update_phase_status(
        self, 
        phase: WorkflowPhase, 
        status: TaskStatus,
        workflow_id: Optional[str] = None,
        message: str = '',
        progress: int = 0
    ):
        """更新阶段状态"""
        with self._lock:
            if phase.value in self.workflow_status:
                self.workflow_status[phase.value].update({
                    'status': status.value,
                    'last_execution': datetime.now().isoformat(),
                    'current_batch_id': workflow_id,
                    'message': message,
                    'progress': progress
                })
                
                if status == TaskStatus.RUNNING:
                    self.workflow_status[phase.value]['execution_count'] += 1
                elif status == TaskStatus.SUCCESS:
                    self.workflow_status[phase.value]['success_count'] += 1
                elif status == TaskStatus.FAILED:
                    self.workflow_status[phase.value]['error_count'] += 1
                
                # 更新所有阶段的可执行状态
                for p in WorkflowPhase:
                    self.workflow_status[p.value]['can_execute'] = self._can_execute_phase(p)
    
    def _record_workflow_execution(self, workflow_id: str, results: Dict):
        """记录工作流执行结果"""
        record = {
            'workflow_id': workflow_id,
            'execution_time': datetime.now().isoformat(),
            'results': results,
            'success': all(r.get('success', False) for r in results.values())
        }
        
        with self._lock:
            self.execution_history.append(record)
            
            # 保持历史记录数量限制
            if len(self.execution_history) > self.max_history_size:
                self.execution_history = self.execution_history[-self.max_history_size:]
    
    def add_cron_job(
        self,
        job_id: str,
        job_name: str,
        func: Callable,
        minute: int = 0,
        hour: int = 0,
        day: Optional[int] = None,
        month: Optional[int] = None,
        day_of_week: Optional[int] = None,
        description: str = "",
        enabled: bool = True
    ) -> bool:
        """添加定时执行的任务"""
        try:
            if not enabled:
                self.logger.info(f"任务 {job_name} 被禁用，跳过添加")
                return False
            
            if CronTrigger is None:
                self.logger.error("APScheduler未安装，无法添加定时任务")
                return False
                
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone='Asia/Shanghai'
            )
            
            if self.scheduler is None:
                self.logger.error("调度器未初始化")
                return False
                
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                name=job_name,
                replace_existing=True
            )
            
            # 记录任务状态
            with self._lock:
                self.tasks_status[job_id] = {
                    'name': job_name,
                    'type': 'cron',
                    'description': description,
                    'enabled': enabled,
                    'created_at': datetime.now().isoformat(),
                    'last_execution': None,
                    'execution_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'config': {
                        'minute': minute,
                        'hour': hour,
                        'day': day,
                        'month': month,
                        'day_of_week': day_of_week
                    }
                }
            
            self.logger.info(f"添加定时任务成功: {job_name} (cron: {hour:02d}:{minute:02d})")
            return True
            
        except Exception as e:
            self.logger.error(f"添加定时任务失败: {str(e)}")
            return False
    
    def add_interval_job(
        self,
        job_id: str,
        job_name: str,
        func: Callable,
        seconds: Optional[int] = None,
        minutes: Optional[int] = None,
        hours: Optional[int] = None,
        days: Optional[int] = None,
        description: str = "",
        enabled: bool = True
    ) -> bool:
        """添加间隔执行的任务"""
        try:
            if not enabled:
                self.logger.info(f"任务 {job_name} 被禁用，跳过添加")
                return False
            
            if IntervalTrigger is None:
                self.logger.error("APScheduler未安装，无法添加间隔任务")
                return False
                
            # 调试信息：显示所有参数值
            self.logger.info(f"添加任务 {job_name} - seconds={seconds}, minutes={minutes}, hours={hours}, days={days}")
            
            # 确保至少有一个时间参数不为None
            if all(param is None for param in [seconds, minutes, hours, days]):
                self.logger.error(f"添加任务失败：所有时间参数都为None - {job_name}")
                return False
                
            # 创建 IntervalTrigger 时只传递非 None 的参数
            trigger_kwargs = {'timezone': 'Asia/Shanghai'}
            if seconds is not None:
                trigger_kwargs['seconds'] = seconds
            if minutes is not None:
                trigger_kwargs['minutes'] = minutes
            if hours is not None:
                trigger_kwargs['hours'] = hours
            if days is not None:
                trigger_kwargs['days'] = days
                
            trigger = IntervalTrigger(**trigger_kwargs)
            
            if self.scheduler is None:
                self.logger.error("调度器未初始化")
                return False
                
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                name=job_name,
                replace_existing=True
            )
            
            # 记录任务状态
            with self._lock:
                self.tasks_status[job_id] = {
                    'name': job_name,
                    'type': 'interval',
                    'description': description,
                    'enabled': enabled,
                    'created_at': datetime.now().isoformat(),
                    'last_execution': None,
                    'execution_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'config': {
                        'seconds': seconds,
                        'minutes': minutes,
                        'hours': hours,
                        'days': days
                    }
                }
            
            interval_str = ""
            if days:
                interval_str += f"{days}天"
            if hours:
                interval_str += f"{hours}小时"
            if minutes:
                interval_str += f"{minutes}分钟"
            if seconds:
                interval_str += f"{seconds}秒"
            
            self.logger.info(f"添加间隔任务成功: {job_name} (间隔: {interval_str})")
            return True
            
        except Exception as e:
            self.logger.error(f"添加间隔任务失败: {str(e)}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """暂停定时任务"""
        try:
            if self.scheduler is None:
                return False
                
            self.scheduler.pause_job(job_id)
            
            with self._lock:
                if job_id in self.tasks_status:
                    self.tasks_status[job_id]['enabled'] = False
            
            self.logger.info(f"暂停定时任务成功: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"暂停定时任务失败: {str(e)}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """恢复定时任务"""
        try:
            if self.scheduler is None:
                return False

            self.scheduler.resume_job(job_id)

            with self._lock:
                if job_id in self.tasks_status:
                    self.tasks_status[job_id]['enabled'] = True

            self.logger.info(f"恢复定时任务成功: {job_id}")
            return True

        except Exception as e:
            self.logger.error(f"恢复定时任务失败: {str(e)}")
            return False

    def trigger_job(self, job_id: str) -> bool:
        """立即执行定时任务"""
        try:
            if self.scheduler is None:
                return False

            # 获取任务并立即执行
            job = self.scheduler.get_job(job_id)
            if job is None:
                self.logger.error(f"任务不存在: {job_id}")
                return False

            # 立即执行任务
            job.modify(next_run_time=datetime.now())

            self.logger.info(f"立即执行定时任务成功: {job_id}")
            return True

        except Exception as e:
            self.logger.error(f"立即执行定时任务失败: {str(e)}")
            return False
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器完整状态"""
        scheduler_jobs = []
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                scheduler_jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
        
        with self._lock:
            return {
                'scheduler_running': self.scheduler.running if self.scheduler else False,
                'current_time': datetime.now().isoformat(),
                'scheduled_jobs': {
                    'count': len(self.tasks_status),
                    'jobs': dict(self.tasks_status),
                    'scheduler_jobs': scheduler_jobs
                },
                'workflow': {
                    'phases': dict(self.workflow_status),
                    'execution_history': self.execution_history[-10:]  # 最近10条记录
                }
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        with self._lock:
            return {
                'phases': dict(self.workflow_status),
                'execution_history': self.execution_history[-20:]
            }
    
    def _job_executed_listener(self, event):
        """任务执行成功监听器"""
        job_id = event.job_id
        
        with self._lock:
            if job_id in self.tasks_status:
                self.tasks_status[job_id]['last_execution'] = datetime.now().isoformat()
                self.tasks_status[job_id]['execution_count'] += 1
                self.tasks_status[job_id]['success_count'] += 1
    
    def _job_error_listener(self, event):
        """任务执行失败监听器"""
        job_id = event.job_id
        
        with self._lock:
            if job_id in self.tasks_status:
                self.tasks_status[job_id]['last_execution'] = datetime.now().isoformat()
                self.tasks_status[job_id]['execution_count'] += 1
                self.tasks_status[job_id]['error_count'] += 1
        
        self.logger.error(f"定时任务执行失败: {job_id}, 错误: {event.exception}")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.logger.info("定时任务调度器已关闭")


# 创建全局调度器实例
scheduler_service = SchedulerService() 