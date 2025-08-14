<template>
  <div class="workflow-mode-config">
    <div class="config-header">
      <h3 class="config-title">🔧 工作流模式配置</h3>
    </div>

    <el-form :model="config" label-width="120px" class="config-form">
      <!-- 答案生成模式配置 -->
      <div class="config-section">
        <h4 class="section-title">📝 答案生成模式</h4>
        
        <el-form-item label="生成模式">
          <el-radio-group v-model="config.answer_generation_mode" size="large">
            <el-radio-button label="manual">手动模式</el-radio-button>
            <el-radio-button label="api">API模式</el-radio-button>
          </el-radio-group>
          <div class="config-tip">
            <div class="tip-item">
              <strong>手动模式：</strong>适用于当前阶段，需要导出Excel进行外部处理，然后导入答案
            </div>
            <div class="tip-item">
              <strong>API模式：</strong>适用于未来，直接调用外部API自动生成答案
            </div>
          </div>
        </el-form-item>

        <!-- 当前模式状态显示 -->
        <el-form-item label="当前状态">
          <el-tag 
            :type="config.answer_generation_mode === 'manual' ? 'warning' : 'success'" 
            size="large"
          >
            {{ config.answer_generation_mode === 'manual' ? '手动处理模式' : '自动API模式' }}
          </el-tag>
          <span class="status-description">
            {{ config.answer_generation_mode === 'manual' 
              ? '需要手动导出Excel进行答案生成' 
              : '自动调用API生成答案' }}
          </span>
        </el-form-item>
      </div>

      <!-- 保存按钮 -->
      <el-form-item>
        <el-button 
          type="primary" 
          @click="saveConfig"
          :loading="saving"
          size="large"
        >
          保存配置
        </el-button>
        <el-button @click="resetConfig" size="large">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWorkflowConfig, updateWorkflowConfig } from '@/api/config'

// 响应式数据
const config = reactive({
  answer_generation_mode: 'manual'
})

const saving = ref(false)
const originalConfig = ref({})

// 加载配置
const loadConfig = async () => {
  try {
    const response = await getWorkflowConfig()
    if (response.success) {
      Object.assign(config, response.data)
      originalConfig.value = { ...response.data }
    }
  } catch (error) {
    console.error('加载工作流配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    const response = await updateWorkflowConfig(config)
    if (response.success) {
      ElMessage.success('工作流配置保存成功')
      originalConfig.value = { ...config }
    } else {
      ElMessage.error(response.message || '保存配置失败')
    }
  } catch (error) {
    console.error('保存工作流配置失败:', error)
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

// 重置配置
const resetConfig = () => {
  Object.assign(config, originalConfig.value)
  ElMessage.info('配置已重置')
}

// 组件挂载时加载配置
onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.workflow-mode-config {
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

.config-form {
  max-width: 800px;
}

.config-section {
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

.config-tip {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

.tip-item {
  margin-bottom: 8px;
}

.status-description {
  margin-left: 12px;
  font-size: 13px;
  color: #909399;
}

:deep(.el-radio-button__inner) {
  padding: 12px 20px;
  font-size: 14px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #606266;
}
</style>
