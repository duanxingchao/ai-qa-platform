#!/usr/bin/env python3
"""插入测试数据脚本"""

from app import create_app
from app.utils.database import db
from sqlalchemy import text
from datetime import datetime, timedelta

def main():
    app = create_app()
    with app.app_context():
        try:
            # 按正确顺序清空数据（考虑外键约束）
            print("清空现有数据...")
            db.session.execute(text('DELETE FROM scores'))
            db.session.execute(text('DELETE FROM answers'))
            db.session.execute(text('DELETE FROM review_status'))
            db.session.execute(text('DELETE FROM question_reclassifications'))
            db.session.execute(text('DELETE FROM questions'))
            db.session.execute(text('DELETE FROM table1'))
            
            # 插入测试数据到table1
            print("插入测试数据...")
            test_data = [
                {
                    'pageid': 'page001',
                    'devicetypename': 'mobile',
                    'sendmessagetime': datetime.now() - timedelta(hours=1),
                    'query': '如何使用这个产品？',
                    'answer': '您可以按照说明书操作',
                    'serviceid': 'service001',
                    'qatype': 'question',
                    'intent': 'product_usage',
                    'iskeyboardinput': True,
                    'isstopanswer': False
                },
                {
                    'pageid': 'page002',
                    'devicetypename': 'desktop',
                    'sendmessagetime': datetime.now() - timedelta(minutes=30),
                    'query': '价格是多少？',
                    'answer': '价格请咨询客服',
                    'serviceid': 'service002',
                    'qatype': 'question',
                    'intent': 'price_inquiry',
                    'iskeyboardinput': True,
                    'isstopanswer': False
                },
                {
                    'pageid': 'page003',
                    'devicetypename': 'tablet',
                    'sendmessagetime': datetime.now() - timedelta(minutes=15),
                    'query': '如何退货？',
                    'answer': '请联系客服办理退货',
                    'serviceid': 'service003',
                    'qatype': 'question',
                    'intent': 'return_policy',
                    'iskeyboardinput': True,
                    'isstopanswer': False
                }
            ]
            
            for data in test_data:
                sql = text('''
                    INSERT INTO table1 (pageid, devicetypename, sendmessagetime, query, answer, serviceid, qatype, intent, iskeyboardinput, isstopanswer)
                    VALUES (:pageid, :devicetypename, :sendmessagetime, :query, :answer, :serviceid, :qatype, :intent, :iskeyboardinput, :isstopanswer)
                ''')
                db.session.execute(sql, data)
            
            db.session.commit()
            print('测试数据插入成功')
            
            # 验证数据
            result = db.session.execute(text('SELECT COUNT(*) FROM table1'))
            count = result.scalar()
            print(f'table1中有 {count} 条记录')
            
            # 显示插入的数据
            result = db.session.execute(text('SELECT pageid, query, sendmessagetime FROM table1 ORDER BY sendmessagetime'))
            print("\n插入的数据:")
            for row in result:
                print(f"  {row[0]}: {row[1]} ({row[2]})")
                
        except Exception as e:
            print(f"错误: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()
