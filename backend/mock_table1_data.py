#!/usr/bin/env python3
"""
Mock table1数据生成脚本
生成100条测试数据到table1表中
"""
import sys
import os
import psycopg2
import random
from datetime import datetime, timedelta

# 数据库连接配置
DB_CONFIG = {
    'host': "test-huiliu-postgresql.ns-q8rah3y5.svc",
    'port': 5432,
    'user': "postgres",
    'password': "l69jjd9n",
    'database': "ai_qa_platform"
}

# Mock数据模板
MOCK_QUESTIONS = [
    "如何重置我的账户密码？",
    "系统登录失败怎么办？",
    "如何导出我的数据？",
    "忘记用户名怎么找回？",
    "如何修改个人资料？",
    "系统响应很慢是什么原因？",
    "如何备份重要文件？",
    "网络连接不稳定怎么解决？",
    "如何设置自动登录？",
    "系统更新失败怎么办？",
    "如何查看使用统计？",
    "如何设置消息提醒？",
    "如何删除不需要的文件？",
    "如何分享文件给其他用户？",
    "如何设置隐私保护？",
    "系统崩溃了怎么恢复？",
    "如何优化系统性能？",
    "如何设置定时任务？",
    "如何查看错误日志？",
    "如何联系技术支持？",
    "如何升级到最新版本？",
    "如何设置多语言界面？",
    "如何导入外部数据？",
    "如何设置访问权限？",
    "如何查看系统状态？",
    "如何设置数据同步？",
    "如何配置邮件通知？",
    "如何设置安全策略？",
    "如何查看操作历史？",
    "如何设置自动备份？",
    "如何优化存储空间？",
    "如何设置用户组？",
    "如何查看系统资源？",
    "如何设置网络代理？",
    "如何查看API文档？",
    "如何设置数据加密？",
    "如何查看性能报告？",
    "如何设置访问控制？",
    "如何查看系统日志？",
    "如何设置数据压缩？",
    "如何优化查询性能？",
    "如何设置缓存策略？",
    "如何查看错误报告？",
    "如何设置负载均衡？",
    "如何查看监控数据？",
    "如何设置故障转移？",
    "如何查看安全报告？",
    "如何设置数据归档？",
    "如何优化内存使用？",
    "如何设置网络防火墙？"
]

MOCK_ANSWERS = [
    "您可以通过以下步骤重置密码：1. 点击登录页面的'忘记密码'链接 2. 输入您的邮箱地址 3. 检查邮箱并点击重置链接 4. 设置新密码。如果遇到问题，请联系客服。",
    "登录失败可能有以下原因：1. 用户名或密码错误 2. 账户被锁定 3. 网络连接问题 4. 系统维护。请检查输入信息，或稍后重试。",
    "导出数据的方法：1. 进入设置页面 2. 选择'数据管理' 3. 点击'导出数据' 4. 选择导出格式和范围 5. 下载文件。支持CSV、JSON等格式。",
    "如果您忘记了用户名，可以：1. 使用注册时的邮箱地址 2. 点击'忘记用户名' 3. 系统会发送用户名到您的邮箱。",
    "修改个人资料：1. 登录后点击头像 2. 选择'个人设置' 3. 修改相关信息 4. 点击保存。支持修改头像、昵称、联系方式等。",
    "系统响应慢的原因：1. 网络连接问题 2. 服务器负载高 3. 本地缓存过多 4. 浏览器问题。建议清理缓存或稍后重试。",
    "备份文件步骤：1. 选择要备份的文件 2. 点击'备份'按钮 3. 选择备份位置 4. 确认备份。建议定期备份重要数据。",
    "网络连接不稳定解决方法：1. 检查网络设置 2. 重启路由器 3. 更换网络环境 4. 联系网络服务商。",
    "设置自动登录：1. 登录后进入设置 2. 找到'安全设置' 3. 开启'自动登录' 4. 设置有效期。注意安全风险。",
    "系统更新失败：1. 检查网络连接 2. 清理系统缓存 3. 重启设备 4. 手动下载更新包。如果问题持续，请联系技术支持。",
    "查看使用统计：1. 进入'统计中心' 2. 选择时间范围 3. 查看各项数据 4. 导出报告。支持多种统计维度。",
    "设置消息提醒：1. 进入通知设置 2. 选择提醒类型 3. 设置提醒时间 4. 配置提醒方式。支持邮件、短信、推送等。",
    "删除文件：1. 选择要删除的文件 2. 点击删除按钮 3. 确认删除操作 4. 检查回收站。删除后可在回收站恢复。",
    "分享文件：1. 选择要分享的文件 2. 点击分享按钮 3. 设置分享权限 4. 生成分享链接。支持公开和私密分享。",
    "设置隐私保护：1. 进入隐私设置 2. 配置数据访问权限 3. 设置隐私级别 4. 启用隐私保护功能。",
    "系统崩溃恢复：1. 重启系统 2. 检查错误日志 3. 运行系统修复 4. 恢复备份数据。建议定期备份。",
    "优化系统性能：1. 清理无用文件 2. 关闭后台程序 3. 更新驱动程序 4. 增加内存容量。",
    "设置定时任务：1. 进入任务管理 2. 创建新任务 3. 设置执行时间 4. 配置任务参数。支持多种任务类型。",
    "查看错误日志：1. 进入系统管理 2. 选择'日志查看' 3. 筛选错误类型 4. 分析错误原因。",
    "联系技术支持：1. 查看帮助文档 2. 提交工单 3. 在线客服咨询 4. 电话联系。提供7x24小时服务。",
    "升级到最新版本：1. 检查更新 2. 下载新版本 3. 备份重要数据 4. 执行升级。建议在维护时间进行。",
    "设置多语言界面：1. 进入语言设置 2. 选择目标语言 3. 下载语言包 4. 重启应用。支持多种语言。",
    "导入外部数据：1. 准备数据文件 2. 选择导入方式 3. 映射字段关系 4. 执行导入。支持多种格式。",
    "设置访问权限：1. 进入权限管理 2. 创建用户组 3. 分配权限 4. 应用到用户。支持细粒度权限控制。",
    "查看系统状态：1. 进入监控面板 2. 查看各项指标 3. 分析系统健康度 4. 生成状态报告。",
    "设置数据同步：1. 配置同步源 2. 设置同步规则 3. 选择同步频率 4. 启动同步任务。",
    "配置邮件通知：1. 设置邮件服务器 2. 配置发件人信息 3. 设置通知模板 4. 测试邮件发送。",
    "设置安全策略：1. 配置密码策略 2. 设置登录限制 3. 启用安全审计 4. 配置防火墙规则。",
    "查看操作历史：1. 进入审计日志 2. 筛选操作类型 3. 查看详细信息 4. 导出历史记录。",
    "设置自动备份：1. 选择备份内容 2. 设置备份计划 3. 配置存储位置 4. 启用自动备份。",
    "优化存储空间：1. 清理临时文件 2. 压缩大文件 3. 删除重复数据 4. 扩展存储容量。",
    "设置用户组：1. 创建用户组 2. 添加用户成员 3. 分配组权限 4. 管理组设置。",
    "查看系统资源：1. 进入资源监控 2. 查看CPU使用率 3. 监控内存占用 4. 分析磁盘使用情况。",
    "设置网络代理：1. 配置代理服务器 2. 设置代理规则 3. 测试连接 4. 启用代理。",
    "查看API文档：1. 访问开发者中心 2. 选择API版本 3. 查看接口说明 4. 下载SDK。",
    "设置数据加密：1. 选择加密算法 2. 配置密钥管理 3. 设置加密范围 4. 启用加密功能。",
    "查看性能报告：1. 进入性能分析 2. 选择分析维度 3. 生成性能报告 4. 优化建议。",
    "设置访问控制：1. 配置访问策略 2. 设置IP白名单 3. 启用访问日志 4. 监控异常访问。",
    "查看系统日志：1. 进入日志管理 2. 筛选日志级别 3. 搜索关键信息 4. 导出日志文件。",
    "设置数据压缩：1. 选择压缩算法 2. 设置压缩级别 3. 配置压缩规则 4. 启用压缩功能。",
    "优化查询性能：1. 分析查询语句 2. 优化索引结构 3. 调整查询参数 4. 监控查询性能。",
    "设置缓存策略：1. 配置缓存类型 2. 设置缓存大小 3. 定义缓存规则 4. 监控缓存命中率。",
    "查看错误报告：1. 进入错误管理 2. 筛选错误类型 3. 分析错误原因 4. 生成修复建议。",
    "设置负载均衡：1. 配置负载均衡器 2. 设置分发策略 3. 监控服务器状态 4. 调整负载分配。",
    "查看监控数据：1. 进入监控面板 2. 选择监控指标 3. 查看实时数据 4. 设置告警规则。",
    "设置故障转移：1. 配置备用服务器 2. 设置故障检测 3. 配置切换策略 4. 测试故障转移。",
    "查看安全报告：1. 进入安全管理 2. 生成安全报告 3. 分析安全风险 4. 制定安全策略。",
    "设置数据归档：1. 选择归档策略 2. 设置归档规则 3. 配置存储位置 4. 执行归档操作。",
    "优化内存使用：1. 分析内存占用 2. 优化数据结构 3. 清理内存泄漏 4. 增加内存容量。",
    "设置网络防火墙：1. 配置防火墙规则 2. 设置访问控制 3. 监控网络流量 4. 处理安全事件。"
]

# 基础配置数据
DEVICE_TYPES = ['PC', 'Mobile', 'Tablet', 'TV', 'SmartWatch']
CLASSIFICATIONS = ['技术问题', '业务咨询', '产品使用', '故障排查', '功能建议', '账户管理', '系统优化', '安全设置']
SERVICE_IDS = ['service_001', 'service_002', 'service_003', 'service_004', 'service_005']
QA_TYPES = ['FAQ', 'CHAT', 'SEARCH', 'HELP', 'SUPPORT']
INTENTS = ['查询', '咨询', '投诉', '建议', '帮助', '设置', '优化', '故障']

def create_table1_if_not_exists():
    """创建table1表（如果不存在）"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'table1'
            );
        """)
        
        if not cursor.fetchone()[0]:
            # 创建表
            cursor.execute("""
                CREATE TABLE table1 (
                    id SERIAL PRIMARY KEY,
                    pageid VARCHAR(100),
                    devicetypename VARCHAR(50),
                    sendmessagetime TIMESTAMP,
                    query TEXT,
                    answer TEXT,
                    serviceid VARCHAR(50),
                    qatype VARCHAR(50),
                    intent VARCHAR(100),
                    classification VARCHAR(50),
                    iskeyboardinput BOOLEAN,
                    isstopanswer BOOLEAN
                );
            """)
            conn.commit()
            print("✅ table1表创建成功")
        else:
            print("✅ table1表已存在")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建table1表失败: {str(e)}")
        return False

def generate_mock_data(count=100):
    """生成mock数据"""
    print(f"🔄 开始生成 {count} 条mock数据...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 清空现有数据（可选）
        cursor.execute("DELETE FROM table1")
        print("🗑️ 已清空现有数据")
        
        # 生成数据
        base_time = datetime.now() - timedelta(days=30)  # 从30天前开始
        
        for i in range(count):
            # 随机选择问题和答案
            query = random.choice(MOCK_QUESTIONS)
            answer = random.choice(MOCK_ANSWERS)
            
            # 生成随机时间（最近30天内）
            random_time = base_time + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # 插入数据
            cursor.execute("""
                INSERT INTO table1 
                (pageid, devicetypename, sendmessagetime, query, answer, serviceid, qatype, intent, classification, iskeyboardinput, isstopanswer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f'page_{random.randint(1000, 9999)}',
                random.choice(DEVICE_TYPES),
                random_time,
                query,
                answer,
                random.choice(SERVICE_IDS),
                random.choice(QA_TYPES),
                random.choice(INTENTS),
                random.choice(CLASSIFICATIONS),
                random.choice([True, False]),
                random.choice([True, False])
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 成功生成 {count} 条mock数据")
        return True
        
    except Exception as e:
        print(f"❌ 生成mock数据失败: {str(e)}")
        return False

def get_table_stats():
    """获取表统计信息"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 总数据量
        cursor.execute("SELECT COUNT(*) FROM table1")
        total_count = cursor.fetchone()[0]
        
        # 有query的数据量
        cursor.execute("SELECT COUNT(*) FROM table1 WHERE query IS NOT NULL AND query != ''")
        query_count = cursor.fetchone()[0]
        
        # 有answer的数据量
        cursor.execute("SELECT COUNT(*) FROM table1 WHERE answer IS NOT NULL AND answer != ''")
        answer_count = cursor.fetchone()[0]
        
        # 时间范围
        cursor.execute("""
            SELECT 
                MIN(sendmessagetime) as earliest_time,
                MAX(sendmessagetime) as latest_time,
                COUNT(DISTINCT pageid) as unique_pages
            FROM table1
            WHERE sendmessagetime IS NOT NULL
        """)
        time_result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("\n📊 table1表统计信息:")
        print(f"   总记录数: {total_count}")
        print(f"   有效问题数: {query_count}")
        print(f"   有效答案数: {answer_count}")
        print(f"   唯一页面数: {time_result[2] if time_result[2] else 0}")
        if time_result[0] and time_result[1]:
            print(f"   时间范围: {time_result[0]} 到 {time_result[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 Mock table1数据生成工具")
    print("=" * 50)
    
    # 1. 创建表
    if not create_table1_if_not_exists():
        return
    
    # 2. 生成数据
    if not generate_mock_data(100):
        return
    
    # 3. 显示统计
    get_table_stats()
    
    print("\n🎉 Mock数据生成完成！")
    print("现在可以启动后端服务测试工作流了。")

if __name__ == "__main__":
    main() 