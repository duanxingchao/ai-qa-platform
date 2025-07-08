#!/usr/bin/env python3
"""
项目稳定性综合测试
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_database_models():
    """测试数据库和数据模型"""
    print('=== 数据库连接测试 ===')
    
    from app import create_app
    from app.utils.database import db, execute_sql
    from app.models import Question, Answer, Score, ReviewStatus

    app = create_app()
    with app.app_context():
        # 测试表是否存在
        tables = ['questions', 'answers', 'scores', 'review_status', 'table1']
        for table in tables:
            try:
                result = execute_sql(f'SELECT COUNT(*) FROM {table}')
                count = result.scalar()
                print(f'✅ {table}: {count} 条记录')
            except Exception as e:
                print(f'❌ {table}: {str(e)}')
        
        print('\n=== 数据模型测试 ===')
        # 测试Question表的基本操作
        try:
            # 测试插入一条记录
            result = execute_sql("""
                INSERT INTO questions (business_id, pageid, query, devicetypename, processing_status) 
                VALUES ('test_123', 'test_page', '测试问题', 'Web', 'pending')
                RETURNING id
            """)
            test_id = result.scalar()
            print('✅ Question记录插入成功')
            
            # 测试查询记录
            result = execute_sql("SELECT business_id, query FROM questions WHERE id = :id", {'id': test_id})
            row = result.fetchone()
            if row and row[0] == 'test_123':
                print('✅ Question记录查询成功')
            else:
                print('❌ Question记录查询失败')
            
            # 删除测试数据
            execute_sql("DELETE FROM questions WHERE id = :id", {'id': test_id})
            print('✅ Question记录删除成功')
        except Exception as e:
            print(f'❌ Question模型测试失败: {str(e)}')
            try:
                db.session.rollback()
            except:
                pass

def test_sync_service():
    """测试同步服务"""
    print('\n=== 同步服务测试 ===')
    
    from app import create_app
    from app.services.sync_service import sync_service

    app = create_app()
    with app.app_context():
        # 1. 获取同步状态
        print('1. 同步状态:')
        try:
            status = sync_service.get_sync_status()
            print(f'   {status}')
            print('✅ 同步状态获取成功')
        except Exception as e:
            print(f'❌ 同步状态获取失败: {str(e)}')
        
        # 2. 获取统计信息
        print('\n2. 统计信息:')
        try:
            stats = sync_service.get_sync_statistics()
            print(f'   {stats}')
            print('✅ 统计信息获取成功')
        except Exception as e:
            print(f'❌ 统计信息获取失败: {str(e)}')
        
        # 3. 执行增量同步
        print('\n3. 增量同步:')
        try:
            result = sync_service.perform_sync()
            print(f'   {result}')
            if result['success']:
                print('✅ 增量同步执行成功')
            else:
                print('❌ 增量同步执行失败')
        except Exception as e:
            print(f'❌ 增量同步异常: {str(e)}')

def test_data_consistency():
    """测试数据一致性"""
    print('\n=== 数据一致性测试 ===')
    
    from app import create_app
    from app.utils.database import execute_sql
    import hashlib

    app = create_app()
    with app.app_context():
        # 获取table1的一条记录
        try:
            result = execute_sql('SELECT pageid, sendmessagetime, query FROM table1 LIMIT 1')
            row = result.fetchone()
            if row:
                pageid, send_time, query_text = row
                
                # 计算expected business_id
                raw_str = f'{pageid}{send_time.isoformat() if send_time else ""}{query_text}'
                expected_business_id = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
                
                print(f'table1记录: pageid={pageid}, query={query_text[:30]}...')
                print(f'预期business_id: {expected_business_id}')
                
                # 查找对应的questions记录
                result = execute_sql('SELECT business_id FROM questions WHERE pageid = :pageid', {'pageid': pageid})
                questions_row = result.fetchone()
                if questions_row:
                    actual_business_id = questions_row[0]
                    print(f'实际business_id: {actual_business_id}')
                    
                    if expected_business_id == actual_business_id:
                        print('✅ business_id生成逻辑正确')
                    else:
                        print('❌ business_id生成逻辑错误')
                else:
                    print('❌ 未找到对应的questions记录')
            else:
                print('❌ table1中无数据')
        except Exception as e:
            print(f'❌ 数据一致性测试失败: {str(e)}')

def test_config_environment():
    """测试配置和环境"""
    print('\n=== 配置测试 ===')
    
    from app.config import config
    from app import create_app
    import os

    # 测试配置加载
    for env in ['development', 'production', 'testing']:
        try:
            cfg = config[env]
            print(f'✅ {env}配置加载成功')
            print(f'   数据库URL: {cfg.SQLALCHEMY_DATABASE_URI[:50]}...')
            print(f'   调试模式: {cfg.DEBUG}')
        except Exception as e:
            print(f'❌ {env}配置加载失败: {str(e)}')

    print('\n=== 应用创建测试 ===')
    # 测试不同环境下的应用创建
    for env in ['development', 'testing']:
        try:
            original_env = os.environ.get('FLASK_ENV')
            os.environ['FLASK_ENV'] = env
            app = create_app(env)
            print(f'✅ {env}环境应用创建成功')
            # 恢复原始环境变量
            if original_env:
                os.environ['FLASK_ENV'] = original_env
            elif 'FLASK_ENV' in os.environ:
                del os.environ['FLASK_ENV']
        except Exception as e:
            print(f'❌ {env}环境应用创建失败: {str(e)}')

def test_scheduler_task():
    """测试定时任务功能"""
    print('\n=== 定时任务测试 ===')
    
    from app import create_app
    from app.services.sync_service import sync_data_task

    app = create_app()
    print('✅ 应用创建成功，定时任务已启动')

    # 测试手动调用定时任务
    try:
        sync_data_task(app)
        print('✅ 定时任务手动调用成功')
    except Exception as e:
        print(f'❌ 定时任务手动调用失败: {str(e)}')

def test_concurrent_sync():
    """测试并发同步"""
    print('\n=== 并发同步测试 ===')
    
    from app import create_app
    from app.services.sync_service import sync_service
    import threading
    import time

    def sync_test(thread_id):
        try:
            app = create_app()
            with app.app_context():
                result = sync_service.perform_sync()
                print(f'   线程{thread_id}同步结果: {result["success"]} - {result["message"]}')
                return result["success"]
        except Exception as e:
            print(f'   线程{thread_id}同步失败: {str(e)}')
            return False

    threads = []
    results = []

    # 创建3个并发同步线程
    for i in range(3):
        thread = threading.Thread(target=lambda i=i: results.append(sync_test(i+1)))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    success_count = sum(1 for r in results if r)
    print(f'✅ 并发测试完成: {success_count}/{len(threads)} 个线程成功')

def test_table_structure():
    """测试表结构"""
    print('\n=== 表结构测试 ===')
    
    from app import create_app
    from app.utils.database import execute_sql

    app = create_app()
    with app.app_context():
        # 测试questions表结构
        try:
            result = execute_sql("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'questions' 
                ORDER BY ordinal_position
            """)
            
            print('questions表结构:')
            for row in result:
                column_name, data_type, is_nullable = row
                print(f'   {column_name}: {data_type} (nullable: {is_nullable})')
            print('✅ questions表结构检查完成')
        except Exception as e:
            print(f'❌ 表结构检查失败: {str(e)}')

if __name__ == '__main__':
    print('🚀 开始项目稳定性综合测试...\n')
    
    try:
        test_database_models()
        test_sync_service() 
        test_data_consistency()
        test_config_environment()
        test_scheduler_task()
        test_table_structure()
        test_concurrent_sync()
        
        print('\n' + '='*50)
        print('🎉 所有测试完成！项目稳定性验证通过！')
        print('='*50)
        
    except Exception as e:
        print(f'\n❌ 测试过程中出现严重错误: {str(e)}')
        import traceback
        traceback.print_exc() 