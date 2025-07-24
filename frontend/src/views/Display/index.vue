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
            <span class="number" ref="metricNumbers">{{ metric.value }}</span>
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
      <!-- 中央状态区域（原来的center-panel，现在移到左侧） -->
      <section class="center-panel">
        <!-- 近一周处理趋势 -->
        <div class="chart-card trend-compact">
          <h3 class="card-title">📈 近一周处理趋势</h3>
          <div ref="trendChart" class="chart-container compact-chart" style="margin: -5px -10px;"></div>
        </div>

        <!-- 系统健康度 -->
        <div class="health-card">
          <h3 class="card-title">💚 系统健康度</h3>
          <div class="health-circle">
            <div ref="healthGauge" class="health-gauge"></div>
            <div class="health-score">
              <span class="score-number">{{ healthScore }}</span>
              <span class="score-unit">%</span>
            </div>
          </div>
          <div class="service-list">
            <div 
              v-for="service in services" 
              :key="service.name"
              class="service-item"
            >
              <span class="service-name">{{ service.name }}</span>
              <span class="service-status" :class="service.status">
                {{ getStatusText(service.status) }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 左侧图表区域（原来的left-panel，现在移到中央） -->
      <section class="left-panel">
        <!-- 数据处理流程图 -->
        <div class="chart-card process-flow">
          <h3 class="card-title">📊 系统流程（当日处理情况）</h3>
          <div class="process-stages">
            <div 
              v-for="(stage, index) in processFlow" 
              :key="stage.name"
              class="stage-item"
              :class="{ 'active': stage.rate > 50 }"
            >
              <div class="stage-icon">{{ stage.icon }}</div>
              <div class="stage-info">
                <div class="stage-name">{{ stage.name }}</div>
                <div class="stage-count">{{ stage.count }}</div>
                <div class="stage-rate">{{ stage.rate }}%</div>
              </div>
              <div v-if="index < processFlow.length - 1" class="stage-arrow">→</div>
            </div>
          </div>
        </div>


      </section>

      <!-- 右侧分析区域 -->
      <section class="right-panel">
        <!-- 预留空间，等待后续功能 -->
        <div class="placeholder-card">
          <h3 class="card-title">📊 数据分析模块</h3>
          <div class="placeholder-content">
            <div class="placeholder-icon">📈</div>
            <div class="placeholder-text">此区域预留给数据分析功能</div>
          </div>
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
        <div class="stream-items" ref="streamItems">
          <div 
            v-for="event in realtimeEvents" 
            :key="event.time + event.message"
            class="stream-item"
            :class="event.type"
          >
            <span class="event-time">{{ event.time }}</span>
            <span class="event-icon">{{ event.icon }}</span>
            <span class="event-message">{{ event.message }}</span>
          </div>
        </div>
      </div>
    </footer>

    <!-- 粒子背景 -->
    <div class="particles-bg" ref="particlesBg"></div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getDisplayDashboard, getRealtimeUpdate } from '@/api/display'

export default {
  name: 'Display',
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
    
    // 图表实例
    let trendChartInstance = null
    let healthGaugeInstance = null
    let categoryChartInstance = null
    
    // 更新定时器
    let updateTimer = null
    let timeTimer = null
    
    // 数据状态
    const coreMetrics = ref([])
    const processFlow = ref([])
    const trendWeek = ref([])
    const services = ref([])
    const hotCategories = ref([])
    const realtimeEvents = ref([])
    
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
    
    // 获取状态文本
    const getStatusText = (status) => {
      const textMap = {
        'online': '正常',
        'offline': '离线',
        'idle': '空闲',
        'warning': '警告',
        'error': '错误'
      }
      return textMap[status] || '未知'
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
          data: ['问题数量', '答案数量', '评分数量'],
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
            name: '问题数量',
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
            name: '答案数量',
            type: 'line',
            smooth: true,
            data: trendWeek.value.map(item => item.answers),
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

    // 更新图表数据
    const updateCharts = (data) => {
      // 更新趋势图
      if (trendChartInstance && data.trends_24h) {
        trendWeek.value = data.trends_24h.map(item => ({
          time: item.time,
          questions: item.questions,
          answers: item.answers,
          scores: item.scores
        }))
        const option = trendChartInstance.getOption()
        option.xAxis[0].data = trendWeek.value.map(item => item.time)
        option.series[0].data = trendWeek.value.map(item => item.questions)
        option.series[1].data = trendWeek.value.map(item => item.answers)
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
          key: 'total_sync_count',
          icon: '📊',
          value: '加载中...',
          unit: '',
          label: '累计问题',
          trend: 'up'
        },
        {
          key: 'monthly_sync_count', 
          icon: '📈',
          value: '加载中...',
          unit: '',
          label: '月新增',
          trend: 'up'
        },
        {
          key: 'daily_sync_count',
          icon: '⚡',
          value: '加载中...',
          unit: '',
          label: '日新增',
          trend: 'up'
        },
        {
          key: 'daily_completion_rate',
          icon: '🎯',
          value: '加载中...',
          unit: '',
          label: '日完成度',
          trend: 'stable'
        },
        {
          key: 'daily_visits',
          icon: '👥',
          value: '加载中...',
          unit: '',
          label: '平台访问',
          trend: 'up'
        }
      ]
      
      // 设置默认处理流程
      processFlow.value = [
        { name: '同步&清洗', count: 0, rate: 0, icon: '📊' },
        { name: 'AI垂域分类', count: 0, rate: 0, icon: '🏷️' },
        { name: 'AI竞品跑测', count: 0, rate: 0, icon: '🤖' },
        { name: 'AI答案评测', count: 0, rate: 0, icon: '⭐' },
        { name: '人工复核', count: 0, rate: 0, icon: '✅' }
      ]
      

      
      // 设置默认服务
      services.value = [
        { name: '同步&清洗', status: 'online' },
        { name: 'AI垂域分类', status: 'online' },
        { name: 'AI竞品跑测', status: 'online' },
        { name: 'AI答案评测', status: 'online' }
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

      trendWeek.value = [
        { time: '一周前', questions: 0, answers: 0, scores: 0 },
        { time: '6天前', questions: 0, answers: 0, scores: 0 },
        { time: '5天前', questions: 0, answers: 0, scores: 0 },
        { time: '4天前', questions: 0, answers: 0, scores: 0 },
        { time: '3天前', questions: 0, answers: 0, scores: 0 },
        { time: '2天前', questions: 0, answers: 0, scores: 0 },
        { time: '昨天', questions: 0, answers: 0, scores: 0 },
        { time: '今天', questions: 0, answers: 0, scores: 0 }
      ]
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
                key: 'total_sync_count',
                icon: '📊',
                value: data.core_metrics.total_sync_count || 0,
                unit: '个',
                label: '累计问题',
                trend: 'up'
              },
              {
                key: 'monthly_sync_count',
                icon: '📈',
                value: data.core_metrics.monthly_sync_count || 0,
                unit: '个',
                label: '月新增',
                trend: 'up'
              },
              {
                key: 'daily_sync_count',
                icon: '⚡',
                value: data.core_metrics.daily_sync_count || 0,
                unit: '个',
                label: '日新增',
                trend: 'up'
              },
              {
                key: 'daily_completion_rate',
                icon: '🎯',
                value: data.core_metrics.daily_completion_rate || 0,
                unit: '%',
                label: '日完成度',
                trend: 'stable'
              },
              {
                key: 'daily_visits',
                icon: '👥',
                value: data.core_metrics.daily_visits || '暂无数据',
                unit: '次',
                label: '平台访问',
                trend: 'up'
              }
            ]
          }
          
          // 更新其他数据
          if (data.process_flow && data.process_flow.stages) {
            processFlow.value = data.process_flow.stages
          }
          if (data.system_status) {
            if (data.system_status.services) {
              services.value = data.system_status.services
            }
          }
          if (data.hot_categories) {
            hotCategories.value = data.hot_categories.categories || data.hot_categories
            categoryTotalCount.value = data.hot_categories.total_count || 0
            categoryTimeRange.value = data.hot_categories.time_range || '近一周'
          }
          if (data.realtime_events) {
            realtimeEvents.value = data.realtime_events
          }
          if (data.trends_24h) {
            trendWeek.value = data.trends_24h.map(item => ({
              time: item.time,
              questions: item.questions,
              answers: item.answers,
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
            key: 'total_sync_count',
            icon: '📊',
            value: 1024,
            unit: '个',
            label: '累计问题',
            trend: 'up'
          },
          {
            key: 'monthly_sync_count',
            icon: '📈',
            value: 156,
            unit: '个',
            label: '月新增',
            trend: 'up'
          },
          {
            key: 'daily_sync_count',
            icon: '⚡',
            value: 42,
            unit: '个',
            label: '日新增',
            trend: 'up'
          },
          {
            key: 'daily_completion_rate',
            icon: '🎯',
            value: 85.6,
            unit: '%',
            label: '日完成度',
            trend: 'stable'
          },
          {
            key: 'daily_visits',
            icon: '👥',
            value: '暂无数据',
            unit: '次',
            label: '平台访问',
            trend: 'up'
          }
        ]
        
        processFlow.value = [
          { name: '同步&清洗', count: 1024, rate: 100, icon: '📊' },
          { name: 'AI垂域分类', count: 856, rate: 83.6, icon: '🏷️' },
          { name: 'AI竞品跑测', count: 742, rate: 72.5, icon: '🤖' },
          { name: 'AI答案评测', count: 658, rate: 64.3, icon: '⭐' },
          { name: '人工复核', count: 234, rate: 22.9, icon: '✅' }
        ]
        
        realtimeEvents.value = [
          {
            time: new Date().toLocaleTimeString(),
            type: 'system',
            message: '数据加载失败，显示模拟数据',
            icon: '⚠️'
          }
        ]
        
        lastUpdate.value = new Date().toLocaleTimeString()
      }
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
      }, 100)
      
      // 延迟加载数据，让用户先看到界面
      setTimeout(async () => {
        await loadDashboardData()
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
      services,
      hotCategories,
      realtimeEvents,
      categoryTotalCount,
      categoryTimeRange,
      trendChart,
      categoryChart,
      getTrendIcon,
      getStatusText,
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
          font-size: 36px;
          font-weight: bold;
          color: #00d4ff;
        }
        
        .unit {
          font-size: 16px;
          color: #8892b0;
        }
      }
      
      .metric-label {
        font-size: 14px;
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
  grid-template-columns: 0.75fr 1fr 0.75fr;
  gap: 25px;
  padding: 30px 40px;
  height: calc(100vh - 350px);
  max-width: 100vw;
  overflow: hidden;
}

// 卡片通用样式
.chart-card, .status-card, .health-card, .placeholder-card {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  overflow: hidden;
  min-width: 0;
  
  .card-title {
    margin: 0 0 20px 0;
    font-size: 18px;
    color: #00d4ff;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    padding-bottom: 10px;
  }
}

// 预留区域样式
.placeholder-card {
  .placeholder-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 150px;
    
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
}

// 左侧面板
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
  max-width: 100%;
  
  .process-flow {
    .process-stages {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      
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
            font-size: 12px;
            color: #8892b0;
            margin-bottom: 4px;
          }
          
          .stage-count {
            font-size: 18px;
            font-weight: bold;
            color: #00d4ff;
          }
          
          .stage-rate {
            font-size: 12px;
            color: #00ff88;
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
  
  .chart-container {
    height: 300px;
  }
}

// 中央面板
.center-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-width: 0;
  max-width: 100%;
  padding: 0 5px;
  
  // 紧凑趋势图样式
  .trend-compact {
    padding: 15px;
    
    .card-title {
      margin-bottom: 10px;
      font-size: 16px;
    }
    
    .compact-chart {
      height: 220px !important;
      width: 100%;
      
      // 确保图表在小容器中清晰显示
      canvas {
        max-width: 100%;
        max-height: 100%;
      }
    }
  }
  
  .model-status {
    .model-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      margin-bottom: 10px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
      
      .model-name {
        font-size: 16px;
        font-weight: 500;
      }
      
      .model-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          
          &.online { background: #00ff88; }
          &.idle { background: #ff8800; }
          &.offline { background: #ff4444; }
        }
        
        .status-text {
          font-size: 14px;
          color: #8892b0;
        }
      }
    }
  }
  
  .health-card {
    .health-circle {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
      
      .health-gauge {
        width: 150px;
        height: 150px;
      }
      
      .health-score {
        position: absolute;
        text-align: center;
        
        .score-number {
          font-size: 36px;
          font-weight: bold;
          color: #00d4ff;
        }
        
        .score-unit {
          font-size: 18px;
          color: #8892b0;
        }
      }
    }
    
    .service-list {
      .service-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        
        .service-name {
          font-size: 14px;
        }
        
        .service-status {
          font-size: 12px;
          
          &.online { color: #00ff88; }
          &.offline { color: #ff4444; }
        }
      }
    }
  }
}

// 右侧面板
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
  max-width: 100%;
  
  .chart-container {
    height: 200px;
    width: 100%;
    overflow: hidden;
  }
  
  .category-chart {
    height: 280px !important;
    width: 100% !important;
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
  height: 100px;
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
    height: 50px;
    overflow: hidden;
    
    .stream-items {
      display: flex;
      animation: scroll-left 60s linear infinite;
      
      .stream-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0 20px;
        white-space: nowrap;
        
        .event-time {
          color: #8892b0;
          font-size: 12px;
        }
        
        .event-icon {
          font-size: 14px;
        }
        
        .event-message {
          font-size: 13px;
          color: #ffffff;
        }
        
        &.question { border-left: 2px solid #00d4ff; }
        &.answer { border-left: 2px solid #00ff88; }
        &.score { border-left: 2px solid #ff8800; }
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
  100% { transform: translateX(-100%); }
}

// 响应式设计
@media (max-width: 1920px) {
  .display-main {
    grid-template-columns: 35% 30% 35%;
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