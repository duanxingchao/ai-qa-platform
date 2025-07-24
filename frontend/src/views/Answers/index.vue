<template>
  <div class="answers">
    <div class="page-header">
      <h1>答案对比</h1>
      <p class="page-description">多AI模型答案对比分析</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" :inline="true" class="search-form">
        <el-form-item label="问题ID">
          <el-input 
            v-model="searchForm.questionId" 
            placeholder="输入问题ID"
            clearable
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="评分状态">
          <el-select v-model="searchForm.scoreStatus" placeholder="选择评分状态" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="已评分" value="scored"></el-option>
            <el-option label="未评分" value="unscored"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 批量操作 -->
      <div class="batch-operations">
        <el-button 
          type="primary" 
          :disabled="selectedQuestions.length === 0"
          @click="showBatchScoreDialog = true"
        >
          <el-icon><Star /></el-icon>
          批量评分 ({{ selectedQuestions.length }})
        </el-button>
        <el-button 
          type="success"
          :disabled="selectedQuestions.length === 0" 
          @click="handleExport"
          :loading="exporting"
        >
          <el-icon><Download /></el-icon>
          导出选中
        </el-button>
      </div>
    </el-card>

    <!-- 答案对比列表 -->
    <el-card class="answers-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>答案对比列表</span>
          <el-tag type="info">共 {{ pagination.total }} 条</el-tag>
        </div>
      </template>

      <el-table 
        :data="questionsList" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        row-key="business_id"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="business_id" label="问题ID" width="120" />
        
        <el-table-column prop="query" label="问题内容" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="classification" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small" v-if="row.classification">{{ row.classification }}</el-tag>
            <span v-else class="text-muted">未分类</span>
          </template>
        </el-table-column>

        <el-table-column label="答案状态" width="150">
          <template #default="{ row }">
            <div class="answer-status">
              <el-tag 
                v-if="row.answers?.original" 
                size="small" 
                type="primary"
              >原始</el-tag>
              <el-tag 
                v-if="row.answers?.doubao" 
                size="small" 
                type="success"
              >豆包</el-tag>
              <el-tag 
                v-if="row.answers?.xiaotian" 
                size="small" 
                type="warning"
              >小天</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="评分状态" width="120">
          <template #default="{ row }">
            <el-tag 
              :type="getScoreStatusType(row)"
              size="small"
            >
              {{ getScoreStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small"
              @click="showComparisonDialog(row)"
            >
              对比查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 答案对比弹窗 -->
    <el-dialog 
      v-model="showComparison" 
      title="答案对比分析"
      width="90%"
      top="5vh"
      :before-close="handleCloseComparison"
    >
      <div v-if="currentComparison" class="comparison-content">
        <!-- 问题信息 -->
        <div class="question-info">
          <h3>{{ currentComparison.query }}</h3>
          <div class="question-meta">
            <el-tag size="small">{{ currentComparison.classification || '未分类' }}</el-tag>
            <span class="question-id">ID: {{ currentComparison.business_id }}</span>
            <span class="question-time">{{ formatDateTime(currentComparison.created_at) }}</span>
          </div>
        </div>

        <!-- 三栏答案对比 -->
        <el-row :gutter="20" class="answers-comparison">
          <!-- 原始答案 -->
          <el-col :span="8">
            <el-card class="answer-card original" shadow="hover">
              <template #header>
                <div class="answer-header">
                  <span class="answer-title">
                    <el-icon><User /></el-icon>
                    原始答案
                  </span>
                  <el-tag type="primary" size="small">原始AI</el-tag>
                </div>
              </template>
              <div class="answer-content">
                <div class="answer-text" v-if="currentComparison.answers?.original">
                  {{ currentComparison.answers.original.answer_text }}
                </div>
                <div class="no-answer" v-else>
                  <el-icon><Warning /></el-icon>
                  暂无答案
                </div>
                <div class="answer-meta" v-if="currentComparison.answers?.original">
                  <div>创建时间: {{ formatDateTime(currentComparison.answers.original.created_at) }}</div>
                  <div v-if="currentComparison.answers.original.is_scored">
                    <el-tag type="success" size="small">已评分</el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 豆包答案 -->
          <el-col :span="8">
            <el-card class="answer-card doubao" shadow="hover">
              <template #header>
                <div class="answer-header">
                  <span class="answer-title">
                    <el-icon><ChatDotRound /></el-icon>
                    豆包答案
                  </span>
                  <el-tag type="success" size="small">豆包AI</el-tag>
                </div>
              </template>
              <div class="answer-content">
                <div class="answer-text" v-if="currentComparison.answers?.doubao">
                  {{ currentComparison.answers.doubao.answer_text }}
                </div>
                <div class="no-answer" v-else>
                  <el-icon><Warning /></el-icon>
                  暂无答案
                </div>
                <div class="answer-meta" v-if="currentComparison.answers?.doubao">
                  <div>创建时间: {{ formatDateTime(currentComparison.answers.doubao.created_at) }}</div>
                  <div v-if="currentComparison.answers.doubao.is_scored">
                    <el-tag type="success" size="small">已评分</el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 小天答案 -->
          <el-col :span="8">
            <el-card class="answer-card xiaotian" shadow="hover">
              <template #header>
                <div class="answer-header">
                  <span class="answer-title">
                    <el-icon><Avatar /></el-icon>
                    小天答案
                  </span>
                  <el-tag type="warning" size="small">小天AI</el-tag>
                </div>
              </template>
              <div class="answer-content">
                <div class="answer-text" v-if="currentComparison.answers?.xiaotian">
                  {{ currentComparison.answers.xiaotian.answer_text }}
                </div>
                <div class="no-answer" v-else>
                  <el-icon><Warning /></el-icon>
                  暂无答案
                </div>
                <div class="answer-meta" v-if="currentComparison.answers?.xiaotian">
                  <div>创建时间: {{ formatDateTime(currentComparison.answers.xiaotian.created_at) }}</div>
                  <div v-if="currentComparison.answers.xiaotian.is_scored">
                    <el-tag type="success" size="small">已评分</el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 评分雷达图对比 -->
        <div class="score-section" v-if="hasAnyScore">
          <h4>评分对比分析</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <div ref="radarChart" style="height: 400px;"></div>
            </el-col>
            <el-col :span="12">
              <div class="score-details">
                <div 
                  v-for="model in ['original', 'doubao', 'xiaotian']" 
                  :key="model"
                  class="score-item"
                  v-if="getModelScore(model)"
                >
                  <div class="score-header">
                    <span class="model-name">{{ getModelDisplayName(model) }}</span>
                    <span class="avg-score">{{ getModelScore(model).average_score }}分</span>
                  </div>
                  <div class="score-dimensions">
                    <div 
                      v-for="(score, index) in getModelScoreDimensions(model)" 
                      :key="index"
                      class="dimension-item"
                    >
                      <span class="dimension-name">{{ score.name }}</span>
                      <el-progress 
                        :percentage="score.value * 20" 
                        :color="getModelColor(model)"
                        :show-text="false"
                        :stroke-width="8"
                      />
                      <span class="dimension-score">{{ score.value }}分</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showComparison = false">关闭</el-button>
          <el-button type="primary" @click="handleScoreAnswer">
            评分管理
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 批量评分弹窗 -->
    <el-dialog v-model="showBatchScoreDialog" title="批量评分" width="500px">
      <el-form :model="batchScoreForm" label-width="100px">
        <el-form-item label="选择模型">
          <el-checkbox-group v-model="batchScoreForm.models">
            <el-checkbox label="original">原始AI</el-checkbox>
            <el-checkbox label="doubao">豆包</el-checkbox>
            <el-checkbox label="xiaotian">小天</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="评分说明">
          <el-input 
            v-model="batchScoreForm.comment" 
            type="textarea" 
            placeholder="请输入评分说明"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showBatchScoreDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleBatchScore"
            :loading="batchScoring"
          >
            开始评分
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { 
  getAnswers, 
  getAnswerComparison, 
  batchScore, 
  exportAnswers 
} from '@/api/answers'
import { getQuestions } from '@/api/questions'

export default {
  name: 'Answers',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const exporting = ref(false)
    const batchScoring = ref(false)
    const showComparison = ref(false)
    const showBatchScoreDialog = ref(false)
    const radarChart = ref(null)
    
    // 搜索表单
    const searchForm = reactive({
      questionId: '',
      scoreStatus: '',
      dateRange: null
    })
    
    // 分页
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })
    
    // 数据
    const questionsList = ref([])
    const selectedQuestions = ref([])
    const currentComparison = ref(null)
    
    // 批量评分表单
    const batchScoreForm = reactive({
      models: ['original', 'doubao', 'xiaotian'],
      comment: ''
    })

    // 加载数据
    const loadData = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.size,
          question_id: searchForm.questionId || undefined,
          score_status: searchForm.scoreStatus || undefined,
          start_time: searchForm.dateRange?.[0] || undefined,
          end_time: searchForm.dateRange?.[1] || undefined
        }
        
        const response = await getQuestions(params)
        questionsList.value = response.data.questions || []
        pagination.total = response.data.total || 0
        
        // 为每个问题加载答案信息
        await loadAnswersForQuestions()
      } catch (error) {
        ElMessage.error('加载数据失败：' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 为问题加载答案信息
    const loadAnswersForQuestions = async () => {
      for (const question of questionsList.value) {
        try {
          const response = await getAnswerComparison(question.business_id)
          question.answers = response.data.answers || {}
        } catch (error) {
          question.answers = {}
        }
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      loadData()
    }

    // 重置
    const handleReset = () => {
      Object.assign(searchForm, {
        questionId: '',
        scoreStatus: '',
        dateRange: null
      })
      pagination.page = 1
      loadData()
    }

    // 分页
    const handleSizeChange = (size) => {
      pagination.size = size
      pagination.page = 1
      loadData()
    }

    const handleCurrentChange = (page) => {
      pagination.page = page
      loadData()
    }

    // 选择改变
    const handleSelectionChange = (selection) => {
      selectedQuestions.value = selection
    }

    // 显示对比弹窗
    const showComparisonDialog = async (question) => {
      try {
        const response = await getAnswerComparison(question.business_id)
        currentComparison.value = {
          ...question,
          answers: response.data.answers || {},
          scores: response.data.scores || {}
        }
        showComparison.value = true
        
        // 延迟渲染雷达图
        nextTick(() => {
          renderRadarChart()
        })
      } catch (error) {
        ElMessage.error('加载答案对比失败：' + error.message)
      }
    }

    // 关闭对比弹窗
    const handleCloseComparison = (done) => {
      if (radarChart.value && echarts.getInstanceByDom(radarChart.value)) {
        echarts.dispose(radarChart.value)
      }
      done()
    }

    // 渲染雷达图
    const renderRadarChart = () => {
      if (!radarChart.value || !hasAnyScore.value) return
      
      const chartInstance = echarts.init(radarChart.value)
      
      // 构建雷达图数据
      const indicator = []
      const seriesData = []
      
      // 获取评分维度
      const sampleScore = getAnyModelScore()
      if (sampleScore) {
        for (let i = 1; i <= 5; i++) {
          const dimensionName = sampleScore[`dimension_${i}_name`] || `维度${i}`
          indicator.push({
            name: dimensionName,
            max: 5
          })
        }
      }
      
      // 添加各模型数据
      const models = ['original', 'doubao', 'xiaotian']
      const colors = ['#409EFF', '#67C23A', '#E6A23C']
      
      models.forEach((model, index) => {
        const score = getModelScore(model)
        if (score) {
          const data = []
          for (let i = 1; i <= 5; i++) {
            data.push(score[`score_${i}`] || 0)
          }
          
          seriesData.push({
            name: getModelDisplayName(model),
            value: data,
            itemStyle: {
              color: colors[index]
            }
          })
        }
      })
      
      const option = {
        title: {
          text: '评分雷达图对比',
          left: 'center'
        },
        legend: {
          data: seriesData.map(item => item.name),
          bottom: 20
        },
        radar: {
          indicator: indicator,
          radius: '60%'
        },
        series: [{
          type: 'radar',
          data: seriesData
        }]
      }
      
      chartInstance.setOption(option)
    }

    // 批量评分
    const handleBatchScore = async () => {
      if (selectedQuestions.value.length === 0) {
        ElMessage.warning('请选择要评分的问题')
        return
      }
      
      if (batchScoreForm.models.length === 0) {
        ElMessage.warning('请选择要评分的模型')
        return
      }
      
      try {
        batchScoring.value = true
        const questionIds = selectedQuestions.value.map(q => q.business_id)
        
        await batchScore({
          question_ids: questionIds,
          models: batchScoreForm.models,
          comment: batchScoreForm.comment
        })
        
        ElMessage.success('批量评分任务已提交')
        showBatchScoreDialog.value = false
        selectedQuestions.value = []
        
        // 重新加载数据
        setTimeout(() => {
          loadData()
        }, 2000)
      } catch (error) {
        ElMessage.error('批量评分失败：' + error.message)
      } finally {
        batchScoring.value = false
      }
    }

    // 导出
    const handleExport = async () => {
      if (selectedQuestions.value.length === 0) {
        ElMessage.warning('请选择要导出的数据')
        return
      }
      
      try {
        exporting.value = true
        const questionIds = selectedQuestions.value.map(q => q.business_id)
        
        const response = await exportAnswers({
          question_ids: questionIds
        })
        
        // 下载文件
        const blob = new Blob([response], { 
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `answers_export_${new Date().getTime()}.xlsx`
        link.click()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('导出成功')
      } catch (error) {
        ElMessage.error('导出失败：' + error.message)
      } finally {
        exporting.value = false
      }
    }

    // 评分答案
    const handleScoreAnswer = () => {
      ElMessage.info('评分管理功能开发中')
    }

    // 辅助方法
    const formatDateTime = (dateTime) => {
      if (!dateTime) return '-'
      return new Date(dateTime).toLocaleString('zh-CN')
    }

    const getScoreStatusType = (question) => {
      const answers = question.answers || {}
      const hasScored = Object.values(answers).some(answer => answer?.is_scored)
      return hasScored ? 'success' : 'info'
    }

    const getScoreStatusText = (question) => {
      const answers = question.answers || {}
      const scoredCount = Object.values(answers).filter(answer => answer?.is_scored).length
      const totalCount = Object.keys(answers).length
      
      if (scoredCount === 0) return '未评分'
      if (scoredCount === totalCount) return '已评分'
      return `部分评分(${scoredCount}/${totalCount})`
    }

    const hasAnyScore = computed(() => {
      if (!currentComparison.value) return false
      const scores = currentComparison.value.scores || {}
      return Object.keys(scores).length > 0
    })

    const getModelScore = (model) => {
      if (!currentComparison.value) return null
      return currentComparison.value.scores?.[model] || null
    }

    const getAnyModelScore = () => {
      if (!currentComparison.value) return null
      const scores = currentComparison.value.scores || {}
      return Object.values(scores)[0] || null
    }

    const getModelDisplayName = (model) => {
      const names = {
        original: '原始AI',
        doubao: '豆包',
        xiaotian: '小天'
      }
      return names[model] || model
    }

    const getModelColor = (model) => {
      const colors = {
        original: '#409EFF',
        doubao: '#67C23A', 
        xiaotian: '#E6A23C'
      }
      return colors[model] || '#909399'
    }

    const getModelScoreDimensions = (model) => {
      const score = getModelScore(model)
      if (!score) return []
      
      const dimensions = []
      for (let i = 1; i <= 5; i++) {
        const name = score[`dimension_${i}_name`] || `维度${i}`
        const value = score[`score_${i}`] || 0
        dimensions.push({ name, value })
      }
      return dimensions
    }

    // 生命周期
    onMounted(() => {
      loadData()
    })

    return {
      // 响应式数据
      loading,
      exporting,
      batchScoring,
      showComparison,
      showBatchScoreDialog,
      radarChart,
      searchForm,
      pagination,
      questionsList,
      selectedQuestions,
      currentComparison,
      batchScoreForm,
      hasAnyScore,
      
      // 方法
      handleSearch,
      handleReset,
      handleSizeChange,
      handleCurrentChange,
      handleSelectionChange,
      showComparisonDialog,
      handleCloseComparison,
      handleBatchScore,
      handleExport,
      handleScoreAnswer,
      formatDateTime,
      getScoreStatusType,
      getScoreStatusText,
      getModelScore,
      getModelDisplayName,
      getModelColor,
      getModelScoreDimensions
    }
  }
}
</script> 

<style lang="scss" scoped>
.answers {
  .page-header {
    margin-bottom: 20px;
    
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #303133;
    }
    
    .page-description {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }

  .search-card {
    margin-bottom: 20px;
    
    .search-form {
      margin-bottom: 16px;
    }
    
    .batch-operations {
      display: flex;
      gap: 12px;
    }
  }

  .answers-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .answer-status {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }
    
    .pagination-wrapper {
      margin-top: 20px;
      text-align: right;
    }
  }

  .comparison-content {
    .question-info {
      margin-bottom: 24px;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;
      
      h3 {
        margin: 0 0 12px 0;
        font-size: 18px;
        color: #303133;
        line-height: 1.4;
      }
      
      .question-meta {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 14px;
        color: #606266;
        
        .question-id {
          color: #909399;
        }
        
        .question-time {
          color: #909399;
        }
      }
    }

    .answers-comparison {
      margin-bottom: 24px;
      
      .answer-card {
        height: 400px;
        
        .answer-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .answer-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
          }
        }
        
        .answer-content {
          height: 300px;
          display: flex;
          flex-direction: column;
          
          .answer-text {
            flex: 1;
            padding: 16px;
            background: #fafafa;
            border-radius: 6px;
            line-height: 1.6;
            font-size: 14px;
            overflow-y: auto;
            margin-bottom: 12px;
          }
          
          .no-answer {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #c0c4cc;
            font-size: 14px;
            
            .el-icon {
              font-size: 24px;
              margin-bottom: 8px;
            }
          }
          
          .answer-meta {
            padding-top: 12px;
            border-top: 1px solid #ebeef5;
            font-size: 12px;
            color: #909399;
            
            > div {
              margin-bottom: 4px;
              
              &:last-child {
                margin-bottom: 0;
              }
            }
          }
        }
        
        &.original {
          border-left: 4px solid #409eff;
        }
        
        &.doubao {
          border-left: 4px solid #67c23a;
        }
        
        &.xiaotian {
          border-left: 4px solid #e6a23c;
        }
      }
    }

    .score-section {
      padding-top: 24px;
      border-top: 1px solid #ebeef5;
      
      h4 {
        margin: 0 0 20px 0;
        font-size: 16px;
        color: #303133;
      }
      
      .score-details {
        .score-item {
          margin-bottom: 24px;
          padding: 16px;
          background: #fafafa;
          border-radius: 8px;
          
          .score-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            
            .model-name {
              font-weight: 600;
              font-size: 16px;
            }
            
            .avg-score {
              font-size: 18px;
              font-weight: bold;
              color: #e6a23c;
            }
          }
          
          .score-dimensions {
            .dimension-item {
              display: flex;
              align-items: center;
              margin-bottom: 8px;
              
              .dimension-name {
                width: 80px;
                font-size: 14px;
                color: #606266;
              }
              
              .el-progress {
                flex: 1;
                margin: 0 12px;
              }
              
              .dimension-score {
                width: 40px;
                text-align: right;
                font-size: 14px;
                font-weight: 600;
              }
            }
          }
        }
      }
    }
  }
}

.text-muted {
  color: #c0c4cc;
}
</style> 