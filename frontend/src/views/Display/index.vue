<template>
  <div class="display-screen" :class="{ 'fullscreen': isFullscreen }">
    <!-- 顶部标题栏 -->
    <header class="display-header">
      <div class="header-left">
        <div class="logo">🏛️</div>
        <span class="lab-name">智能实验室</span>
      </div>
      <div class="header-center">
        <h1>AI自动化测试中心实时监控大屏</h1>
      </div>
      <div class="header-right">
        <div class="current-time">{{ currentTime }}</div>
        <div class="status-indicator" :class="systemStatus">
          <span class="dot"></span>
          {{ systemStatusText }}
        </div>
        <button class="fullscreen-btn" @click="toggleFullscreen">
          <i :class="isFullscreen ? 'el-icon-copy-document' : 'el-icon-full-screen'"></i>
        </button>
      </div>
    </header>

    <!-- 核心指标横条 -->
    <section class="metrics-bar">
      <div class="metric-item" v-for="metric in coreMetrics" :key="metric.key">
        <div class="metric-icon">{{ metric.icon }}</div>
        <div class="metric-content">
          <div class="metric-value">
            <span class="number" ref="metricNumbers">
              {{ metric.weeklyValue !== null ? `${metric.value}/${metric.weeklyValue}` : metric.value }}
            </span>
            <span class="unit">{{ metric.unit }}</span>
          </div>
          <div class="metric-label">{{ metric.label }}</div>
        </div>
        <div class="metric-trend" :class="metric.trend">
          <i :class="getTrendIcon(metric.trend)"></i>
        </div>
      </div>
    </section>

    <!-- 主要内容区域 -->
    <main class="display-main">
      <!-- 左侧面板 -->
      <section class="left-panel">
        <!-- 近一周处理趋势 -->
        <div class="chart-card trend-compact">
          <h3 class="card-title">📈 近一周处理趋势</h3>
          <div ref="trendChart" class="chart-container compact-chart" style="margin: -5px -10px;"></div>
        </div>

        <!-- 热词分析 -->
        <div class="word-cloud-card">
          <WordCloudChart :time-range="'week'" :auto-refresh="true" />
        </div>
      </section>

      <!-- 系统流程面板 -->
      <section class="center-panel flow-panel">
        <!-- 数据处理流程图 -->
        <div class="chart-card process-flow">
          <h3 class="card-title">📊 系统流程（本周处理情况）</h3>
          <div class="process-stages compact-flow">
            <div class="pipeline-container">
              <!-- 第一个流程项 -->
              <div class="stage-item" :class="{ 'active': processFlow[0]?.rate > 50 }">
                <div class="stage-icon">{{ processFlow[0]?.icon }}</div>
              <div class="stage-info">
                  <div class="stage-name">{{ processFlow[0]?.name }}</div>
                  <div class="stage-count">{{ processFlow[0]?.count }}</div>
                  <div class="stage-rate">{{ processFlow[0]?.rate }}%</div>
                  <div class="stage-status" :class="getStatusClass(processFlow[0]?.status)">
                    <span class="status-indicator"></span>
                    <span class="status-text">{{ getStatusText(processFlow[0]?.status) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 第一个箭头 -->
              <div class="pipeline-arrow">
                <span class="simple-arrow">→</span>
              </div>
              
              <!-- 第二个流程项 -->
              <div class="stage-item" :class="{ 'active': processFlow[1]?.rate > 50 }">
                <div class="stage-icon">{{ processFlow[1]?.icon }}</div>
                <div class="stage-info">
                  <div class="stage-name">{{ processFlow[1]?.name }}</div>
                  <div class="stage-count">{{ processFlow[1]?.count }}</div>
                  <div class="stage-rate">{{ processFlow[1]?.rate }}%</div>
                  <div class="stage-status" :class="getStatusClass(processFlow[1]?.status)">
                    <span class="status-indicator"></span>
                    <span class="status-text">{{ getStatusText(processFlow[1]?.status) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 第二个箭头 -->
              <div class="pipeline-arrow">
                <span class="simple-arrow">→</span>
              </div>
              
              <!-- 第三个流程项 -->
              <div class="stage-item" :class="{ 'active': processFlow[2]?.rate > 50 }">
                <div class="stage-icon">{{ processFlow[2]?.icon }}</div>
                <div class="stage-info">
                  <div class="stage-name">{{ processFlow[2]?.name }}</div>
                  <div class="stage-count">{{ processFlow[2]?.count }}</div>
                  <div class="stage-rate">{{ processFlow[2]?.rate }}%</div>
                  <div class="stage-status" :class="getStatusClass(processFlow[2]?.status)">
                    <span class="status-indicator"></span>
                    <span class="status-text">{{ getStatusText(processFlow[2]?.status) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 第三个箭头 -->
              <div class="pipeline-arrow">
                <span class="simple-arrow">→</span>
              </div>
              
              <!-- 第四个流程项 -->
              <div class="stage-item" :class="{ 'active': processFlow[3]?.rate > 50 }">
                <div class="stage-icon">{{ processFlow[3]?.icon }}</div>
                <div class="stage-info">
                  <div class="stage-name">{{ processFlow[3]?.name }}</div>
                  <div class="stage-count">{{ processFlow[3]?.count }}</div>
                  <div class="stage-rate">{{ processFlow[3]?.rate }}%</div>
                  <div class="stage-status" :class="getStatusClass(processFlow[3]?.status)">
                    <span class="status-indicator"></span>
                    <span class="status-text">{{ getStatusText(processFlow[3]?.status) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 第四个箭头 -->
              <div class="pipeline-arrow">
                <span class="simple-arrow">→</span>
              </div>
              
              <!-- 第五个流程项 -->
              <div class="stage-item" :class="{ 'active': processFlow[4]?.rate > 50 }">
                <div class="stage-icon">{{ processFlow[4]?.icon }}</div>
                <div class="stage-info">
                  <div class="stage-name">{{ processFlow[4]?.name }}</div>
                  <div class="stage-count">{{ processFlow[4]?.count }}</div>
                  <div class="stage-rate">{{ processFlow[4]?.rate }}%</div>
                  <div class="stage-status" :class="getStatusClass(processFlow[4]?.status)">
                    <span class="status-indicator"></span>
                    <span class="status-text">{{ getStatusText(processFlow[4]?.status) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>
      
      <!-- AI分类评分对比面板 -->
      <section class="center-panel feature-panel">
        <!-- AI分类评分对比卡片 -->
        <div class="chart-card ai-category-scores">
          <h3 class="card-title">🤖 AI分类评分对比</h3>
          <div class="chart-container" ref="aiCategoryChart"></div>
        </div>
      </section>

      <!-- 右侧分析区域 -->
      <section class="right-panel">
        <!-- badcase 分析及优化模块 -->
        <div class="badcase-analysis-module">
          <BigScreenBadcase />
        </div>

        <!-- 热门问题分类 -->
        <div class="chart-card">
          <h3 class="card-title">🔥 热门问题分类</h3>
          <div class="category-summary">
            <span class="total-count">总计: {{ categoryTotalCount }}个问题</span>
            <span class="time-range">{{ categoryTimeRange }}</span>
          </div>
          <div ref="categoryChart" class="chart-container category-chart"></div>
        </div>
      </section>
    </main>

    <!-- 底部实时数据流 -->
    <footer class="realtime-footer">
      <div class="stream-header">
        <span class="stream-title">🔄 实时数据流</span>
        <span class="stream-time">{{ lastUpdate }}</span>
      </div>
      <div class="stream-content">
        <!-- 第一排数据流 -->
        <div class="stream-row">
          <div class="stream-items stream-items-1" ref="streamItems1">
            <div
              v-for="(event, index) in realtimeEventsRow1"
              :key="'row1-' + index + '-' + event.time + event.message"
              class="stream-item"
              :class="event.type"
            >
              <span class="event-time">{{ event.time }}</span>
              <span class="event-icon">{{ event.icon }}</span>
              <span class="event-message">{{ event.message }}</span>
            </div>
          </div>
        </div>

        <!-- 第二排数据流 -->
        <div class="stream-row">
          <div class="stream-items stream-items-2" ref="streamItems2">
            <div
              v-for="(event, index) in realtimeEventsRow2"
              :key="'row2-' + index + '-' + event.time + event.message"
              class="stream-item"
              :class="event.type"
            >
              <span class="event-time">{{ event.time }}</span>
              <span class="event-icon">{{ event.icon }}</span>
              <span class="event-message">{{ event.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </footer>

    <!-- 粒子背景 -->
    <div class="particles-bg" ref="particlesBg"></div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getDisplayDashboard } from '@/api/display'
import { getAiCategoryScores } from '@/api/display'
import BigScreenBadcase from '@/components/BigScreenBadcase.vue'
import WordCloudChart from '@/components/WordCloudChart.vue'

export default {
  name: 'Display',
  components: {
    BigScreenBadcase,
    WordCloudChart
  },
  setup() {
    // 响应式数据
    const isFullscreen = ref(false)
    const currentTime = ref('')
    const lastUpdate = ref('')
    const systemStatus = ref('online')
    const healthScore = ref(95)
    
    // 图表DOM refs
    const trendChart = ref(null)
    const categoryChart = ref(null)
    const aiCategoryChart = ref(null)

    // 图表实例
    let trendChartInstance = null
    let healthGaugeInstance = null
    let categoryChartInstance = null
    let aiCategoryChartInstance = null
    
    // 更新定时器
    let updateTimer = null
    let timeTimer = null
    
    // 数据状态
    const coreMetrics = ref([])
    const processFlow = ref([])
    const trendWeek = ref([])
    const hotCategories = ref([])
    const realtimeEvents = ref([])
    const realtimeEventsRow1 = ref([])
    const realtimeEventsRow2 = ref([])
    const aiCategoryScores = ref([])

    // 分类数据
    const categoryTotalCount = ref(0)
    const categoryTimeRange = ref('近一周')
    
    // 系统状态文本映射
    const systemStatusText = ref('系统正常')
    
    // 初始化时间显示
    const updateCurrentTime = () => {
      const now = new Date()
      currentTime.value = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    // 获取趋势图标
    const getTrendIcon = (trend) => {
      const iconMap = {
        'up': 'el-icon-top',
        'down': 'el-icon-bottom',
        'stable': 'el-icon-minus'
      }
      return iconMap[trend] || 'el-icon-minus'
    }

    // 获取状态样式类
    const getStatusClass = (status) => {
      const classMap = {
        '空闲': 'status-idle',
        '进行中': 'status-running',
        '异常': 'status-error'
      }
      return classMap[status] || 'status-idle'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const textMap = {
        'online': '正常',
        'offline': '离线',
        'idle': '空闲',
        'warning': '警告',
        'error': '错误',
        '空闲': '空闲',
        '进行中': '进行中',
        '异常': '异常'
      }
      return textMap[status] || status || '空闲'
    }
    
    // 全屏切换
    const toggleFullscreen = () => {
      if (!isFullscreen.value) {
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen()
        }
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen()
        }
      }
      isFullscreen.value = !isFullscreen.value
    }
    
    // 初始化趋势图表
    const initTrendChart = () => {
      if (!trendChart.value) return
      
      trendChartInstance = echarts.init(trendChart.value)
      
      // 检查是否是紧凑模式（根据容器父元素类名判断）
      const isCompact = trendChart.value.closest('.trend-compact') !== null
      
      const option = {
        backgroundColor: 'transparent',
        grid: {
          left: isCompact ? '3%' : '3%',
          right: isCompact ? '3%' : '4%',
          bottom: isCompact ? '5%' : '3%',
          top: isCompact ? '18%' : '15%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.9)',
          borderColor: '#00d4ff',
          borderWidth: 1,
          textStyle: { 
            color: '#ffffff',
            fontSize: isCompact ? 10 : 12
          }
        },
        legend: {
          data: ['同步&清洗数', '分类数量', '评分数量'],
          textStyle: {
            color: '#8892b0',
            fontSize: isCompact ? 10 : 12
          },
          top: isCompact ? '0' : '5%',
          itemWidth: isCompact ? 12 : 25,
          itemHeight: isCompact ? 8 : 14,
          itemGap: isCompact ? 10 : 20
        },
        xAxis: {
          type: 'category',
          data: trendWeek.value.map(item => item.time),
          axisLine: { lineStyle: { color: '#2d3748' } },
          axisTick: { show: false },
          axisLabel: { 
            color: '#8892b0',
            fontSize: isCompact ? 9 : 12,
            rotate: isCompact ? 30 : 0,
            margin: isCompact ? 6 : 8
          }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { 
            color: '#8892b0',
            fontSize: isCompact ? 10 : 12
          },
          splitLine: { lineStyle: { color: '#2d3748' } }
        },
        series: [
          {
            name: '同步&清洗数',
            type: 'line',
            smooth: true,
            data: trendWeek.value.map(item => item.questions),
            lineStyle: { color: '#00d4ff', width: isCompact ? 2 : 3 },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
                { offset: 1, color: 'rgba(0, 212, 255, 0.01)' }
              ])
            }
          },
          {
            name: '分类数量',
            type: 'line',
            smooth: true,
            data: trendWeek.value.map(item => item.classifications),
            lineStyle: { color: '#00ff88', width: isCompact ? 2 : 3 },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(0, 255, 136, 0.3)' },
                { offset: 1, color: 'rgba(0, 255, 136, 0.01)' }
              ])
            }
          },
          {
            name: '评分数量',
            type: 'line',
            smooth: true,
            data: trendWeek.value.map(item => item.scores),
            lineStyle: { color: '#ff8800', width: isCompact ? 2 : 3 },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(255, 136, 0, 0.3)' },
                { offset: 1, color: 'rgba(255, 136, 0, 0.01)' }
              ])
            }
          }
        ]
      }
      
      trendChartInstance.setOption(option)
    }
    

    
    // 初始化健康度仪表盘
    const initHealthGauge = () => {
      const chartDom = document.querySelector('[ref="healthGauge"]')
      if (!chartDom) return
      
      healthGaugeInstance = echarts.init(chartDom)
      
      const option = {
        backgroundColor: 'transparent',
        series: [
          {
            type: 'gauge',
            startAngle: 90,
            endAngle: -270,
            pointer: { show: false },
            progress: {
              show: true,
              overlap: false,
              roundCap: true,
              clip: false,
              itemStyle: {
                borderWidth: 1,
                borderColor: '#00d4ff'
              }
            },
            axisLine: {
              lineStyle: {
                width: 15,
                color: [[1, '#2d3748']]
              }
            },
            splitLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: false },
            data: [
              {
                value: healthScore.value,
                itemStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#00ff88' },
                    { offset: 1, color: '#00d4ff' }
                  ])
                }
              }
            ],
            title: { show: false },
            detail: { show: false }
          }
        ]
      }
      
      healthGaugeInstance.setOption(option)
    }
    
    // 初始化分类饼图
    const initCategoryChart = () => {
      if (!categoryChart.value) return
      
      categoryChartInstance = echarts.init(categoryChart.value)
      
      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#00d4ff',
          borderWidth: 1,
          textStyle: { color: '#ffffff' },
          formatter: function(params) {
            return `<div style="padding: 5px;">
              <div style="color: #00d4ff; font-weight: bold; margin-bottom: 5px;">${params.name}</div>
              <div>数量: <span style="color: #00ff88;">${params.value}个</span></div>
              <div>占比: <span style="color: #ff8800;">${params.percent}%</span></div>
            </div>`
          }
        },
        legend: {
          orient: 'vertical',
          right: '10',
          top: 'center',
          textStyle: {
            color: '#8892b0',
            fontSize: 12
          },
          itemWidth: 10,
          itemHeight: 10,
          formatter: function(name) {
            return name.length > 6 ? name.substring(0, 6) + '...' : name
          }
        },
        series: [
          {
            name: '问题分类',
            type: 'pie',
            radius: ['30%', '60%'],
            center: ['40%', '50%'],
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              position: 'outside',
              color: '#8892b0',
              fontSize: 10,
              formatter: function(params) {
                if (params.percent < 5) return '' // 小于5%不显示标签
                return `${params.name}\n${params.percent}%`
              }
            },
            labelLine: {
              show: true,
              lineStyle: {
                color: '#8892b0'
              }
            },
            itemStyle: {
              borderColor: '#1a1f36',
              borderWidth: 2
            }
          }
        ],
        color: [
          '#00d4ff', '#00ff88', '#ff8800', '#ff4757', '#3742fa',
          '#70a1ff', '#5352ed', '#ff3838', '#ff9ff3', '#54a0ff',
          '#5f27cd', '#00d2d3', '#ff9f43', '#10ac84', '#ee5a24',
          '#0984e3'
        ]
      }
      
      categoryChartInstance.setOption(option)
    }

    // 初始化AI分类评分图表
    const initAiCategoryChart = () => {
      if (!aiCategoryChart.value) return

      aiCategoryChartInstance = echarts.init(aiCategoryChart.value)

      // 初始化空图表，等待数据加载
      const option = {
        backgroundColor: 'transparent',
        grid: [
          {
            left: '5%',
            right: '5%',
            top: '5%',
            height: '40%',
            containLabel: true
          },
          {
            left: '5%',
            right: '5%',
            top: '55%',
            height: '40%',
            containLabel: true
          }
        ],
        legend: {
          data: ['YOYO', '豆包', '小天'],
          top: '2%',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
          itemWidth: 15,
          itemHeight: 10
        },
        xAxis: [
          {
            type: 'category',
            data: [],
            gridIndex: 0,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10,
              rotate: 45
            },
            axisLine: {
              lineStyle: { color: '#444' }
            }
          },
          {
            type: 'category',
            data: [],
            gridIndex: 1,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10,
              rotate: 45
            },
            axisLine: {
              lineStyle: { color: '#444' }
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            gridIndex: 0,
            min: 0,
            max: 5,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10
            },
            axisLine: {
              lineStyle: { color: '#444' }
            },
            splitLine: {
              lineStyle: { color: '#333' }
            }
          },
          {
            type: 'value',
            gridIndex: 1,
            min: 0,
            max: 5,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10
            },
            axisLine: {
              lineStyle: { color: '#444' }
            },
            splitLine: {
              lineStyle: { color: '#333' }
            }
          }
        ],
        series: [],
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#00d4ff',
          textStyle: {
            color: '#ffffff'
          }
        }
      }

      aiCategoryChartInstance.setOption(option)
    }

    // 更新AI分类评分图表
    const updateAiCategoryChart = () => {
      if (!aiCategoryChartInstance || !aiCategoryScores.value.length) return

      // 分两排显示，每排8个分类
      const firstRowData = aiCategoryScores.value.slice(0, 8)
      const secondRowData = aiCategoryScores.value.slice(8, 16)

      console.log('更新AI分类评分图表:', {
        totalCategories: aiCategoryScores.value.length,
        firstRowCount: firstRowData.length,
        secondRowCount: secondRowData.length,
        firstRowCategories: firstRowData.map(item => item.category),
        secondRowCategories: secondRowData.map(item => item.category)
      })

      const option = {
        backgroundColor: 'transparent',
        grid: [
          {
            left: '5%',
            right: '5%',
            top: '8%',
            height: '38%',
            containLabel: true
          },
          {
            left: '5%',
            right: '5%',
            top: '52%',
            height: '38%',
            containLabel: true
          }
        ],
        legend: {
          data: ['YOYO', '豆包', '小天'],
          top: '2%',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          },
          itemWidth: 15,
          itemHeight: 10
        },
        xAxis: [
          {
            type: 'category',
            data: firstRowData.map(item => item.category),
            gridIndex: 0,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10,
              rotate: 45,
              interval: 0  // 强制显示所有标签
            },
            axisLine: {
              lineStyle: { color: '#444' }
            }
          },
          {
            type: 'category',
            data: secondRowData.map(item => item.category),
            gridIndex: 1,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10,
              rotate: 45,
              interval: 0  // 强制显示所有标签
            },
            axisLine: {
              lineStyle: { color: '#444' }
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            gridIndex: 0,
            min: 0,
            max: 5,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10
            },
            axisLine: {
              lineStyle: { color: '#444' }
            },
            splitLine: {
              lineStyle: { color: '#333' }
            }
          },
          {
            type: 'value',
            gridIndex: 1,
            min: 0,
            max: 5,
            axisLabel: {
              color: '#ffffff',
              fontSize: 10
            },
            axisLine: {
              lineStyle: { color: '#444' }
            },
            splitLine: {
              lineStyle: { color: '#333' }
            }
          }
        ],
        series: [
          // 第一排 - YOYO
          {
            name: 'YOYO',
            type: 'bar',
            xAxisIndex: 0,
            yAxisIndex: 0,
            data: firstRowData.map(item => item.YOYO || 0),
            itemStyle: {
              color: '#00d4ff'
            },
            barWidth: '20%'
          },
          // 第一排 - 豆包
          {
            name: '豆包',
            type: 'bar',
            xAxisIndex: 0,
            yAxisIndex: 0,
            data: firstRowData.map(item => item.豆包 || 0),
            itemStyle: {
              color: '#00ff88'
            },
            barWidth: '20%'
          },
          // 第一排 - 小天
          {
            name: '小天',
            type: 'bar',
            xAxisIndex: 0,
            yAxisIndex: 0,
            data: firstRowData.map(item => item.小天 || 0),
            itemStyle: {
              color: '#ff6b6b'
            },
            barWidth: '20%'
          },
          // 第二排 - YOYO (使用不同的名称避免冲突)
          {
            name: 'YOYO_2',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: secondRowData.map(item => item.YOYO || 0),
            itemStyle: {
              color: '#00d4ff'
            },
            barWidth: '20%',
            legendHoverLink: false  // 不与图例交互
          },
          // 第二排 - 豆包 (使用不同的名称避免冲突)
          {
            name: '豆包_2',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: secondRowData.map(item => item.豆包 || 0),
            itemStyle: {
              color: '#00ff88'
            },
            barWidth: '20%',
            legendHoverLink: false  // 不与图例交互
          },
          // 第二排 - 小天 (使用不同的名称避免冲突)
          {
            name: '小天_2',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: secondRowData.map(item => item.小天 || 0),
            itemStyle: {
              color: '#ff6b6b'
            },
            barWidth: '20%',
            legendHoverLink: false  // 不与图例交互
          }
        ],
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#00d4ff',
          textStyle: {
            color: '#ffffff'
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>'
            params.forEach(param => {
              result += param.seriesName + ': ' + param.value + '分<br/>'
            })
            return result
          }
        }
      }

      aiCategoryChartInstance.setOption(option, true)  // 第二个参数为true表示不合并，完全替换

      // 强制重新调整图表大小
      setTimeout(() => {
        if (aiCategoryChartInstance) {
          aiCategoryChartInstance.resize()
        }
      }, 50)
    }

    // 更新图表数据
    const updateCharts = (data) => {
      // 更新趋势图
      if (trendChartInstance && data.trends_24h) {
        trendWeek.value = data.trends_24h.map(item => ({
          time: item.time,
          questions: item.questions,
          classifications: item.classifications,
          scores: item.scores
        }))
        const option = trendChartInstance.getOption()
        option.xAxis[0].data = trendWeek.value.map(item => item.time)
        option.series[0].data = trendWeek.value.map(item => item.questions)
        option.series[1].data = trendWeek.value.map(item => item.classifications)
        option.series[2].data = trendWeek.value.map(item => item.scores)
        trendChartInstance.setOption(option)
      }
      

      
      // 更新健康度
      if (healthGaugeInstance && data.system_status) {
        healthScore.value = data.system_status.health_score
        const option = healthGaugeInstance.getOption()
        option.series[0].data[0].value = healthScore.value
        healthGaugeInstance.setOption(option)
      }
      
      // 更新分类饼图
      if (categoryChartInstance && data.hot_categories) {
        const categories = data.hot_categories.categories || data.hot_categories
        const chartData = categories.map(item => ({
          name: item.name,
          value: item.count,
          percentage: item.percentage
        }))
        
        const option = categoryChartInstance.getOption()
        option.series[0].data = chartData
        option.legend[0].data = chartData.map(item => item.name)
        categoryChartInstance.setOption(option)
        
        // 更新总计数据
        categoryTotalCount.value = data.hot_categories.total_count || chartData.reduce((sum, item) => sum + item.value, 0)
        categoryTimeRange.value = data.hot_categories.time_range || '近一周'
      }
    }
    
    // 初始化默认数据
    const initDefaultData = () => {
      // 设置默认核心指标
      coreMetrics.value = [
        {
          key: 'total_data_count',
          icon: '📊',
          value: '加载中',
          weeklyValue: null, // 累计数据量不需要显示第二个数值
          unit: '次',
          label: '累计数据量',
          trend: 'up'
        },
        {
          key: 'weekly_new_data_count',
          icon: '📈',
          value: '加载中',
          weeklyValue: null, // 周新增数据量不需要显示第二个数值
          unit: '次',
          label: '周新增数据量',
          trend: 'up'
        },
        {
          key: 'weekly_classified_count',
          icon: '⚡',
          value: '加载中',
          weeklyValue: null, // 周抽样跑测量只显示本周数据
          unit: '次',
          label: '周抽样跑测量',
          trend: 'up'
        },
        {
          key: 'platform_visits',
          icon: '👥',
          value: '加载中',
          weeklyValue: '...',
          unit: '次',
          label: '平台访问量（累计/本周）',
          trend: 'up'
        }
      ]
      
      // 设置默认处理流程
      processFlow.value = [
        { name: '同步&清洗', count: 0, rate: 0, icon: '📊' },
        { name: 'AI垂域分类', count: 0, rate: 0, icon: '🏷️' },
        { name: '竞品跑测', count: 0, rate: 0, icon: '🤖' },
        { name: 'AI竞品横评', count: 0, rate: 0, icon: '⭐' },
        { name: '人工复核', count: 0, rate: 0, icon: '✅' }
      ]
      


      
      // 设置默认分类
      hotCategories.value = [
        { name: '技术问题', count: 0, percentage: 0 },
        { name: '功能建议', count: 0, percentage: 0 },
        { name: '产品使用', count: 0, percentage: 0 }
      ]
      
      // 设置默认事件
      realtimeEvents.value = [
        {
          time: new Date().toLocaleTimeString(),
          type: 'system',
          message: '系统正在初始化...',
          icon: '🔄'
        }
      ]
      splitEventsToRows(realtimeEvents.value)

      trendWeek.value = [
        { time: '一周前', questions: 0, classifications: 0, scores: 0 },
        { time: '6天前', questions: 0, classifications: 0, scores: 0 },
        { time: '5天前', questions: 0, classifications: 0, scores: 0 },
        { time: '4天前', questions: 0, classifications: 0, scores: 0 },
        { time: '3天前', questions: 0, classifications: 0, scores: 0 },
        { time: '2天前', questions: 0, classifications: 0, scores: 0 },
        { time: '昨天', questions: 0, classifications: 0, scores: 0 },
        { time: '今天', questions: 0, classifications: 0, scores: 0 }
      ]
    }

    // 加载AI分类评分数据
    const loadAiCategoryScores = async () => {
      try {
        const response = await getAiCategoryScores()
        if (response && response.success && response.data) {
          const realData = response.data.chart_data || []
          console.log('AI分类评分数据加载成功:', {
            dataSource: response.data.data_source,
            timeRange: response.data.time_range,
            categoriesCount: realData.length,
            categories: realData.map(item => item.category)
          })

          if (realData.length > 0) {
            aiCategoryScores.value = realData
            console.log('使用真实数据，共', realData.length, '个分类')
            console.log('分类详情:', realData.map(item => ({
              category: item.category,
              YOYO: item.YOYO,
              豆包: item.豆包,
              小天: item.小天
            })))
          } else {
            console.warn('API返回空数据，使用模拟数据')
            aiCategoryScores.value = generateMockAiCategoryData()
          }

          // 更新AI分类评分图表
          setTimeout(() => {
            updateAiCategoryChart()
          }, 100)
        } else {
          console.warn('API响应格式异常，使用模拟数据')
          aiCategoryScores.value = generateMockAiCategoryData()
          setTimeout(() => {
            updateAiCategoryChart()
          }, 100)
        }
      } catch (error) {
        console.error('加载AI分类评分数据失败:', error)
        console.warn('API调用失败，使用模拟数据')
        // 使用模拟数据
        aiCategoryScores.value = generateMockAiCategoryData()
        setTimeout(() => {
          updateAiCategoryChart()
        }, 100)
      }
    }

    // 生成模拟AI分类评分数据（与后端16个分类保持一致）
    const generateMockAiCategoryData = () => {
      const categories = [
        '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
        '其他', '工程问题', '科学问题', '教育问题', '经济问题',
        '账户管理', '系统优化', '安全设置', '数据分析',
        '用户体验', '性能优化'
      ]

      return categories.map(category => ({
        category,
        YOYO: +(Math.random() * 1.5 + 3.5).toFixed(2), // 3.5-5.0
        豆包: +(Math.random() * 1.2 + 3.2).toFixed(2), // 3.2-4.4
        小天: +(Math.random() * 1.0 + 3.0).toFixed(2)  // 3.0-4.0
      }))
    }

    // 加载大屏数据
    const loadDashboardData = async () => {
      console.log('开始加载大屏数据...')
      try {
        const response = await getDisplayDashboard()
        console.log('API响应:', response)
        
        if (response && response.success && response.data) {
          const data = response.data
          console.log('数据解析成功:', data)
          
          // 更新核心指标
          if (data.core_metrics) {
            coreMetrics.value = [
              {
                key: 'total_data_count',
                icon: '📊',
                value: data.core_metrics.total_data_count || data.core_metrics.total_sync_count || 0,
                weeklyValue: null, // 累计数据量不需要显示第二个数值
                unit: '次',
                label: '累计数据量',
                trend: 'up'
              },
              {
                key: 'weekly_new_data_count',
                icon: '📈',
                value: data.core_metrics.weekly_new_data_count || data.core_metrics.weekly_sync_count || 0,
                weeklyValue: null, // 周新增数据量不需要显示第二个数值
                unit: '次',
                label: '周新增数据量',
                trend: 'up'
              },
              {
                key: 'weekly_classified_count',
                icon: '⚡',
                value: data.core_metrics.weekly_classified_count || data.core_metrics.weekly_scored_count || 0,
                weeklyValue: null, // 周抽样跑测量只显示本周数据
                unit: '次',
                label: '周抽样跑测量',
                trend: 'up'
              },
              {
                key: 'platform_visits',
                icon: '👥',
                value: data.core_metrics.platform_visits || data.core_metrics.total_visits || 0,
                weeklyValue: data.core_metrics.weekly_visits || 0,
                unit: '次',
                label: '平台访问量（累计/本周）',
                trend: 'up'
              }
            ]
          }
          
          // 更新其他数据
          if (data.process_flow && data.process_flow.stages) {
            processFlow.value = data.process_flow.stages
          }

          if (data.hot_categories) {
            hotCategories.value = data.hot_categories.categories || data.hot_categories
            categoryTotalCount.value = data.hot_categories.total_count || 0
            categoryTimeRange.value = data.hot_categories.time_range || '近一周'
          }
          if (data.realtime_events) {
            realtimeEvents.value = data.realtime_events
            splitEventsToRows(data.realtime_events)
          }
          if (data.trends_24h) {
            trendWeek.value = data.trends_24h.map(item => ({
              time: item.time,
              questions: item.questions,
              classifications: item.classifications,
              scores: item.scores
            }))
          }
          
          // 更新图表
          updateCharts(data)
          
          lastUpdate.value = new Date().toLocaleTimeString()
          console.log('数据更新完成')
        } else {
          console.warn('API响应格式错误:', response)
          throw new Error('API响应格式错误')
        }
      } catch (error) {
        console.error('加载大屏数据失败:', error)
        
        // API失败时使用模拟数据
        coreMetrics.value = [
          {
            key: 'total_data_count',
            icon: '📊',
            value: 1024,
            weeklyValue: null, // 累计数据量不需要显示第二个数值
            unit: '次',
            label: '累计数据量',
            trend: 'up'
          },
          {
            key: 'weekly_new_data_count',
            icon: '📈',
            value: 156,
            weeklyValue: null, // 周新增数据量不需要显示第二个数值
            unit: '次',
            label: '周新增数据量',
            trend: 'up'
          },
          {
            key: 'weekly_classified_count',
            icon: '⚡',
            value: 42,
            weeklyValue: null, // 周抽样跑测量只显示本周数据
            unit: '次',
            label: '周抽样跑测量',
            trend: 'up'
          },
          {
            key: 'platform_visits',
            icon: '👥',
            value: 512,
            weeklyValue: 67,
            unit: '次',
            label: '平台访问量（累计/本周）',
            trend: 'up'
          }
        ]
        
        processFlow.value = [
          { name: '同步&清洗', count: 573, rate: 100, icon: '📊', status: '异常' },
          { name: 'AI垂域分类', count: 371, rate: 64.7, icon: '🏷️', status: '进行中' },
          { name: '竞品跑测', count: 1599, rate: 279.1, icon: '🤖', status: '空闲' },
          { name: 'AI竞品横评', count: 990, rate: 61.9, icon: '⭐', status: '进行中' },
          { name: '人工复核', count: 0, rate: 0, icon: '✅', status: '进行中' }
        ]
        
        realtimeEvents.value = [
          {
            time: new Date().toLocaleTimeString(),
            type: 'system',
            message: '数据加载失败，显示模拟数据',
            icon: '⚠️'
          }
        ]
        splitEventsToRows(realtimeEvents.value)
        
        lastUpdate.value = new Date().toLocaleTimeString()
      }
    }

    // 将事件数据分配到两排
    const splitEventsToRows = (events) => {
      if (!events || events.length === 0) {
        realtimeEventsRow1.value = []
        realtimeEventsRow2.value = []
        return
      }

      // 复制事件数组以创建更多数据流动效果
      const duplicatedEvents = [...events, ...events, ...events]

      // 将事件分配到两排，奇数索引到第一排，偶数索引到第二排
      realtimeEventsRow1.value = duplicatedEvents.filter((_, index) => index % 2 === 0)
      realtimeEventsRow2.value = duplicatedEvents.filter((_, index) => index % 2 === 1)
    }

    // 初始化粒子背景
    const initParticles = () => {
      // 这里可以添加粒子动画效果
      // 简化版本暂时省略
    }
    
    // 图表自适应
    const resizeCharts = () => {
      if (trendChartInstance) trendChartInstance.resize()
      if (healthGaugeInstance) healthGaugeInstance.resize()
      if (categoryChartInstance) categoryChartInstance.resize()
      if (aiCategoryChartInstance) aiCategoryChartInstance.resize()
    }
    
    // 组件挂载
    onMounted(async () => {
      await nextTick()
      
      // 先初始化默认数据，显示"加载中"状态
      initDefaultData()
      
      // 初始化时间
      updateCurrentTime()
      timeTimer = setInterval(updateCurrentTime, 1000)
      
      // 初始化图表
      setTimeout(() => {
        initTrendChart()
        initHealthGauge()
        initCategoryChart()
        initAiCategoryChart()
      }, 100)
      
      // 延迟加载数据，让用户先看到界面
      setTimeout(async () => {
        await loadDashboardData()
        await loadAiCategoryScores()
      }, 500)
      
      // 设置定时更新
      updateTimer = setInterval(() => {
        loadDashboardData()
      }, 30000) // 30秒更新一次
      
      // 初始化粒子背景
      initParticles()
      
      // 监听窗口大小变化
      window.addEventListener('resize', resizeCharts)
    })
    
    // 组件卸载
    onUnmounted(() => {
      if (updateTimer) clearInterval(updateTimer)
      if (timeTimer) clearInterval(timeTimer)
      window.removeEventListener('resize', resizeCharts)
      
      if (trendChartInstance) trendChartInstance.dispose()
      if (healthGaugeInstance) healthGaugeInstance.dispose()
      if (categoryChartInstance) categoryChartInstance.dispose()
      if (aiCategoryChartInstance) aiCategoryChartInstance.dispose()
    })
    
    return {
      isFullscreen,
      currentTime,
      lastUpdate,
      systemStatus,
      systemStatusText,
      healthScore,
      coreMetrics,
      processFlow,
      hotCategories,
      realtimeEvents,
      realtimeEventsRow1,
      realtimeEventsRow2,
      categoryTotalCount,
      categoryTimeRange,
      trendChart,
      categoryChart,
      aiCategoryChart,
      getTrendIcon,
      getStatusText,
      getStatusClass,
      toggleFullscreen
    }
  }
}
</script>

<style lang="scss" scoped>
// 确保没有溢出的CSS重置
* {
  box-sizing: border-box;
}

.display-screen {
  min-height: 100vh;
  max-width: 100vw;
  background: linear-gradient(135deg, #0a1628 0%, #112A43 30%, #1B4A73 100%);
  color: #ffffff;
  font-family: 'Microsoft YaHei', sans-serif;
  position: relative;
  overflow-x: hidden;
  margin: 0;
  padding: 0;
  
  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 9999;
  }
}

// 顶部标题栏
.display-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  height: 80px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;
    flex: 1;
    
    .logo {
      font-size: 32px;
    }
    
    .lab-name {
      font-size: 14px;
      color: #8892b0;
    }
  }
  
  .header-center {
    flex: 2;
    display: flex;
    justify-content: center;
    align-items: center;
    
    h1 {
      margin: 0;
      font-size: 32px;
      font-weight: bold;
      background: linear-gradient(45deg, #00d4ff, #00ff88);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      text-align: center;
      text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
      letter-spacing: 2px;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 30px;
    flex: 1;
    
    .current-time {
      font-size: 18px;
      font-weight: bold;
      color: #00d4ff;
    }
    
    .status-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 20px;
      background: rgba(0, 0, 0, 0.3);
      
      .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00ff88;
        animation: pulse 2s infinite;
      }
      
      &.online .dot { background: #00ff88; }
      &.warning .dot { background: #ff8800; }
      &.error .dot { background: #ff4444; }
    }
    
    .fullscreen-btn {
      background: transparent;
      border: 1px solid #00d4ff;
      color: #00d4ff;
      padding: 8px 12px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: #00d4ff;
        color: #0f1419;
      }
    }
  }
}

// 核心指标横条
.metrics-bar {
  display: flex;
  justify-content: space-around;
  padding: 30px 0;
  background: rgba(0, 0, 0, 0.2);
  margin: 20px 40px 0 40px;
  border-radius: 12px;
  
  .metric-item {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .metric-icon {
      font-size: 32px;
    }
    
    .metric-content {
      .metric-value {
        display: flex;
        align-items: baseline;
        gap: 4px;

        .number {
          font-size: 24px;
          font-weight: bold;
          color: #00d4ff;
        }

        .unit {
          font-size: 14px;
          color: #8892b0;
        }
      }

      .metric-label {
        font-size: 12px;
        color: #8892b0;
        margin-top: 4px;
      }
    }
    
    .metric-trend {
      font-size: 20px;
      
      &.up { color: #00ff88; }
      &.down { color: #ff4444; }
      &.stable { color: #8892b0; }
    }
  }
}

// 主要内容区域
.display-main {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;  /* 三等分 */
  grid-template-rows: minmax(320px, auto) 1fr;  /* 第一行固定高度，第二行填充剩余空间 */
  gap: 25px;
  padding: 30px 40px;
  height: calc(100vh - 350px);
  max-width: 100vw;
  overflow: hidden;
}

// 卡片通用样式
.chart-card, .status-card, .word-cloud-card, .placeholder-card {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  overflow: hidden;
  min-width: 0;
  height: 100%;  /* 确保所有卡片高度一致 */
  display: flex;
  flex-direction: column;
  
  .card-title {
    margin: 0 0 20px 0;
    font-size: 18px;
    color: #00d4ff;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    padding-bottom: 10px;
    flex-shrink: 0;  /* 防止标题被压缩 */
  }
}

// 预留区域样式
.placeholder-card, .future-feature {
  .placeholder-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: auto;  /* 自动高度 */
    flex: 1;
    
    .placeholder-icon {
      font-size: 48px;
      margin-bottom: 20px;
      opacity: 0.8;
    }
    
    .placeholder-text {
      font-size: 16px;
      color: #8892b0;
      text-align: center;
      margin-bottom: 15px;
    }
    
          .feature-coming-soon {
        font-size: 18px;
        color: #00d4ff;
        font-weight: bold;
        margin-top: 15px;
        border-top: 1px dashed rgba(0, 212, 255, 0.3);
        padding-top: 15px;
        width: 80%;
        text-align: center;
      }
  }
}

// AI分类评分图表样式
.ai-category-scores {
  height: 100%;   /* 填充整个容器高度 */
  margin-top: 0;  /* 移除上边距 */

  .card-title {
    margin-bottom: 15px;  /* 减小标题下方间距 */
    color: #ffffff;
    font-size: 16px;
    font-weight: bold;
  }

  .chart-container {
    height: calc(100% - 50px);  /* 减去标题高度 */
    width: 100%;
    min-height: 400px;  /* 增加最小高度以容纳两排分类 */
  }
}

// 左侧和右侧面板
.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
  max-width: 100%;
  height: 100%;  /* 确保面板高度一致 */
  align-items: stretch; /* 子元素拉伸填满容器宽度 */
}

// 左侧面板定位
.left-panel {
  grid-column: 1;
  grid-row: 1 / span 2; // 跨越两行
}

// 右侧面板定位
.right-panel {
  grid-column: 3;
  grid-row: 1 / span 2; // 跨越两行
}

// 中央面板
.center-panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
  max-width: 100%;
  padding: 0 5px;
  
  // 系统流程面板
  &.flow-panel {
    grid-column: 2;     // 放在第二列
    grid-row: 1;        // 放在第一行
    height: 100%;       // 填充容器高度
    margin-bottom: 0;   // 移除底部外边距
    align-items: stretch; // 子元素拉伸填满容器宽度
  }
  
  // 功能开发区面板
  &.feature-panel {
    grid-column: 2;     // 放在第二列
    grid-row: 2;        // 放在第二行
    height: 100%;       // 填充容器高度
    margin-top: 0;      // 移除顶部外边距
    align-items: stretch; // 子元素拉伸填满容器宽度
  }
}

// 紧凑趋势图样式
.trend-compact {
  padding: 15px;
  flex: 1;  /* 允许图表占用可用空间 */
  
  .card-title {
    margin-bottom: 10px;
    font-size: 16px;
  }
  
  .compact-chart {
    height: 100% !important;  /* 填充可用空间 */
    width: 100%;
    min-height: 220px;  /* 设置最小高度 */
    
    // 确保图表在小容器中清晰显示
    canvas {
      max-width: 100%;
      max-height: 100%;
    }
  }
}

// 处理流程图样式
.process-flow {
  padding-bottom: 15px;  // 底部内边距
  height: 100%;          // 填充容器高度
  min-height: 320px;     // 最小高度
  display: flex;         // 使用弹性布局
  flex-direction: column;// 垂直排列
  justify-content: space-between; // 内容均匀分布
}

// 处理流程区域紧凑化
.process-stages.compact-flow {
  padding: 20px 0;
  flex: 1; /* 填充可用空间 */
  
  .pipeline-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 100%;
  padding: 10px 0;
  }
  
  .stage-item {
    padding: 15px 10px;
    min-width: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: rgba(0, 30, 60, 0.3);
    border-radius: 8px;
    border: 1px solid rgba(0, 212, 255, 0.3);
    transition: all 0.3s ease;
    flex: 1;
    max-width: 120px;
    
    &.active {
      border-color: rgba(0, 212, 255, 0.5);
      box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
      background: rgba(0, 30, 60, 0.5);
    }
    
    .stage-icon {
      font-size: 24px;
      margin-bottom: 10px;
      width: 45px;
      height: 45px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0, 212, 255, 0.1);
      border-radius: 50%;
      border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .stage-info {
      text-align: center;
      width: 100%;
      
      .stage-name {
        color: #8892b0;
        font-size: 16px;
        margin-bottom: 4px;
        font-weight: 500;
      }

      .stage-count {
        font-size: 20px;
        font-weight: bold;
        color: #00d4ff;
        text-shadow: 0 0 5px rgba(0, 212, 255, 0.5);
      }

      .stage-rate {
        color: #00ff88;
        font-size: 16px;
        margin-top: 2px;
        font-weight: 500;
      }
    }
  }
  
  .pipeline-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 5px;
    
    .simple-arrow {
      font-size: 28px;
      color: #00ff88;
      text-shadow: 0 0 10px rgba(0, 255, 136, 0.8);
      animation: arrowPulse 1.5s infinite;
    margin: 0 5px;
    }
    
    @keyframes arrowPulse {
      0% { opacity: 0.7; }
      50% { opacity: 1; }
      100% { opacity: 0.7; }
    }
  }
}

// 流程状态样式
.stage-status {
  display: flex;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;

  .status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 4px;
    display: inline-block;
  }

  .status-text {
    font-size: 12px;
    font-weight: 500;
  }

  // 空闲状态
  &.status-idle {
    .status-indicator {
      background-color: #00ff88;
      box-shadow: 0 0 6px rgba(0, 255, 136, 0.6);
    }
    .status-text {
      color: #00ff88;
    }
  }

  // 进行中状态
  &.status-running {
    .status-indicator {
      background-color: #00d4ff;
      box-shadow: 0 0 6px rgba(0, 212, 255, 0.6);
      animation: statusPulse 1.5s infinite;
    }
    .status-text {
      color: #00d4ff;
    }
  }

  // 异常状态
  &.status-error {
    .status-indicator {
      background-color: #ff4757;
      box-shadow: 0 0 6px rgba(255, 71, 87, 0.6);
    }
    .status-text {
      color: #ff4757;
    }
  }
}

@keyframes statusPulse {
  0% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
  100% { opacity: 0.7; transform: scale(1); }
}

// 热词分析卡片
.word-cloud-card {
  flex: 1;  /* 允许词云卡片占用可用空间 */
  display: flex;
  flex-direction: column;
  min-height: 300px;  /* 设置最小高度 */
}

// 处理流程图
.process-flow {
  flex: 1;  /* 填充可用空间 */
  display: flex;
  flex-direction: column;
  
  .process-stages {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    flex: 1;  /* 填充可用空间 */
    
    .stage-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 15px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
      min-width: 80px;
      transition: all 0.3s;
      
      &.active {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
      }
      
      .stage-icon {
        font-size: 24px;
        margin-bottom: 8px;
      }
      
      .stage-info {
        text-align: center;
        
        .stage-name {
          font-size: 16px;
          color: #8892b0;
          margin-bottom: 4px;
          font-weight: 500;
        }

        .stage-count {
          font-size: 20px;
          font-weight: bold;
          color: #00d4ff;
        }

        .stage-rate {
          font-size: 16px;
          color: #00ff88;
          font-weight: 500;
        }

        .stage-status {
          display: flex;
          align-items: center;
          margin-top: 4px;
          font-size: 12px;

          .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
            display: inline-block;
          }

          .status-text {
            font-size: 12px;
            font-weight: 500;
          }

          // 空闲状态
          &.status-idle {
            .status-indicator {
              background-color: #00ff88;
              box-shadow: 0 0 6px rgba(0, 255, 136, 0.6);
            }
            .status-text {
              color: #00ff88;
            }
          }

          // 进行中状态
          &.status-running {
            .status-indicator {
              background-color: #00d4ff;
              box-shadow: 0 0 6px rgba(0, 212, 255, 0.6);
              animation: statusPulse 1.5s infinite;
            }
            .status-text {
              color: #00d4ff;
            }
          }

          // 异常状态
          &.status-error {
            .status-indicator {
              background-color: #ff4757;
              box-shadow: 0 0 6px rgba(255, 71, 87, 0.6);
            }
            .status-text {
              color: #ff4757;
            }
          }
        }
      }
      
      .stage-arrow {
        font-size: 20px;
        color: #8892b0;
        margin: 0 10px;
      }
    }
  }
  
  // 添加服务状态列表样式
  .service-list {
    margin-top: auto;    // 自动调整顶部外边距，推到底部
    padding-top: 15px;
    padding-bottom: 15px; // 增加底部内边距
    margin-bottom: 0;     // 移除底部外边距
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    
    .service-item {
      display: flex;
      justify-content: space-between;
      padding: 5px 10px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 4px;
      
      .service-name {
        font-size: 14px;
      }
      
      .service-status {
        font-size: 12px;
        
        &.online { color: #00ff88; }
        &.offline { color: #ff4444; }
        &.warning { color: #ff8800; }
        &.error { color: #ff4444; }
      }
    }
  }
}

// 右侧面板的卡片
.right-panel {
  .placeholder-card, .chart-card, .badcase-analysis-module {
    flex: 1;  /* 右侧两个卡片平分空间 */
  }

  // badcase分析模块样式
  .badcase-analysis-module {
    background: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 0; // 让内部组件自己控制padding
    overflow: hidden;
    min-width: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .placeholder-content {
    height: auto;  /* 自动高度 */
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    
    .placeholder-icon {
      font-size: 48px;
      margin-bottom: 15px;
      opacity: 0.6;
    }
    
    .placeholder-text {
      font-size: 16px;
      color: #8892b0;
      opacity: 0.8;
    }
  }
  
  .chart-container {
    height: auto;  /* 自动高度 */
    flex: 1;
    min-height: 200px;  /* 设置最小高度 */
  }
  
  .category-chart {
    height: auto !important;  /* 自动高度 */
    min-height: 280px;  /* 设置最小高度 */
    width: 100% !important;
    flex: 1;  /* 填充可用空间 */
  }
  
  .category-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 0 10px;
    
    .total-count {
      font-size: 14px;
      color: #00d4ff;
      font-weight: bold;
    }
    
    .time-range {
      font-size: 12px;
      color: #8892b0;
    }
  }
}

// 底部实时数据流
.realtime-footer {
  height: 120px;
  background: rgba(0, 0, 0, 0.4);
  border-top: 1px solid rgba(0, 212, 255, 0.2);
  padding: 15px 40px;

  .stream-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;

    .stream-title {
      font-size: 16px;
      color: #00d4ff;
      font-weight: bold;
    }

    .stream-time {
      font-size: 12px;
      color: #8892b0;
    }
  }

  .stream-content {
    height: 70px;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 5px;

    &::before, &::after {
      content: '';
      position: absolute;
      top: 0;
      height: 100%;
      width: 40px;
      z-index: 2;
      pointer-events: none;
    }

    &::before {
      left: 0;
      background: linear-gradient(to right, rgba(0, 0, 0, 0.4), transparent);
    }

    &::after {
      right: 0;
      background: linear-gradient(to left, rgba(0, 0, 0, 0.4), transparent);
    }

    .stream-row {
      height: 30px;
      overflow: hidden;
      position: relative;

      .stream-items {
        display: flex;
        padding: 0 40px;

        &.stream-items-1 {
          animation: scroll-left 80s linear infinite;
        }

        &.stream-items-2 {
          animation: scroll-left 75s linear infinite;
        }

        .stream-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 0 15px;
          white-space: nowrap;
          margin-right: 15px;
          border-radius: 4px;
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(5px);

          .event-time {
            color: #8892b0;
            font-size: 11px;
          }

          .event-icon {
            font-size: 12px;
          }

          .event-message {
            font-size: 12px;
            color: #ffffff;
          }

          &.question { border-left: 2px solid #00d4ff; }
          &.answer { border-left: 2px solid #00ff88; }
          &.score { border-left: 2px solid #ff8800; }
          &.system { border-left: 2px solid #ff3366; }
        }
      }
    }
  }
}

// 粒子背景
.particles-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
}

// 动画
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes scroll-left {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-200%); }
}

// 响应式设计
@media (max-width: 1920px) {
  .display-main {
    grid-template-columns: 1fr 1fr 1fr;  /* 保持三等分 */
  }
}

@media (max-width: 1440px) {
  .display-main {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    gap: 20px;
  }
  
  .metrics-bar {
    flex-wrap: wrap;
    gap: 20px;
  }
}
</style> 