<template>
  <el-card class="scheduler-status">
    <template #header>
      <div class="card-header">
        <span>📊 调度器状态概览</span>
      </div>
    </template>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="status-item">
          <div class="status-label">调度器状态</div>
          <div class="status-value">
            <el-tag :type="statusType" size="large">
              <el-icon class="status-icon">
                <component :is="statusIcon" />
              </el-icon>
              {{ statusText }}
            </el-tag>
          </div>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="status-item">
          <div class="status-label">最后执行时间</div>
          <div class="status-value">
            <span class="time-text">{{ lastExecutionTime }}</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheck, CircleClose, Warning } from '@element-plus/icons-vue'

const props = defineProps({
  status: {
    type: Object,
    required: true,
    default: () => ({
      running: false,
      lastExecution: null
    })
  }
})

const statusType = computed(() => {
  if (props.status.running) return 'success'
  return 'danger'
})

const statusText = computed(() => {
  if (props.status.running) return '运行中'
  return '已停止'
})

const statusIcon = computed(() => {
  if (props.status.running) return CircleCheck
  return CircleClose
})

const lastExecutionTime = computed(() => {
  if (!props.status.lastExecution) return '从未执行'
  
  try {
    const time = new Date(props.status.lastExecution)
    const now = new Date()
    const diff = Math.floor((now - time) / 1000 / 60) // 分钟差
    
    if (diff < 1) return '刚刚'
    if (diff < 60) return `${diff}分钟前`
    if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
    return time.toLocaleDateString() + ' ' + time.toLocaleTimeString()
  } catch (error) {
    return '时间格式错误'
  }
})
</script>

<style scoped>
.scheduler-status {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.status-item {
  text-align: center;
  padding: 16px 0;
}

.status-label {
  font-size: 15px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
}

.status-icon {
  margin-right: 8px;
}

.time-text {
  color: #303133;
  font-size: 16px;
}

.el-tag {
  padding: 10px 20px;
  font-size: 15px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .status-item {
    padding: 12px 0;
  }

  .status-value {
    font-size: 16px;
  }

  .status-label {
    font-size: 14px;
  }
}
</style>
