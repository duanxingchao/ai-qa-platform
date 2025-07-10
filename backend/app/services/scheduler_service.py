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
            
            # 注册关闭回调
            import atexit
            atexit.register(self.shutdown)
            
        except Exception as e:
            self.logger.error(f"定时任务调度器初始化失败: {str(e)}")
            raise
    
    def _register_default_jobs(self, app):
        """注册默认的定时任务"""
        # 主工作流任务 - 每天凌晨2点执行
        self.add_cron_job(
            job_id='daily_workflow',
            job_name='每日AI处理工作流',
            func=lambda: self.execute_full_workflow(app),
            hour=2,
            minute=0,
            description='每日自动执行完整的AI数据处理工作流',
            enabled=True
        )
        
        # 数据同步任务 - 可独立执行
        self.add_cron_job(
            job_id='daily_data_sync',
            job_name='每日数据同步',
            func=lambda: self.execute_workflow_phase(app, WorkflowPhase.DATA_SYNC),
            hour=1,
            minute=30,
            description='每日自动同步数据（可独立执行）',
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
        """执行答案生成阶段"""
        self.logger.info(f"开始执行答案生成阶段 [workflow: {workflow_id}]")
        
        try:
            # TODO: 创建AI处理服务后取消注释
            # from app.services.ai_processing_service import ai_processing_service
            # result = ai_processing_service.process_answer_generation_batch()
            
            # 临时返回成功结果
            result = {
                'success': True, 
                'message': '答案生成阶段完成（待实现具体逻辑）',
                'processed_count': 0
            }
            return result
            
        except Exception as e:
            error_msg = f"答案生成阶段异常: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'message': error_msg}
    
    def _execute_scoring_phase(self, app, workflow_id: str) -> Dict[str, Any]:
        """执行评分处理阶段"""
        self.logger.info(f"开始执行评分处理阶段 [workflow: {workflow_id}]")
        
        try:
            # TODO: 创建AI处理服务后取消注释
            # from app.services.ai_processing_service import ai_processing_service
            # result = ai_processing_service.process_scoring_batch()
            
            # 临时返回成功结果
            result = {
                'success': True, 
                'message': '评分处理阶段完成（待实现具体逻辑）',
                'processed_count': 0
            }
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