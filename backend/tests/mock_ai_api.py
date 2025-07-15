#!/usr/bin/env python3
"""
Mock AI API服务器
模拟豆包AI和小天AI的答案生成接口，用于测试答案生成流程

启动方式:
python mock_ai_api.py --port 8002  # 豆包API (默认)
python mock_ai_api.py --port 8003 --service xiaotian  # 小天API
"""
import random
import time
import argparse
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock答案模板
DOUBAO_ANSWERS = [
    "根据您的问题，我来为您详细解答。这个问题涉及到多个方面，让我从基础原理开始分析。首先需要了解相关的背景知识，然后我们可以针对具体情况提供解决方案。建议您可以从以下几个步骤开始...",
    
    "这是一个很好的问题。基于我的理解和分析，我认为有几个关键点需要注意。第一，我们需要明确问题的核心；第二，要考虑各种可能的解决途径；第三，选择最适合的方法来实施。具体来说...",
    
    "感谢您的提问。对于这个问题，我建议采用系统性的方法来处理。首先，我们需要收集相关信息；其次，分析问题的根本原因；最后，制定具体的行动计划。在实际操作中，您可以参考以下建议...",
    
    "这个问题确实值得深入探讨。从理论角度来看，我们需要考虑多个维度的因素。从实践角度来说，有几种经过验证的方法可以帮助解决这个问题。我建议您可以尝试以下几个方案...",
    
    "根据当前的情况和您提供的信息，我认为最佳的解决方案是采用渐进式的方法。这样既能保证效果，又能控制风险。具体的实施步骤包括：前期准备、中期执行、后期优化等三个阶段...",
]

XIAOTIAN_ANSWERS = [
    "针对您的问题，小天为您提供专业解答！这个问题的关键在于理解其本质，我们可以从多个角度来分析。通过深入研究相关资料和案例，我发现最有效的方法是...",
    
    "您好！小天很高兴为您解答这个问题。基于我的知识库和经验分析，我认为这个问题可以通过以下方式来解决。首先要建立正确的思维框架，然后制定合理的执行策略...",
    
    "这是个很有意思的问题呢！小天建议您从基础概念开始理解，然后逐步深入到具体的应用层面。在我看来，解决这类问题的关键是要掌握核心原理，同时结合实际情况灵活运用...",
    
    "小天为您分析：这个问题涉及到理论与实践的结合。我推荐您采用循序渐进的学习方法，先掌握基础知识，再通过实际练习来加深理解。具体的学习路径可以这样安排...",
    
    "根据小天的分析，这个问题的解决需要综合考虑多个因素。我建议您可以从现状分析开始，然后制定目标，最后选择最合适的实现路径。在这个过程中，以下几点特别重要...",
]

# 服务配置
SERVICE_CONFIG = {
    'doubao': {
        'name': '豆包AI',
        'model': 'doubao-pro-128k',
        'answers': DOUBAO_ANSWERS,
        'style': 'professional',
        'max_tokens': 1000,
        'temperature': 0.7
    },
    'xiaotian': {
        'name': '小天AI', 
        'model': 'xiaotian-v2.0',
        'answers': XIAOTIAN_ANSWERS,
        'style': 'friendly',
        'max_length': 500,
        'temperature': 0.8
    }
}

# 全局配置
current_service = 'doubao'

def generate_answer(question, service_type='doubao', context=None):
    """
    生成AI答案
    
    Args:
        question: 问题文本
        service_type: 服务类型 (doubao/xiaotian)
        context: 上下文信息
    
    Returns:
        dict: 答案生成结果
    """
    config = SERVICE_CONFIG[service_type]
    
    # 基于问题内容智能选择答案模板
    question_lower = question.lower()
    answer_templates = config['answers']
    
    # 简单的关键词匹配逻辑
    if any(keyword in question_lower for keyword in ['如何', '怎么', '怎样']):
        # 偏向选择指导性的答案
        answer = random.choice(answer_templates[:3])
    elif any(keyword in question_lower for keyword in ['什么', '是什么', '定义']):
        # 偏向选择解释性的答案
        answer = random.choice(answer_templates[1:4])
    else:
        # 随机选择
        answer = random.choice(answer_templates)
    
    # 根据问题长度调整答案长度
    if len(question) < 20:
        answer = answer[:200] + "..."
    elif len(question) > 100:
        answer = answer + "\n\n如果您需要更详细的信息，请随时提问。"
    
    # 如果有上下文，在答案中体现
    if context and '分类:' in context:
        classification = context.split('分类:')[1].strip()
        answer = f"针对{classification}类型的问题，{answer}"
    
    return {
        'answer': answer,
        'confidence': round(random.uniform(0.8, 0.98), 2),
        'model': config['model'],
        'style': config['style'],
        'tokens_used': len(answer.split()) * 2 if service_type == 'doubao' else None,
        'length': len(answer) if service_type == 'xiaotian' else None,
        'processing_time': round(random.uniform(500, 2000), 2),
        'service': config['name']
    }

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': SERVICE_CONFIG[current_service]['name'],
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'model': SERVICE_CONFIG[current_service]['model']
    })

@app.route('/generate', methods=['POST'])  # 豆包API接口
def doubao_generate():
    """豆包AI答案生成接口"""
    if current_service != 'doubao':
        return jsonify({'error': 'Wrong service endpoint'}), 400
    
    try:
        # 模拟API延迟
        time.sleep(random.uniform(0.3, 1.0))
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        question = data.get('question')
        if not question:
            return jsonify({'error': 'Missing required field: question'}), 400
        
        context = data.get('context')
        max_tokens = data.get('max_tokens', 1000)
        temperature = data.get('temperature', 0.7)
        model = data.get('model', 'doubao-default')
        
        # 验证认证
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return jsonify({'error': 'Missing authentication'}), 401
        
        # 模拟偶尔的错误（3%概率）
        if random.random() < 0.03:
            return jsonify({'error': 'Service temporarily unavailable'}), 503
        
        # 生成答案
        result = generate_answer(question, 'doubao', context)
        result.update({
            'max_tokens': max_tokens,
            'temperature': temperature,
            'model': model
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Answer generation failed: {str(e)}'}), 500

@app.route('/answer', methods=['POST'])  # 小天API接口
def xiaotian_answer():
    """小天AI答案生成接口"""
    if current_service != 'xiaotian':
        return jsonify({'error': 'Wrong service endpoint'}), 400
    
    try:
        # 模拟API延迟
        time.sleep(random.uniform(0.2, 0.8))
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        question = data.get('question')
        if not question:
            return jsonify({'error': 'Missing required field: question'}), 400
        
        context = data.get('context')
        style = data.get('style', 'professional')
        max_length = data.get('max_length', 500)
        
        # 验证认证
        auth_header = request.headers.get('X-Auth-Token', '')
        if not auth_header:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        # 模拟偶尔的错误（2%概率）
        if random.random() < 0.02:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # 生成答案
        result = generate_answer(question, 'xiaotian', context)
        result.update({
            'style': style,
            'max_length': max_length
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Answer generation failed: {str(e)}'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取API统计信息"""
    config = SERVICE_CONFIG[current_service]
    return jsonify({
        'service': config['name'],
        'model': config['model'],
        'total_requests': random.randint(5000, 15000),
        'success_rate': round(random.uniform(0.96, 0.99), 3),
        'average_response_time': round(random.uniform(800, 1500), 2),
        'average_answer_length': random.randint(150, 300),
        'supported_features': {
            'context_aware': True,
            'multi_turn': True,
            'streaming': False,
            'batch_processing': False
        },
        'uptime': f"{random.randint(30, 120)} days"
    })

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Mock AI API服务器')
    parser.add_argument('--port', type=int, default=8002, help='服务端口 (默认: 8002)')
    parser.add_argument('--service', choices=['doubao', 'xiaotian'], default='doubao', 
                        help='AI服务类型 (默认: doubao)')
    
    args = parser.parse_args()
    
    global current_service
    current_service = args.service
    
    config = SERVICE_CONFIG[current_service]
    
    print(f"🤖 启动{config['name']} Mock API服务器...")
    print(f"📍 地址: http://localhost:{args.port}")
    print(f"🔗 健康检查: http://localhost:{args.port}/health")
    
    if current_service == 'doubao':
        print(f"🔗 答案生成: POST http://localhost:{args.port}/generate")
    else:
        print(f"🔗 答案生成: POST http://localhost:{args.port}/answer")
    
    print(f"📊 统计接口: http://localhost:{args.port}/stats")
    print("-" * 50)
    print("📝 POST数据格式:")
    
    if current_service == 'doubao':
        print("""   {
       "question": "用户问题文本",
       "context": "上下文信息（可选）",
       "max_tokens": 1000,
       "temperature": 0.7,
       "model": "doubao-pro-128k"
   }""")
        print("🔑 认证: Authorization: Bearer your-api-key")
    else:
        print("""   {
       "question": "用户问题文本", 
       "context": "上下文信息（可选）",
       "style": "professional",
       "max_length": 500
   }""")
        print("🔑 认证: X-Auth-Token: your-api-key")
    
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main() 