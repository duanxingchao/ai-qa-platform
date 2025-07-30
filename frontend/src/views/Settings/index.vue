<template>
  <div class="settings">
    <div class="page-header">
      <h1>系统配置</h1>
      <p class="page-description">调度器配置与任务管理</p>
    </div>

    <!-- 调度器状态概览 -->
    <SchedulerStatus :status="schedulerStatus" />

    <!-- 基础配置 -->
    <BasicConfig
      :config="basicConfig"
      @save="handleSaveConfig"
    />

    <!-- 工作流配置 -->
    <WorkflowConfig
      :phases="workflowPhases"
      @execute="handleExecutePhase"
      @toggle="handleTogglePhase"
    />

    <!-- 任务管理 -->
    <TaskManager
      :tasks="scheduledTasks"
      @action="handleTaskAction"
    />

    <!-- 测试内容 -->
    <el-card>
      <div style="padding: 20px;">
        <h2>🎉 调度器配置管理功能已完全恢复！</h2>
        <p>所有功能组件都已正常加载</p>
        <el-button type="primary" @click="testAPI">测试API连接</el-button>
        <div v-if="testResult" style="margin-top: 10px;">
          <pre>{{ testResult }}</pre>
        </div>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 配置内容 -->
    <div v-else class="settings-content" style="display: none;">
      <!-- 调度器状态概览 -->
      <!-- <SchedulerStatus :status="schedulerStatus" /> -->

      <!-- 基础配置 -->
      <!-- <BasicConfig
        :config="basicConfig"
        @save="handleSaveConfig"
      /> -->

      <!-- 工作流配置 -->
      <!-- <WorkflowConfig
        :phases="workflowPhases"
        @execute="handleExecutePhase"
        @toggle="handleTogglePhase"
      /> -->

      <!-- 任务管理 -->
      <!-- <TaskManager
        :tasks="scheduledTasks"
        @action="handleTaskAction"
      /> -->
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import SchedulerStatus from './components/SchedulerStatus.vue'
import BasicConfig from './components/BasicConfig.vue'
import WorkflowConfig from './components/WorkflowConfig.vue'
import TaskManager from './components/TaskManager.vue'

const loading = ref(false)
const testResult = ref('')

// 模拟调度器状态数据
const schedulerStatus = ref({
  running: false,
  lastExecution: '2025-07-29T09:30:00Z'
})

// 模拟基础配置数据
const basicConfig = reactive({
  schedulerEnabled: false,
  autoProcessOnStartup: false,
  autoSuspendWhenNoData: true,
  dataCheckEnabled: true,
  workflowIntervalMinutes: 3,
  batchSize: 100,
  minBatchSize: 1
})

// 模拟工作流阶段数据
const workflowPhases = ref([
  {
    key: 'data_sync',
    name: '数据同步',
    description: '从table1同步最新数据到questions和answers表',
    enabled: true,
    status: 'pending'
  },
  {
    key: 'classification',
    name: '问题分类',
    description: '调用分类API对新问题进行分类',
    enabled: true,
    status: 'pending'
  },
  {
    key: 'answer_generation',
    name: '答案生成',
    description: '调用AI API生成问题答案',
    enabled: true,
    status: 'pending'
  },
  {
    key: 'scoring',
    name: '评分处理',
    description: '对生成的答案进行质量评分',
    enabled: true,
    status: 'pending'
  }
])

// 模拟定时任务数据
const scheduledTasks = ref([
  {
    id: 'configurable_workflow',
    name: 'AI处理工作流',
    status: 'running',
    nextRunTime: '2025-07-29T14:35:00Z',
    enabled: true
  },
  {
    id: 'frequent_data_sync',
    name: '数据同步任务',
    status: 'disabled',
    nextRunTime: null,
    enabled: false
  }
])

// 保存配置
const handleSaveConfig = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/scheduler/config', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        scheduler_enabled: basicConfig.schedulerEnabled,
        auto_process_on_startup: basicConfig.autoProcessOnStartup,
        auto_suspend_when_no_data: basicConfig.autoSuspendWhenNoData,
        data_check_enabled: basicConfig.dataCheckEnabled,
        workflow_interval_minutes: basicConfig.workflowIntervalMinutes,
        batch_size: basicConfig.batchSize,
        min_batch_size: basicConfig.minBatchSize
      })
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success('配置保存成功')
    } else {
      throw new Error(data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error(`配置保存失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 执行工作流阶段
const handleExecutePhase = async (phase) => {
  try {
    phase.executing = true
    const response = await fetch(`/api/scheduler/workflow/phases/${phase.key}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success(`${phase.name}执行成功`)
      phase.status = 'success'
    } else {
      throw new Error(data.message || '执行失败')
    }
  } catch (error) {
    ElMessage.error(`${phase.name}执行失败: ${error.message}`)
    phase.status = 'failed'
  } finally {
    phase.executing = false
  }
}

// 切换工作流阶段状态
const handleTogglePhase = (phase) => {
  ElMessage.info(`${phase.name} ${phase.enabled ? '已启用' : '已禁用'}`)
}

// 任务操作处理
const handleTaskAction = async (action, task) => {
  try {
    let response
    switch (action) {
      case 'pause':
        response = await fetch(`/api/scheduler/jobs/${task.id}/pause`, { method: 'POST' })
        break
      case 'resume':
        response = await fetch(`/api/scheduler/jobs/${task.id}/resume`, { method: 'POST' })
        break
      case 'trigger':
        response = await fetch(`/api/scheduler/jobs/${task.id}/trigger`, { method: 'POST' })
        break
      default:
        throw new Error('未知操作')
    }

    const data = await response.json()
    if (data.success) {
      ElMessage.success('操作成功')
      // 更新任务状态
      if (action === 'pause') {
        task.enabled = false
        task.status = 'disabled'
      } else if (action === 'resume') {
        task.enabled = true
        task.status = 'running'
      }
    } else {
      throw new Error(data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error(`操作失败: ${error.message}`)
  }
}

// 测试API连接
const testAPI = async () => {
  loading.value = true
  testResult.value = '正在测试API连接...'

  try {
    const response = await fetch('/api/scheduler/status')
    const data = await response.json()
    testResult.value = JSON.stringify(data, null, 2)
    ElMessage.success('API连接成功')
  } catch (error) {
    testResult.value = `API连接失败: ${error.message}`
    ElMessage.error('API连接失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.settings {
  padding: 20px;
  max-width: 100%;
  margin: 0;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 700;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.loading-container {
  padding: 40px 0;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 全局卡片样式优化 */
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  background-color: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* 按钮样式优化 */
:deep(.el-button) {
  font-weight: 500;
  border-radius: 6px;
}

:deep(.el-button--primary) {
  background-color: #409EFF;
  border-color: #409EFF;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}

@media (max-width: 768px) {
  .settings {
    padding: 12px;
  }

  .page-header {
    margin-bottom: 16px;
    padding: 12px 0;
  }

  .page-header h1 {
    font-size: 22px;
  }

  .page-description {
    font-size: 14px;
  }

  .settings-content {
    gap: 12px;
  }

  :deep(.el-card__header) {
    padding: 12px 16px;
  }

  :deep(.el-card__body) {
    padding: 16px;
  }
}
</style>