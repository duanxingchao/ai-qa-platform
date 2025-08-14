<template>
  <el-card class="config-card">
    <template #header>
      <div class="card-header">
        <span>Badcase监控配置</span>
        <el-button type="primary" size="small" @click="saveConfig" :loading="saving">
          保存配置
        </el-button>
      </div>
    </template>

    <el-form :model="configForm" label-width="150px" class="config-form">
      <el-form-item label="Badcase评分阈值">
        <div class="threshold-config">
          <el-input-number
            v-model="configForm.badcaseThreshold"
            :min="0"
            :max="5"
            :step="0.1"
            :precision="1"
            style="width: 120px;"
          />
          <span class="threshold-desc">
            当YOYO模型任一评分维度（准确性、完整性、清晰度、实用性、创新性）低于此阈值时，将被标记为badcase
          </span>

          <!-- 延迟生效提示 -->
          <div v-if="hasThresholdChange" class="delay-notice">
            <el-alert
              :title="`阈值变更将于 ${nextWeekStartFormatted} 生效`"
              type="info"
              :description="thresholdChangeDesc"
              show-icon
              :closable="false"
            />
          </div>

          <!-- 待生效的变更 -->
          <div v-if="pendingChanges.length > 0" class="pending-changes">
            <h4>📅 待生效的配置变更</h4>
            <el-table :data="pendingChanges" size="small" style="margin-top: 10px;">
              <el-table-column prop="config_key" label="配置项" width="150" />
              <el-table-column label="当前值" width="100">
                <template #default="{ row }">
                  <el-tag type="success">{{ row.current_value }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="新值" width="100">
                <template #default="{ row }">
                  <el-tag type="warning">{{ row.new_value }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="effective_time" label="生效时间" width="150">
                <template #default="{ row }">
                  {{ formatDateTime(row.effective_time) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="danger"
                    @click="cancelChange(row.config_key)"
                  >
                    取消
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="自动检测开关">
        <el-switch
          v-model="configForm.autoDetection"
          active-text="开启"
          inactive-text="关闭"
        />
        <span class="config-desc">
          开启后，问题评分完成时自动检测badcase
        </span>
      </el-form-item>



      <el-form-item label="通知设置">
        <el-switch
          v-model="configForm.enableNotification"
          active-text="开启"
          inactive-text="关闭"
        />
        <span class="config-desc">
          检测到新badcase时发送通知
        </span>
      </el-form-item>


    </el-form>


  </el-card>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'MonitorConfig',
  setup() {
    const saving = ref(false)

    
    const configForm = ref({
      badcaseThreshold: 2.5,
      autoDetection: true,
      enableNotification: true
    })

    const originalThreshold = ref(2.5)
    const nextWeekStart = ref('')
    const nextWeekStartFormatted = ref('')
    const pendingChanges = ref([])
    


    // 计算属性
    const hasThresholdChange = computed(() => {
      return configForm.value.badcaseThreshold !== originalThreshold.value
    })

    const thresholdChangeDesc = computed(() => {
      return `当前阈值 ${originalThreshold.value} 将在本周继续使用，新阈值 ${configForm.value.badcaseThreshold} 将从下周一开始生效，确保数据统计的一致性。`
    })

    // 加载配置
    const loadConfig = async () => {
      try {
        // TODO: 调用获取配置API
        console.log('加载配置...')
        originalThreshold.value = configForm.value.badcaseThreshold
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    }

    // 加载下周开始时间
    const loadNextWeekStart = async () => {
      try {
        const response = await fetch('/api/config/next-week-start')
        const data = await response.json()
        if (data.success) {
          nextWeekStart.value = data.data.next_week_start
          nextWeekStartFormatted.value = data.data.formatted
        }
      } catch (error) {
        console.error('获取下周开始时间失败:', error)
      }
    }

    // 加载待生效变更
    const loadPendingChanges = async () => {
      try {
        const response = await fetch('/api/config/pending')
        const data = await response.json()
        if (data.success) {
          pendingChanges.value = data.data
        }
      } catch (error) {
        console.error('加载待生效变更失败:', error)
      }
    }

    // 取消变更
    const cancelChange = async (configKey) => {
      try {
        const response = await fetch(`/api/config/schedule/${configKey}`, {
          method: 'DELETE'
        })
        const data = await response.json()

        if (data.success) {
          ElMessage.success('已取消配置变更')
          await loadPendingChanges()
          await loadConfig()
        } else {
          ElMessage.error(data.message || '取消变更失败')
        }
      } catch (error) {
        console.error('取消变更失败:', error)
        ElMessage.error('取消变更失败')
      }
    }

    // 格式化日期时间
    const formatDateTime = (dateTimeStr) => {
      if (!dateTimeStr) return ''
      const date = new Date(dateTimeStr)
      return date.toLocaleString('zh-CN')
    }

    // 保存配置
    const saveConfig = async () => {
      try {
        saving.value = true

        if (hasThresholdChange.value) {
          // 阈值有变化，使用延迟生效
          const response = await fetch('/api/config/schedule', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              key: 'badcase_score_threshold',
              value: configForm.value.badcaseThreshold,
              effective_time: nextWeekStart.value,
              reason: '用户手动调整badcase检测阈值'
            })
          })

          const data = await response.json()
          if (data.success) {
            ElMessage.success('阈值变更已安排，将在下周一生效')
            await loadPendingChanges()
          } else {
            ElMessage.error(data.message || '安排配置变更失败')
          }
        } else {
          // 其他配置立即生效
          console.log('保存其他配置:', configForm.value)
          ElMessage.success('配置保存成功')
        }
      } catch (error) {
        console.error('保存配置失败:', error)
        ElMessage.error('保存配置失败')
      } finally {
        saving.value = false
      }
    }



    onMounted(async () => {
      await Promise.all([
        loadConfig(),
        loadNextWeekStart(),
        loadPendingChanges()
      ])
    })

    return {
      saving,

      configForm,
      originalThreshold,
      nextWeekStartFormatted,
      pendingChanges,
      hasThresholdChange,
      thresholdChangeDesc,

      saveConfig,

      cancelChange,
      formatDateTime
    }
  }
}
</script>

<style lang="scss" scoped>
.config-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      font-weight: bold;
      color: #303133;
    }
  }
  
  .config-form {
    .threshold-config {
      .threshold-desc {
        display: block;
        margin-top: 8px;
        color: #606266;
        font-size: 13px;
      }

      .delay-notice {
        margin-top: 15px;
      }

      .pending-changes {
        margin-top: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 4px;

        h4 {
          margin: 0 0 10px 0;
          color: #606266;
          font-size: 14px;
        }
      }
    }
    

    

    
    .config-desc {
      margin-left: 15px;
      color: #606266;
      font-size: 13px;
    }
  }
  

}
</style>
