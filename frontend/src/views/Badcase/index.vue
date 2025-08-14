<template>
  <div class="badcase">
    <div class="page-header">
      <h1>🔍 badcase 分析及优化</h1>
      <p class="page-description">AI模型问题案例分析、错误识别与优化建议</p>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon error">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalBadcases }}</div>
              <div class="stat-label">总badcase数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingCases }}</div>
              <div class="stat-label">待处理案例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.resolvedCases }}</div>
              <div class="stat-label">已复核案例</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon info">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.improvementRate }}%</div>
              <div class="stat-label">复核率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析图表 -->
    <el-row :gutter="20" class="charts-row">
      <!-- badcase分类分布 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>badcase分类分布</span>
              <el-button type="primary" size="small" @click="refreshCategoryChart">刷新</el-button>
            </div>
          </template>
          <div ref="categoryChart" style="height: 350px;"></div>
        </el-card>
      </el-col>

      <!-- 趋势分析 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>badcase趋势分析</span>
              <el-button type="primary" size="small" @click="refreshTrendChart">刷新</el-button>
            </div>
          </template>
          <div ref="trendChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI模型badcase对比 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>AI模型badcase对比分析</span>
              <el-button type="primary" size="small" @click="refreshModelChart">刷新</el-button>
            </div>
          </template>
          <div ref="modelChart" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- badcase列表 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>badcase详细列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索badcase..."
              style="width: 200px; margin-right: 10px;"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="severityFilter"
              placeholder="严重程度"
              style="width: 120px; margin-right: 10px;"
              clearable
            >
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
            <el-select
              v-model="statusFilter"
              placeholder="处理状态"
              style="width: 120px; margin-right: 10px;"
              clearable
            >
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已解决" value="resolved" />
            </el-select>
            <el-button type="primary" @click="loadBadcases">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="badcasesList"
        :loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ai_model" label="AI模型" width="100">
          <template #default="{ row }">
            <el-tag :type="getModelTagType(row.ai_model)">
              {{ getModelName(row.ai_model) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="问题分类" width="120" />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="处理状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发现时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="warning" size="small" @click="optimizeCase(row)">
              优化
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="Badcase详情"
      width="800px"
      :before-close="handleDetailClose"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="问题ID">
            {{ currentDetail.business_id }}
          </el-descriptions-item>
          <el-descriptions-item label="发现时间">
            {{ formatDate(currentDetail.badcase_detected_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentDetail.badcase_review_status)">
              {{ getStatusText(currentDetail.badcase_review_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            {{ currentDetail.classification || '未分类' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">问题内容</el-divider>
        <div class="question-content">
          {{ currentDetail.query }}
        </div>

        <el-divider content-position="left">答案内容</el-divider>
        <div class="answer-content">
          {{ currentDetail.answer_text || '暂无答案' }}
        </div>

        <el-divider content-position="left">评分详情</el-divider>
        <div v-if="currentDetail.score_details" class="score-details">
          <el-row :gutter="16">
            <el-col :span="8" v-for="score in currentDetail.score_details" :key="score.dimension_name">
              <el-card class="score-card">
                <div class="score-item">
                  <div class="score-name">{{ score.dimension_name }}</div>
                  <div class="score-value" :class="{ 'low-score': score.score < 3 }">
                    {{ score.score }}/5
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <el-divider content-position="left">低分维度</el-divider>
        <div v-if="currentDetail.badcase_dimensions" class="low-dimensions">
          <el-tag
            v-for="dim in parseBadcaseDimensions(currentDetail.badcase_dimensions)"
            :key="dim.dimension_name"
            type="danger"
            class="dimension-tag"
          >
            {{ dim.dimension_name }}: {{ dim.score }}/5
          </el-tag>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button
            v-if="currentDetail && currentDetail.badcase_review_status === 'pending'"
            type="success"
            @click="markAsResolved"
          >
            标记为已处理
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getBadcaseStatistics, getBadcaseList, getBadcaseDetail } from '@/api/badcase'

export default {
  name: 'Badcase',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const stats = ref({
      totalBadcases: 0,
      pendingCases: 0,
      resolvedCases: 0,
      improvementRate: 0
    })
    
    // 图表引用
    const categoryChart = ref(null)
    const trendChart = ref(null)
    const modelChart = ref(null)
    
    // 表格数据
    const badcasesList = ref([])
    const searchKeyword = ref('')
    const severityFilter = ref('')
    const statusFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)

    // 详情弹窗
    const detailVisible = ref(false)
    const currentDetail = ref(null)
    
    // 图表实例
    let categoryChartInstance = null
    let trendChartInstance = null
    let modelChartInstance = null
    
    // 加载统计数据
    const loadStats = async () => {
      try {
        loading.value = true
        const response = await getBadcaseStatistics({ time_range: 'all' })
        if (response.success) {
          const data = response.data
          stats.value = {
            totalBadcases: data.total_badcases || 0,
            pendingCases: data.pending_count || 0,
            resolvedCases: data.reviewed_count || 0,
            improvementRate: data.improvement_rate || 0
          }
        } else {
          ElMessage.error('获取统计数据失败')
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 初始化分类分布图
    const initCategoryChart = () => {
      if (!categoryChart.value) return

      categoryChartInstance = echarts.init(categoryChart.value)
      const option = {
        title: {
          text: 'badcase分类分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [{
          name: 'badcase分类',
          type: 'pie',
          radius: '60%',
          data: [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      categoryChartInstance.setOption(option)
    }

    // 更新分类分布图
    const updateCategoryChart = (categoryData) => {
      if (!categoryChartInstance) return

      const data = Object.entries(categoryData).map(([name, value]) => ({
        name,
        value
      }))

      categoryChartInstance.setOption({
        series: [{
          data: data
        }]
      })
    }
    
    // 工具函数
    const getModelTagType = (model) => {
      const typeMap = { yoyo: 'info', doubao: 'primary', xiaotian: 'success' }
      return typeMap[model] || 'info'
    }
    
    const getModelName = (model) => {
      const nameMap = { yoyo: 'YOYO', doubao: '豆包', xiaotian: '小天' }
      return nameMap[model] || model
    }
    
    const getSeverityTagType = (severity) => {
      const typeMap = { high: 'danger', medium: 'warning', low: 'info' }
      return typeMap[severity] || 'info'
    }
    
    const getSeverityText = (severity) => {
      const textMap = { high: '高', medium: '中', low: '低' }
      return textMap[severity] || severity
    }
    
    const getStatusTagType = (status) => {
      const typeMap = { pending: 'warning', processing: 'primary', resolved: 'success' }
      return typeMap[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const textMap = { pending: '待处理', processing: '处理中', resolved: '已解决' }
      return textMap[status] || status
    }
    
    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleString()
    }
    
    // 加载badcase列表
    const loadBadcases = async () => {
      try {
        loading.value = true
        const params = {
          time_range: 'all',
          page: currentPage.value,
          page_size: pageSize.value
        }

        if (statusFilter.value) {
          params.status_filter = statusFilter.value
        }

        if (searchKeyword.value.trim()) {
          params.search = searchKeyword.value.trim()
        }

        const response = await getBadcaseList(params)
        if (response.success) {
          const data = response.data
          badcasesList.value = data.badcases || []
          total.value = data.total || 0

          // 更新分类分布图数据
          if (data.category_distribution) {
            updateCategoryChart(data.category_distribution)
          }
        } else {
          ElMessage.error('获取badcase列表失败')
        }
      } catch (error) {
        console.error('加载badcase列表失败:', error)
        ElMessage.error('加载badcase列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 事件处理
    const handleSearch = () => {
      currentPage.value = 1
      loadBadcases()
    }

    // 状态筛选变化
    const handleStatusFilterChange = () => {
      currentPage.value = 1
      loadBadcases()
    }

    // 分页变化
    const handlePageChange = (page) => {
      currentPage.value = page
      loadBadcases()
    }

    // 页面大小变化
    const handlePageSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadBadcases()
    }
    
    const refreshCategoryChart = () => {
      loadBadcases()
    }

    const refreshTrendChart = () => {
      loadTrendData()
    }

    const refreshModelChart = () => {
      loadModelData()
    }

    // 加载趋势数据
    const loadTrendData = async () => {
      try {
        const response = await getBadcaseStatistics({ time_range: 'month' })
        if (response.success && response.data.trend_data) {
          updateTrendChart(response.data.trend_data)
        }
      } catch (error) {
        console.error('加载趋势数据失败:', error)
      }
    }

    // 初始化趋势图
    const initTrendChart = () => {
      if (!trendChart.value) return

      trendChartInstance = echarts.init(trendChart.value)
      const option = {
        title: {
          text: 'badcase趋势分析',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: 'badcase数量',
          type: 'line',
          data: [],
          smooth: true
        }]
      }
      trendChartInstance.setOption(option)
    }

    // 更新趋势图
    const updateTrendChart = (trendData) => {
      if (!trendChartInstance) return

      const dates = Object.keys(trendData).sort()
      const values = dates.map(date => trendData[date])

      trendChartInstance.setOption({
        xAxis: {
          data: dates
        },
        series: [{
          data: values
        }]
      })
    }

    // 加载模型对比数据
    const loadModelData = async () => {
      try {
        const response = await getBadcaseStatistics({ time_range: 'all' })
        if (response.success && response.data.model_distribution) {
          updateModelChart(response.data.model_distribution)
        }
      } catch (error) {
        console.error('加载模型数据失败:', error)
      }
    }

    // 初始化模型对比图
    const initModelChart = () => {
      if (!modelChart.value) return

      modelChartInstance = echarts.init(modelChart.value)
      const option = {
        title: {
          text: 'AI模型badcase对比',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: ['YOYO', '豆包', '小天']
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: 'badcase数量',
          type: 'bar',
          data: [0, 0, 0],
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      modelChartInstance.setOption(option)
    }

    // 更新模型对比图
    const updateModelChart = (modelData) => {
      if (!modelChartInstance) return

      const data = [
        modelData.yoyo || 0,
        modelData.doubao || 0,
        modelData.xiaotian || 0
      ]

      modelChartInstance.setOption({
        series: [{
          data: data
        }]
      })
    }
    
    const viewDetail = async (row) => {
      try {
        loading.value = true
        const response = await getBadcaseDetail(row.id)
        if (response.success) {
          currentDetail.value = response.data
          detailVisible.value = true
        } else {
          ElMessage.error('获取详情失败')
        }
      } catch (error) {
        console.error('获取详情失败:', error)
        ElMessage.error('获取详情失败')
      } finally {
        loading.value = false
      }
    }

    const optimizeCase = (row) => {
      ElMessage.info('优化功能开发中...')
    }

    // 详情弹窗相关
    const handleDetailClose = () => {
      detailVisible.value = false
      currentDetail.value = null
    }

    // 解析badcase维度数据
    const parseBadcaseDimensions = (dimensionsStr) => {
      try {
        const data = JSON.parse(dimensionsStr)
        return data.low_score_dimensions || []
      } catch (error) {
        return []
      }
    }

    // 标记为已处理
    const markAsResolved = async () => {
      try {
        // 这里应该调用标记为已处理的API
        ElMessage.success('标记成功')
        detailVisible.value = false
        loadBadcases() // 刷新列表
      } catch (error) {
        ElMessage.error('标记失败')
      }
    }
    
    // 生命周期
    onMounted(() => {
      loadStats()
      loadBadcases()
      nextTick(() => {
        initCategoryChart()
        initTrendChart()
        initModelChart()
        loadTrendData()
        loadModelData()
      })
    })
    
    return {
      loading,
      stats,
      categoryChart,
      trendChart,
      modelChart,
      badcasesList,
      searchKeyword,
      severityFilter,
      statusFilter,
      currentPage,
      pageSize,
      total,
      getModelTagType,
      getModelName,
      getSeverityTagType,
      getSeverityText,
      getStatusTagType,
      getStatusText,
      formatDate,
      loadBadcases,
      handleSearch,
      refreshCategoryChart,
      refreshTrendChart,
      refreshModelChart,
      viewDetail,
      optimizeCase,
      handleStatusFilterChange,
      handlePageChange,
      handlePageSizeChange,
      detailVisible,
      currentDetail,
      handleDetailClose,
      parseBadcaseDimensions,
      markAsResolved
    }
  }
}
</script>

<style lang="scss" scoped>
.badcase {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #303133;
    }

    .page-description {
      margin: 0;
      color: #606266;
      font-size: 14px;
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;

          .el-icon {
            font-size: 24px;
            color: white;
          }

          &.error {
            background: linear-gradient(135deg, #f56c6c, #f78989);
          }

          &.warning {
            background: linear-gradient(135deg, #e6a23c, #ebb563);
          }

          &.success {
            background: linear-gradient(135deg, #67c23a, #85ce61);
          }

          &.info {
            background: linear-gradient(135deg, #409eff, #66b1ff);
          }
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #303133;
            line-height: 1;
            margin-bottom: 4px;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;

    .chart-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        span {
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }

  .table-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      span {
        font-weight: bold;
        color: #303133;
      }

      .header-actions {
        display: flex;
        align-items: center;
      }
    }

    .pagination-container {
      margin-top: 20px;
      text-align: right;
    }
  }

  // 详情弹窗样式
  .detail-content {
    .question-content, .answer-content {
      padding: 12px;
      background-color: #f5f7fa;
      border-radius: 4px;
      margin: 8px 0;
      line-height: 1.6;
    }

    .score-details {
      .score-card {
        margin-bottom: 8px;

        .score-item {
          text-align: center;

          .score-name {
            font-size: 12px;
            color: #606266;
            margin-bottom: 4px;
          }

          .score-value {
            font-size: 18px;
            font-weight: bold;
            color: #409EFF;

            &.low-score {
              color: #F56C6C;
            }
          }
        }
      }
    }

    .low-dimensions {
      .dimension-tag {
        margin-right: 8px;
        margin-bottom: 8px;
      }
    }
  }
}
</style>
