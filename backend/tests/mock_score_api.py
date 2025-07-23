#!/usr/bin/env python3
"""
Mock评分API服务器
按照用户指定的格式模拟评分API，支持多模型评分

启动方式:
python mock_score_api.py --port 8004
"""
import random
import time
import json
import argparse
import socket
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# 根据分类领域定义不同的评分维度（按照用户需求）
CLASSIFICATION_DIMENSIONS = {
    '技术问题': ['信息准确性', '逻辑性', '流畅性', '创新性', '实用性'],
    '经济问题': ['数据准确性', '分析深度', '表达清晰度', '前瞻性', '实用性'],
    '教育问题': ['知识准确性', '逻辑严密性', '表达流畅性', '启发性', '适用性'],
    '工程问题': ['技术准确性', '逻辑严谨性', '表达清晰度', '创新性', '可操作性'],
    '医疗问题': ['医学准确性', '逻辑推理', '表达清晰度', '安全性', '实用性'],
    '法律问题': ['法理准确性', '逻辑严密性', '表达精确性', '适用性', '权威性'],
    '科学问题': ['科学准确性', '逻辑性', '表达清晰度', '创新性', '验证性'],
    '艺术问题': ['创意性', '表达美感', '文化内涵', '独特性', '感染力'],
    '历史问题': ['史实准确性', '逻辑关联性', '表达清晰度', '深度分析', '启发性'],
    '地理问题': ['地理准确性', '逻辑关联性', '表达清晰度', '实用性', '时效性'],
    '心理问题': ['心理准确性', '逻辑性', '表达温和性', '实用性', '安全性'],
    '社会问题': ['社会洞察力', '逻辑分析', '表达平衡性', '建设性', '实用性'],
    '环境问题': ['环境准确性', '逻辑分析', '表达清晰度', '前瞻性', '可行性'],
    '体育问题': ['专业准确性', '逻辑性', '表达清晰度', '实用性', '时效性'],
    '娱乐问题': ['信息准确性', '趣味性', '表达生动性', '时效性', '吸引力'],
    '其他问题': ['信息准确性', '逻辑性', '流畅性', '创新性', '有用性']  # 默认维度
}

# 模型名称映射（按照用户需求）
MODEL_NAMES = {
    'our_ai': 'yoyo',      # 用户的AI问答软件
    'doubao': '豆包',       # 豆包模型
    'xiaotian': '小天'      # 小天模型
}

def get_dimensions_for_classification(classification):
    """根据分类获取对应的评分维度"""
    # 清理分类名称，移除可能的额外字符
    clean_classification = classification.strip() if classification else ''
    
    # 查找匹配的维度，如果没找到使用默认维度
    if clean_classification in CLASSIFICATION_DIMENSIONS:
        return CLASSIFICATION_DIMENSIONS[clean_classification]
    
    # 模糊匹配
    for key in CLASSIFICATION_DIMENSIONS:
        if key in clean_classification or clean_classification in key:
            return CLASSIFICATION_DIMENSIONS[key]
    
    # 默认维度
    return CLASSIFICATION_DIMENSIONS['其他问题']

def analyze_answer_quality(question, answer, classification, model_type):
    """分析答案质量并生成评分"""
    # 获取当前分类的评分维度
    dimensions = get_dimensions_for_classification(classification)
    
    if not answer or not answer.strip():
        # 空答案给低分
        scores = {dim: random.randint(1, 2) for dim in dimensions}
        reason = "答案为空或过短，无法提供有效信息"
        return scores, reason
    
    # 基础评分（根据模型类型设置不同基准）
    if model_type == 'our_ai':
        # yoyo模型稍微低一些
        base_range = (2, 4)
    elif model_type == 'doubao':
        # 豆包模型稍微高一些
        base_range = (3, 5)
    else:  # xiaotian
        # 小天模型中等水平
        base_range = (2, 4)
    
    scores = {}
    
    # 分析答案内容
    answer_lower = answer.lower()
    question_lower = question.lower() if question else ""
    
    # 为每个维度生成评分
    for i, dimension in enumerate(dimensions):
        base_score = random.randint(*base_range)
        
        # 根据维度类型调整评分
        if '准确性' in dimension:
            if any(word in answer_lower for word in ['准确', '正确', '事实', '数据']):
                base_score = min(5, base_score + 1)
            if any(word in answer_lower for word in ['错误', '不对', '不确定']):
                base_score = max(1, base_score - 1)
        elif '逻辑' in dimension:
            if any(word in answer_lower for word in ['因为', '所以', '因此', '导致']):
                base_score = min(5, base_score + 1)
        elif '流畅' in dimension or '清晰' in dimension:
            if len(answer) > 50 and '。' in answer:
                base_score = min(5, base_score + 1)
        elif '创新' in dimension:
            if any(word in answer_lower for word in ['新', '创新', '独特', 'novel']):
                base_score = min(5, base_score + 1)
        
        scores[dimension] = base_score
    
    # 生成评分理由
    reasons = []
    avg_score = sum(scores.values()) / len(scores)
    
    if avg_score >= 4:
        reasons.append(f"{MODEL_NAMES[model_type]}回答质量优秀")
    elif avg_score >= 3:
        reasons.append(f"{MODEL_NAMES[model_type]}回答质量良好")
    else:
        reasons.append(f"{MODEL_NAMES[model_type]}回答质量有待提升")
    
    if len(answer) > 100:
        reasons.append("回答内容详细")
    if '例如' in answer or '比如' in answer:
        reasons.append("提供了具体例子")
    
    reason = "，".join(reasons) + f"。各维度评分：{', '.join([f'{k}:{v}分' for k, v in scores.items()])}"
    
    return scores, reason

def generate_multi_model_scores(question, our_answer, doubao_answer, xiaotian_answer, classification):
    """生成多模型评分结果 - 按照用户的确切格式"""
    
    # 获取当前分类的评分维度
    dimensions = get_dimensions_for_classification(classification)
    
    # 确保有5个维度（补充或截取）
    if len(dimensions) < 5:
        # 如果不足5个，用默认维度补充
        default_dims = CLASSIFICATION_DIMENSIONS['其他问题']
        dimensions.extend([d for d in default_dims if d not in dimensions])
    dimensions = dimensions[:5]  # 只取前5个
    
    scores_list = []
    
    # 为三个模型生成评分
    models_data = [
        ('our_ai', 'yoyo', our_answer),
        ('doubao', '豆包', doubao_answer), 
        ('xiaotian', '小天', xiaotian_answer)
    ]
    
    for model_key, model_name, answer in models_data:
        if not answer or answer.strip() == '':
            # 空答案处理
            scores, reason = analyze_answer_quality(question, '', classification, model_key)
        else:
            scores, reason = analyze_answer_quality(question, answer, classification, model_key)
        
        # 按照用户的确切JSON格式构建结果
        model_result = {
            "模型名称": model_name
        }
        
        # 动态添加当前分类的5个维度评分
        for i, dimension in enumerate(dimensions):
            if dimension in scores:
                model_result[dimension] = str(scores[dimension])  # 转换为字符串
            else:
                model_result[dimension] = str(random.randint(2, 4))  # 默认评分转换为字符串
        
        model_result["理由"] = reason
        scores_list.append(model_result)
    
    return scores_list

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'mock-score-api',
        'version': '1.0.0',
        'timestamp': time.time(),
        'supported_models': list(MODEL_NAMES.values()),
        'scoring_dimensions': list(CLASSIFICATION_DIMENSIONS.values()) # Changed to CLASSIFICATION_DIMENSIONS
    })

@app.route('/score', methods=['POST'])
def score_answers():
    """多模型答案评分接口 - 按照用户指定的格式"""
    try:
        # 模拟API延迟
        time.sleep(random.uniform(0.8, 2.0))
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid JSON data'
            }), 400
        
        # 检查inputs字段
        inputs = data.get('inputs')
        if not inputs:
            return jsonify({
                'error': 'Missing required field: inputs'
            }), 400
        
        # 检查必需的输入字段
        question = inputs.get('question')
        our_answer = inputs.get('our_answer', '')
        doubao_answer = inputs.get('doubao_answer', '')
        xiaotian_answer = inputs.get('xiaotian_answer', '')
        classification = inputs.get('classification', '')
        
        if not question:
            return jsonify({
                'error': 'Missing required field: inputs.question'
            }), 400
        
        # 验证API密钥
        api_key = request.headers.get('X-API-Key', '')
        if not api_key:
            return jsonify({
                'error': 'Missing API key'
            }), 401
        
        # 模拟偶尔的服务错误（5%概率）
        if random.random() < 0.05:
            return jsonify({
                'error': 'Internal server error'
            }), 500
        
        # 模拟偶尔的速率限制（2%概率）
        if random.random() < 0.02:
            return jsonify({
                'error': 'Rate limit exceeded'
            }), 429
        
        # 生成评分结果
        start_time = time.time()
        score_results = generate_multi_model_scores(
            question, our_answer, doubao_answer, xiaotian_answer, classification
        )
        
        # 按照用户指定的格式返回
        response_data = {
            "data": {
                "outputs": {
                    "text": json.dumps(score_results, ensure_ascii=False, indent=2)
                }
            },
            "processing_time": round((time.time() - start_time) * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Scoring failed: {str(e)}'
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取API统计信息"""
    return jsonify({
        'total_requests': random.randint(500, 2000),
        'success_rate': round(random.uniform(0.95, 0.99), 3),
        'average_response_time': round(random.uniform(800, 1500), 2),
        'models_supported': len(MODEL_NAMES),
        'dimensions_count': len(CLASSIFICATION_DIMENSIONS), # Changed to CLASSIFICATION_DIMENSIONS
        'score_distribution': {
            '5分': random.randint(15, 30),
            '4分': random.randint(25, 40), 
            '3分': random.randint(20, 35),
            '2分': random.randint(10, 20),
            '1分': random.randint(5, 15)
        },
        'models': list(MODEL_NAMES.values()),
        'dimensions': list(CLASSIFICATION_DIMENSIONS.values()), # Changed to CLASSIFICATION_DIMENSIONS
        'uptime': f"{random.randint(20, 100)} days"
    })

@app.route('/test', methods=['POST'])
def test_scoring():
    """测试接口，返回格式化的响应"""
    data = request.get_json() or {}
    
    test_result = generate_multi_model_scores(
        question="这是一个测试问题",
        our_answer="这是原始模型的回答",
        doubao_answer="这是豆包模型的回答", 
        xiaotian_answer="这是小天模型的回答",
        classification="技术问题"
    )
    
    return jsonify({
        "data": {
            "outputs": {
                "text": json.dumps(test_result, ensure_ascii=False, indent=2)
            }
        },
        "message": "测试成功"
    })

def find_available_port(start_port=8004, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"无法找到可用端口（尝试范围: {start_port}-{start_port + max_attempts - 1}）")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Mock评分API服务器')
    parser.add_argument('--port', type=int, default=8004, help='指定端口号（默认8004）')
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
            print(f"   1. 使用其他端口: python {__file__} --port 8005")
            print(f"   2. 自动查找端口: python {__file__} --auto-port")
            print(f"   3. 停止占用程序: sudo lsof -i :{port}")
            exit(1)
    
    print("🤖 启动Mock评分API服务器...")
    print(f"📍 地址: http://localhost:{port}")
    print(f"🔗 健康检查: http://localhost:{port}/health")
    print(f"🔗 评分接口: POST http://localhost:{port}/score")
    print(f"📊 统计接口: http://localhost:{port}/stats")
    print(f"🧪 测试接口: POST http://localhost:{port}/test")
    print("-" * 60)
    print("📝 POST数据格式（按照您的需求）:")
    print("""   {
       "inputs": {
           "question": "用户问题文本",
           "our_answer": "原始模型答案",
           "doubao_answer": "豆包模型答案", 
           "xiaotian_answer": "小天模型答案",
           "classification": "问题分类"
       }
   }""")
    print("🔑 认证: X-API-Key: your-api-key")
    print("-" * 60)
    print("📋 支持的模型:")
    for key, name in MODEL_NAMES.items():
        print(f"   {key}: {name}")
    print("📋 评分维度:")
    for key, name in CLASSIFICATION_DIMENSIONS.items(): # Changed to CLASSIFICATION_DIMENSIONS
        print(f"   {key}: {name}")
    print("-" * 60)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print(f"\n🛑 Mock评分API服务器已停止")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {port} 已被占用")
            if args.auto_port:
                try:
                    new_port = find_available_port(port + 1)
                    print(f"🔄 自动切换到端口 {new_port}")
                    app.run(host='0.0.0.0', port=new_port, debug=False, use_reloader=False)
                except RuntimeError as re:
                    print(f"❌ {re}")
                    exit(1)
            else:
                print("💡 解决方案:")
                print(f"   1. 使用其他端口: python {__file__} --port {port + 1}")
                print(f"   2. 自动查找端口: python {__file__} --auto-port")
                print(f"   3. 停止占用程序: pkill -f mock_score_api")
                exit(1)
        else:
            raise

if __name__ == '__main__':
    main() 