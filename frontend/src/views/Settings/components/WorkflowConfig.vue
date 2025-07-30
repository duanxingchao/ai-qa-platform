<template>
  <el-card class="workflow-config">
    <template #header>
      <div class="card-header">
        <span>🔄 工作流阶段配置</span>
      </div>
    </template>
    
    <el-row :gutter="24" class="workflow-phases">
      <el-col :span="8" v-for="(phase, index) in phases" :key="phase.key">
        <div class="phase-item">
          <div class="phase-info">
            <div class="phase-number">{{ index + 1 }}</div>
            <div class="phase-details">
              <div class="phase-name">{{ phase.name }}</div>
              <div class="phase-description">{{ phase.description }}</div>
            </div>
          </div>

          <div class="phase-status">
            <el-tag
              :type="getStatusType(phase.status)"
              size="small"
              class="status-tag"
            >
              {{ getStatusText(phase.status) }}
            </el-tag>
          </div>

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
  </el-card>
</template>

<script setup>
import { ElMessage } from 'element-plus'

const props = defineProps({
  phases: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['execute', 'toggle'])

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
</script>

<style scoped>
.workflow-config {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.workflow-phases {
  margin-bottom: 32px;
}

.phase-item {
  display: flex;
  flex-direction: column;
  padding: 24px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  background-color: #FAFAFA;
  transition: all 0.3s ease;
  height: 100%;
  min-height: 220px;
  margin-bottom: 20px;
}

.phase-item:hover {
  background-color: #F5F7FA;
  border-color: #C6E2FF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.phase-info {
  display: flex;
  align-items: flex-start;
  flex: 1;
  margin-bottom: 20px;
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
