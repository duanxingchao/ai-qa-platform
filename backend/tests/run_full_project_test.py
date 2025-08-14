#!/usr/bin/env python3
"""
🧪 AI问答平台项目全面功能测试套件
系统地测试所有已实现的功能模块，生成详细的测试报告
"""
import sys
import os
import time
import subprocess
import json
import traceback
from datetime import datetime
from sqlalchemy import inspect
from typing import Dict, List, Any
import threading
import signal

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class EnhancedProjectTestSuite:
    """增强版项目全面测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.environment_info = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warning_tests = 0
        self.test_start_time = datetime.now()
        self.mock_processes = []
        
    def log_test_result(self, category: str, test_name: str, success: bool, 
                       message: str, details: Dict = None, performance: Dict = None):
        """记录测试结果"""
        self.total_tests += 1
        
        if success is True:
            self.passed_tests += 1
            status = "✅ PASS"
        elif success is False:
            self.failed_tests += 1
            status = "❌ FAIL"
        else:  # None表示警告
            self.warning_tests += 1
            status = "⚠️  WARN"
        
        if category not in self.test_results:
            self.test_results[category] = []
            
        result = {
            'test_name': test_name,
            'status': status,
            'success': success,
            'message': message,
            'details': details or {},
            'performance': performance or {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.test_results[category].append(result)
        
        print(f"    {status} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"      {key}: {value}")
    
    def collect_environment_info(self):
        """收集环境信息"""
        print("🔍 收集环境信息...")
        
        try:
            # Python环境
            self.environment_info['python_version'] = sys.version
            self.environment_info['platform'] = sys.platform
            
            # 项目结构
            backend_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
            backend_dirs = len([d for d in os.listdir('.') if os.path.isdir(d)])
            
            # 检查关键目录
            key_directories = ['app', 'tests', 'venv']
            missing_dirs = [d for d in key_directories if not os.path.exists(d)]
            
            # 检查关键文件
            key_files = ['requirements.txt', 'run.py', 'init_db.py']
            missing_files = [f for f in key_files if not os.path.exists(f)]
            
            self.environment_info.update({
                'backend_files': backend_files,
                'backend_directories': backend_dirs,
                'missing_directories': missing_dirs,
                'missing_files': missing_files,
                'test_time': self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            self.environment_info['error'] = str(e)
    
    def test_project_structure(self):
        """测试项目结构完整性"""
        print("\n📁 测试项目结构...")
        
        # 检查核心目录
        required_dirs = {
            'app': '应用核心目录',
            'app/models': '数据模型目录',
            'app/api': 'API接口目录',
            'app/services': '业务服务目录',
            'app/utils': '工具函数目录',
            'tests': '测试目录',
        }
        
        missing_dirs = []
        for dir_path, description in required_dirs.items():
            if not os.path.exists(dir_path):
                missing_dirs.append(f"{dir_path} ({description})")
        
        # 检查关键文件
        required_files = {
            'requirements.txt': 'Python依赖文件',
            'run.py': '启动文件',
            'init_db.py': '数据库初始化文件',
            'app/__init__.py': '应用工厂文件',
            'app/config.py': '配置文件',
        }
        
        missing_files = []
        for file_path, description in required_files.items():
            if not os.path.exists(file_path):
                missing_files.append(f"{file_path} ({description})")
        
        structure_ok = len(missing_dirs) == 0 and len(missing_files) == 0
        
        details = {}
        if missing_dirs:
            details['missing_directories'] = missing_dirs
        if missing_files:
            details['missing_files'] = missing_files
        
        self.log_test_result(
            "项目结构",
            "目录文件完整性",
            structure_ok,
            "项目结构完整" if structure_ok else f"缺少{len(missing_dirs)}个目录，{len(missing_files)}个文件",
            details
        )
    
    def test_configuration(self):
        """测试配置完整性"""
        print("\n⚙️ 测试配置...")
        
        try:
            from app.config import Config
            
            # 检查关键配置项
            required_configs = [
                'DATABASE_URL', 'SECRET_KEY', 'CLASSIFY_API_URL',
                'DOUBAO_API_URL', 'XIAOTIAN_API_URL', 'SCORE_API_URL'
            ]
            
            missing_configs = []
            for config_name in required_configs:
                if not hasattr(Config, config_name) or not getattr(Config, config_name):
                    missing_configs.append(config_name)
            
            config_ok = len(missing_configs) == 0
            
            self.log_test_result(
                "配置管理",
                "配置项完整性",
                config_ok,
                "所有配置项完整" if config_ok else f"缺少配置项: {missing_configs}",
                {'missing_configs': missing_configs} if missing_configs else {}
            )
            
        except Exception as e:
            self.log_test_result(
                "配置管理",
                "配置加载",
                False,
                f"配置加载失败: {str(e)}"
            )
    
    def test_database_comprehensive(self):
        """全面测试数据库功能"""
        print("\n🗄️ 测试数据库...")
        
        try:
            from app import create_app
            from app.utils.database import db
            from app.models import Question, Answer, Score, ReviewStatus
            
            app = create_app()
            with app.app_context():
                start_time = time.time()
                
                # 1. 连接测试
                db.session.execute(db.text("SELECT 1")).fetchone()
                
                # 2. 表结构测试（兼容多方言）
                expected_tables = ['questions', 'answers', 'scores', 'review_status', 'table1']
                dialect_name = db.session.bind.dialect.name if db.session.bind else ''
                if dialect_name == 'sqlite':
                    rows = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table'"))
                    actual_table_names = [r[0] for r in rows.fetchall()]
                else:
                    actual_table_names = inspect(db.engine).get_table_names()
                missing_tables = set(expected_tables) - set(actual_table_names)
                
                # 3. 数据统计
                stats = {}
                for table in ['questions', 'answers', 'scores', 'review_status']:
                    if table in actual_table_names:
                        count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                        stats[f"{table}_count"] = count
                
                # 4. 模型测试
                model_tests = {}
                try:
                    Question.query.count()
                    model_tests['Question_model'] = '正常'
                except Exception as e:
                    model_tests['Question_model'] = f'错误: {str(e)}'
                
                try:
                    Answer.query.count()
                    model_tests['Answer_model'] = '正常'
                except Exception as e:
                    model_tests['Answer_model'] = f'错误: {str(e)}'
                
                end_time = time.time()
                performance = {'response_time': f"{(end_time - start_time)*1000:.2f}ms"}
                
                db_ok = len(missing_tables) == 0
                
                details = {**stats, **model_tests}
                if missing_tables:
                    details['missing_tables'] = list(missing_tables)
                
                self.log_test_result(
                    "数据库",
                    "连接和表结构",
                    db_ok,
                    "数据库功能正常" if db_ok else f"缺少表: {missing_tables}",
                    details,
                    performance
                )
                
        except Exception as e:
            self.log_test_result(
                "数据库",
                "连接测试",
                False,
                f"数据库连接失败: {str(e)}"
            )
    
    def start_mock_servers(self):
        """启动Mock服务器"""
        print("\n🚀 启动Mock服务器...")
        
        mock_servers = [
            {
                'name': '分类API',
                'script': 'tests/mock_classification_api.py',
                'port': 8001,
                'args': ['--auto-port']
            },
            {
                'name': '豆包AI',
                'script': 'tests/mock_ai_api.py',
                'port': 8002,
                'args': ['--port', '8002', '--service', 'doubao', '--auto-port']
            },
            {
                'name': '小天AI',
                'script': 'tests/mock_ai_api.py',
                'port': 8003,
                'args': ['--port', '8003', '--service', 'xiaotian', '--auto-port']
            }
        ]
        
        for server in mock_servers:
            try:
                cmd = [sys.executable, server['script']] + server['args']
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
                self.mock_processes.append(process)
                print(f"    ✅ 启动 {server['name']} (PID: {process.pid})")
                
            except Exception as e:
                print(f"    ❌ 启动 {server['name']} 失败: {str(e)}")
        
        # 等待服务器启动
        print("    ⏳ 等待服务器启动...")
        time.sleep(5)
    
    def test_api_clients(self):
        """测试API客户端"""
        print("\n🔌 测试API客户端...")
        
        try:
            from app.services.api_client import APIClientFactory
            
            # 测试客户端工厂
            try:
                classification_client = APIClientFactory.get_classification_client()
                self.log_test_result(
                    "API客户端",
                    "分类客户端创建",
                    True,
                    "分类客户端创建成功"
                )
            except Exception as e:
                self.log_test_result(
                    "API客户端",
                    "分类客户端创建",
                    False,
                    f"分类客户端创建失败: {str(e)}"
                )
            
            try:
                doubao_client = APIClientFactory.get_doubao_client()
                self.log_test_result(
                    "API客户端",
                    "豆包客户端创建",
                    True,
                    "豆包客户端创建成功"
                )
            except Exception as e:
                self.log_test_result(
                    "API客户端",
                    "豆包客户端创建",
                    False,
                    f"豆包客户端创建失败: {str(e)}"
                )
            
            try:
                xiaotian_client = APIClientFactory.get_xiaotian_client()
                self.log_test_result(
                    "API客户端",
                    "小天客户端创建",
                    True,
                    "小天客户端创建成功"
                )
            except Exception as e:
                self.log_test_result(
                    "API客户端",
                    "小天客户端创建",
                    False,
                    f"小天客户端创建失败: {str(e)}"
                )
            
        except Exception as e:
            self.log_test_result(
                "API客户端",
                "模块导入",
                False,
                f"API客户端模块导入失败: {str(e)}"
            )
    
    def test_ai_services(self):
        """测试AI处理服务"""
        print("\n🤖 测试AI处理服务...")
        
        try:
            from app import create_app
            from app.services.ai_processing_service import AIProcessingService
            
            app = create_app()
            with app.app_context():
                ai_service = AIProcessingService()
                
                # 测试服务初始化
                self.log_test_result(
                    "AI服务",
                    "服务初始化",
                    True,
                    "AI处理服务初始化成功"
                )
                
                # 测试统计功能
                try:
                    stats = ai_service.get_processing_statistics(days_back=7)
                    if 'error' in stats:
                        self.log_test_result(
                            "AI服务",
                            "统计功能",
                            False,
                            f"统计功能异常: {stats['error']}"
                        )
                    else:
                        self.log_test_result(
                            "AI服务",
                            "统计功能",
                            True,
                            "统计功能正常",
                            {
                                'questions_total': stats.get('questions', {}).get('total', 0),
                                'answers_total': stats.get('answers', {}).get('total', 0)
                            }
                        )
                except Exception as e:
                    self.log_test_result(
                        "AI服务",
                        "统计功能",
                        False,
                        f"统计功能异常: {str(e)}"
                    )
                
                # 测试分类方法存在性
                methods_to_check = [
                    'process_classification_batch',
                    'process_answer_generation_batch', 
                    'process_scoring_batch'
                ]
                
                for method_name in methods_to_check:
                    has_method = hasattr(ai_service, method_name)
                    self.log_test_result(
                        "AI服务",
                        f"{method_name}方法",
                        has_method,
                        "方法存在" if has_method else "方法不存在"
                    )
                
        except Exception as e:
            self.log_test_result(
                "AI服务",
                "服务加载",
                False,
                f"AI服务加载失败: {str(e)}"
            )
    
    def test_sync_service(self):
        """测试数据同步服务"""
        print("\n🔄 测试数据同步服务...")
        
        try:
            from app import create_app
            from app.services.sync_service import SyncService
            
            app = create_app()
            with app.app_context():
                sync_service = SyncService()
                
                # 测试同步状态
                try:
                    status = sync_service.get_sync_status()
                    self.log_test_result(
                        "同步服务",
                        "状态查询",
                        True,
                        "同步状态查询成功",
                        {
                            'status': status.get('status', 'unknown'),
                            'total_synced': status.get('total_synced', 0)
                        }
                    )
                except Exception as e:
                    self.log_test_result(
                        "同步服务",
                        "状态查询",
                        False,
                        f"状态查询失败: {str(e)}"
                    )
                
                # 测试统计功能
                try:
                    statistics = sync_service.get_sync_statistics()
                    self.log_test_result(
                        "同步服务",
                        "统计功能",
                        True,
                        "统计功能正常",
                        {
                            'questions_count': statistics.get('questions_count', 0),
                            'answers_count': statistics.get('answers_count', 0)
                        }
                    )
                except Exception as e:
                    self.log_test_result(
                        "同步服务",
                        "统计功能",
                        False,
                        f"统计功能失败: {str(e)}"
                    )
                
        except Exception as e:
            self.log_test_result(
                "同步服务",
                "服务加载",
                False,
                f"同步服务加载失败: {str(e)}"
            )
    
    def test_scheduler_service(self):
        """测试定时任务调度器"""
        print("\n⏰ 测试定时任务调度器...")
        
        try:
            from app import create_app
            from app.services.scheduler_service import SchedulerService
            
            app = create_app()
            with app.app_context():
                scheduler_service = SchedulerService()
                
                # 测试调度器初始化
                self.log_test_result(
                    "调度器",
                    "服务初始化",
                    True,
                    "调度器服务初始化成功"
                )
                
                # 测试状态查询
                try:
                    status = scheduler_service.get_scheduler_status()
                    self.log_test_result(
                        "调度器",
                        "状态查询",
                        True,
                        "状态查询成功",
                        {
                            'scheduler_running': status.get('scheduler_running', False),
                            'total_jobs': status.get('total_jobs', 0)
                        }
                    )
                except Exception as e:
                    self.log_test_result(
                        "调度器",
                        "状态查询",
                        False,
                        f"状态查询失败: {str(e)}"
                    )
                
        except Exception as e:
            self.log_test_result(
                "调度器",
                "服务加载",
                False,
                f"调度器服务加载失败: {str(e)}"
            )
    
    def test_web_apis(self):
        """测试Web API端点"""
        print("\n🌐 测试Web API...")
        
        try:
            # 测试应用启动
            from app import create_app
            app = create_app()
            
            # 测试客户端
            with app.test_client() as client:
                
                # 测试同步API
                try:
                    response = client.get('/api/sync/status')
                    self.log_test_result(
                        "Web API",
                        "同步状态API",
                        response.status_code == 200,
                        f"状态码: {response.status_code}",
                        {'response_length': len(response.data)}
                    )
                except Exception as e:
                    self.log_test_result(
                        "Web API",
                        "同步状态API",
                        False,
                        f"API调用失败: {str(e)}"
                    )
                
                # 测试问题查询API
                try:
                    response = client.get('/api/questions?page=1&page_size=5')
                    self.log_test_result(
                        "Web API",
                        "问题查询API",
                        response.status_code in [200, 404],
                        f"状态码: {response.status_code}",
                        {'response_length': len(response.data)}
                    )
                except Exception as e:
                    self.log_test_result(
                        "Web API",
                        "问题查询API",
                        False,
                        f"API调用失败: {str(e)}"
                    )
        
        except Exception as e:
            self.log_test_result(
                "Web API",
                "应用启动",
                False,
                f"Web应用启动失败: {str(e)}"
            )
    
    def run_existing_tests(self):
        """运行现有的测试套件"""
        print("\n🧪 运行现有测试套件...")
        
        # 运行comprehensive_test_suite.py（存在才执行）
        comp_path = os.path.join(os.path.dirname(__file__), 'comprehensive_test_suite.py')
        if os.path.exists(comp_path):
            try:
                print("    运行comprehensive_test_suite.py...")
                result = subprocess.run([
                    sys.executable, comp_path
                ], capture_output=True, text=True, timeout=300)
                success = result.returncode == 0
                self.log_test_result(
                    "现有测试",
                    "综合测试套件",
                    success,
                    "测试通过" if success else "测试失败",
                    {
                        'returncode': result.returncode,
                        'stdout_lines': len(result.stdout.split('\n')),
                        'stderr_lines': len(result.stderr.split('\n'))
                    }
                )
            except subprocess.TimeoutExpired:
                self.log_test_result(
                    "现有测试",
                    "综合测试套件",
                    False,
                    "测试超时（300秒）"
                )
            except Exception as e:
                self.log_test_result(
                    "现有测试",
                    "综合测试套件",
                    False,
                    f"测试执行失败: {str(e)}"
                )
        else:
            self.log_test_result(
                "现有测试",
                "综合测试套件",
                None,
                "文件不存在，跳过",
                {'path': comp_path}
            )
        
        # 运行tests目录下的测试
        test_files = ['test_core.py', 'test_api.py']
        
        for test_file in test_files:
            if os.path.exists(f'tests/{test_file}'):
                try:
                    print(f"    运行tests/{test_file}...")
                    result = subprocess.run([
                        sys.executable, f'tests/{test_file}'
                    ], capture_output=True, text=True, timeout=180)
                    
                    success = result.returncode == 0
                    self.log_test_result(
                        "现有测试",
                        test_file,
                        success,
                        "测试通过" if success else "测试失败",
                        {
                            'returncode': result.returncode,
                            'has_output': len(result.stdout) > 0
                        }
                    )
                    
                except subprocess.TimeoutExpired:
                    self.log_test_result(
                        "现有测试",
                        test_file,
                        False,
                        "测试超时（180秒）"
                    )
                except Exception as e:
                    self.log_test_result(
                        "现有测试", 
                        test_file,
                        False,
                        f"测试执行失败: {str(e)}"
                    )
    
    def performance_test(self):
        """性能测试"""
        print("\n⚡ 性能测试...")
        
        try:
            from app import create_app
            from app.utils.database import db
            
            app = create_app()
            with app.app_context():
                
                # 数据库查询性能
                start_time = time.time()
                result = db.session.execute(db.text("SELECT COUNT(*) FROM questions")).fetchone()
                query_time = (time.time() - start_time) * 1000
                
                self.performance_metrics['db_query_time_ms'] = query_time
                
                performance_ok = query_time < 1000  # 1秒内
                
                self.log_test_result(
                    "性能测试",
                    "数据库查询",
                    performance_ok,
                    f"查询耗时: {query_time:.2f}ms",
                    {'question_count': result[0] if result else 0},
                    {'query_time_ms': query_time}
                )
                
        except Exception as e:
            self.log_test_result(
                "性能测试",
                "数据库查询",
                False,
                f"性能测试失败: {str(e)}"
            )
    
    def cleanup_mock_servers(self):
        """清理Mock服务器"""
        print("\n🧹 清理Mock服务器...")
        
        for process in self.mock_processes:
            try:
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                print(f"    ✅ 停止进程 PID: {process.pid}")
            except Exception as e:
                print(f"    ⚠️  停止进程失败 PID: {process.pid}, 错误: {str(e)}")
        
        self.mock_processes = []
    
    def generate_test_report(self):
        """生成详细测试报告"""
        total_time = datetime.now() - self.test_start_time
        
        print("\n" + "="*80)
        print("📊 AI问答平台项目全面测试报告")
        print("="*80)
        
        # 基本统计
        print(f"🕐 测试时间: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')} - "
              f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  总耗时: {total_time.total_seconds():.1f}秒")
        print(f"📈 总测试数: {self.total_tests}")
        print(f"✅ 通过: {self.passed_tests}")
        print(f"❌ 失败: {self.failed_tests}")
        print(f"⚠️  警告: {self.warning_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"🎯 成功率: {success_rate:.1f}%")
        
        # 按类别显示结果
        print(f"\n📋 分类测试结果:")
        for category, results in self.test_results.items():
            category_passed = sum(1 for r in results if r['success'] is True)
            category_total = len(results)
            print(f"\n  📂 {category} ({category_passed}/{category_total})")
            
            for result in results:
                print(f"    {result['status']} {result['test_name']}: {result['message']}")
                if result['details']:
                    for key, value in result['details'].items():
                        print(f"      {key}: {value}")
        
        # 性能指标
        if self.performance_metrics:
            print(f"\n⚡ 性能指标:")
            for metric, value in self.performance_metrics.items():
                print(f"  {metric}: {value}")
        
        # 环境信息
        print(f"\n🔧 环境信息:")
        for key, value in self.environment_info.items():
            print(f"  {key}: {value}")
        
        # 项目状态评估
        print(f"\n🎯 项目状态评估:")
        if self.failed_tests == 0:
            print("  🎉 优秀！所有测试都通过了")
            print("  ✅ 项目核心功能完整，可以进入下一阶段开发")
        elif self.failed_tests <= 3:
            print("  👍 良好！大部分功能正常，有少量问题")
            print("  🔧 建议优先修复失败的测试项")
        else:
            print("  ⚠️  一般，项目存在一些问题需要解决")
            print("  🛠️  建议逐一修复失败的测试项后再继续开发")
        
        # 推荐后续行动
        print(f"\n🚀 推荐后续行动:")
        if self.failed_tests == 0:
            print("  1. 开始前端界面开发")
            print("  2. 完善API文档")
            print("  3. 进行压力测试")
            print("  4. 准备生产环境部署")
        else:
            print("  1. 修复所有失败的测试项")
            print("  2. 补充单元测试覆盖率")
            print("  3. 优化性能瓶颈")
            print("  4. 完善错误处理机制")
    
    def run_full_test(self):
        """运行完整测试流程"""
        try:
            print("🎬 开始AI问答平台项目全面功能测试")
            print("="*80)
            
            # 收集环境信息
            self.collect_environment_info()
            
            # 测试序列
            test_sequence = [
                ("项目结构", self.test_project_structure),
                ("配置管理", self.test_configuration),
                ("数据库", self.test_database_comprehensive),
                ("Mock服务器", self.start_mock_servers),
                ("API客户端", self.test_api_clients),
                ("AI服务", self.test_ai_services),
                ("同步服务", self.test_sync_service),
                ("调度器", self.test_scheduler_service),
                ("Web API", self.test_web_apis),
                ("现有测试", self.run_existing_tests),
                ("性能测试", self.performance_test),
            ]
            
            for test_name, test_func in test_sequence:
                print(f"\n🔍 测试阶段: {test_name}")
                try:
                    test_func()
                    time.sleep(0.5)  # 短暂间隔
                except Exception as e:
                    print(f"    ❌ 测试阶段 {test_name} 异常: {str(e)}")
                    traceback.print_exc()
            
            # 生成测试报告
            self.generate_test_report()
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 用户中断测试")
        finally:
            # 清理资源
            self.cleanup_mock_servers()
            print(f"\n🏁 测试完成")

def main():
    """主函数"""
    test_suite = EnhancedProjectTestSuite()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print(f"\n🛑 收到中断信号，正在清理...")
        test_suite.cleanup_mock_servers()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行测试
    test_suite.run_full_test()
    
    # 返回测试结果
    return test_suite.failed_tests == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 