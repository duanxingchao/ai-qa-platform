"""
答案生成管理API
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from app.services.answer_generation_service import AnswerGenerationService
from app.utils.response import api_response, error_response
import tempfile
import os

# 创建蓝图
answer_generation_bp = Blueprint('answer_generation', __name__, url_prefix='/api/answer-generation')


@answer_generation_bp.route('/export/questions-count', methods=['GET'])
def get_export_questions_count():
    """获取待导出问题数量"""
    try:
        service = AnswerGenerationService()
        count = service.get_export_questions_count()
        
        return api_response(
            data={'count': count},
            message=f"获取待导出问题数量成功，共{count}条"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取待导出问题数量时出错: {str(e)}")
        return error_response(f"获取待导出问题数量失败: {str(e)}")


@answer_generation_bp.route('/export/questions-for-answer-generation', methods=['POST'])
def export_questions_for_answer_generation():
    """导出问题Excel文件"""
    try:
        data = request.get_json() or {}
        
        # 获取可选的筛选条件
        time_range = data.get('time_range')  # 时间范围
        batch_size = data.get('batch_size')  # 批次大小
        
        service = AnswerGenerationService()
        
        # 导出Excel文件
        file_path, filename = service.export_questions_to_excel(
            time_range=time_range,
            batch_size=batch_size
        )
        
        if not file_path or not os.path.exists(file_path):
            return error_response("导出文件生成失败")
        
        # 返回文件
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # 清理临时文件
            os.unlink(file_path)

            # 创建响应
            from flask import Response
            response = Response(
                file_content,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )

            return response

        except Exception as file_error:
            if os.path.exists(file_path):
                os.unlink(file_path)
            raise file_error
        
    except Exception as e:
        current_app.logger.error(f"导出问题Excel时出错: {str(e)}")
        return error_response(f"导出问题Excel失败: {str(e)}")


@answer_generation_bp.route('/import/validate-file', methods=['POST'])
def validate_import_file():
    """验证导入文件格式"""
    try:
        if 'file' not in request.files:
            return error_response("请选择要上传的文件")
        
        file = request.files['file']
        if file.filename == '':
            return error_response("请选择要上传的文件")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return error_response("请上传Excel文件（.xlsx或.xls格式）")
        
        service = AnswerGenerationService()
        
        # 保存临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_file.name)
        temp_file.close()
        
        try:
            # 验证文件格式
            validation_result = service.validate_import_file(temp_file.name)
            
            return api_response(
                data=validation_result,
                message="文件验证完成"
            )
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        
    except Exception as e:
        current_app.logger.error(f"验证导入文件时出错: {str(e)}")
        return error_response(f"验证导入文件失败: {str(e)}")


@answer_generation_bp.route('/import/generated-answers', methods=['POST'])
def import_generated_answers():
    """导入生成的答案"""
    try:
        if 'file' not in request.files:
            return error_response("请选择要上传的文件")
        
        file = request.files['file']
        if file.filename == '':
            return error_response("请选择要上传的文件")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return error_response("请上传Excel文件（.xlsx或.xls格式）")
        
        service = AnswerGenerationService()
        
        # 保存临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_file.name)
        temp_file.close()
        
        try:
            # 导入答案数据
            import_result = service.import_answers_from_excel(temp_file.name)
            
            return api_response(
                data=import_result,
                message=f"导入完成，成功{import_result['summary']['success_count']}条，失败{import_result['summary']['failed_count']}条"
            )
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        
    except Exception as e:
        current_app.logger.error(f"导入答案时出错: {str(e)}")
        return error_response(f"导入答案失败: {str(e)}")


@answer_generation_bp.route('/import/history', methods=['GET'])
def get_import_history():
    """获取导入历史记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        service = AnswerGenerationService()
        history = service.get_import_history(page=page, per_page=per_page)
        
        return api_response(
            data=history,
            message="获取导入历史成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取导入历史时出错: {str(e)}")
        return error_response(f"获取导入历史失败: {str(e)}")
