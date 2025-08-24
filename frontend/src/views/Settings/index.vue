<template>
  <div class="settings">
    <!-- 页面标题和帮助 -->
    <div class="page-header">
      <div class="page-title-wrapper">
        <h1 class="page-title">系统配置帮助说明</h1>
        <p class="page-description">配置AI自动化处理系统的各项参数和功能</p>
      </div>
      <el-button
        type="primary"
        :icon="QuestionFilled"
        circle
        size="large"
        class="help-button"
        @click="showHelpDialog = true"
        title="查看配置说明"
      />
    </div>

    <!-- 调度器配置 -->
    <div class="config-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Setting /></el-icon>
          调度器配置
        </h2>
        <p class="section-description">配置调度器的基本参数和工作流程</p>
      </div>

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
    </div>

    <!-- 监控配置 -->
    <div class="config-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Monitor /></el-icon>
          监控配置
        </h2>
        <p class="section-description">配置Badcase检测阈值和监控参数</p>
      </div>

      <!-- 监控配置 -->
      <MonitorConfig />
    </div>

    <!-- 大屏展示配置 -->
    <div class="config-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><DataAnalysis /></el-icon>
          大屏展示配置
        </h2>
        <p class="section-description">配置大屏展示页面的各项显示参数和数据范围</p>
      </div>

      <!-- 大屏展示配置 -->
      <DisplayConfig />
    </div>

    <!-- 工作流模式配置 -->
    <div class="config-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Setting /></el-icon>
          工作流模式配置
        </h2>
        <p class="section-description">配置工作流中各阶段的处理模式，支持手动和自动模式切换</p>
      </div>

      <!-- 工作流模式配置 -->
      <WorkflowModeConfig />
    </div>

    <!-- 答案生成管理 -->
    <div class="config-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><DataAnalysis /></el-icon>
          答案生成管理
        </h2>
        <p class="section-description">管理答案生成的导出导入流程，支持Excel文件处理</p>
      </div>

      <!-- 答案生成管理 -->
      <AnswerGenerationManager />
    </div>

    <!-- 定时任务配置 -->
    <div class="config-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Timer /></el-icon>
          定时任务配置
        </h2>
        <p class="section-description">管理系统中的定时任务，包括启用、暂停和手动执行</p>
      </div>

      <!-- 任务管理 -->
      <TaskManager
        :tasks="scheduledTasks"
        @action="handleTaskAction"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 帮助对话框 -->
    <el-dialog
      v-model="showHelpDialog"
      title="系统配置功能说明"
      width="800px"
      :before-close="handleCloseHelp"
    >
      <div class="help-content">
        <el-tabs v-model="activeHelpTab" type="border-card">
          <el-tab-pane label="📋 概述" name="overview">
            <div class="help-section">
              <h3>🎯 系统配置功能概述</h3>
              <p>系统配置页面用于管理AI自动化处理系统的各项参数和功能，包括调度器配置、监控配置和定时任务管理。</p>

              <h4>🔧 主要功能模块</h4>
              <ul>
                <li><strong>调度器配置</strong>：控制AI处理工作流的基本参数和执行流程</li>
                <li><strong>监控配置</strong>：设置Badcase检测阈值和质量监控参数</li>
                <li><strong>定时任务配置</strong>：管理系统中的所有定时任务</li>
                <li><strong>大屏展示配置</strong>：配置大屏展示页面的各项显示参数</li>
              </ul>

              <h4>👥 适用人群</h4>
              <ul>
                <li><strong>系统管理员</strong>：负责系统配置和维护</li>
                <li><strong>运维人员</strong>：监控系统运行状态</li>
                <li><strong>业务人员</strong>：了解系统处理流程</li>
              </ul>
            </div>
          </el-tab-pane>

          <el-tab-pane label="⚙️ 调度器配置" name="scheduler">
            <div class="help-section">
              <h3>⚙️ 调度器配置详解</h3>

              <h4>🔄 基础配置</h4>
              <ul>
                <li><strong>启用调度器</strong>：控制整个定时任务系统的开启/关闭</li>
                <li><strong>启动时自动处理</strong>：系统启动时是否立即处理已有数据</li>
                <li><strong>无数据时挂起</strong>：没有待处理数据时自动暂停工作流</li>
                <li><strong>启用数据检测</strong>：执行前检查是否有数据需要处理</li>
              </ul>

              <h4>📊 处理参数</h4>
              <ul>
                <li><strong>工作流间隔</strong>：自动执行工作流的时间间隔（分钟）</li>
                <li><strong>批处理大小</strong>：每次处理的数据条数（1-1000条）</li>
                <li><strong>最小批处理</strong>：低于此数量时挂起处理（1-100条）</li>
              </ul>

              <h4>🔄 工作流阶段</h4>
              <ol>
                <li><strong>数据同步</strong>：从源数据表同步最新问题到系统</li>
                <li><strong>问题分类</strong>：使用AI对问题进行智能分类</li>
                <li><strong>答案生成</strong>：调用AI模型生成问题答案</li>
                <li><strong>答案评分</strong>：对生成的答案进行质量评分</li>
                <li><strong>人工审核</strong>：人工审核处理结果</li>
              </ol>

              <div class="help-tip">
                <strong>💡 提示</strong>：修改工作流间隔时间后，点击"保存配置"会自动重新加载任务，使新配置立即生效。
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="📊 监控配置" name="monitor">
            <div class="help-section">
              <h3>📊 Badcase监控配置详解</h3>

              <h4>🎯 评分阈值设置</h4>
              <ul>
                <li><strong>设置范围</strong>：0.0 - 5.0分</li>
                <li><strong>触发条件</strong>：当YOYO模型任一评分维度低于此阈值时标记为badcase</li>
                <li><strong>评分维度</strong>：准确性、完整性、清晰度、实用性、创新性</li>
              </ul>

              <h4>⏰ 延迟生效机制</h4>
              <ul>
                <li><strong>生效时间</strong>：阈值变更将在下周一生效</li>
                <li><strong>设计原因</strong>：确保数据统计的一致性</li>
                <li><strong>避免影响</strong>：避免周中变更影响统计结果</li>
              </ul>

              <h4>🔍 自动检测功能</h4>
              <ul>
                <li><strong>实时监控</strong>：启用后系统自动监控新生成的答案</li>
                <li><strong>自动标记</strong>：实时标记低质量答案</li>
                <li><strong>通知提醒</strong>：检测到badcase时发送通知提醒</li>
              </ul>

              <div class="help-warning">
                <strong>⚠️ 注意</strong>：Badcase阈值的修改会影响质量评估标准，请谨慎调整。
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="📋 任务管理" name="tasks">
            <div class="help-section">
              <h3>📋 定时任务管理详解</h3>

              <h4>📊 任务状态说明</h4>
              <ul>
                <li><strong>运行中</strong>：任务正在按计划执行</li>
                <li><strong>已暂停</strong>：任务被手动暂停，不会执行</li>
                <li><strong>已禁用</strong>：任务被禁用，需要手动启用</li>
                <li><strong>等待中</strong>：任务等待下次执行时间</li>
              </ul>

              <h4>⏰ 执行时间显示</h4>
              <ul>
                <li><strong>下次执行时间</strong>：显示任务的下次预定执行时间</li>
                <li><strong>相对时间</strong>：支持相对时间显示（如"3分钟后"）</li>
                <li><strong>过期显示</strong>：过期任务会显示"已过期"</li>
              </ul>

              <h4>🎮 操作按钮说明</h4>
              <ul>
                <li><strong>暂停</strong>：暂停正在运行的任务</li>
                <li><strong>启用</strong>：启用已暂停的任务</li>
                <li><strong>立即执行</strong>：手动触发任务立即执行</li>
              </ul>

              <h4>📝 使用注意事项</h4>
              <ul>
                <li>修改工作流间隔时间后任务会自动重新加载</li>
                <li>暂停的任务不会自动执行</li>
                <li>立即执行不影响下次计划执行时间</li>
              </ul>
            </div>
          </el-tab-pane>

          <el-tab-pane label="📊 大屏展示" name="display">
            <div class="help-section">
              <h3>📊 大屏展示配置</h3>

              <h4>🔥 热门问题分类配置</h4>
              <ul>
                <li><strong>近一周</strong>：只显示近7天内有问题的分类，通常6-10个分类，数据更聚焦</li>
                <li><strong>全部时间</strong>：显示所有16个分类，按近期活跃度排序，数据更全面</li>
              </ul>

              <h4>🎯 使用建议</h4>
              <ul>
                <li><strong>日常监控</strong>：建议使用"近一周"模式，关注当前热点问题</li>
                <li><strong>全面分析</strong>：建议使用"全部时间"模式，了解整体问题分布</li>
                <li><strong>定期切换</strong>：可根据业务需要灵活切换时间范围</li>
              </ul>

              <h4>🚀 即将支持</h4>
              <ul>
                <li>AI性能对比图表配置</li>
                <li>实时数据流显示数量</li>
                <li>趋势图时间范围</li>
                <li>自动刷新间隔</li>
              </ul>
            </div>
          </el-tab-pane>

          <el-tab-pane label="❓ 常见问题" name="faq">
            <div class="help-section">
              <h3>❓ 常见问题解答</h3>

              <div class="faq-item">
                <h4>Q: 修改工作流间隔时间后为什么没有立即生效？</h4>
                <p><strong>A:</strong> 请确保点击了"保存配置"按钮。系统会自动重新加载任务，使新的间隔时间立即生效。如果仍未生效，可以点击"重新加载任务"按钮手动触发。</p>
              </div>

              <div class="faq-item">
                <h4>Q: Badcase阈值什么时候生效？</h4>
                <p><strong>A:</strong> 为了确保数据统计的一致性，Badcase阈值的修改将在下周一生效。这样可以避免周中变更对统计结果的影响。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 如何暂停所有定时任务？</h4>
                <p><strong>A:</strong> 可以在基础配置中关闭"启用调度器"开关，这样会停止所有定时任务的执行。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 立即执行任务会影响下次计划执行时间吗？</h4>
                <p><strong>A:</strong> 不会。立即执行只是手动触发一次任务执行，不会改变任务的计划执行时间。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 工作流阶段可以跳过某些步骤吗？</h4>
                <p><strong>A:</strong> 可以。您可以通过禁用某个工作流阶段来跳过该步骤。但请注意，某些阶段之间存在依赖关系。</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showHelpDialog = false">关闭</el-button>
          <el-button type="primary" @click="showHelpDialog = false">我知道了</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, Timer, Monitor, QuestionFilled, DataAnalysis } from '@element-plus/icons-vue'
import BasicConfig from './components/BasicConfig.vue'
import WorkflowConfig from './components/WorkflowConfig.vue'
import TaskManager from './components/TaskManager.vue'
import MonitorConfig from './components/MonitorConfig.vue'
import DisplayConfig from './components/DisplayConfig.vue'
import WorkflowModeConfig from './components/WorkflowModeConfig.vue'
import AnswerGenerationManager from './components/AnswerGenerationManager.vue'

const loading = ref(false)

// 帮助对话框状态
const showHelpDialog = ref(false)
const activeHelpTab = ref('overview')



// 基础配置数据
const basicConfig = reactive({
  schedulerEnabled: false,
  autoProcessOnStartup: false,
  autoSuspendWhenNoData: true,
  dataCheckEnabled: true,
  workflowIntervalMinutes: 120,
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

// 定时任务数据
const scheduledTasks = ref([
  {
    id: 'configurable_workflow',
    name: 'AI处理工作流',
    status: 'running',
    nextRunTime: '2025-07-30T14:50:00Z',
    enabled: true
  }
])

// 保存配置
const handleSaveConfig = async () => {
  loading.value = true
  try {
    const { updateSchedulerConfig } = await import('@/api/scheduler')
    const result = await updateSchedulerConfig({
      scheduler_enabled: basicConfig.schedulerEnabled,
      auto_process_on_startup: basicConfig.autoProcessOnStartup,
      auto_suspend_when_no_data: basicConfig.autoSuspendWhenNoData,
      data_check_enabled: basicConfig.dataCheckEnabled,
      workflow_interval_minutes: basicConfig.workflowIntervalMinutes,
      batch_size: basicConfig.batchSize,
      min_batch_size: basicConfig.minBatchSize
    })

    if (result.success) {
      ElMessage.success('配置保存成功')
    } else {
      throw new Error(result.message || '保存失败')
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
    const { executeWorkflowPhase } = await import('@/api/scheduler')
    const result = await executeWorkflowPhase(phase.key)

    if (result.success) {
      ElMessage.success(`${phase.name}执行成功`)
      phase.status = 'success'
    } else {
      throw new Error(result.message || '执行失败')
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
    const { pauseJob, resumeJob, triggerJob } = await import('@/api/scheduler')
    let result

    switch (action) {
      case 'pause':
        result = await pauseJob(task.id)
        break
      case 'resume':
        result = await resumeJob(task.id)
        break
      case 'trigger':
        result = await triggerJob(task.id)
        break
      default:
        throw new Error('未知操作')
    }

    if (result.success) {
      ElMessage.success('操作成功')
      // 重新加载任务列表以获取最新状态
      await loadScheduledTasks()
    } else {
      throw new Error(result.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error(`操作失败: ${error.message}`)
  }
}

// 加载定时任务数据
const loadScheduledTasks = async () => {
  try {
    const { getScheduledJobs } = await import('@/api/scheduler')
    const result = await getScheduledJobs()

    if (result.success && result.data) {
      // 转换后端数据格式为前端需要的格式
      const tasks = []

      if (result.data.scheduler_jobs && result.data.scheduler_jobs.length > 0) {
        result.data.scheduler_jobs.forEach(job => {
          const taskInfo = result.data.jobs[job.id]
          if (taskInfo) {
            tasks.push({
              id: job.id,
              name: taskInfo.name,
              status: taskInfo.enabled ? (job.next_run_time ? 'running' : 'paused') : 'disabled',
              nextRunTime: job.next_run_time,
              enabled: taskInfo.enabled
            })
          }
        })
        scheduledTasks.value = tasks
      }
    }
  } catch (error) {
    console.error('加载定时任务失败:', error)
    // 如果API调用失败，保持默认的模拟数据
  }
}

// 加载配置数据
const loadConfig = async () => {
  try {
    const { getSchedulerConfig } = await import('@/api/scheduler')
    const result = await getSchedulerConfig()

    if (result.success && result.data) {
      // 更新配置数据
      basicConfig.schedulerEnabled = result.data.scheduler_enabled
      basicConfig.autoProcessOnStartup = result.data.auto_process_on_startup
      basicConfig.autoSuspendWhenNoData = result.data.auto_suspend_when_no_data
      basicConfig.dataCheckEnabled = result.data.data_check_enabled
      basicConfig.workflowIntervalMinutes = result.data.workflow_interval_minutes
      basicConfig.batchSize = result.data.batch_size
      basicConfig.minBatchSize = result.data.min_batch_size
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error(`加载配置失败: ${error.message}`)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadConfig()
  loadScheduledTasks()
})

// 帮助对话框方法
const handleCloseHelp = (done) => {
  done()
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

/* 页面标题样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px 28px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
}

.page-title-wrapper {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.help-button {
  width: 48px;
  height: 48px;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.help-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}



/* 配置分组样式 */
.config-section {
  margin-bottom: 32px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.section-header {
  padding: 24px 28px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 2px solid #e4e7ed;
}

.section-title {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 24px;
  color: #409EFF;
}

.section-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
}

.config-section :deep(.el-card) {
  margin: 0;
  border: none;
  box-shadow: none;
  border-radius: 0;
}

.config-section :deep(.el-card:last-child) {
  border-bottom: none;
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



  .config-section {
    margin-bottom: 20px;
    border-radius: 8px;
  }

  .section-header {
    padding: 16px 20px 12px;
  }

  .section-title {
    font-size: 18px;
    gap: 8px;
  }

  .section-icon {
    font-size: 20px;
  }

  .section-description {
    font-size: 13px;
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

/* 帮助对话框样式 */
.help-content {
  max-height: 60vh;
  overflow-y: auto;
}

.help-section {
  padding: 20px;
  line-height: 1.6;
}

.help-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.help-section h4 {
  margin: 16px 0 8px 0;
  font-size: 16px;
  color: #409eff;
  font-weight: 600;
}

.help-section ul, .help-section ol {
  margin: 8px 0 16px 0;
  padding-left: 20px;
}

.help-section li {
  margin: 4px 0;
  color: #606266;
}

.help-section li strong {
  color: #303133;
}

.help-section p {
  margin: 8px 0;
  color: #606266;
}

.help-tip {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 16px 0;
  color: #0066cc;
}

.help-warning {
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 16px 0;
  color: #f56c6c;
}

.faq-item {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.faq-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.faq-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: white;
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

:deep(.el-tabs__header) {
  margin: 0 0 16px 0;
}

:deep(.el-tabs__item) {
  font-weight: 500;
}
</style>