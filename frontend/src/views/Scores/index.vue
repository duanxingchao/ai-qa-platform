<template>
  <div class="scores">
    <div class="page-header">
      <h1>评分分析</h1>
      <p class="page-description">AI模型评分结果分析与性能对比</p>
    </div>

    <!-- AI模型性能对比 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>AI模型性能对比</span>
              <el-button type="primary" size="small" @click="refreshModelChart">刷新</el-button>
            </div>
          </template>
          <div ref="modelChart" style="height: 400px;"></div>
        </el-card>
      </el-col>

      <!-- 评分分布统计 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>评分分布统计</span>
            </div>
          </template>
          <div ref="scoreDistChart" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细评分数据表格 -->
    <el-row :gutter="20" class="table-row">
      <el-col :span="24">
        <el-card class="table-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>评分详情列表</span>
              <div class="header-actions">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索问题关键词"
                  style="width: 200px; margin-right: 10px;"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select v-model="assistantFilter" placeholder="筛选AI类型" style="width: 120px;">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="原始模型" value="our_ai"></el-option>
                  <el-option label="豆包模型" value="doubao"></el-option>
                  <el-option label="小天模型" value="xiaotian"></el-option>
                </el-select>
              </div>
            </div>
          </template>
          
          <!-- 评分列表表格 -->
          <el-table :data="scoresList" v-loading="loading" stripe>
            <el-table-column prop="question_text" label="问题内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="assistant_type" label="AI类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getModelTagType(row.assistant_type)">
                  {{ getModelName(row.assistant_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_score" label="总分" width="80" sortable>
              <template #default="{ row }">
                <el-tag :type="getScoreTagType(row.total_score)">
                  {{ row.total_score }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="relevance_score" label="相关性" width="80" sortable />
            <el-table-column prop="accuracy_score" label="准确性" width="80" sortable />
            <el-table-column prop="completeness_score" label="完整性" width="80" sortable />
            <el-table-column prop="clarity_score" label="清晰度" width="80" sortable />
            <el-table-column prop="helpfulness_score" label="有用性" width="80" sortable />
            <el-table-column prop="created_at" label="评分时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
      </div>
    </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getScores, getScoreStatistics } from '@/api/scores'

export default {
  name: 'Scores',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const modelChart = ref(null)
    const scoreDistChart = ref(null)
    const searchKeyword = ref('')
    const assistantFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const scoresList = ref([])

    // 图表实例
    let modelChartInstance = null
    let scoreDistChartInstance = null
    let searchTimer = null

    // 初始化模型性能对比雷达图
    const initModelChart = () => {
      if (!modelChart.value) return
      
      modelChartInstance = echarts.init(modelChart.value)
      const option = {
        title: {
          text: 'AI模型性能对比',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `${params.name}: ${params.value}`
          }
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'middle'
        },
        radar: {
          indicator: [
            { name: '相关性', max: 10 },
            { name: '准确性', max: 10 },
            { name: '完整性', max: 10 },
            { name: '清晰度', max: 10 },
            { name: '有用性', max: 10 }
          ]
        },
        series: [{
            type: 'radar',
            data: [
              {
              value: [8, 7, 9, 8, 8],
              name: '原始模型'
              },
              {
              value: [7, 8, 7, 9, 8],
              name: '豆包模型'
              },
              {
              value: [9, 8, 8, 7, 9],
              name: '小天模型'
              }
            ]
        }]
      }
      modelChartInstance.setOption(option)
    }

    // 初始化评分分布统计图
    const initScoreDistChart = () => {
      if (!scoreDistChart.value) return
      
      scoreDistChartInstance = echarts.init(scoreDistChart.value)
      const option = {
        title: {
          text: '评分分布统计',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['原始模型', '豆包模型', '小天模型']
        },
        xAxis: {
          type: 'category',
          data: ['0-2分', '2-4分', '4-6分', '6-8分', '8-10分']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '原始模型',
            type: 'bar',
            data: [5, 10, 15, 20, 25]
          },
          {
            name: '豆包模型',
            type: 'bar',
            data: [3, 8, 18, 22, 23]
          },
          {
            name: '小天模型',
            type: 'bar',
            data: [4, 12, 16, 24, 21]
          }
        ]
      }
      scoreDistChartInstance.setOption(option)
    }

    // 加载评分数据
    const loadScoresData = async () => {
      try {
        loading.value = true
        const res = await getScores({
          page: currentPage.value,
          page_size: pageSize.value,
          keyword: searchKeyword.value,
          assistant_type: assistantFilter.value
        })
        if (res.success && res.data) {
          scoresList.value = res.data.items
          total.value = res.data.pagination.total
        }
      } catch (error) {
        ElMessage.error('加载评分数据失败')
      } finally {
        loading.value = false
      }
    }

    // 加载统计数据
    const loadStatisticsData = async () => {
      try {
        const res = await getScoreStatistics()
        if (res.success && res.data) {
          // 更新雷达图数据
          if (res.data.radar_chart && modelChartInstance) {
            updateRadarChart(res.data.radar_chart)
          }
          // 更新分布图数据
          if (res.data.distribution_chart && scoreDistChartInstance) {
            updateDistributionChart(res.data.distribution_chart)
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    // 更新雷达图
    const updateRadarChart = (chartData) => {
      if (!modelChartInstance) return
      
      const option = {
        title: {
          text: 'AI模型性能对比',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `${params.name}: ${params.value}`
          }
        },
        legend: {
          data: chartData.legend
        },
        radar: {
          indicator: chartData.indicators
        },
        series: [{
            type: 'radar',
            data: chartData.data.map((item, index) => ({
            ...item,
              itemStyle: { 
              color: ['#FF6B6B', '#4ECDC4', '#45B7D1'][index]
            }
            }))
        }]
      }
      modelChartInstance.setOption(option)
    }

    // 更新分布图
    const updateDistributionChart = (chartData) => {
      if (!scoreDistChartInstance) return
      
      const option = {
        title: {
          text: '评分分布统计',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: chartData.legend
        },
        xAxis: {
          type: 'category',
          data: chartData.categories
        },
        yAxis: {
          type: 'value'
        },
        series: chartData.series
      }
      scoreDistChartInstance.setOption(option)
    }

    // 工具函数
    const getModelName = (type) => {
      const names = {
        'our_ai': '原始模型',
        'doubao': '豆包模型',
        'xiaotian': '小天模型'
      }
      return names[type] || type
    }

    const getModelTagType = (type) => {
      const types = {
        'our_ai': '',
        'doubao': 'success',
        'xiaotian': 'warning'
      }
      return types[type] || ''
    }

    const getScoreTagType = (score) => {
      if (score >= 8) return 'success'
      if (score >= 6) return 'warning'
      return 'danger'
    }

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString()
    }

    // 刷新模型图表
    const refreshModelChart = () => {
      loadStatisticsData()
    }

    // 分页处理
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadScoresData()
    }

    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadScoresData()
    }

    // 图表自适应
    const resizeCharts = () => {
      if (modelChartInstance) {
        modelChartInstance.resize()
      }
      if (scoreDistChartInstance) {
        scoreDistChartInstance.resize()
      }
    }

    // 监听搜索变化
    watch([searchKeyword, assistantFilter], () => {
      if (searchTimer) {
        clearTimeout(searchTimer)
      }
      searchTimer = setTimeout(() => {
        currentPage.value = 1
        loadScoresData()
      }, 500)
    })

    // 组件挂载
    onMounted(async () => {
      await nextTick()
      
      // 初始化图表
      initModelChart()
      initScoreDistChart()
      
      // 加载数据
      await loadScoresData()
      await loadStatisticsData()
      
      // 监听窗口大小变化
      window.addEventListener('resize', resizeCharts)
    })

    return {
      loading,
      modelChart,
      scoreDistChart,
      searchKeyword,
      assistantFilter,
      currentPage,
      pageSize,
      total,
      scoresList,
      getModelName,
      getModelTagType,
      getScoreTagType,
      formatTime,
      refreshModelChart,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script> 

<style lang="scss" scoped>
.scores {
  .page-header {
    margin-bottom: 20px;
    
    h1 {
      margin: 0;
      color: #2c3e50;
      font-size: 24px;
      font-weight: bold;
    }
    
    .page-description {
      margin: 8px 0 0 0;
      color: #7f8c8d;
      font-size: 14px;
    }
  }

  .charts-row {
    margin-bottom: 20px;
  }

  .table-row {
    margin-bottom: 20px;
  }

  .chart-card, .table-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header-actions {
      display: flex;
      align-items: center;
    }
  }

  .pagination-wrapper {
    margin-top: 20px;
    text-align: center;
  }
  }
</style> 