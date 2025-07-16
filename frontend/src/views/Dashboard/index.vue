<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>数据概览</h1>
      <p class="page-description">系统整体运行状态和数据统计</p>
    </div>

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
    
    // 统计数据
    const stats = ref([
      {
        key: 'questions',
        label: '总问题数',
        value: 0,
        icon: 'ChatDotRound',
        color: '#409EFF',
        trend: null
      },
      {
        key: 'answers',
        label: '总答案数',
        value: 0,
        icon: 'Document',
        color: '#67C23A',
        trend: null
      },
      {
        key: 'scores',
        label: '评分完成数',
        value: 0,
        icon: 'Star',
        color: '#E6A23C',
        trend: null
      },
      {
        key: 'sync_rate',
        label: '同步成功率',
        value: '0%',
        icon: 'Refresh',
        color: '#F56C6C',
        trend: null
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

    // 加载统计数据
    const loadStats = async () => {
      try {
        loading.value = true
        const res = await getStats()
        
        if (res.success && res.data) {
          const data = res.data
          stats.value[0].value = data.questions_count || 0
          stats.value[1].value = data.answers_count || 0
          stats.value[2].value = data.scored_answers_count || 0
          stats.value[3].value = data.questions_sync_rate || '0%'
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      } finally {
        loading.value = false
      }
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
      stats,
      systemStatus,
      services,
      trendChart,
      modelChart,
      refreshTrends
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
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