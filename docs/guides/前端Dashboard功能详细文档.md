# AI问答平台管理后台 - 前端Dashboard功能详细文档

## 1. 总体架构

### 1.1 技术栈
- **前端框架**: Vue 3 (Composition API)
- **UI组件库**: Element Plus
- **图表库**: ECharts 5.x
- **状态管理**: Vue 3 Reactivity API
- **HTTP客户端**: Axios
- **样式预处理**: SCSS

### 1.2 文件结构
```
frontend/src/views/Dashboard/
├── index.vue              # Dashboard主页面组件
frontend/src/api/
├── dashboard.js           # Dashboard相关API接口
├── index.js              # Axios配置和请求拦截器
```

## 2. 组件功能详解

### 2.1 页面头部区域

**功能**: 展示页面标题和描述
**位置**: `<div class="page-header">`

```vue
<div class="page-header">
  <h1>数据概览</h1>
  <p class="page-description">系统整体运行状态和数据统计</p>
</div>
```

**特点**:
- 静态内容，无后端交互
- 提供页面功能说明

### 2.2 时间筛选器

**功能**: 控制统计数据的时间范围
**位置**: `<el-row class="filter-row">`

#### 2.2.1 UI组件
```vue
<el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
  <el-radio-button label="today">本日</el-radio-button>
  <el-radio-button label="week">本周</el-radio-button>
  <el-radio-button label="month">本月</el-radio-button>
  <el-radio-button label="year">本年</el-radio-button>
  <el-radio-button label="all">总计</el-radio-button>
</el-radio-group>
```

#### 2.2.2 数据逻辑
```javascript
const timeRange = ref('all')  // 默认选择总计

// 时间范围参数生成
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
```

#### 2.2.3 后端交互
- **触发时机**: 用户选择不同时间范围
- **调用方法**: `handleTimeRangeChange(value)`
- **API调用**: 自动调用 `loadStats()` 重新获取统计数据

### 2.3 统计卡片区域

**功能**: 展示核心统计指标
**位置**: `<el-row class="stats-row">`

#### 2.3.1 统计指标定义
```javascript
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
```

#### 2.3.2 卡片UI结构
```vue
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
```

#### 2.3.3 数据计算逻辑
```javascript
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
```

#### 2.3.4 后端交互
- **API端点**: `GET /api/dashboard`
- **请求参数**: 时间范围参数（start_time, end_time, time_range）
- **响应数据结构**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_questions": 120,
      "total_answers": 280,
      "scored_answers": 85
    },
    "classification_distribution": {
      "技术问题": 45,
      "产品咨询": 38,
      "其他": 37
    }
  }
}
```

### 2.4 图表区域

#### 2.4.1 问题处理趋势图

**功能**: 展示最近7天的处理量趋势
**位置**: `<el-col :span="12">` (左侧)
**图表类型**: ECharts 折线图

**配置选项**:
```javascript
const initTrendChart = () => {
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
```

**特点**:
- 目前使用模拟数据
- 支持刷新功能
- 响应式布局

#### 2.4.2 AI模型性能对比图

**功能**: 展示三个AI模型的多维度评分对比
**位置**: `<el-col :span="12">` (右侧)
**图表类型**: ECharts 雷达图

**配置选项**:
```javascript
const initModelChart = () => {
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
```

**评分维度**:
- 准确性：答案的正确程度
- 完整性：答案的全面程度
- 清晰度：答案的表达清晰度
- 相关性：答案与问题的相关性
- 有用性：答案的实用价值

### 2.5 系统状态监控区域

**功能**: 监控4个AI API服务的运行状态
**位置**: `<el-row class="status-row">`

#### 2.5.1 服务状态定义
```javascript
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
```

#### 2.5.2 状态UI组件
```vue
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
```

#### 2.5.3 系统状态汇总
```javascript
const systemStatus = ref({
  type: 'success',
  text: '系统正常'
})
```

**状态类型**:
- `success`: 系统正常 (绿色)
- `warning`: 部分异常 (橙色)
- `danger`: 系统异常 (红色)

#### 2.5.4 后端交互
- **API端点**: `GET /api/scheduler/status`
- **调用时机**: 页面加载、手动刷新、时间范围切换
- **更新机制**: 目前无自动定时更新

## 3. API接口详解

### 3.1 Dashboard API (`/api/dashboard.js`)

#### 3.1.1 获取统计数据
```javascript
export function getStats(params) {
  return request({
    url: '/dashboard',
    method: 'get',
    params
  })
}
```

**请求参数**:
- `time_range`: 时间范围类型 (today/week/month/year/all)
- `start_time`: 开始时间 (ISO字符串)
- `end_time`: 结束时间 (ISO字符串)

**响应格式**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_questions": 120,
      "total_answers": 280,
      "scored_answers": 85
    },
    "classification_distribution": {
      "技术问题": 45,
      "产品咨询": 38,
      "其他": 37
    }
  }
}
```

#### 3.1.2 获取系统健康状态
```javascript
export function getSystemHealth() {
  return request({
    url: '/scheduler/status',
    method: 'get'
  })
}
```

#### 3.1.3 获取同步状态
```javascript
export function getSyncStatus() {
  return request({
    url: '/sync/status',
    method: 'get'
  })
}
```

#### 3.1.4 获取趋势数据 (未使用)
```javascript
export function getTrends(params) {
  return request({
    url: '/questions/statistics',
    method: 'get',
    params
  })
}
```

#### 3.1.5 获取模型对比数据 (未使用)
```javascript
export function getModelComparison() {
  return request({
    url: '/process/statistics',
    method: 'get'
  })
}
```

### 3.2 HTTP配置 (`/api/index.js`)

```javascript
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8088/api',
  timeout: 10000
})

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    return Promise.reject(error)
  }
)

export default request
```

## 4. 生命周期和事件流

### 4.1 组件初始化流程

```javascript
onMounted(async () => {
  // 1. 加载统计数据
  await loadStats()
  
  // 2. 等待DOM更新
  await nextTick()
  
  // 3. 初始化图表
  initTrendChart()
  initModelChart()
  
  // 4. 绑定窗口缩放事件
  window.addEventListener('resize', resizeCharts)
})
```

### 4.2 用户交互事件流

#### 4.2.1 时间范围切换
```
用户选择时间范围 → handleTimeRangeChange() → loadStats() → 更新统计卡片
```

#### 4.2.2 手动刷新
```
用户点击刷新按钮 → refreshStats() → loadStats() → 更新统计卡片
```

#### 4.2.3 趋势图刷新
```
用户点击趋势图刷新 → refreshTrends() → 显示成功消息
```

### 4.3 数据更新时机

1. **页面初始加载**: 自动加载默认时间范围(总计)的数据
2. **时间范围切换**: 立即重新获取对应时间范围的数据
3. **手动刷新**: 用户主动触发数据更新
4. **窗口缩放**: 自动调整图表尺寸

## 5. 样式设计

### 5.1 设计原则
- **现代简洁**: 使用Element Plus的现代设计语言
- **信息层次**: 通过字体大小、颜色区分信息重要性
- **状态可视化**: 用颜色直观表示状态（绿色=正常，红色=异常）
- **响应式布局**: 支持不同屏幕尺寸

### 5.2 颜色规范
- **主色调**: #409EFF (Element Plus primary)
- **成功色**: #67C23A (绿色)
- **警告色**: #E6A23C (橙色)
- **危险色**: #F56C6C (红色)
- **文本色**: #303133 (主要文本), #909399 (次要文本), #C0C4CC (辅助文本)

### 5.3 布局结构
```
页面头部 (标题+描述)
    ↓
时间筛选器 (单行，全宽)
    ↓
统计卡片区 (4个卡片，25%宽度平分)
    ↓
图表区域 (2个图表，50%宽度平分)
    ↓
系统状态监控 (4个服务状态，25%宽度平分)
```

## 6. 优化建议

### 6.1 已实现功能
✅ 时间范围筛选  
✅ 统计数据实时更新  
✅ 响应式图表  
✅ 统一错误处理  
✅ Loading状态管理  

### 6.2 可优化的功能

#### 6.2.1 数据刷新机制
- **当前**: 手动刷新 + 时间切换触发
- **建议**: 添加定时自动刷新（每30秒或1分钟）
- **实现**: 使用 `setInterval` 或 Vue 3 的 `useIntervalFn`

#### 6.2.2 图表数据动态化
- **当前**: 使用静态模拟数据
- **建议**: 从后端API获取真实数据
- **实现**: 添加对应的API端点和数据处理逻辑

#### 6.2.3 系统状态实时监控
- **当前**: 静态状态显示
- **建议**: 实时检测API服务状态
- **实现**: 定时ping各个服务端点

#### 6.2.4 性能优化
- **图表懒加载**: 只在需要时初始化图表
- **数据缓存**: 缓存近期查询的数据
- **防抖处理**: 防止快速切换时间范围导致的重复请求

#### 6.2.5 用户体验增强
- **数据对比**: 显示同比/环比变化趋势
- **异常告警**: 系统状态异常时弹窗提醒
- **数据导出**: 支持统计数据导出Excel
- **个性化配置**: 用户可自定义显示的统计指标

## 7. 技术细节

### 7.1 Vue 3 Composition API使用
- 使用 `ref` 管理响应式数据
- 使用 `onMounted` 处理组件生命周期
- 使用 `nextTick` 确保DOM更新完成

### 7.2 ECharts集成
- 手动管理图表实例生命周期
- 响应式图表尺寸调整
- 主题色彩与UI保持一致

### 7.3 错误处理机制
- API请求异常捕获
- 用户友好的错误提示
- 降级处理（显示默认值）

### 7.4 组件复用性
- 统计卡片数据驱动渲染
- 图表配置可抽取为公共方法
- 样式使用SCSS变量便于主题切换

---

**文档版本**: v1.0  
**最后更新**: 2024年当前日期  
**维护人员**: AI问答平台开发团队 