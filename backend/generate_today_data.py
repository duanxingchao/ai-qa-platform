#!/usr/bin/env python3
"""
生成今日的mock数据
确保数据能正确显示在dashboard中
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
    "如何联系技术支持？"
]

MOCK_ANSWERS = [
    "您可以通过以下步骤重置密码：1. 点击登录页面的'忘记密码'链接 2. 输入您的邮箱地址 3. 检查邮箱并点击重置链接 4. 设置新密码。",
    "登录失败可能有以下原因：1. 用户名或密码错误 2. 账户被锁定 3. 网络连接问题 4. 系统维护。请检查输入信息，或稍后重试。",
    "导出数据的方法：1. 进入设置页面 2. 选择'数据管理' 3. 点击'导出数据' 4. 选择导出格式和范围 5. 下载文件。",
    "如果您忘记了用户名，可以：1. 使用注册时的邮箱地址 2. 点击'忘记用户名' 3. 系统会发送用户名到您的邮箱。",
    "修改个人资料：1. 登录后点击头像 2. 选择'个人设置' 3. 修改相关信息 4. 点击保存。",
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
    "联系技术支持：1. 查看帮助文档 2. 提交工单 3. 在线客服咨询 4. 电话联系。提供7x24小时服务。"
]

# 基础配置数据
DEVICE_TYPES = ['PC', 'Mobile', 'Tablet', 'TV']
CLASSIFICATIONS = ['技术问题', '业务咨询', '产品使用', '故障排查', '功能建议', '其他']
SERVICE_IDS = ['service_001', 'service_002', 'service_003', 'service_004']
QA_TYPES = ['FAQ', 'CHAT', 'SEARCH', 'HELP']
INTENTS = ['查询', '咨询', '投诉', '建议', '帮助']

def generate_today_data(count=50):
    """生成今日的mock数据"""
    print(f"🔄 开始生成今日 {count} 条mock数据...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 获取今日的时间范围
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = today_start + timedelta(days=1)
        
        print(f"📅 今日时间范围: {today_start} 到 {today_end}")
        
        # 生成数据
        for i in range(count):
            # 随机选择问题和答案
            query = random.choice(MOCK_QUESTIONS)
            answer = random.choice(MOCK_ANSWERS)
            
            # 生成今日内的随机时间
            random_seconds = random.randint(0, 24 * 60 * 60 - 1)  # 今日内的随机秒数
            random_time = today_start + timedelta(seconds=random_seconds)
            
            # 插入数据到table1
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
        
        print(f"✅ 成功生成今日 {count} 条mock数据")
        return True
        
    except Exception as e:
        print(f"❌ 生成今日数据失败: {str(e)}")
        return False

def get_today_stats():
    """获取今日数据统计"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        # table1中今日的数据
        cursor.execute("""
            SELECT COUNT(*) FROM table1 
            WHERE DATE(sendmessagetime) = %s
        """, (today,))
        table1_today = cursor.fetchone()[0]
        
        # questions表中今日的数据
        cursor.execute("""
            SELECT COUNT(*) FROM questions 
            WHERE DATE(created_at) = %s
        """, (today,))
        questions_today = cursor.fetchone()[0]
        
        # answers表中今日的数据
        cursor.execute("""
            SELECT COUNT(*) FROM answers 
            WHERE DATE(created_at) = %s
        """, (today,))
        answers_today = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 今日数据统计:")
        print(f"   table1表: {table1_today}条")
        print(f"   questions表: {questions_today}条")
        print(f"   answers表: {answers_today}条")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取今日统计失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 生成今日Mock数据工具")
    print("=" * 50)
    
    # 1. 生成今日数据
    if not generate_today_data(50):
        return
    
    # 2. 显示统计
    get_today_stats()
    
    print("\n🎉 今日数据生成完成！")
    print("现在可以测试dashboard的'本日'筛选功能了。")

if __name__ == "__main__":
    main() 