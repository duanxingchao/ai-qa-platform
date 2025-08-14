<template>
  <div class="badcase-simple">
    <h2>🔍 Badcase分析及优化</h2>

    <div class="test-buttons">
      <el-button @click="testStatistics" type="primary" :loading="loading">
        测试统计API
      </el-button>
      <el-button @click="testList" type="success" :loading="loading">
        测试列表API
      </el-button>
    </div>
    
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      正在加载...
    </div>
    
    <div v-if="statistics" class="statistics">
      <h3>统计数据</h3>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_questions }}</div>
              <div class="stat-label">问题总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.badcase_count }}</div>
              <div class="stat-label">Badcase数量</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.badcase_ratio }}%</div>
              <div class="stat-label">Badcase占比</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.pending_count }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div v-if="badcaseList && badcaseList.length > 0" class="badcase-list">
      <h3>Badcase列表</h3>
      <el-table :data="badcaseList" style="width: 100%">
        <el-table-column prop="query" label="问题" width="300" />
        <el-table-column prop="classification" label="分类" width="120" />
        <el-table-column prop="review_status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.review_status)">
              {{ getStatusText(scope.row.review_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detected_at" label="检测时间" width="180" />
        <el-table-column label="低分维度">
          <template #default="scope">
            <el-tag 
              v-for="dim in scope.row.low_score_dimensions" 
              :key="dim.dimension_name"
              size="small"
              type="warning"
              style="margin-right: 5px;"
            >
              {{ dim.dimension_name }}({{ dim.score }})
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div v-if="error" class="error">
      <h4>错误信息：</h4>
      <pre>{{ error }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getBadcaseStatistics, getBadcaseList } from './api/badcase'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const statistics = ref(null)
const badcaseList = ref([])
const error = ref(null)

const testStatistics = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('测试统计API...')
    const response = await getBadcaseStatistics('all')
    console.log('统计API响应:', response)
    
    if (response && response.data) {
      statistics.value = response.data
      ElMessage.success('统计数据加载成功！')
    } else {
      throw new Error('响应数据格式错误')
    }
  } catch (err) {
    console.error('统计API测试失败:', err)
    error.value = err.message || '未知错误'
    ElMessage.error('统计数据加载失败：' + (err.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const testList = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('测试列表API...')
    const response = await getBadcaseList({
      time_range: 'all',
      page: 1,
      page_size: 10
    })
    console.log('列表API响应:', response)
    
    if (response && response.data && response.data.list) {
      badcaseList.value = response.data.list
      ElMessage.success(`加载了 ${response.data.list.length} 个Badcase！`)
    } else {
      throw new Error('响应数据格式错误')
    }
  } catch (err) {
    console.error('列表API测试失败:', err)
    error.value = err.message || '未知错误'
    ElMessage.error('列表数据加载失败：' + (err.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'reviewed': 'info',
    'optimized': 'success'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'reviewed': '已复核',
    'optimized': '已优化'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.badcase-simple {
  padding: 20px;
}

.test-buttons {
  margin: 20px 0;
}

.loading {
  margin: 20px 0;
  text-align: center;
  color: #409EFF;
}

.statistics {
  margin: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.badcase-list {
  margin: 20px 0;
}

.error {
  margin: 20px 0;
  padding: 15px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56565;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
