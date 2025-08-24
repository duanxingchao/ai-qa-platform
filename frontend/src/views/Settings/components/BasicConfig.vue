<template>
  <div class="basic-config">
    <div class="config-header">
      <h3 class="config-title">⚙️ 基础配置</h3>
      <el-button
        type="primary"
        size="small"
        @click="handleSave"
        :loading="saving"
      >
        保存配置
      </el-button>
    </div>

    <el-form :model="config" label-width="140px">
      <!-- 功能开关区域 -->
      <div class="config-section">
        <h4 class="section-title">功能开关</h4>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="启用调度器">
              <el-switch v-model="config.schedulerEnabled" size="large" />
              <div class="config-tip">控制整个调度器的启用状态</div>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="启动时自动处理">
              <el-switch v-model="config.autoProcessOnStartup" size="large" />
              <div class="config-tip">应用启动时是否立即处理已有数据</div>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="无数据时挂起">
              <el-switch v-model="config.autoSuspendWhenNoData" size="large" />
              <div class="config-tip">没有待处理数据时自动挂起工作流</div>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="启用数据检测">
              <el-switch v-model="config.dataCheckEnabled" size="large" />
              <div class="config-tip">执行前检查是否有数据需要处理</div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <!-- 处理参数区域 -->
      <div class="config-section">
        <h4 class="section-title">处理参数</h4>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="工作流间隔">
              <div class="input-control-group">
                <div class="number-input-wrapper">
                  <el-input-number
                    v-model="config.workflowIntervalMinutes"
                    :min="1"
                    :max="720"
                    controls-position="right"
                    size="default"
                    class="compact-number-input"
                  />
                  <span class="input-unit">分钟</span>
                </div>
                <div class="config-tip">自动执行工作流的间隔时间</div>
              </div>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="批处理大小">
              <div class="input-control-group">
                <div class="number-input-wrapper">
                  <el-input-number
                    v-model="config.batchSize"
                    :min="1"
                    :max="1000"
                    controls-position="right"
                    size="default"
                    class="compact-number-input"
                  />
                  <span class="input-unit">条</span>
                </div>
                <div class="config-tip">每次处理的数据量</div>
              </div>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="最小批处理">
              <div class="input-control-group">
                <div class="number-input-wrapper">
                  <el-input-number
                    v-model="config.minBatchSize"
                    :min="1"
                    :max="100"
                    controls-position="right"
                    size="default"
                    class="compact-number-input"
                  />
                  <span class="input-unit">条</span>
                </div>
                <div class="config-tip">低于此数量时挂起</div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  config: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['save'])

const saving = ref(false)

const handleSave = async () => {
  saving.value = true
  try {
    await emit('save')
  } catch (error) {
    console.error('保存配置失败:', error)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.basic-config {
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

.config-section {
  margin-bottom: 20px;
}

.section-title {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.config-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  margin: 0;
  padding-left: 2px; /* 与输入框左边缘对齐 */
}

.el-form-item {
  margin-bottom: 16px;
}

:deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

:deep(.el-switch__label) {
  font-size: 14px;
  font-weight: 500;
}

/* 输入控件组容器 */
.input-control-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 数字输入框容器 */
.number-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 32px; /* 确保容器高度一致 */
}

/* 紧凑型数字输入框 */
.compact-number-input {
  width: 100px !important;
  flex-shrink: 0;
}

/* 单位文字 */
.input-unit {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
  line-height: 32px; /* 与输入框高度对齐 */
}

:deep(.compact-number-input .el-input__inner) {
  font-size: 14px;
  text-align: center;
}

:deep(.compact-number-input .el-input-number__increase),
:deep(.compact-number-input .el-input-number__decrease) {
  width: 28px;
}

@media (max-width: 1200px) {
  .el-col:nth-child(3) {
    margin-top: 16px;
  }
}

@media (max-width: 768px) {
  .config-section .el-row .el-col {
    margin-bottom: 16px;
  }

  /* 移动端数字输入框调整 */
  .compact-number-input {
    width: 80px !important;
  }

  .number-input-wrapper {
    gap: 6px;
  }

  .input-unit {
    font-size: 13px;
  }

  .config-tip {
    font-size: 11px;
  }

  .input-control-group {
    gap: 4px;
  }
}
</style>
