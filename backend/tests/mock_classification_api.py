#!/usr/bin/env python3
"""
Mock分类API服务器
模拟外部分类API，用于测试API客户端功能
"""
import random
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# 固定的16个问题分类 - 所有问题都应该从这16个类别中随机分配
CATEGORIES = [
    '技术问题',
    '产品使用',
    '业务咨询',
    '功能建议',
    '故障排查',
    '其他',
    '工程问题',
    '科学问题',
    '教育问题',
    '经济问题',
    '账户管理',
    '系统优化',
    '安全设置',
    '数据分析',
    '用户体验',
    '性能优化'
]

def classify_question_and_answer(question_text, answer_text=None):
    """
    真正随机地从16个固定分类中返回一个分类
    确保每次调用都有相等的概率选择任意分类

    Args:
        question_text: 问题文本
        answer_text: 答案文本（可选）

    Returns:
        dict: 分类结果
    """
    # 使用真正的随机选择，确保分布均匀
    selected_category = random.choice(CATEGORIES)

    # 生成随机的置信度（0.7-0.95之间）
    confidence = round(random.uniform(0.7, 0.95), 2)

    # 生成一些模拟的分析标签
    sample_tags = ['关键词1', '关键词2', '关键词3']
    selected_tags = random.sample(sample_tags, random.randint(1, 3))

    return {
        'category': selected_category,
        'category_id': selected_category.lower().replace(' ', '_'),
        'confidence': confidence,
        'subcategory': f'{selected_category}子类',
        'tags': selected_tags,
        'analysis': {
            'question_weight': 1.0,
            'answer_weight': 0.5 if answer_text else 0.0,
            'total_keywords_matched': len(selected_tags),
            'random_selection': True
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
    """问题分类接口 - 符合用户的API格式"""
    try:
        # 模拟API延迟
        time.sleep(random.uniform(0.1, 0.5))
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid JSON data'
            }), 400
        
        # 检查用户的API格式
        inputs = data.get('inputs')
        if not inputs:
            return jsonify({
                'error': 'Missing required field: inputs'
            }), 400
        
        question = inputs.get('QUERY')
        if not question:
            return jsonify({
                'error': 'Missing required field: inputs.QUERY'
            }), 400
        
        # 答案字段是可选的
        answer = inputs.get('ANSWER', '')
        
        # 检查其他必需字段
        response_mode = data.get('response_mode')
        user = data.get('user')
        
        if response_mode != 'blocking':
            return jsonify({
                'error': 'Only blocking response mode is supported'
            }), 400
        
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
        classification_result = classify_question_and_answer(question, answer)
        processing_time = (time.time() - start_time) * 1000
        
        # 按照用户的API响应格式返回
        response_data = {
            "data": {
                "outputs": {
                    "text": classification_result['category']  # 只返回分类名称
                }
            },
            "metadata": {
                "processing_time": round(processing_time, 2),
                "user": user,
                "request_info": {
                    'question_length': len(question),
                    'answer_length': len(answer) if answer else 0,
                    'has_answer': bool(answer)
                }
            }
        }
        
        return jsonify(response_data)
        
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
            'categories': CATEGORIES
        },
        'features': {
            'random_classification': True,
            'fixed_16_categories': True,
            'confidence_scoring': True
        },
        'uptime': f"{random.randint(10, 100)} days"
    })

@app.route('/categories', methods=['GET'])
def get_categories():
    """获取支持的分类列表"""
    categories_list = []
    for i, category_name in enumerate(CATEGORIES):
        categories_list.append({
            'id': f'category_{i+1}',
            'name': category_name,
            'subcategories': [f'{category_name}子类1', f'{category_name}子类2'],
            'keyword_count': random.randint(5, 15)
        })

    return jsonify({
        'total_count': len(CATEGORIES),
        'categories': categories_list
    })

def find_available_port(start_port=8001, max_attempts=10):
    """查找可用端口"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue

    raise RuntimeError(f"无法找到可用端口（尝试范围: {start_port}-{start_port + max_attempts - 1}）")

if __name__ == '__main__':
    import argparse
    import socket

    # 命令行参数解析
    parser = argparse.ArgumentParser(description='Mock分类API服务器')
    parser.add_argument('--port', type=int, default=8001, help='指定端口号（默认8001）')
    parser.add_argument('--auto-port', action='store_true', help='自动查找可用端口')
    args = parser.parse_args()

    # 确定使用的端口
    if args.auto_port:
        try:
            port = find_available_port(args.port)
            print(f"🔍 自动找到可用端口: {port}")
        except RuntimeError as e:
            print(f"❌ {e}")
            exit(1)
    else:
        port = args.port
        # 检查端口是否可用
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
        except OSError:
            print(f"❌ 端口 {port} 已被占用")
            print("💡 解决方案:")
            print(f"   1. 使用其他端口: python {__file__} --port 8002")
            print(f"   2. 自动查找端口: python {__file__} --auto-port")
            print(f"   3. 停止占用程序: sudo lsof -i :{port}")
            exit(1)

    print("🤖 启动Mock分类API服务器...")
    print(f"📍 地址: http://localhost:{port}")
    print(f"🔗 健康检查: http://localhost:{port}/health")
    print(f"🔗 分类接口: POST http://localhost:{port}/classify")
    print(f"📊 统计接口: http://localhost:{port}/stats")
    print(f"📋 分类列表: http://localhost:{port}/categories")
    print("-" * 50)
    print("📝 按照您的API格式 POST数据:")
    print("""   {
       "inputs": {
           "QUERY": "用户问题文本",
           "ANSWER": "AI回答文本（可选）"
       },
       "response_mode": "blocking",
       "user": "00031559"
   }""")
    print("-" * 50)
    print("📋 支持的16个固定分类:")
    for i, category in enumerate(CATEGORIES, 1):
        print(f"   {i:2d}. {category}")
    print("-" * 50)

    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print(f"\n🛑 Mock分类API服务器已停止")