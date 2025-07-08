"""
创建table1表和测试数据
"""
import psycopg2
from datetime import datetime, timedelta
import random
import json

# 数据库连接配置
conn = psycopg2.connect(
    host="test-huiliu-postgresql.ns-q8rah3y5.svc",
    port=5432,
    user="postgres",
    password="l69jjd9n",
    database="ai_qa_platform"
)
conn.autocommit = True
cursor = conn.cursor()

try:
    # 创建table1表（如果不存在）
    print("创建table1表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table1 (
            id SERIAL PRIMARY KEY,
            pageid VARCHAR(100),
            devicetypename VARCHAR(50),
            sendmessagetime TIMESTAMP,
            query TEXT,
            serviceid VARCHAR(50),
            qatype VARCHAR(50),
            intent VARCHAR(100),
            classification VARCHAR(50),
            iskeyboardinput BOOLEAN,
            isstopanswer BOOLEAN
        );
    """)
    print("✅ table1表创建成功")
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM table1")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"ℹ️  table1表已有 {count} 条数据")
    else:
        # 插入测试数据
        print("插入测试数据...")
        
        # 测试问题列表
        test_queries = [
            "如何查询账户余额？",
            "怎么修改密码？", 
            "我的订单在哪里查看？",
            "如何联系客服？",
            "退款流程是什么？",
            "如何绑定银行卡？",
            "积分如何使用？",
            "会员权益有哪些？",
            "发票怎么开？",
            "配送费用怎么计算？",
            "如何取消订单？",
            "怎么申请退货？",
            "支付失败怎么办？",
            "如何查看物流信息？",
            "优惠券在哪里领取？"
        ]
        
        # 设备类型
        device_types = ["iOS", "Android", "Web", "H5"]
        
        # 服务ID
        service_ids = ["service_001", "service_002", "service_003"]
        
        # QA类型
        qa_types = ["FAQ", "智能问答", "人工客服"]
        
        # 意图分类
        intents = ["查询", "操作指导", "投诉", "咨询", "反馈"]
        
        # 插入数据
        for i in range(30):  # 插入30条测试数据
            pageid = f"page_{random.randint(1000, 9999)}"
            devicetypename = random.choice(device_types)
            # 生成最近7天内的随机时间
            sendmessagetime = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            query = random.choice(test_queries)
            serviceid = random.choice(service_ids)
            qatype = random.choice(qa_types)
            intent = random.choice(intents)
            classification = None  # 初始为空，等待分类API填充
            iskeyboardinput = random.choice([True, False])
            isstopanswer = random.choice([True, False])
            
            cursor.execute("""
                INSERT INTO table1 (
                    pageid, devicetypename, sendmessagetime, query,
                    serviceid, qatype, intent, classification,
                    iskeyboardinput, isstopanswer
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pageid, devicetypename, sendmessagetime, query,
                serviceid, qatype, intent, classification,
                iskeyboardinput, isstopanswer
            ))
        
        print("✅ 成功插入30条测试数据")
    
    # 显示数据统计
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT pageid) as unique_pages,
            MIN(sendmessagetime) as earliest_time,
            MAX(sendmessagetime) as latest_time
        FROM table1
    """)
    
    stats = cursor.fetchone()
    print("\n📊 数据统计:")
    print(f"  总记录数: {stats[0]}")
    print(f"  唯一页面数: {stats[1]}")
    print(f"  最早时间: {stats[2]}")
    print(f"  最新时间: {stats[3]}")
    
except Exception as e:
    print(f"❌ 错误: {str(e)}")
finally:
    cursor.close()
    conn.close()
    
print("\n✅ 测试数据准备完成！") 