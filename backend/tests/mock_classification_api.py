#!/usr/bin/env python3
"""
Mock分类API服务器
模拟外部分类API，用于测试API客户端功能
"""
import random
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# 预定义的16种问题分类
CATEGORIES = {
    'education': {
        'keywords': ['教育', '学习', '课程', '培训', '考试', '学校', '大学', '老师', '学生', '知识', '技能', '证书', '学历', '专业'],
        'name': '教育',
        'subcategories': ['基础教育', '高等教育', '职业培训', '在线学习', '考试认证']
    },
    'health_medical': {
        'keywords': ['健康', '医疗', '医院', '医生', '病', '症状', '治疗', '药物', '体检', '保健', '养生', '疾病', '康复', '护理'],
        'name': '医疗健康',
        'subcategories': ['疾病咨询', '健康保健', '医疗服务', '药物咨询', '康复护理']
    },
    'finance_economics': {
        'keywords': ['金融', '经济', '银行', '投资', '理财', '保险', '贷款', '股票', '基金', '财务', '税务', '预算', '收入', '支出'],
        'name': '经济金融',
        'subcategories': ['银行服务', '投资理财', '保险产品', '税务咨询', '经济分析']
    },
    'technology': {
        'keywords': ['科技', '技术', '电脑', '手机', '软件', '网络', '互联网', 'AI', '人工智能', '编程', '数据', '云计算', '区块链'],
        'name': '科技技术',
        'subcategories': ['软件技术', '硬件设备', '网络通信', '人工智能', '数据科学']
    },
    'legal': {
        'keywords': ['法律', '法规', '合同', '诉讼', '律师', '权利', '义务', '违法', '犯罪', '维权', '仲裁', '司法', '法院'],
        'name': '法律',
        'subcategories': ['民事法律', '刑事法律', '商事法律', '劳动法律', '知识产权']
    },
    'entertainment': {
        'keywords': ['娱乐', '电影', '音乐', '游戏', '明星', '综艺', '电视', '演出', '票务', '休闲', '爱好', '文化', '艺术'],
        'name': '娱乐',
        'subcategories': ['影视娱乐', '音乐艺术', '游戏娱乐', '文化活动', '票务服务']
    },
    'sports': {
        'keywords': ['体育', '运动', '健身', '比赛', '球类', '跑步', '游泳', '瑜伽', '健身房', '教练', '锻炼', '竞技', '赛事'],
        'name': '体育运动',
        'subcategories': ['健身运动', '竞技体育', '户外运动', '体育赛事', '运动器材']
    },
    'travel': {
        'keywords': ['旅游', '旅行', '景点', '酒店', '机票', '火车', '攻略', '导游', '签证', '度假', '出行', '预订', '住宿'],
        'name': '旅游',
        'subcategories': ['国内旅游', '国际旅游', '酒店住宿', '交通预订', '旅游攻略']
    },
    'food': {
        'keywords': ['美食', '餐饮', '菜谱', '烹饪', '外卖', '餐厅', '食材', '营养', '饮食', '特色菜', '小吃', '饮品', '厨艺'],
        'name': '美食餐饮',
        'subcategories': ['餐厅推荐', '菜谱烹饪', '外卖服务', '食材选购', '营养健康']
    },
    'shopping': {
        'keywords': ['购物', '商品', '价格', '优惠', '促销', '品牌', '质量', '售后', '退换货', '物流', '支付', '电商', '商场'],
        'name': '购物消费',
        'subcategories': ['网购服务', '实体购物', '品牌商品', '优惠活动', '售后服务']
    },
    'transportation': {
        'keywords': ['交通', '出行', '公交', '地铁', '打车', '驾驶', '汽车', '车辆', '路线', '停车', '违章', '驾照', '保养'],
        'name': '交通出行',
        'subcategories': ['公共交通', '私家车', '出租车', '交通违章', '车辆服务']
    },
    'real_estate': {
        'keywords': ['房产', '房子', '买房', '租房', '装修', '房价', '楼盘', '中介', '物业', '户型', '地段', '贷款', '契税'],
        'name': '房产置业',
        'subcategories': ['买房置业', '租房服务', '装修装饰', '物业管理', '房产投资']
    },
    'career_work': {
        'keywords': ['工作', '职业', '求职', '招聘', '简历', '面试', '薪资', '升职', '跳槽', '职场', '同事', '领导', '技能'],
        'name': '工作职场',
        'subcategories': ['求职招聘', '职业发展', '职场技能', '薪资福利', '工作环境']
    },
    'relationships': {
        'keywords': ['感情', '恋爱', '婚姻', '家庭', '朋友', '人际关系', '沟通', '约会', '结婚', '离婚', '育儿', '亲子', '社交'],
        'name': '情感关系',
        'subcategories': ['恋爱交友', '婚姻家庭', '亲子关系', '人际交往', '心理咨询']
    },
    'life_services': {
        'keywords': ['生活', '服务', '家政', '维修', '快递', '充值', '缴费', '证件', '办事', '社区', '便民', '日常', '琐事'],
        'name': '生活服务',
        'subcategories': ['家政服务', '维修服务', '快递物流', '生活缴费', '证件办理']
    },
    'government_social': {
        'keywords': ['政务', '政府', '社会', '公共', '民生', '政策', '社保', '公积金', '户籍', '证明', '申请', '办理', '咨询'],
        'name': '政务社会',
        'subcategories': ['政务服务', '社会保障', '公共政策', '民生服务', '社会事务']
    }
}

def classify_question_and_answer(question_text, answer_text=None):
    """
    基于问题和答案内容进行分类
    
    Args:
        question_text: 问题文本
        answer_text: 答案文本（可选）
    
    Returns:
        dict: 分类结果
    """
    # 合并问题和答案文本进行分析
    combined_text = question_text.lower()
    if answer_text:
        combined_text += " " + answer_text.lower()
    
    # 计算每个类别的匹配分数
    scores = {}
    for category_id, category_info in CATEGORIES.items():
        score = 0
        matched_keywords = []
        
        for keyword in category_info['keywords']:
            if keyword.lower() in combined_text:
                score += 1
                matched_keywords.append(keyword)
        
        # 答案文本权重稍高一些
        if answer_text:
            for keyword in category_info['keywords']:
                if keyword.lower() in answer_text.lower():
                    score += 0.5  # 额外权重
        
        scores[category_id] = {
            'score': score,
            'matched_keywords': matched_keywords
        }
    
    # 找到最高分的类别
    best_score = max(scores.values(), key=lambda x: x['score'])['score']
    
    if best_score > 0:
        best_category = max(scores.keys(), key=lambda k: scores[k]['score'])
        confidence = min(0.6 + best_score * 0.1, 0.98)
        matched_keywords = scores[best_category]['matched_keywords']
    else:
        # 默认分类
        best_category = 'life_services'
        confidence = 0.3
        matched_keywords = []
    
    category_info = CATEGORIES[best_category]
    subcategory = random.choice(category_info['subcategories'])
    
    return {
        'category': category_info['name'],
        'category_id': best_category,
        'confidence': round(confidence, 2),
        'subcategory': subcategory,
        'tags': matched_keywords[:3],  # 最多返回3个匹配的关键词
        'analysis': {
            'question_weight': 1.0,
            'answer_weight': 0.5 if answer_text else 0.0,
            'total_keywords_matched': len(matched_keywords)
        }
    }

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'mock-classification-api',
        'version': '1.0.0',
        'timestamp': time.time(),
        'supported_categories': len(CATEGORIES)
    })

@app.route('/classify', methods=['POST'])
def classify():
    """问题分类接口"""
    try:
        # 模拟API延迟
        time.sleep(random.uniform(0.1, 0.5))
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid JSON data'
            }), 400
        
        # 检查必需字段
        question = data.get('question')
        if not question:
            return jsonify({
                'error': 'Missing required field: question'
            }), 400
        
        # 答案字段是可选的
        answer = data.get('answer')
        
        # 验证API密钥
        auth_header = request.headers.get('Authorization', '')
        api_key_header = request.headers.get('X-API-Key', '')
        
        if not auth_header and not api_key_header:
            return jsonify({
                'error': 'Missing authentication'
            }), 401
        
        # 模拟偶尔的服务器错误（5%概率）
        if random.random() < 0.05:
            return jsonify({
                'error': 'Internal server error'
            }), 500
        
        # 模拟偶尔的速率限制（2%概率）
        if random.random() < 0.02:
            return jsonify({
                'error': 'Rate limit exceeded'
            }), 429
        
        # 执行分类
        start_time = time.time()
        result = classify_question_and_answer(question, answer)
        processing_time = (time.time() - start_time) * 1000
        
        # 添加处理时间和请求信息
        result['processing_time'] = round(processing_time, 2)
        result['request_info'] = {
            'question_length': len(question),
            'answer_length': len(answer) if answer else 0,
            'has_answer': bool(answer)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Classification failed: {str(e)}'
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取API统计信息"""
    return jsonify({
        'total_requests': random.randint(1000, 5000),
        'success_rate': round(random.uniform(0.95, 0.99), 3),
        'average_response_time': round(random.uniform(200, 500), 2),
        'categories': {
            'total_count': len(CATEGORIES),
            'categories': list(CATEGORIES.keys())
        },
        'features': {
            'question_analysis': True,
            'answer_analysis': True,
            'keyword_matching': True,
            'confidence_scoring': True
        },
        'uptime': f"{random.randint(10, 100)} days"
    })

@app.route('/categories', methods=['GET'])
def get_categories():
    """获取支持的分类列表"""
    categories_list = []
    for category_id, info in CATEGORIES.items():
        categories_list.append({
            'id': category_id,
            'name': info['name'],
            'subcategories': info['subcategories'],
            'keyword_count': len(info['keywords'])
        })
    
    return jsonify({
        'total_count': len(CATEGORIES),
        'categories': categories_list
    })

if __name__ == '__main__':
    print("🤖 启动Mock分类API服务器...")
    print("📍 地址: http://localhost:8001")
    print("🔗 健康检查: http://localhost:8001/health") 
    print("🔗 分类接口: POST http://localhost:8001/classify")
    print("📊 统计接口: http://localhost:8001/stats")
    print("📋 分类列表: http://localhost:8001/categories")
    print("-" * 50)
    print("📝 POST数据格式:")
    print("""   {
       "question": "用户问题文本", 
       "answer": "AI回答文本（可选）"
   }""")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=8001, debug=True) 