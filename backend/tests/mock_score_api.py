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

# 评分维度定义
SCORING_DIMENSIONS = {
    'accuracy': '准确性',
    'completeness': '完整性', 
    'clarity': '清晰度',
    'relevance': '相关性',
    'helpfulness': '有用性'
}

# 模型名称映射
MODEL_NAMES = {
    'our_ai': '原始模型',
    'doubao': '豆包模型',
    'xiaotian': '小天模型'
}

def analyze_answer_quality(question, answer, classification, model_type):
    """分析答案质量并生成评分"""
    if not answer or not answer.strip():
        # 空答案给低分
        scores = {dim: random.randint(1, 2) for dim in SCORING_DIMENSIONS.keys()}
        reason = "答案为空或过短，无法提供有效信息"
        return scores, reason
    
    # 基础评分（根据模型类型设置不同基准）
    if model_type == 'our_ai':
        # 原始模型稍微低一些
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
    
    # 准确性评分
    accuracy_score = random.randint(*base_range)
    if any(word in answer_lower for word in ['准确', '正确', '事实', '数据']):
        accuracy_score = min(5, accuracy_score + 1)
    if any(word in answer_lower for word in ['错误', '不对', '不确定']):
        accuracy_score = max(1, accuracy_score - 1)
    scores['accuracy'] = accuracy_score
    
    # 完整性评分
    completeness_score = random.randint(*base_range)
    if len(answer) > 200:
        completeness_score = min(5, completeness_score + 1)
    if any(word in answer for word in ['首先', '其次', '最后', '总结']):
        completeness_score = min(5, completeness_score + 1)
    scores['completeness'] = completeness_score
    
    # 清晰度评分
    clarity_score = random.randint(*base_range)
    if any(word in answer for word in ['清楚', '明确', '简单', '易懂']):
        clarity_score = min(5, clarity_score + 1)
    scores['clarity'] = clarity_score
    
    # 相关性评分 
    relevance_score = random.randint(*base_range)
    if question and classification:
        # 检查答案是否与问题和分类相关
        if any(word in answer_lower for word in question_lower.split()):
            relevance_score = min(5, relevance_score + 1)
    scores['relevance'] = relevance_score
    
    # 有用性评分
    helpfulness_score = random.randint(*base_range)
    if any(word in answer_lower for word in ['建议', '方法', '解决', '帮助', '指导']):
        helpfulness_score = min(5, helpfulness_score + 1)
    scores['helpfulness'] = helpfulness_score
    
    # 生成评分理由
    avg_score = sum(scores.values()) / len(scores)
    if avg_score >= 4.0:
        reason_prefix = "答案质量优秀："
    elif avg_score >= 3.0:
        reason_prefix = "答案质量良好："
    else:
        reason_prefix = "答案质量一般："
    
    # 具体理由分析
    strong_points = []
    weak_points = []
    
    for dim, score in scores.items():
        if score >= 4:
            strong_points.append(SCORING_DIMENSIONS[dim])
        elif score <= 2:
            weak_points.append(SCORING_DIMENSIONS[dim])
    
    reason_parts = [reason_prefix]
    if strong_points:
        reason_parts.append(f"{','.join(strong_points)}表现突出")
    if weak_points:
        reason_parts.append(f"{','.join(weak_points)}有待改进")
    
    reason = "，".join(reason_parts) + "。"
    
    return scores, reason

def generate_multi_model_scores(question, our_answer, doubao_answer, xiaotian_answer, classification):
    """生成多模型评分结果"""
    results = []
    
    # 评分数据结构：[模型名, 答案内容, 模型类型]
    models_data = [
        (MODEL_NAMES['our_ai'], our_answer, 'our_ai'),
        (MODEL_NAMES['doubao'], doubao_answer, 'doubao'), 
        (MODEL_NAMES['xiaotian'], xiaotian_answer, 'xiaotian')
    ]
    
    for model_name, answer, model_type in models_data:
        # 生成该模型的评分
        scores, reason = analyze_answer_quality(question, answer, classification, model_type)
        
        # 构造返回格式
        model_result = {
            "模型名称": model_name,
            "准确性": scores['accuracy'],
            "完整性": scores['completeness'],
            "清晰度": scores['clarity'],
            "相关性": scores['relevance'],
            "有用性": scores['helpfulness'],
            "理由": reason
        }
        
        results.append(model_result)
    
    return results

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'mock-score-api',
        'version': '1.0.0',
        'timestamp': time.time(),
        'supported_models': list(MODEL_NAMES.values()),
        'scoring_dimensions': list(SCORING_DIMENSIONS.values())
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
        'dimensions_count': len(SCORING_DIMENSIONS),
        'score_distribution': {
            '5分': random.randint(15, 30),
            '4分': random.randint(25, 40), 
            '3分': random.randint(20, 35),
            '2分': random.randint(10, 20),
            '1分': random.randint(5, 15)
        },
        'models': list(MODEL_NAMES.values()),
        'dimensions': list(SCORING_DIMENSIONS.values()),
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
    for key, name in SCORING_DIMENSIONS.items():
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