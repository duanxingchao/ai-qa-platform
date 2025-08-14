<template>
  <div class="display-config">
    <div class="config-header">
      <h3 class="config-title">📊 大屏展示配置</h3>
      <el-button
        type="primary"
        size="small"
        @click="handleSave"
        :loading="saving"
      >
        保存配置
      </el-button>
    </div>

    <el-form :model="config" label-width="160px">
      <!-- 热门问题分类配置 -->
      <div class="config-section">
        <h4 class="section-title">🔥 热门问题分类</h4>
        <el-form-item label="时间范围">
          <el-radio-group v-model="config.hotCategoriesTimeRange" size="large">
            <el-radio-button label="week">近一周</el-radio-button>
            <el-radio-button label="all">全部时间</el-radio-button>
          </el-radio-group>
          <div class="config-tip">
            <div class="tip-item">
              <strong>近一周：</strong>只显示近7天内有问题的分类，数据更加聚焦当前热点
            </div>
            <div class="tip-item">
              <strong>全部时间：</strong>显示所有16个分类，按近期活跃度排序，数据更全面
            </div>
          </div>
        </el-form-item>
      </div>


    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDisplayConfigs, updateDisplayConfigs } from '@/api/displayConfig'

const saving = ref(false)

// 配置数据
const config = reactive({
  hotCategoriesTimeRange: 'all'
})

// 保存配置
const handleSave = async () => {
  saving.value = true
  try {
    const result = await updateDisplayConfigs({
      hot_categories_time_range: config.hotCategoriesTimeRange
    })

    if (result.success) {
      ElMessage.success('大屏展示配置保存成功')
    } else {
      throw new Error(result.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error(`配置保存失败: ${error.message}`)
  } finally {
    saving.value = false
  }
}

// 加载配置
const loadConfig = async () => {
  try {
    const result = await getDisplayConfigs()
    
    if (result.success && result.data) {
      config.hotCategoriesTimeRange = result.data.hot_categories_time_range || 'all'
    }
  } catch (error) {
    console.error('加载大屏展示配置失败:', error)
    ElMessage.error(`加载配置失败: ${error.message}`)
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.display-config {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.config-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.config-section {
  margin-bottom: 32px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #606266;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

.config-tip {
  margin-top: 16px;
  margin-left: 8px;
  font-size: 13px;
  color: #909399;
  padding-left: 12px;
  border-left: 2px solid #e4e7ed;
}

.tip-item {
  margin-bottom: 6px;
  line-height: 1.5;
}



:deep(.el-radio-button__inner) {
  padding: 8px 16px;
}

:deep(.el-alert) {
  border-radius: 6px;
}

:deep(.el-alert__content) {
  font-size: 13px;
}

:deep(.el-alert ul) {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

:deep(.el-alert li) {
  margin-bottom: 4px;
}
</style>
