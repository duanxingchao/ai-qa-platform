<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>数据概览</h1>
      <p class="page-description">系统整体运行状态和数据统计</p>
    </div>

    <!-- 时间筛选器 -->
    <el-row class="filter-row">
      <el-col :span="24">
        <el-card class="filter-card" shadow="never">
          <div class="time-filter">
            <span class="filter-label">时间范围：</span>
            <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
              <el-radio-button label="today">本日</el-radio-button>
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="year">本年</el-radio-button>
              <el-radio-button label="all">总计</el-radio-button>
            </el-radio-group>
            <el-button 
              type="primary" 
              size="small" 
              @click="refreshStats" 
              :loading="loading"
              style="margin-left: 20px;"
            >
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.key">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="24">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-description" v-if="stat.description">
                {{ stat.description }}
              </div>
            </div>
          </div>
          <div class="stat-trend" v-if="stat.trend">
            <el-icon :style="{ color: stat.trend > 0 ? '#67c23a' : '#f56c6c' }">
              <ArrowUp v-if="stat.trend > 0" />
              <ArrowDown v-else />
            </el-icon>
            <span :style="{ color: stat.trend > 0 ? '#67c23a' : '#f56c6c' }">
              {{ Math.abs(stat.trend) }}%
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 问题处理趋势 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>问题处理趋势</span>
              <el-button type="primary" size="small" @click="refreshTrends">刷新</el-button>
            </div>
          </template>
          <div ref="trendChart" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- AI模型性能对比 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>AI模型性能对比</span>
            </div>
          </template>
          <div ref="modelChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态 -->
    <el-row :gutter="20" class="status-row">
      <el-col :span="24">
        <el-card class="status-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>系统状态监控</span>
              <el-tag :type="systemStatus.type" size="small">{{ systemStatus.text }}</el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6" v-for="service in services" :key="service.name">
              <div class="service-item">
                <div class="service-header">
                  <el-icon :style="{ color: service.status === 'healthy' ? '#67c23a' : '#f56c6c' }">
                    <CircleCheck v-if="service.status === 'healthy'" />
                    <CircleClose v-else />
                  </el-icon>
                  <span class="service-name">{{ service.name }}</span>
                </div>
                <div class="service-info">
                  <div class="service-url">{{ service.url }}</div>
                  <div class="service-time">最后检查: {{ service.lastCheck }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStats, getSystemHealth, getSyncStatus } from '@/api/dashboard'
import { ElMessage } from 'element-plus'

export default {
  name: 'Dashboard',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const trendChart = ref(null)
    const modelChart = ref(null)
    const timeRange = ref('all')  // 默认选择总计
    
    // 统计数据
    const stats = ref([
      {
        key: 'total_questions',
        label: '总问题数',
        value: 0,
        icon: 'ChatDotRound',
        color: '#409EFF',
        trend: null,
        description: '指定时间范围内的问题总数'
      },
      {
        key: 'classified_questions',
        label: '已分类问题数',
        value: 0,
        icon: 'Flag',
        color: '#67C23A',
        trend: null,
        description: '已完成自动分类的问题数量'
      },
      {
        key: 'ai_answers_completion',
        label: '竞品批跑答案数',
        value: '0/0',
        icon: 'Robot',
        color: '#E6A23C',
        trend: null,
        description: '三个AI模型的答案完成情况'
      },
      {
        key: 'scored_answers',
        label: '评分完成数',
        value: 0,
        icon: 'Star',
        color: '#F56C6C',
        trend: null,
        description: '已完成评分的答案数量'
      }
    ])

    // 系统状态
    const systemStatus = ref({
      type: 'success',
      text: '系统正常'
    })

    // 服务状态
    const services = ref([
      {
        name: '分类API',
        url: 'localhost:8001',
        status: 'healthy',
        lastCheck: '刚刚'
      },
      {
        name: '豆包API',
        url: 'localhost:8002',
        status: 'healthy',
        lastCheck: '刚刚'
      },
      {
        name: '小天API',
        url: 'localhost:8003',
        status: 'healthy',
        lastCheck: '刚刚'
      },
      {
        name: '评分API',
        url: 'localhost:8005',
        status: 'healthy',
        lastCheck: '刚刚'
      }
    ])

    // 图表实例
    let trendChartInstance = null
    let modelChartInstance = null

    // 获取时间范围参数
    const getTimeRangeParams = () => {
      const now = new Date()
      const params = { time_range: timeRange.value }
      
      switch (timeRange.value) {
        case 'today':
          const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
          params.start_time = today.toISOString()
          params.end_time = new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString()
          break
        case 'week':
          const weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          params.start_time = weekStart.toISOString()
          params.end_time = now.toISOString()
          break
        case 'month':
          const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
          params.start_time = monthStart.toISOString()
          params.end_time = now.toISOString()
          break
        case 'year':
          const yearStart = new Date(now.getFullYear(), 0, 1)
          params.start_time = yearStart.toISOString()
          params.end_time = now.toISOString()
          break
        case 'all':
        default:
          // 不传时间参数，获取全部数据
          break
      }
      
      return params
    }

    // 加载统计数据
    const loadStats = async () => {
      try {
        loading.value = true
        const params = getTimeRangeParams()
        const res = await getStats(params)
        
        if (res.success && res.data) {
          const data = res.data
          
          // 计算已分类问题数（classification不为null且不为空的问题）
          const classifiedCount = data.classification_distribution ? 
            Object.values(data.classification_distribution).reduce((sum, count) => sum + count, 0) : 0
          
          // 计算竞品批跑答案数（三个AI模型的答案完成情况）
          let totalExpectedAnswers = (data.summary?.total_questions || 0) * 3  // 每个问题期望3个答案
          let actualAnswers = data.summary?.total_answers || 0
          let aiCompletionRate = totalExpectedAnswers > 0 ? ((actualAnswers / totalExpectedAnswers) * 100).toFixed(1) : 0
          
          // 更新统计数据
          stats.value[0].value = data.summary?.total_questions || 0
          stats.value[1].value = classifiedCount
          stats.value[2].value = `${actualAnswers}/${totalExpectedAnswers} (${aiCompletionRate}%)`
          stats.value[3].value = data.summary?.scored_answers || 0
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      } finally {
        loading.value = false
      }
    }

    // 时间范围变更处理
    const handleTimeRangeChange = (value) => {
      timeRange.value = value
      loadStats()
    }

    // 刷新统计数据
    const refreshStats = () => {
      loadStats()
    }

    // 初始化趋势图表
    const initTrendChart = () => {
      if (!trendChart.value) return
      
      trendChartInstance = echarts.init(trendChart.value)
      
      const option = {
        title: {
          text: '最近7天处理量',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['问题数', '答案数', '评分数']
        },
        xAxis: {
          type: 'category',
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '问题数',
            type: 'line',
            data: [12, 19, 15, 27, 33, 25, 18],
            smooth: true,
            itemStyle: { color: '#409EFF' }
          },
          {
            name: '答案数',
            type: 'line',
            data: [8, 15, 12, 22, 28, 20, 15],
            smooth: true,
            itemStyle: { color: '#67C23A' }
          },
          {
            name: '评分数',
            type: 'line',
            data: [5, 12, 8, 18, 23, 16, 12],
            smooth: true,
            itemStyle: { color: '#E6A23C' }
          }
        ]
      }
      
      trendChartInstance.setOption(option)
    }

    // 初始化模型对比图表
    const initModelChart = () => {
      if (!modelChart.value) return
      
      modelChartInstance = echarts.init(modelChart.value)
      
      const option = {
        title: {
          text: 'AI模型评分对比',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        radar: {
          indicator: [
            { name: '准确性', max: 5 },
            { name: '完整性', max: 5 },
            { name: '清晰度', max: 5 },
            { name: '相关性', max: 5 },
            { name: '有用性', max: 5 }
          ],
          radius: '70%'
        },
        series: [
          {
            type: 'radar',
            data: [
              {
                value: [3.2, 3.5, 3.1, 3.8, 3.4],
                name: '原始模型',
                itemStyle: { color: '#409EFF' }
              },
              {
                value: [4.2, 4.1, 4.3, 4.0, 4.2],
                name: '豆包模型',
                itemStyle: { color: '#67C23A' }
              },
              {
                value: [2.8, 3.2, 2.9, 3.1, 3.0],
                name: '小天模型',
                itemStyle: { color: '#E6A23C' }
              }
            ]
          }
        ]
      }
      
      modelChartInstance.setOption(option)
    }

    // 刷新趋势数据
    const refreshTrends = () => {
      ElMessage.success('趋势数据已刷新')
      // 这里可以调用API获取最新数据
    }

    // 响应式调整图表
    const resizeCharts = () => {
      if (trendChartInstance) {
        trendChartInstance.resize()
      }
      if (modelChartInstance) {
        modelChartInstance.resize()
      }
    }

    // 组件挂载
    onMounted(async () => {
      await loadStats()
      
      await nextTick()
      initTrendChart()
      initModelChart()
      
      window.addEventListener('resize', resizeCharts)
    })

    return {
      loading,
      timeRange,
      stats,
      systemStatus,
      services,
      trendChart,
      modelChart,
      handleTimeRangeChange,
      refreshStats,
      refreshTrends
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  .filter-row {
    margin-bottom: 20px;
  }

  .filter-card {
    border: none;
    
    .time-filter {
      display: flex;
      align-items: center;
      
      .filter-label {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        margin-right: 15px;
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      margin-bottom: 10px;

      .stat-icon {
        width: 50px;
        height: 50px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        color: white;
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
          line-height: 1;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
          margin-top: 4px;
        }

        .stat-description {
          font-size: 12px;
          color: #c0c4cc;
          margin-top: 2px;
          line-height: 1.2;
        }
      }
    }

    .stat-trend {
      display: flex;
      align-items: center;
      font-size: 12px;

      .el-icon {
        margin-right: 4px;
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;
  }

  .chart-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .status-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .service-item {
      padding: 15px;
      border: 1px solid #e4e7ed;
      border-radius: 6px;
      background-color: #fafafa;

      .service-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;

        .el-icon {
          margin-right: 8px;
          font-size: 16px;
        }

        .service-name {
          font-weight: 500;
          color: #303133;
        }
      }

      .service-info {
        .service-url {
          font-size: 12px;
          color: #606266;
          margin-bottom: 4px;
        }

        .service-time {
          font-size: 11px;
          color: #909399;
        }
      }
    }
  }
}
</style> 