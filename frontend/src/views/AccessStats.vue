<template>
  <div class="access-stats">
    <div class="page-header">
      <h2>📊 访问统计</h2>
      <p>查看用户访问统计数据和系统使用情况</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon login">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_logins || 0 }}</div>
              <div class="stat-label">总登录次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon active">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active_users || 0 }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon today">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_logins || 0 }}</div>
              <div class="stat-label">今日登录</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon online">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.online_users || 0 }}</div>
              <div class="stat-label">在线用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>登录趋势</span>
              <el-select v-model="chartTimeRange" @change="loadChartData" size="small">
                <el-option label="最近7天" value="7d" />
                <el-option label="最近30天" value="30d" />
                <el-option label="最近90天" value="90d" />
              </el-select>
            </div>
          </template>
          <div ref="loginTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <span>用户活跃度</span>
          </template>
          <div ref="userActivityChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 访问日志 -->
    <el-card class="logs-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>访问日志</span>
          <div class="header-actions">
            <el-select v-model="logFilter.action" placeholder="操作类型" clearable size="small" @change="loadAccessLogs">
              <el-option label="全部" value="" />
              <el-option label="登录" value="login" />
              <el-option label="登出" value="logout" />
            </el-select>
            <el-button type="text" @click="loadAccessLogs" size="small">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="logsLoading"
        :data="accessLogs"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="username" label="用户" width="120">
          <template #default="{ row }">
            <span>{{ row.username }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }">
            <el-tag :type="row.action === 'login' ? 'success' : 'info'" size="small">
              {{ row.action === 'login' ? '登录' : '登出' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP地址" width="140">
          <template #default="{ row }">
            <code>{{ row.ip_address || '-' }}</code>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="duration" label="操作时长" width="120">
          <template #default="{ row }">
            <span v-if="row.action === 'login'">{{ row.duration || '-' }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        

      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="logsPagination.page"
          v-model:page-size="logsPagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="logsPagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleLogsSizeChange"
          @current-change="handleLogsCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  UserFilled,
  Calendar,
  Connection,
  Refresh
} from '@element-plus/icons-vue'
import { getAccessStats, getAccessLogs } from '@/api/stats'
import { formatDateTime } from '@/utils/datetime'
import * as echarts from 'echarts'

export default {
  name: 'AccessStats',
  components: {
    User,
    UserFilled,
    Calendar,
    Connection,
    Refresh
  },
  setup() {
    const stats = ref({})
    const accessLogs = ref([])
    const logsLoading = ref(false)
    const chartTimeRange = ref('7d')
    
    // 图表实例
    const loginTrendChart = ref(null)
    const userActivityChart = ref(null)
    let loginTrendChartInstance = null
    let userActivityChartInstance = null
    
    // 日志筛选
    const logFilter = reactive({
      action: ''
    })
    
    // 日志分页
    const logsPagination = reactive({
      page: 1,
      pageSize: 20,
      total: 0
    })
    
    // 加载统计数据
    const loadStats = async () => {
      try {
        const response = await getAccessStats()
        if (response.success) {
          stats.value = response.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }
    
    // 加载访问日志
    const loadAccessLogs = async () => {
      try {
        logsLoading.value = true
        const response = await getAccessLogs({
          ...logFilter,
          page: logsPagination.page,
          page_size: logsPagination.pageSize
        })
        
        if (response.success) {
          accessLogs.value = response.data.logs || []
          logsPagination.total = response.data.total || 0
        }
      } catch (error) {
        console.error('加载访问日志失败:', error)
      } finally {
        logsLoading.value = false
      }
    }
    
    // 加载图表数据
    const loadChartData = async () => {
      try {
        // 这里应该调用具体的图表数据API
        // 暂时使用模拟数据
        const mockLoginTrendData = generateMockLoginTrendData()
        const mockUserActivityData = generateMockUserActivityData()
        
        updateLoginTrendChart(mockLoginTrendData)
        updateUserActivityChart(mockUserActivityData)
      } catch (error) {
        console.error('加载图表数据失败:', error)
      }
    }
    
    // 初始化登录趋势图表
    const initLoginTrendChart = () => {
      if (loginTrendChart.value) {
        loginTrendChartInstance = echarts.init(loginTrendChart.value)
      }
    }
    
    // 初始化用户活跃度图表
    const initUserActivityChart = () => {
      if (userActivityChart.value) {
        userActivityChartInstance = echarts.init(userActivityChart.value)
      }
    }
    
    // 更新登录趋势图表
    const updateLoginTrendChart = (data) => {
      if (!loginTrendChartInstance) return
      
      const option = {
        title: {
          text: '登录趋势',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.dates
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: '登录次数',
          type: 'line',
          data: data.values,
          smooth: true,
          areaStyle: {
            opacity: 0.3
          },
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      
      loginTrendChartInstance.setOption(option)
    }
    
    // 更新用户活跃度图表
    const updateUserActivityChart = (data) => {
      if (!userActivityChartInstance) return
      
      const option = {
        title: {
          text: '用户活跃度',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'item'
        },
        series: [{
          name: '用户活跃度',
          type: 'pie',
          radius: '60%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      
      userActivityChartInstance.setOption(option)
    }
    
    // 生成模拟登录趋势数据
    const generateMockLoginTrendData = () => {
      const days = parseInt(chartTimeRange.value)
      const dates = []
      const values = []
      
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        dates.push(date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }))
        values.push(Math.floor(Math.random() * 50) + 10)
      }
      
      return { dates, values }
    }
    
    // 生成模拟用户活跃度数据
    const generateMockUserActivityData = () => {
      return [
        { value: 60, name: '活跃用户' },
        { value: 25, name: '一般用户' },
        { value: 15, name: '不活跃用户' }
      ]
    }
    
    // 日志分页处理
    const handleLogsSizeChange = (size) => {
      logsPagination.pageSize = size
      logsPagination.page = 1
      loadAccessLogs()
    }
    
    const handleLogsCurrentChange = (page) => {
      logsPagination.page = page
      loadAccessLogs()
    }
    
    // 工具函数
    const getAvatarUrl = (username) => {
      return `https://api.dicebear.com/7.x/initials/svg?seed=${username}&backgroundColor=random`
    }
    
    // 时间格式化函数已通过import导入
    

    
    // 初始化
    onMounted(async () => {
      await loadStats()
      await loadAccessLogs()
      
      await nextTick()
      initLoginTrendChart()
      initUserActivityChart()
      loadChartData()
      
      // 监听窗口大小变化
      window.addEventListener('resize', () => {
        if (loginTrendChartInstance) {
          loginTrendChartInstance.resize()
        }
        if (userActivityChartInstance) {
          userActivityChartInstance.resize()
        }
      })
    })
    
    return {
      stats,
      accessLogs,
      logsLoading,
      chartTimeRange,
      loginTrendChart,
      userActivityChart,
      logFilter,
      logsPagination,
      loadAccessLogs,
      loadChartData,
      handleLogsSizeChange,
      handleLogsCurrentChange,
      getAvatarUrl,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.access-stats {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.today {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.online {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.chart-container {
  height: 320px;
}

.logs-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-weight: 500;
}

.user-agent {
  color: #606266;
  font-size: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
