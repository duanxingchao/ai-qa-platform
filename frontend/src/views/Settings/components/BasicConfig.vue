<template>
  <el-card class="basic-config">
    <template #header>
      <div class="card-header">
        <span>⚙️ 基础配置</span>
        <el-button 
          type="primary" 
          size="small" 
          @click="handleSave"
          :loading="saving"
        >
          保存配置
        </el-button>
      </div>
    </template>
    
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
              <el-input-number
                v-model="config.workflowIntervalMinutes"
                :min="1"
                :max="60"
                controls-position="right"
                style="width: 100%"
                size="large"
              />
              <div class="config-tip">分钟 - 自动执行工作流的间隔时间</div>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="批处理大小">
              <el-input-number
                v-model="config.batchSize"
                :min="1"
                :max="1000"
                controls-position="right"
                style="width: 100%"
                size="large"
              />
              <div class="config-tip">条 - 每次处理的数据量</div>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="最小批处理">
              <el-input-number
                v-model="config.minBatchSize"
                :min="1"
                :max="100"
                controls-position="right"
                style="width: 100%"
                size="large"
              />
              <div class="config-tip">条 - 低于此数量时挂起</div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-form>
  </el-card>
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
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
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
  font-size: 13px;
  color: #606266;
  margin-top: 6px;
  line-height: 1.4;
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

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input-number .el-input__inner) {
  font-size: 14px;
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
}
</style>
