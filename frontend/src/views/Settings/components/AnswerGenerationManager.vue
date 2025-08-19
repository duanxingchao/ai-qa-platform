<template>
  <div class="answer-generation-manager">
    <div class="config-header">
      <h3 class="config-title">📝 答案生成管理</h3>
    </div>

    <!-- 导出功能区 -->
    <div class="function-section">
      <h4 class="section-title">📤 导出问题</h4>
      
      <div class="export-info">
        <el-statistic 
          title="待导出问题数量" 
          :value="exportCount" 
          suffix="条"
          :loading="loadingCount"
        />
        <el-button 
          type="primary" 
          @click="refreshCount"
          :loading="loadingCount"
          size="small"
        >
          刷新
        </el-button>
      </div>

      <div class="export-controls">
        <el-form :model="exportForm" inline>
          <el-form-item label="时间范围">
            <el-select v-model="exportForm.time_range" placeholder="选择时间范围">
              <el-option label="全部时间" value="" />
              <el-option label="近一周" value="week" />
              <el-option label="近一月" value="month" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="批次大小">
            <el-input-number 
              v-model="exportForm.batch_size" 
              :min="1" 
              :max="1000"
              placeholder="不限制"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="exportQuestions"
              :loading="exporting"
              :disabled="exportCount === 0"
            >
              导出Excel
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 操作指引 -->
    <div class="function-section">
      <h4 class="section-title">📋 操作指引</h4>
      <div class="operation-guide">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="导出Excel" description="下载包含问题和分类的文件" />
          <el-step title="填写答案" description="在Excel中填写豆包和小天答案" />
          <el-step title="验证文件" description="检查文件格式和内容" />
          <el-step title="导入答案" description="完成处理，自动进入评分阶段" />
        </el-steps>

        <div class="guide-details">
          <el-alert type="info" :closable="false" show-icon>
            <template #title>重要说明</template>
            <ul class="guide-list">
              <li><strong>yoyo答案已存在：</strong>系统中已有原始yoyo答案，无需填写</li>
              <li><strong>只需填写竞品答案：</strong>在Excel的D列填写豆包答案，E列填写小天答案</li>
              <li><strong>三个答案完整：</strong>只有yoyo+豆包+小天三个答案都完整时，问题才会进入评分阶段</li>
              <li><strong>自动流程衔接：</strong>导入完成后，系统会自动检查并触发评分阶段</li>
            </ul>
          </el-alert>
        </div>
      </div>
    </div>

    <!-- 导入功能区 -->
    <div class="function-section">
      <h4 class="section-title">📥 导入答案</h4>
      
      <div class="import-controls">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
        >
          <el-button type="primary">选择Excel文件</el-button>
          <template #tip>
            <div class="el-upload__tip">
              只能上传Excel文件(.xlsx/.xls)，且不超过10MB
            </div>
          </template>
        </el-upload>

        <div class="import-actions" v-if="selectedFile">
          <el-button @click="validateFile" :loading="validating">
            验证文件
          </el-button>
          <el-button 
            type="success" 
            @click="importAnswers"
            :loading="importing"
            :disabled="!fileValidated"
          >
            导入答案
          </el-button>
        </div>
      </div>

      <!-- 文件验证结果 -->
      <div v-if="validationResult" class="validation-result">
        <el-alert
          :type="validationResult.valid ? 'success' : 'error'"
          :title="validationResult.valid ? '文件验证通过' : '文件验证失败'"
          :description="validationResult.error || `共${validationResult.total_rows}行数据`"
          show-icon
          :closable="false"
        />
        
        <div v-if="validationResult.valid && validationResult.data_quality" class="data-quality">
          <h5>数据质量检查：</h5>
          <ul>
            <li>空business_id: {{ validationResult.data_quality.empty_business_id }}行</li>
            <li>空豆包答案: {{ validationResult.data_quality.empty_doubao_answer }}行</li>
            <li>空小天答案: {{ validationResult.data_quality.empty_xiaotian_answer }}行</li>
          </ul>
        </div>
      </div>

      <!-- 导入结果 -->
      <div v-if="importResult" class="import-result">
        <el-alert
          type="info"
          :title="`导入完成：成功${importResult.summary.success_count}条，失败${importResult.summary.failed_count}条`"
          :description="`成功率：${importResult.summary.success_rate}`"
          show-icon
          :closable="false"
        />
        
        <!-- 失败详情 -->
        <div v-if="importResult.failed_items && importResult.failed_items.length > 0" class="failed-details">
          <h5>失败详情：</h5>
          <el-table :data="importResult.failed_items" size="small" max-height="300">
            <el-table-column prop="row_number" label="行号" width="80" />
            <el-table-column prop="business_id" label="问题ID" width="120" />
            <el-table-column prop="error" label="失败原因" />
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getExportQuestionsCount, 
  exportQuestionsForAnswerGeneration,
  validateImportFile,
  importGeneratedAnswers
} from '@/api/config'

// 响应式数据
const exportCount = ref(0)
const loadingCount = ref(false)
const exporting = ref(false)
const validating = ref(false)
const importing = ref(false)
const fileValidated = ref(false)

const exportForm = reactive({
  time_range: '',
  batch_size: null
})

const selectedFile = ref(null)
const validationResult = ref(null)
const importResult = ref(null)
const uploadRef = ref()

// 操作步骤状态
const currentStep = ref(0)

// 加载待导出问题数量
const loadExportCount = async () => {
  loadingCount.value = true
  try {
    const response = await getExportQuestionsCount()
    if (response.success) {
      exportCount.value = response.data.count
    }
  } catch (error) {
    console.error('获取待导出问题数量失败:', error)
    ElMessage.error('获取待导出问题数量失败')
  } finally {
    loadingCount.value = false
  }
}

// 刷新数量
const refreshCount = () => {
  loadExportCount()
}

// 导出问题
const exportQuestions = async () => {
  if (exportCount.value === 0) {
    ElMessage.warning('没有待导出的问题')
    return
  }

  exporting.value = true
  try {
    const response = await exportQuestionsForAnswerGeneration(exportForm)

    // 从axios响应中获取blob数据
    const blob = response.data

    // 生成文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
    const filename = `questions_for_answer_generation_${timestamp}.xlsx`

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('Excel文件导出成功，请在Excel中填写豆包和小天答案')

    // 更新步骤状态
    currentStep.value = 1

    // 导出后刷新数量
    setTimeout(() => {
      loadExportCount()
    }, 1000)
    
  } catch (error) {
    console.error('导出问题失败:', error)
    ElMessage.error('导出问题失败')
  } finally {
    exporting.value = false
  }
}

// 文件选择处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  validationResult.value = null
  importResult.value = null
  fileValidated.value = false
}

// 文件移除处理
const handleFileRemove = () => {
  selectedFile.value = null
  validationResult.value = null
  importResult.value = null
  fileValidated.value = false
}

// 验证文件
const validateFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  validating.value = true
  try {
    const response = await validateImportFile(selectedFile.value)
    // 响应拦截器已经返回了data部分，所以直接使用response
    validationResult.value = response.data || response
    fileValidated.value = (response.data || response).valid

    if ((response.data || response).valid) {
      ElMessage.success('文件验证通过，可以进行导入')
      currentStep.value = 2
    } else {
      ElMessage.error('文件验证失败')
      currentStep.value = 1
    }
  } catch (error) {
    console.error('验证文件失败:', error)
    ElMessage.error('验证文件失败')
  } finally {
    validating.value = false
  }
}

// 导入答案
const importAnswers = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  if (!fileValidated.value) {
    ElMessage.warning('请先验证文件')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要导入答案数据吗？此操作将创建新的答案记录。',
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  importing.value = true
  try {
    const response = await importGeneratedAnswers(selectedFile.value)
    // 响应拦截器已经返回了data部分，所以直接使用response
    importResult.value = response.data || response

    // 检查是否触发了评分阶段
    const message = response.message || '答案导入完成'
    const scoringTriggered = (response.data || response)?.scoring_triggered || false

    ElMessage.success(message)

    // 更新步骤状态
    currentStep.value = 3

    if (scoringTriggered) {
      ElMessage.info('系统已自动触发评分阶段', { duration: 3000 })
    }

    // 导入后刷新数量
    setTimeout(() => {
      loadExportCount()
    }, 1000)

  } catch (error) {
    console.error('导入答案失败:', error)
    ElMessage.error('导入答案失败')
  } finally {
    importing.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadExportCount()
})
</script>

<style scoped>
.answer-generation-manager {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.config-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.config-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.function-section {
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

/* 操作指引样式 */
.operation-guide {
  .guide-details {
    margin-top: 24px;
  }

  .guide-list {
    margin: 0;
    padding-left: 20px;

    li {
      margin-bottom: 8px;
      line-height: 1.6;

      strong {
        color: #409eff;
      }
    }
  }
}

.export-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.export-controls {
  margin-top: 16px;
}

.import-controls {
  margin-bottom: 16px;
}

.import-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.validation-result,
.import-result {
  margin-top: 16px;
  padding: 16px;
  background: white;
  border-radius: 6px;
}

.data-quality h5,
.failed-details h5 {
  margin: 12px 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.data-quality ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #909399;
}

.failed-details {
  margin-top: 12px;
}
</style>
