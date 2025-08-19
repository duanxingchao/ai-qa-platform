<template>
  <div class="workflow-config">
    <div class="config-header">
      <h3 class="config-title">🔄 工作流阶段配置</h3>
    </div>

    <!-- 手动模式状态提示 -->
    <div v-if="manualStatus.is_waiting" class="manual-waiting-alert">
      <el-alert
        title="等待手动处理答案生成"
        type="warning"
        show-icon
        :closable="false"
        class="manual-alert"
      >
        <template #default>
          <p>当前有 <strong>{{ manualStatus.pending_count }}</strong> 个问题需要手动生成豆包和小天答案</p>
          <p class="alert-description">这些问题已有yoyo答案和分类，需要补充竞品答案</p>
          <div class="alert-actions">
            <el-button type="primary" size="small" @click="goToAnswerGeneration">
              前往处理 →
            </el-button>
            <el-button size="small" @click="refreshManualStatus" :loading="loadingManualStatus">
              刷新状态
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <el-row :gutter="24" class="workflow-phases">
      <el-col :span="8" v-for="(phase, index) in phases" :key="phase.key">
        <div class="phase-item">
          <!-- 标题行：序号 + 名称 + 状态标签 -->
          <div class="phase-header">
            <div class="phase-title-section">
              <div class="phase-number">{{ index + 1 }}</div>
              <div class="phase-name">{{ phase.name }}</div>
            </div>
            <el-tag
              :type="getStatusType(phase.status)"
              size="small"
              class="status-tag"
            >
              {{ getStatusText(phase.status) }}
            </el-tag>
          </div>

          <!-- 描述行 -->
          <div class="phase-description">{{ phase.description }}</div>

          <!-- 控制按钮行 -->
          <div class="phase-controls">
            <el-switch
              v-model="phase.enabled"
              @change="handlePhaseToggle(phase)"
              active-text="启用"
              inactive-text="禁用"
              class="phase-switch"
            />
            <el-button
              size="small"
              @click="executePhase(phase)"
              :disabled="!phase.enabled"
              :loading="phase.executing"
            >
              手动执行
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getManualWorkflowStatus } from '@/api/scheduler'
import { useRouter } from 'vue-router'

const props = defineProps({
  phases: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['execute', 'toggle'])
const router = useRouter()

// 手动模式状态
const manualStatus = ref({
  is_waiting: false,
  pending_count: 0,
  mode: 'api',
  message: '',
  action_required: 'none'
})
const loadingManualStatus = ref(false)

const getStatusType = (status) => {
  switch (status) {
    case 'success':
      return 'success'
    case 'running':
      return 'warning'
    case 'failed':
      return 'danger'
    case 'disabled':
      return 'info'
    default:
      return ''
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'success':
      return '已完成'
    case 'running':
      return '运行中'
    case 'failed':
      return '失败'
    case 'disabled':
      return '已禁用'
    case 'pending':
      return '等待中'
    default:
      return '未知'
  }
}

const handlePhaseToggle = (phase) => {
  emit('toggle', phase)
}

const executePhase = (phase) => {
  if (!phase.enabled) {
    ElMessage.warning('请先启用该阶段')
    return
  }

  phase.executing = true
  emit('execute', phase)

  // 模拟执行完成后重置状态
  setTimeout(() => {
    phase.executing = false
  }, 2000)
}

// 加载手动模式状态
const loadManualStatus = async () => {
  try {
    loadingManualStatus.value = true
    const response = await getManualWorkflowStatus()

    if (response.success && response.data) {
      manualStatus.value = response.data
    }
  } catch (error) {
    console.error('获取手动模式状态失败:', error)
  } finally {
    loadingManualStatus.value = false
  }
}

// 刷新手动模式状态
const refreshManualStatus = () => {
  loadManualStatus()
  ElMessage.success('状态已刷新')
}

// 跳转到答案生成管理页面
const goToAnswerGeneration = () => {
  // 滚动到答案生成管理部分
  const answerGenerationSection = document.querySelector('.config-section:nth-child(4)')
  if (answerGenerationSection) {
    answerGenerationSection.scrollIntoView({ behavior: 'smooth' })
    ElMessage.info('已跳转到答案生成管理部分')
  }
}

// 组件挂载时加载状态
onMounted(() => {
  loadManualStatus()
})
</script>

<style scoped>
.workflow-config {
  padding: 24px;
  border-bottom: 1px solid #e4e7ed;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.config-title {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

/* 手动模式状态提示样式 */
.manual-waiting-alert {
  margin-bottom: 24px;
}

.manual-alert {
  border-radius: 8px;
}

.alert-description {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.alert-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.workflow-phases {
  margin-bottom: 32px;
}

.phase-item {
  display: flex;
  flex-direction: column;
  padding: 20px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  background-color: #FAFAFA;
  transition: all 0.3s ease;
  height: 100%;
  min-height: 180px;
  margin-bottom: 20px;
}

.phase-item:hover {
  background-color: #F5F7FA;
  border-color: #C6E2FF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

/* 新的标题行布局 */
.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.phase-title-section {
  display: flex;
  align-items: center;
}

.phase-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin-right: 16px;
  flex-shrink: 0;
}

.phase-details {
  flex: 1;
}

.phase-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.phase-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

.phase-status {
  margin-bottom: 20px;
  text-align: center;
}

.status-tag {
  font-size: 13px;
  font-weight: 500;
  padding: 6px 12px;
}

.phase-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: auto;
}

.phase-switch {
  margin-right: 8px;
}

:deep(.el-switch__label) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-button) {
  font-size: 13px;
  padding: 8px 16px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .phase-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .phase-info {
    width: 100%;
  }
  
  .phase-status,
  .phase-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .phase-controls {
    justify-content: flex-end;
  }
}
</style>
