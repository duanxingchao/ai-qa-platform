#!/usr/bin/env python3
"""
重置分类工作流程
1. 清除questions表中的错误分类数据
2. 触发AI分类处理，通过外部API重新分类
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """获取数据库连接"""
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')
    
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def analyze_current_classification_data():
    """分析当前questions表中的分类数据"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 分析questions表中的分类数据...")
        
        # 获取总记录数
        cursor.execute("SELECT COUNT(*) FROM questions")
        total_count = cursor.fetchone()[0]
        
        # 获取有分类的记录数
        cursor.execute("SELECT COUNT(*) FROM questions WHERE classification IS NOT NULL AND classification != ''")
        classified_count = cursor.fetchone()[0]
        
        # 获取无分类的记录数
        unclassified_count = total_count - classified_count
        
        print(f"📊 questions表统计:")
        print(f"   总记录数: {total_count}")
        print(f"   已分类记录: {classified_count}")
        print(f"   未分类记录: {unclassified_count}")
        
        if classified_count > 0:
            # 获取分类分布
            cursor.execute("""
                SELECT classification, COUNT(*) as count 
                FROM questions 
                WHERE classification IS NOT NULL AND classification != ''
                GROUP BY classification 
                ORDER BY count DESC
            """)
            
            classifications = cursor.fetchall()
            
            print(f"\n🏷️ 当前分类分布 ({len(classifications)}种分类):")
            for row in classifications:
                print(f"   {row['classification']}: {row['count']}条记录")
            
            # 检查是否有非标准分类
            standard_classifications = [
                '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
                '其他', '工程问题', '科学问题', '教育问题', '经济问题',
                '账户管理', '系统优化', '安全设置', '数据分析',
                '用户体验', '性能优化'
            ]
            
            non_standard = [row for row in classifications if row['classification'] not in standard_classifications]
            
            if non_standard:
                print(f"\n❌ 发现非标准分类 ({len(non_standard)}种):")
                for row in non_standard:
                    print(f"   {row['classification']}: {row['count']}条记录")
            else:
                print(f"\n✅ 所有分类都是标准分类")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
    finally:
        cursor.close()
        conn.close()

def clear_classification_data(dry_run=True):
    """清除questions表中的分类数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 获取当前有分类的记录数
        cursor.execute("SELECT COUNT(*) FROM questions WHERE classification IS NOT NULL AND classification != ''")
        classified_count = cursor.fetchone()[0]
        
        if classified_count == 0:
            print("✅ questions表中没有分类数据需要清除")
            return True
        
        print(f"🧹 准备清除 {classified_count} 条记录的分类数据")
        
        if dry_run:
            print("💡 这是模拟运行，实际数据未被修改")
            print("   如需执行实际清除，请添加 --execute 参数")
            return True
        
        # 清除分类数据
        cursor.execute("UPDATE questions SET classification = NULL WHERE classification IS NOT NULL")
        updated_rows = cursor.rowcount
        
        conn.commit()
        print(f"✅ 成功清除了 {updated_rows} 条记录的分类数据")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 清除分类数据失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def trigger_ai_classification():
    """触发AI分类处理"""
    print("🤖 触发AI分类处理...")
    
    try:
        # 调用AI处理API
        response = requests.post("http://localhost:8088/api/ai/process-batch", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ AI分类处理触发成功")
                print(f"   处理结果: {data.get('message', '无详细信息')}")
                return True
            else:
                print(f"❌ AI分类处理失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ AI分类API调用失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ AI分类API调用异常: {e}")
        return False

def verify_classification_results():
    """验证分类结果"""
    print("🔍 验证AI分类结果...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 获取分类统计
        cursor.execute("SELECT COUNT(*) FROM questions")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM questions WHERE classification IS NOT NULL AND classification != ''")
        classified_count = cursor.fetchone()[0]
        
        print(f"📊 AI分类处理结果:")
        print(f"   总记录数: {total_count}")
        print(f"   已分类记录: {classified_count}")
        print(f"   分类完成率: {(classified_count/total_count*100):.1f}%" if total_count > 0 else "0%")
        
        if classified_count > 0:
            # 获取分类分布
            cursor.execute("""
                SELECT classification, COUNT(*) as count 
                FROM questions 
                WHERE classification IS NOT NULL AND classification != ''
                GROUP BY classification 
                ORDER BY count DESC
            """)
            
            classifications = cursor.fetchall()
            
            print(f"\n🏷️ 新的分类分布 ({len(classifications)}种分类):")
            for row in classifications:
                print(f"   {row['classification']}: {row['count']}条记录")
            
            # 验证是否都是标准分类
            standard_classifications = [
                '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
                '其他', '工程问题', '科学问题', '教育问题', '经济问题',
                '账户管理', '系统优化', '安全设置', '数据分析',
                '用户体验', '性能优化'
            ]
            
            if len(classifications) == 16 and all(row['classification'] in standard_classifications for row in classifications):
                print(f"\n🎉 分类结果完美！所有分类都是标准的16种分类")
            else:
                print(f"\n⚠️ 分类结果需要检查，可能存在非标准分类")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("🚀 开始重置分类工作流程")
    print("=" * 60)
    print("📝 正确的分类工作流程:")
    print("   1. table1存储原始数据（无classification）")
    print("   2. 同步到questions表（classification初始为NULL）")
    print("   3. AI处理服务调用外部分类API")
    print("   4. 将API返回的分类结果填充到questions.classification")
    print("=" * 60)
    
    # 分析当前状态
    analyze_current_classification_data()
    
    # 检查命令行参数
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print(f"\n⚠️ 这是模拟运行模式")
        print("   如需执行实际重置，请添加 --execute 参数")
    
    # 清除现有分类数据
    print(f"\n🧹 第一步：清除现有分类数据")
    clear_success = clear_classification_data(dry_run=dry_run)
    
    if not clear_success:
        print("❌ 清除分类数据失败，停止后续操作")
        return
    
    if not dry_run:
        # 触发AI分类处理
        print(f"\n🤖 第二步：触发AI分类处理")
        ai_success = trigger_ai_classification()
        
        if ai_success:
            print(f"\n🔍 第三步：验证分类结果")
            verify_classification_results()
        else:
            print("❌ AI分类处理失败")
    else:
        print(f"\n💡 模拟运行完成")
        print("   实际执行时将会:")
        print("   1. 清除questions表中的所有分类数据")
        print("   2. 调用AI处理API重新分类")
        print("   3. 验证分类结果")

if __name__ == '__main__':
    main()
