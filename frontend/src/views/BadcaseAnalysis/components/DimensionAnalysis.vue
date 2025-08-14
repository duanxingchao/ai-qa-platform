<template>
  <el-card class="dimension-analysis-card">
    <template #header>
      <div class="card-header">
        <span>维度分析</span>
        <div class="header-controls">
          <el-select
            v-model="selectedClassification"
            placeholder="选择分类"
            style="width: 150px; margin-right: 10px;"
            @change="handleClassificationChange"
          >
            <el-option
              v-for="category in categories"
              :key="category.value"
              :label="category.label"
              :value="category.value"
            />
          </el-select>
          


          <el-button-group>
            <el-button 
              :type="chartType === 'pie' ? 'primary' : ''"
              size="small"
              @click="chartType = 'pie'"
            >
              饼图
            </el-button>
            <el-button 
              :type="chartType === 'bar' ? 'primary' : ''"
              size="small"
              @click="chartType = 'bar'"
            >
              柱图
            </el-button>
            <el-button 
              :type="chartType === 'table' ? 'primary' : ''"
              size="small"
              @click="chartType = 'table'"
            >
              表格
            </el-button>
          </el-button-group>
        </div>
      </div>
    </template>

    <div v-loading="loading" class="analysis-content">
      <div v-if="!selectedClassification" class="empty-state">
        <el-empty description="请选择一个分类来查看维度分析" />
      </div>
      
      <div v-else-if="analysisData" class="data-content">
        <!-- 统计信息 -->
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-label">总问题数:</span>
            <span class="stat-value">{{ analysisData.total_questions }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">总badcase数:</span>
            <span class="stat-value">{{ analysisData.total_badcases }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">badcase率:</span>
            <span class="stat-value">{{ analysisData.badcase_rate }}%</span>
          </div>
        </div>

        <!-- 图表展示 -->
        <div v-if="chartType !== 'table'" class="chart-container">
          <div ref="chartRef" class="chart" style="height: 400px;"></div>
        </div>

        <!-- 表格展示 -->
        <div v-if="chartType === 'table'" class="table-container">
          <el-table :data="analysisData.dimension_analysis" stripe>
            <el-table-column prop="dimension_name" label="维度名称" width="150" />
            <el-table-column prop="badcase_count" label="badcase数量" width="120" />
            <el-table-column prop="total_questions_with_dimension" label="该维度总数" width="120" />
            <el-table-column prop="percentage" label="占比" width="100">
              <template #default="{ row }">
                {{ row.percentage }}%
              </template>
            </el-table-column>
            <el-table-column label="进度条" min-width="200">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.percentage" 
                  :color="getProgressColor(row.percentage)"
                  :show-text="false"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getDimensionAnalysis } from '@/api/badcase'
import { ElMessage } from 'element-plus'

export default {
  name: 'DimensionAnalysis',
  props: {
    categories: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const loading = ref(false)
    const selectedClassification = ref('')
    const chartType = ref('pie')
    const analysisData = ref(null)
    const chartRef = ref(null)
    let chartInstance = null

    // 加载维度分析数据
    const loadDimensionData = async () => {
      if (!selectedClassification.value) return
      
      try {
        loading.value = true
        const params = {
          classification: selectedClassification.value,
          time_range: 'all'
        }
        
        const response = await getDimensionAnalysis(params)
        if (response.success) {
          analysisData.value = response.data
          await nextTick()
          renderChart()
        } else {
          ElMessage.error('获取维度分析数据失败')
        }
      } catch (error) {
        console.error('加载维度分析数据失败:', error)
        ElMessage.error('加载维度分析数据失败')
      } finally {
        loading.value = false
      }
    }

    // 处理分类变化
    const handleClassificationChange = () => {
      analysisData.value = null
      loadDimensionData()
    }

    // 渲染图表
    const renderChart = () => {
      if (!chartRef.value || !analysisData.value || chartType.value === 'table') return
      
      if (chartInstance) {
        chartInstance.dispose()
      }
      
      chartInstance = echarts.init(chartRef.value)
      
      const data = analysisData.value.dimension_analysis
      if (!data || data.length === 0) return
      
      let option = {}
      
      if (chartType.value === 'pie') {
        option = {
          title: {
            text: `${selectedClassification.value} - 维度badcase分布`,
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          series: [
            {
              name: 'badcase数量',
              type: 'pie',
              radius: '50%',
              data: data.map(item => ({
                value: item.badcase_count,
                name: item.dimension_name
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }
      } else if (chartType.value === 'bar') {
        option = {
          title: {
            text: `${selectedClassification.value} - 维度badcase分布`,
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: data.map(item => item.dimension_name),
            axisTick: {
              alignWithLabel: true
            }
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: 'badcase数量',
              type: 'bar',
              barWidth: '60%',
              data: data.map(item => item.badcase_count),
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#83bff6' },
                  { offset: 0.5, color: '#188df0' },
                  { offset: 1, color: '#188df0' }
                ])
              }
            }
          ]
        }
      }
      
      chartInstance.setOption(option)
    }

    // 获取进度条颜色
    const getProgressColor = (percentage) => {
      if (percentage >= 30) return '#F56C6C'
      if (percentage >= 20) return '#E6A23C'
      if (percentage >= 10) return '#409EFF'
      return '#67C23A'
    }

    // 监听图表类型变化
    watch(chartType, () => {
      if (analysisData.value) {
        nextTick(() => {
          renderChart()
        })
      }
    })

    // 监听窗口大小变化
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }

    onMounted(() => {
      window.addEventListener('resize', handleResize)
    })

    return {
      loading,
      selectedClassification,
      chartType,
      analysisData,
      chartRef,
      loadDimensionData,
      handleClassificationChange,
      getProgressColor
    }
  }
}
</script>

<style lang="scss" scoped>
.dimension-analysis-card {
  margin-top: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      font-weight: bold;
      color: #303133;
    }
    
    .header-controls {
      display: flex;
      align-items: center;
    }
  }
  
  .analysis-content {
    min-height: 300px;
    
    .empty-state {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 300px;
    }
    
    .stats-row {
      display: flex;
      justify-content: space-around;
      margin-bottom: 20px;
      padding: 15px;
      background-color: #f5f7fa;
      border-radius: 4px;
      
      .stat-item {
        text-align: center;
        
        .stat-label {
          display: block;
          font-size: 14px;
          color: #606266;
          margin-bottom: 5px;
        }
        
        .stat-value {
          display: block;
          font-size: 20px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
    
    .chart-container {
      margin-top: 20px;
    }
    
    .table-container {
      margin-top: 20px;
    }
  }
}
</style>
