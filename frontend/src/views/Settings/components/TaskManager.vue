<template>
  <div class="task-manager">
    <div class="config-header">
      <h3 class="config-title">📋 定时任务管理</h3>
    </div>

    <el-table
      :data="tasks" 
      style="width: 100%"
      empty-text="暂无定时任务"
    >
      <el-table-column prop="name" label="任务名称" min-width="200">
        <template #default="{ row }">
          <div class="task-name">
            <el-icon class="task-icon">
              <Timer />
            </el-icon>
            {{ row.name }}
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag 
            :type="getTaskStatusType(row.enabled, row.status)" 
            size="small"
          >
            {{ getTaskStatusText(row.enabled, row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="nextRunTime" label="下次执行" width="160">
        <template #default="{ row }">
          <span class="next-run-time">
            {{ formatNextRunTime(row.nextRunTime) }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <div class="task-actions">
            <el-button
              v-if="row.enabled"
              size="small"
              type="warning"
              @click="handleTaskAction('pause', row)"
            >
              暂停
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="handleTaskAction('resume', row)"
            >
              启用
            </el-button>
            
            <el-button
              size="small"
              type="primary"
              @click="handleTaskAction('trigger', row)"
              :disabled="!row.enabled"
            >
              立即执行
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    
    <div v-if="tasks.length === 0" class="empty-state">
      <el-icon size="48" color="#C0C4CC">
        <DocumentCopy />
      </el-icon>
      <p>暂无定时任务</p>
    </div>
  </div>
</template>

<script setup>
import { Timer, DocumentCopy } from '@element-plus/icons-vue'

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['action'])

const getTaskStatusType = (enabled, status) => {
  if (!enabled) return 'info'
  if (status === 'running') return 'success'
  if (status === 'paused') return 'warning'
  return 'info'
}

const getTaskStatusText = (enabled, status) => {
  if (!enabled) return '已禁用'
  if (status === 'running') return '运行中'
  if (status === 'paused') return '已暂停'
  return '等待中'
}

const formatNextRunTime = (nextRunTime) => {
  if (!nextRunTime) return '-'
  
  try {
    const time = new Date(nextRunTime)
    const now = new Date()
    const diff = Math.floor((time - now) / 1000 / 60) // 分钟差
    
    if (diff < 0) return '已过期'
    if (diff < 1) return '即将执行'
    if (diff < 60) return `${diff}分钟后`
    if (diff < 1440) return `${Math.floor(diff / 60)}小时后`
    
    return time.toLocaleDateString() + ' ' + time.toLocaleTimeString()
  } catch (error) {
    return '时间格式错误'
  }
}

const handleTaskAction = (action, task) => {
  emit('action', action, task)
}
</script>

<style scoped>
.task-manager {
  padding: 24px;
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

.task-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
}

.task-icon {
  color: #409EFF;
  font-size: 18px;
}

.next-run-time {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.task-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.empty-state p {
  margin: 16px 0 0 0;
  font-size: 15px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-table td) {
  font-size: 14px;
}

:deep(.el-tag) {
  font-size: 13px;
  font-weight: 500;
  padding: 6px 12px;
}

:deep(.el-button) {
  font-size: 13px;
  padding: 8px 16px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .task-actions {
    flex-direction: column;
    gap: 6px;
  }

  .task-actions .el-button {
    width: 100%;
  }

  .task-name {
    font-size: 14px;
  }

  .next-run-time {
    font-size: 13px;
  }
}
</style>
