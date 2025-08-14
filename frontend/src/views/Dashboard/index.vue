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
            <!-- 统计逻辑：按数据入库时间(created_at)筛选，与监控大屏保持一致 -->
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
        <el-card class="stat-card" shadow="hover" :body-style="{ height: '100%', display: 'flex', flexDirection: 'column' }">
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

      <!-- 实时数据监控 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>实时数据监控</span>
              <el-button type="primary" size="small" @click="refreshSystemData">刷新</el-button>
            </div>
          </template>
          <div class="real-time-monitor">
            <!-- 数据更新状态 -->
            <div class="monitor-section">
              <h4>数据更新状态</h4>
              <div class="status-items">
                <div class="status-item">
                  <div class="status-icon">
                    <el-icon :color="dataUpdateStatus.color"><Clock /></el-icon>
                  </div>
                  <div class="status-info">
                    <div class="status-label">最后更新</div>
                    <div class="status-value">{{ dataUpdateStatus.lastUpdate }}</div>
                  </div>
                </div>
                <div class="status-item">
                  <div class="status-icon">
                    <el-icon :color="syncStatus.color"><Refresh /></el-icon>
                  </div>
                  <div class="status-info">
                    <div class="status-label">同步状态</div>
                    <div class="status-value">{{ syncStatus.text }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 处理队列状态 -->
            <div class="monitor-section">
              <h4>处理队列</h4>
              <div class="queue-progress">
                <div class="queue-item">
                  <span>分类待处理</span>
                  <el-progress :percentage="queueStatus.classify" :status="queueStatus.classify === 100 ? 'success' : ''" />
                </div>
                <div class="queue-item">
                  <span>答案生成中</span>
                  <el-progress :percentage="queueStatus.generate" :status="queueStatus.generate === 100 ? 'success' : ''" />
                </div>
                <div class="queue-item">
                  <span>竞品横评中</span>
                  <el-progress :percentage="queueStatus.score" :status="queueStatus.score === 100 ? 'success' : ''" />
                </div>
              </div>
            </div>

            <!-- 今日处理量 -->
            <div class="monitor-section">
              <h4>今日处理量</h4>
              <div class="daily-stats">
                <div class="daily-item">
                  <span class="daily-number">{{ dailyStats.questions }}</span>
                  <span class="daily-label">新增问题</span>
                </div>
                <div class="daily-item">
                  <span class="daily-number">{{ dailyStats.answers }}</span>
                  <span class="daily-label">生成答案</span>
                </div>
                <div class="daily-item">
                  <span class="daily-number">{{ dailyStats.scores }}</span>
                  <span class="daily-label">完成横评</span>
                </div>
              </div>
            </div>
          </div>
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
import {
  Refresh,
  ChatDotRound,
  Flag,
  Star,
  ArrowUp,
  ArrowDown,
  Clock,
  CircleCheck,
  CircleClose,
  Document,
  TrendCharts
} from '@element-plus/icons-vue'
import { getStats, getSystemHealth, getSyncStatus } from '@/api/dashboard'
import { ElMessage } from 'element-plus'

export default {
  name: 'Dashboard',
  components: {
    Refresh,
    ChatDotRound,
    Flag,
    Star,
    ArrowUp,
    ArrowDown,
    Clock,
    CircleCheck,
    CircleClose,
    Document,
    TrendCharts
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const trendChart = ref(null)
    const timeRange = ref('all')  // 默认选择总计
    
    // 实时监控数据
    const dataUpdateStatus = ref({
      lastUpdate: '2分钟前',
      color: '#67C23A'
    })
    
    const syncStatus = ref({
      text: '正常运行',
      color: '#67C23A'
    })
    
    const queueStatus = ref({
      classify: 85,
      generate: 92,
      score: 78
    })
    
    const dailyStats = ref({
      questions: 156,
      answers: 312,
      scores: 89
    })

    // 统计数据 - 统计逻辑已与监控大屏保持一致
    const stats = ref([
      {
        key: 'total_questions',
        label: '总问题数',
        value: 0,
        icon: ChatDotRound,
        color: '#409EFF',
        trend: null,
        description: '指定时间范围内同步入库的问题总数'
      },
      {
        key: 'classified_questions',
        label: '已分类问题数',
        value: 0,
        icon: Flag,
        color: '#67C23A',
        trend: null,
        description: '指定时间范围内已完成自动分类的问题数量'
      },
      {
        key: 'ai_answers_completion',
        label: '竞品跑测完成度',
        value: 0,
        icon: Document,
        color: '#E6A23C',
        trend: null,
        description: '指定时间范围内已分类问题的豆包/小天竞品答案数'
      },
      {
        key: 'scored_answers',
        label: '竞品横评数',
        value: 0,
        icon: Star,
        color: '#F56C6C',
        trend: null,
        description: '指定时间范围内完成横评的问题数（三个AI都已评分）'
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
        name: '横评API',
        url: 'localhost:8005',
        status: 'healthy',
        lastCheck: '刚刚'
      }
    ])

    // 图表实例
    let trendChartInstance = null

    // 获取时间范围参数 - 与监控大屏保持一致的时间计算方式
    const getTimeRangeParams = () => {
      const now = new Date()
      const params = { time_range: timeRange.value }

      switch (timeRange.value) {
        case 'today':
          const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
          params.start_time = today.toISOString()
          params.end_time = now.toISOString()
          break
        case 'week':
          // 本周：从本周一0点开始到现在（与监控大屏一致）
          const weekStart = new Date(now)
          weekStart.setDate(now.getDate() - now.getDay() + 1) // 设置为本周一
          weekStart.setHours(0, 0, 0, 0) // 设置为0点
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

          // 竞品跑测完成度 - 显示实际生成的竞品答案数（与大屏展示系统流程一致）
          let actualCompetitorAnswers = data.summary?.competitor_answers?.total || 0

          // 更新统计数据
          stats.value[0].value = data.summary?.total_questions || 0
          stats.value[1].value = classifiedCount
          stats.value[2].value = actualCompetitorAnswers  // 直接显示实际答案数，不再计算百分比
          stats.value[3].value = data.summary?.scored_answers || 0  // 现在是完成横评的问题数
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      } finally {
        loading.value = false
      }
    }

    // 加载趋势数据（独立于时间筛选，固定显示最近7天）
    const loadTrendData = async () => {
      try {
        // 固定获取最近7天的趋势数据，不受时间筛选影响
        const res = await getStats({ time_range: 'week' })
        
        if (res.success && res.data) {
          const data = res.data
          
          // 更新趋势数据
          if (data.trend_data && data.trend_data.length > 0) {
            trendData.value.dates = data.trend_data.map(item => item.date)
            trendData.value.questions = data.trend_data.map(item => item.questions)
            trendData.value.classifications = data.trend_data.map(item => item.classifications)
            trendData.value.scores = data.trend_data.map(item => item.scores)
            
            // 重新初始化图表
            if (trendChartInstance) {
              initTrendChart()
            }
          }
        }
      } catch (error) {
        console.error('加载趋势数据失败:', error)
        ElMessage.error('加载趋势数据失败')
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

    // 趋势数据
    const trendData = ref({
      dates: [],
      questions: [],
      classifications: [],
      scores: []
    })

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
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: function(params) {
            let result = params[0].axisValue + '<br/>'
            params.forEach(param => {
              result += param.marker + param.seriesName + ': ' + param.value + '<br/>'
            })
            return result
          }
        },
        legend: {
          data: ['问题数', '分类数', '横评数'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: trendData.value.dates,
          axisLine: {
            lineStyle: {
              color: '#ddd'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            formatter: function(value) {
              // 格式化日期显示为 MM-DD 格式
              const date = new Date(value)
              return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            lineStyle: {
              color: '#f5f5f5'
            }
          }
        },
        series: [
          {
            name: '问题数',
            type: 'line',
            data: trendData.value.questions,
            smooth: false,
            symbol: 'circle',
            symbolSize: 6,
            z: 3,
            lineStyle: {
              width: 3,
              color: '#409EFF'
            },
            itemStyle: { 
              color: '#409EFF',
              borderWidth: 2,
              borderColor: '#fff'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                  { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
                ]
              }
            }
          },
          {
            name: '分类数',
            type: 'line',
            data: trendData.value.classifications,
            smooth: false,
            symbol: 'circle',
            symbolSize: 6,
            z: 2,
            lineStyle: {
              width: 3,
              color: '#67C23A'
            },
            itemStyle: { 
              color: '#67C23A',
              borderWidth: 2,
              borderColor: '#fff'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
                  { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
                ]
              }
            }
          },
          {
            name: '横评数',
            type: 'line',
            data: trendData.value.scores,
            smooth: false,
            symbol: 'circle',
            symbolSize: 6,
            z: 1,
            lineStyle: {
              width: 3,
              color: '#E6A23C'
            },
            itemStyle: { 
              color: '#E6A23C',
              borderWidth: 2,
              borderColor: '#fff'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
                  { offset: 1, color: 'rgba(230, 162, 60, 0.1)' }
                ]
              }
            }
          }
        ]
      }
      
      trendChartInstance.setOption(option)
    }

    // 刷新趋势数据
    const refreshTrends = () => {
      loadTrendData()
      ElMessage.success('趋势数据已刷新')
    }

    // 刷新系统数据
    const refreshSystemData = () => {
      // 模拟数据更新
      dataUpdateStatus.value.lastUpdate = '刚刚'
      dataUpdateStatus.value.color = '#67C23A'
      syncStatus.value.text = '正常运行'
      syncStatus.value.color = '#67C23A'
      queueStatus.value.classify = 85
      queueStatus.value.generate = 92
      queueStatus.value.score = 78
      dailyStats.value.questions = 156
      dailyStats.value.answers = 312
      dailyStats.value.scores = 89
      ElMessage.success('系统数据已刷新')
    }

    // 响应式调整图表
    const resizeCharts = () => {
      if (trendChartInstance) {
        trendChartInstance.resize()
      }
    }

    // 组件挂载
    onMounted(async () => {
      await loadStats()
      await loadTrendData() // 加载趋势数据
      
      await nextTick()
      initTrendChart()
      
      window.addEventListener('resize', resizeCharts)
    })

    return {
      loading,
      timeRange,
      stats,
      systemStatus,
      services,
      trendChart,
      trendData,
      dataUpdateStatus,
      syncStatus,
      queueStatus,
      dailyStats,
      handleTimeRangeChange,
      refreshStats,
      refreshTrends,
      refreshSystemData
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
    
    .el-col {
      margin-bottom: 20px;
    }
  }

  .stat-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    
    .stat-content {
      display: flex;
      align-items: flex-start;
      margin-bottom: 10px;
      flex: 1;

      .stat-icon {
        width: 50px;
        height: 50px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        color: white;
        flex-shrink: 0;
      }

      .stat-info {
        flex: 1;
        min-width: 0;

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
          line-height: 1.2;
          margin-bottom: 4px;
          word-break: break-all;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
          margin-bottom: 4px;
          font-weight: 500;
        }

        .stat-description {
          font-size: 12px;
          color: #c0c4cc;
          line-height: 1.3;
          word-break: break-all;
        }
      }
    }

    .stat-trend {
      display: flex;
      align-items: center;
      font-size: 12px;
      margin-top: auto;

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

  .real-time-monitor {
    padding: 10px 0;

    .monitor-section {
      margin-bottom: 25px;

      h4 {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        margin: 0 0 12px 0;
        border-left: 3px solid #409EFF;
        padding-left: 8px;
      }

      .status-items {
        display: flex;
        gap: 20px;
      }

      .status-item {
        display: flex;
        align-items: center;
        gap: 10px;

        .status-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background-color: #f5f7fa;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .status-info {
          .status-label {
            font-size: 12px;
            color: #909399;
            margin-bottom: 2px;
          }

          .status-value {
            font-size: 14px;
            font-weight: 500;
            color: #303133;
          }
        }
      }

      .queue-progress {
        .queue-item {
          display: flex;
          align-items: center;
          margin-bottom: 8px;

          span {
            width: 80px;
            font-size: 12px;
            color: #606266;
          }

          .el-progress {
            flex: 1;
            margin-left: 10px;
          }
        }
      }

      .daily-stats {
        display: flex;
        justify-content: space-around;

        .daily-item {
          text-align: center;

          .daily-number {
            display: block;
            font-size: 20px;
            font-weight: bold;
            color: #409EFF;
            margin-bottom: 4px;
          }

          .daily-label {
            font-size: 12px;
            color: #909399;
          }
        }
      }
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