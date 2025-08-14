<template>
  <div class="word-cloud-container">
    <div class="header">
      <div class="title">
        <i class="icon">🔥</i>
        <span>热词分析</span>
      </div>
      <div class="period">{{ analysisPeriod }}</div>
    </div>
    
    <div class="word-cloud-chart" ref="chartRef"></div>
    
    <div class="stats-info" v-if="statistics">
      <span class="stat-item">
        <i class="stat-icon">📊</i>
        {{ statistics.totalQuestions }} 个问题
      </span>
      <span class="stat-item">
        <i class="stat-icon">🔤</i>
        {{ statistics.uniqueWords }} 个热词
      </span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { getWordCloudData } from '@/api/analysis'

export default {
  name: 'WordCloudChart',
  props: {
    timeRange: {
      type: String,
      default: 'week'
    },
    autoRefresh: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const chartRef = ref(null)
    const chart = ref(null)
    const wordCloudData = ref([])
    const analysisPeriod = ref('')
    const statistics = ref(null)
    const loading = ref(false)
    
    let refreshTimer = null
    
    // 初始化图表
    const initChart = () => {
      if (!chartRef.value) return
      
      chart.value = echarts.init(chartRef.value)
      
      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          show: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          textStyle: {
            color: '#ffffff'
          },
          formatter: function(params) {
            return `${params.name}: ${params.value}次`
          }
        },
        series: [{
          type: 'wordCloud',
          gridSize: 8,
          sizeRange: [12, 48],
          rotationRange: [-45, 45],
          rotationStep: 45,
          shape: 'circle',
          width: '100%',
          height: '100%',
          textStyle: {
            fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
            fontWeight: 'normal',
            color: function() {
              // 渐变色系
              const colors = [
                '#4fc3f7', '#29b6f6', '#03a9f4', '#039be5', '#0288d1',
                '#0277bd', '#01579b', '#00bcd4', '#00acc1', '#0097a7',
                '#00838f', '#006064', '#26a69a', '#4db6ac', '#80cbc4',
                '#b2dfdb', '#e0f2f1', '#ff7043', '#ff5722', '#f4511e'
              ]
              return colors[Math.floor(Math.random() * colors.length)]
            }
          },
          emphasis: {
            focus: 'self',
            textStyle: {
              shadowBlur: 10,
              shadowColor: '#333'
            }
          },
          data: []
        }]
      }
      
      chart.value.setOption(option)
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    }
    
    // 处理窗口大小变化
    const handleResize = () => {
      if (chart.value) {
        chart.value.resize()
      }
    }
    
    // 加载词云数据
    const loadWordCloudData = async () => {
      if (loading.value) return
      
      try {
        loading.value = true
        console.log('开始加载词云数据...')
        
        const response = await getWordCloudData({
          time_range: props.timeRange,
          limit: 40
        })
        
        if (response.success && response.data) {
          wordCloudData.value = response.data.word_cloud || []
          analysisPeriod.value = response.data.analysis_period || ''
          statistics.value = {
            totalQuestions: response.data.total_questions || 0,
            uniqueWords: response.data.unique_words || 0
          }
          
          console.log('词云数据加载成功:', wordCloudData.value.length, '个热词')
          updateChart()
        } else {
          console.error('词云数据加载失败:', response.message)
          loadDefaultData()
        }
      } catch (error) {
        console.error('加载词云数据失败:', error)
        loadDefaultData()
      } finally {
        loading.value = false
      }
    }
    
    // 加载默认数据
    const loadDefaultData = () => {
      console.log('使用默认词云数据')
      wordCloudData.value = [
        {name: '登录问题', value: 156},
        {name: '密码重置', value: 134},
        {name: '系统故障', value: 98},
        {name: '网络连接', value: 87},
        {name: '数据同步', value: 76},
        {name: '权限管理', value: 65},
        {name: '账号异常', value: 54},
        {name: '服务器错误', value: 43},
        {name: 'API接口', value: 38},
        {name: '数据库连接', value: 32},
        {name: '性能优化', value: 28},
        {name: '用户权限', value: 25},
        {name: '系统升级', value: 22},
        {name: '功能测试', value: 19},
        {name: '配置错误', value: 16},
        {name: '界面优化', value: 14},
        {name: '响应超时', value: 12},
        {name: '数据导入', value: 10},
        {name: '备份恢复', value: 8},
        {name: '日志分析', value: 6}
      ]
      analysisPeriod.value = '近一周数据（模拟）'
      statistics.value = {
        totalQuestions: 1234,
        uniqueWords: 456
      }
      updateChart()
    }
    
    // 更新图表
    const updateChart = () => {
      if (!chart.value || !wordCloudData.value.length) return
      
      chart.value.setOption({
        series: [{
          data: wordCloudData.value
        }]
      })
    }
    
    // 设置自动刷新
    const setupAutoRefresh = () => {
      if (props.autoRefresh) {
        refreshTimer = setInterval(() => {
          loadWordCloudData()
        }, 60000) // 每分钟刷新一次
      }
    }
    
    // 清理定时器
    const clearTimer = () => {
      if (refreshTimer) {
        clearInterval(refreshTimer)
        refreshTimer = null
      }
    }
    
    onMounted(async () => {
      await nextTick()
      initChart()
      loadWordCloudData()
      setupAutoRefresh()
    })
    
    onUnmounted(() => {
      clearTimer()
      window.removeEventListener('resize', handleResize)
      if (chart.value) {
        chart.value.dispose()
      }
    })
    
    return {
      chartRef,
      analysisPeriod,
      statistics,
      loading
    }
  }
}
</script>

<style lang="scss" scoped>
.word-cloud-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-shrink: 0;
    
    .title {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;
      
      .icon {
        margin-right: 8px;
        font-size: 18px;
      }
    }
    
    .period {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.7);
    }
  }
  
  .word-cloud-chart {
    flex: 1;
    width: 100%;
    min-height: 200px;
  }
  
  .stats-info {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 8px;
    flex-shrink: 0;
    
    .stat-item {
      display: flex;
      align-items: center;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.8);
      
      .stat-icon {
        margin-right: 4px;
        font-size: 12px;
      }
    }
  }
}

// 响应式适配
@media (max-width: 1366px) {
  .word-cloud-container {
    padding: 12px;
    
    .header {
      margin-bottom: 8px;
      
      .title {
        font-size: 14px;
        
        .icon {
          font-size: 16px;
        }
      }
      
      .period {
        font-size: 10px;
      }
    }
    
    .stats-info {
      gap: 16px;
      margin-top: 6px;
      
      .stat-item {
        font-size: 10px;
        
        .stat-icon {
          font-size: 11px;
        }
      }
    }
  }
}
</style>
