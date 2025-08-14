<template>
  <div class="questions">
    <div class="page-header">
      <h1>问题管理</h1>
      <p class="page-description">查看和管理所有问题数据</p>
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
              :loading="statsLoading"
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

    <!-- 搜索筛选区域 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="searchForm" label-width="80px" :inline="true">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索问题内容"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.classification"
            placeholder="选择分类"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="category in categories"
              :key="category.value"
              :label="category.label"
              :value="category.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select
            v-model="searchForm.status"
            placeholder="选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="待处理" value="pending" />
            <el-option label="已分类" value="classified" />
            <el-option label="已生成答案" value="answers_generated" />
            <el-option label="已评分" value="scored" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 300px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮区域 -->
    <el-card class="toolbar-card" shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            type="success"
            @click="handleExport"
            :loading="exportLoading"
          >
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="loadQuestions">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="query" label="问题内容" min-width="300">
          <template #default="scope">
            <div class="question-content">
              <el-text line-clamp="2">{{ scope.row.query }}</el-text>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="classification" label="分类" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.classification" size="small">
              {{ scope.row.classification }}
            </el-tag>
            <el-text v-else type="info">未分类</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="processing_status" label="处理状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.processing_status)" size="small">
              {{ getStatusText(scope.row.processing_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sendmessagetime" label="创建时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.sendmessagetime) }}
          </template>
        </el-table-column>
        <el-table-column prop="pageid" label="页面ID" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleViewDetail(scope.row)"
            >
              详情
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="openReclassifyDialog(scope.row)"
              :loading="scope.row.reclassifying"
            >
              重新分类
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 问题详情弹窗 - 增强版 -->
    <el-dialog
      v-model="detailDrawer.visible"
      title="问题详情"
      width="80%"
      :close-on-click-modal="false"
      class="question-detail-dialog"
    >
      <div v-if="detailDrawer.data" class="detail-content">
        <!-- 基本信息卡片 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>📋 基本信息</span>
              <el-tag :type="getStatusType(detailDrawer.data.processing_status)" size="small">
                {{ getStatusText(detailDrawer.data.processing_status) }}
              </el-tag>
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-descriptions :column="1" size="small">
                <el-descriptions-item label="问题ID">
                  <el-text type="primary">{{ detailDrawer.data.id }}</el-text>
                </el-descriptions-item>
                <el-descriptions-item label="业务ID">
                  <el-text>{{ detailDrawer.data.business_id }}</el-text>
                </el-descriptions-item>
                <el-descriptions-item label="页面ID">
                  <el-text>{{ detailDrawer.data.pageid || '未知' }}</el-text>
                </el-descriptions-item>
                <el-descriptions-item label="设备类型">
                  <el-tag size="small">{{ detailDrawer.data.devicetypename || '未知' }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </el-col>
            <el-col :span="12">
              <el-descriptions :column="1" size="small">
                <el-descriptions-item label="分类">
                  <el-tag v-if="detailDrawer.data.classification" type="success" size="small">
                    {{ detailDrawer.data.classification }}
                  </el-tag>
                  <el-text v-else type="info">未分类</el-text>
                </el-descriptions-item>
                <el-descriptions-item label="服务ID">
                  <el-text>{{ detailDrawer.data.serviceid || '未知' }}</el-text>
                </el-descriptions-item>
                <el-descriptions-item label="QA类型">
                  <el-text>{{ detailDrawer.data.qatype || '未知' }}</el-text>
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  <el-text>{{ formatTime(detailDrawer.data.sendmessagetime) }}</el-text>
                </el-descriptions-item>
              </el-descriptions>
            </el-col>
          </el-row>
        </el-card>

        <!-- 问题内容卡片 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <span>❓ 问题内容</span>
          </template>
          <div class="question-text">
            {{ detailDrawer.data.query }}
          </div>
        </el-card>

        <!-- 统计信息卡片 -->
        <el-card v-if="detailDrawer.data.statistics" class="info-card" shadow="never">
          <template #header>
            <span>📊 统计信息</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="答案总数" :value="detailDrawer.data.statistics.total_answers" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已评分答案" :value="detailDrawer.data.statistics.scored_answers" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="AI类型数" :value="detailDrawer.data.statistics.assistant_types.length" />
            </el-col>
            <el-col :span="6">
              <el-statistic
                title="平均评分"
                :value="getOverallAvgScore(detailDrawer.data.statistics.avg_scores)"
                :precision="2"
              />
            </el-col>
          </el-row>
        </el-card>

        <!-- 答案列表卡片 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <span>🤖 AI答案列表</span>
          </template>
          <el-empty v-if="!detailDrawer.data.answers || detailDrawer.data.answers.length === 0"
                    description="暂无答案数据" />
          <div v-else class="answers-container">
            <el-collapse v-model="activeAnswers" accordion>
              <el-collapse-item
                v-for="answer in detailDrawer.data.answers"
                :key="answer.id"
                :name="answer.id.toString()"
              >
                <template #title>
                  <div class="answer-title">
                    <el-tag :type="getAnswerTagType(answer.assistant_type)" size="small">
                      {{ getAnswerTypeName(answer.assistant_type) }}
                    </el-tag>
                    <el-tag v-if="answer.is_scored" type="success" size="small">已评分</el-tag>
                    <el-tag v-else type="warning" size="small">未评分</el-tag>
                    <span class="answer-time">{{ formatTime(answer.created_at) }}</span>
                  </div>
                </template>

                <div class="answer-content">
                  <div class="answer-text">
                    {{ answer.answer_text }}
                  </div>

                  <!-- 评分信息 -->
                  <div v-if="answer.score" class="score-section">
                    <el-divider content-position="left">评分详情</el-divider>
                    <el-row :gutter="16">
                      <el-col :span="4">
                        <el-statistic
                          title="综合评分"
                          :value="answer.score.average_score"
                          :precision="2"
                          suffix="分"
                        />
                      </el-col>
                      <el-col :span="20">
                        <div class="dimensions-scores">
                          <el-tag
                            v-for="(score, dimension) in answer.score.dimensions"
                            :key="dimension"
                            :type="getScoreTagType(score)"
                            size="small"
                            class="dimension-tag"
                          >
                            {{ dimension }}: {{ score }}分
                          </el-tag>
                        </div>
                      </el-col>
                    </el-row>
                    <div v-if="answer.score.comment" class="score-comment">
                      <strong>评分理由：</strong>{{ answer.score.comment }}
                    </div>
                  </div>

                  <!-- 评分历史 -->
                  <div v-if="answer.score_history && answer.score_history.length > 1" class="score-history">
                    <el-divider content-position="left">评分历史</el-divider>
                    <el-timeline>
                      <el-timeline-item
                        v-for="(score, index) in answer.score_history"
                        :key="score.id"
                        :timestamp="formatTime(score.rated_at)"
                        :type="index === 0 ? 'primary' : 'info'"
                      >
                        <div class="history-item">
                          <span>综合评分: {{ score.average_score }}分</span>
                          <div v-if="score.comment" class="history-comment">{{ score.comment }}</div>
                        </div>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>

        <!-- 审核状态卡片 -->
        <el-card v-if="detailDrawer.data.review_status" class="info-card" shadow="never">
          <template #header>
            <span>👥 审核状态</span>
          </template>
          <el-descriptions :column="2" size="small">
            <el-descriptions-item label="审核状态">
              <el-tag :type="detailDrawer.data.review_status.is_reviewed ? 'success' : 'warning'">
                {{ detailDrawer.data.review_status.is_reviewed ? '已审核' : '待审核' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审核人员">
              {{ detailDrawer.data.review_status.reviewer_id || '未指定' }}
            </el-descriptions-item>
            <el-descriptions-item label="审核时间" :span="2">
              {{ detailDrawer.data.review_status.reviewed_at ? formatTime(detailDrawer.data.review_status.reviewed_at) : '未审核' }}
            </el-descriptions-item>
            <el-descriptions-item v-if="detailDrawer.data.review_status.review_comment" label="审核备注" :span="2">
              {{ detailDrawer.data.review_status.review_comment }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- Badcase信息卡片 -->
        <el-card v-if="detailDrawer.data.is_badcase" class="info-card badcase-card" shadow="never">
          <template #header>
            <span>⚠️ Badcase信息</span>
          </template>
          <el-descriptions :column="2" size="small">
            <el-descriptions-item label="检测时间">
              {{ formatTime(detailDrawer.data.badcase_detected_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="复核状态">
              <el-tag :type="getBadcaseReviewTagType(detailDrawer.data.badcase_review_status)">
                {{ getBadcaseReviewText(detailDrawer.data.badcase_review_status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="detailDrawer.data.badcase_dimensions" label="问题维度" :span="2">
              {{ detailDrawer.data.badcase_dimensions }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>
    </el-dialog>

    <!-- 重新分类对话框 -->
    <el-dialog
      v-model="reclassifyDialog.visible"
      title="重新分类"
      width="480px"
    >
      <el-form label-width="90px">
        <el-form-item label="新分类">
          <el-select v-model="reclassifyDialog.newClassification" placeholder="请选择" style="width: 300px">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注(可选)">
          <el-input v-model="reclassifyDialog.reason" type="textarea" rows="3" placeholder="填写重新分类的原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reclassifyDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitReclassify">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getQuestions,
  getQuestionDetail,
  reclassifyQuestion,
  exportQuestions,
  getQuestionCategories
} from '@/api/questions'
import { getStats } from '@/api/dashboard'
import {
  Refresh,
  ChatDotRound,
  Flag,
  Star,
  ArrowUp,
  ArrowDown,
  Document,
  Search,
  Download
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

export default {
  name: 'Questions',
  components: {
    Refresh,
    ChatDotRound,
    Flag,
    Star,
    ArrowUp,
    ArrowDown,
    Document,
    Search,
    Download
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const exportLoading = ref(false)
    const statsLoading = ref(false)
    const tableData = ref([])
    const categories = ref([])
    const timeRange = ref('all')  // 默认选择总计

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

    // 搜索表单
    const searchForm = reactive({
      keyword: '',
      classification: '',
      status: '',
      dateRange: null
    })

    // 分页数据
    const pagination = reactive({
      page: 1,
      pageSize: 20,
      total: 0
    })

    // 详情弹窗
    const detailDrawer = reactive({
      visible: false,
      data: null,
      answers: []
    })

    // 答案折叠面板激活项
    const activeAnswers = ref([])

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
        statsLoading.value = true
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
        statsLoading.value = false
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

    // 加载问题列表
    const loadQuestions = async () => {
      try {
        loading.value = true
        
        const params = {
          page: pagination.page,
          page_size: pagination.pageSize,
          ...searchForm
        }

        // 处理日期范围
        if (searchForm.dateRange && searchForm.dateRange.length === 2) {
          params.start_time = dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD HH:mm:ss')
          params.end_time = dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD HH:mm:ss')
        }

        const res = await getQuestions(params)
        
        if (res.success) {
          tableData.value = res.data || []
          pagination.total = res.total || 0
        }
      } catch (error) {
        console.error('加载问题列表失败:', error)
        ElMessage.error('加载数据失败')
      } finally {
        loading.value = false
      }
    }

    // 加载分类列表
    const loadCategories = async () => {
      try {
        console.log('开始加载分类列表...')
        const res = await getQuestionCategories()
        console.log('分类列表响应:', res)

        if (res.success) {
          categories.value = res.data || []
          console.log('分类列表加载成功:', categories.value)
        } else {
          console.error('分类列表加载失败:', res.message)
          ElMessage.error(res.message || '加载分类列表失败')
        }
      } catch (error) {
        console.error('加载分类列表失败:', error)
        ElMessage.error('加载分类列表失败')
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      loadQuestions()
    }

    // 重置搜索
    const handleReset = () => {
      Object.assign(searchForm, {
        keyword: '',
        classification: '',
        status: '',
        dateRange: null
      })
      pagination.page = 1
      loadQuestions()
    }

    // 分页大小变更
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      pagination.page = 1
      loadQuestions()
    }

    // 当前页变更
    const handleCurrentChange = (page) => {
      pagination.page = page
      loadQuestions()
    }

    // 查看详情 - 增强版
    const handleViewDetail = async (row) => {
      try {
        const res = await getQuestionDetail(row.id)
        if (res.success) {
          detailDrawer.data = res.data
          detailDrawer.answers = res.data.answers || []
          detailDrawer.visible = true
          // 默认展开第一个答案
          if (res.data.answers && res.data.answers.length > 0) {
            activeAnswers.value = [res.data.answers[0].id.toString()]
          }
        }
      } catch (error) {
        console.error('获取问题详情失败:', error)
        ElMessage.error('获取详情失败')
      }
    }

    // 重新分类对话框
    const reclassifyDialog = reactive({
      visible: false,
      targetRow: null,
      newClassification: '',
      reason: ''
    })

    const openReclassifyDialog = (row) => {
      console.log('打开重新分类对话框:', { row, categories: categories.value })

      // 确保分类数据已加载
      if (categories.value.length === 0) {
        loadCategories()
      }

      reclassifyDialog.targetRow = row
      reclassifyDialog.newClassification = ''
      reclassifyDialog.reason = ''
      reclassifyDialog.visible = true
    }

    const submitReclassify = async () => {
      try {
        if (!reclassifyDialog.newClassification) {
          ElMessage.warning('请选择新的分类')
          return
        }

        if (!reclassifyDialog.targetRow) {
          ElMessage.error('未找到要重新分类的问题')
          return
        }

        console.log('开始重新分类:', {
          newClassification: reclassifyDialog.newClassification,
          reason: reclassifyDialog.reason,
          targetRow: reclassifyDialog.targetRow
        })

        reclassifyDialog.targetRow.reclassifying = true
        const result = await reclassifyQuestion(reclassifyDialog.targetRow.id, {
          new_classification: reclassifyDialog.newClassification,
          reason: reclassifyDialog.reason
        })
        console.log('重新分类结果:', result)

        ElMessage.success('重新分类成功')
        reclassifyDialog.visible = false
        loadQuestions()
      } catch (error) {
        console.error('重新分类失败:', error)
        let msg = '重新分类失败'

        if (error.response && error.response.data) {
          msg = error.response.data.message || msg
        } else if (error.message) {
          msg = error.message
        }

        ElMessage.error(msg)
      } finally {
        if (reclassifyDialog.targetRow) {
          reclassifyDialog.targetRow.reclassifying = false
        }
      }
    }

    // 导出数据
    const handleExport = async () => {
      try {
        exportLoading.value = true
        
        const params = { ...searchForm }
        if (searchForm.dateRange && searchForm.dateRange.length === 2) {
          params.start_time = dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD HH:mm:ss')
          params.end_time = dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD HH:mm:ss')
        }

        const res = await exportQuestions(params)
        
        // 创建下载链接
        const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `questions_${dayjs().format('YYYY-MM-DD_HH-mm-ss')}.xlsx`
        link.click()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败')
      } finally {
        exportLoading.value = false
      }
    }

    // 格式化时间
    const formatTime = (time) => {
      return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        pending: 'info',
        classified: 'warning',
        answers_generated: 'primary',
        scored: 'success',
        completed: 'success'
      }
      return statusMap[status] || 'info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        pending: '待处理',
        classified: '已分类',
        answers_generated: '已生成答案',
        scored: '已评分',
        completed: '已完成'
      }
      return statusMap[status] || '未知'
    }

    // 获取答案类型标签颜色
    const getAnswerTagType = (type) => {
      const typeMap = {
        yoyo: 'info',
        doubao: 'primary',
        xiaotian: 'success'
      }
      return typeMap[type] || 'info'
    }

    // 获取答案类型名称
    const getAnswerTypeName = (type) => {
      const nameMap = {
        yoyo: '自研AI',
        doubao: '豆包',
        xiaotian: '小天'
      }
      return nameMap[type] || type
    }

    // 获取整体平均分
    const getOverallAvgScore = (avgScores) => {
      if (!avgScores || Object.keys(avgScores).length === 0) return 0
      const scores = Object.values(avgScores)
      return scores.reduce((sum, score) => sum + score, 0) / scores.length
    }

    // 获取评分标签类型
    const getScoreTagType = (score) => {
      if (score >= 4) return 'success'
      if (score >= 3) return 'warning'
      return 'danger'
    }

    // 获取Badcase复核状态标签类型
    const getBadcaseReviewTagType = (status) => {
      const typeMap = {
        'pending': 'warning',
        'reviewed': 'success',
        'rejected': 'danger'
      }
      return typeMap[status] || 'info'
    }

    // 获取Badcase复核状态文本
    const getBadcaseReviewText = (status) => {
      const textMap = {
        'pending': '待复核',
        'reviewed': '已复核',
        'rejected': '已驳回'
      }
      return textMap[status] || status
    }

    // 组件挂载
    onMounted(async () => {
      await loadStats()
      await loadQuestions()
      await loadCategories()
    })

    return {
      loading,
      exportLoading,
      statsLoading,
      tableData,
      categories,
      searchForm,
      pagination,
      detailDrawer,
      activeAnswers,
      timeRange,
      stats,
      loadQuestions,
      loadStats,
      handleTimeRangeChange,
      refreshStats,
      handleSearch,
      handleReset,
      handleSizeChange,
      handleCurrentChange,
      handleViewDetail,
      reclassifyDialog,
      openReclassifyDialog,
      submitReclassify,
      handleExport,
      formatTime,
      getStatusType,
      getStatusText,
      getAnswerTagType,
      getAnswerTypeName,
      getOverallAvgScore,
      getScoreTagType,
      getBadcaseReviewTagType,
      getBadcaseReviewText
    }
  }
}
</script>

<style lang="scss" scoped>
.questions {
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

  .filter-card,
  .toolbar-card,
  .table-card {
    margin-bottom: 20px;
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .toolbar-left,
    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }

  .question-content {
    .el-text {
      line-height: 1.4;
    }
  }

  .pagination-wrapper {
    margin-top: 20px;
    text-align: right;
  }

  .detail-content {
    padding: 0 20px;

    .question-detail {
      .question-text {
        padding: 15px;
        background-color: #f5f7fa;
        border-radius: 6px;
        border-left: 4px solid #409eff;
        line-height: 1.6;
        margin-top: 10px;
      }
    }

    .answers-section {
      .answer-item {
        margin-bottom: 20px;
        border: 1px solid #e4e7ed;
        border-radius: 6px;
        overflow: hidden;

        .answer-header {
          padding: 12px 15px;
          background-color: #f5f7fa;
          border-bottom: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-between;
          align-items: center;

          .answer-time {
            font-size: 12px;
            color: #909399;
          }
        }

        .answer-content {
          padding: 15px;
          line-height: 1.6;
          color: #606266;
        }
      }
    }
  }

  // 问题详情弹窗增强样式
  .info-card {
    margin-bottom: 16px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
  }

  .question-text {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    line-height: 1.6;
    white-space: pre-wrap;
    border-left: 4px solid #409eff;
    font-size: 14px;
  }

  .answers-container {
    .answer-title {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;

      .answer-time {
        margin-left: auto;
        color: #909399;
        font-size: 12px;
      }
    }
  }

  .answer-content {
    .answer-text {
      background: #f8f9fa;
      padding: 16px;
      border-radius: 8px;
      line-height: 1.6;
      white-space: pre-wrap;
      margin-bottom: 16px;
      border-left: 3px solid #67c23a;
    }

    .score-section {
      margin-top: 16px;

      .dimensions-scores {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .dimension-tag {
          margin: 0;
        }
      }

      .score-comment {
        margin-top: 12px;
        padding: 12px;
        background: #f0f9ff;
        border-radius: 6px;
        font-size: 13px;
        line-height: 1.5;
      }
    }

    .score-history {
      margin-top: 16px;

      .history-item {
        .history-comment {
          margin-top: 4px;
          font-size: 12px;
          color: #666;
        }
      }
    }
  }

  .badcase-card {
    border-left: 4px solid #f56c6c !important;

    :deep(.el-card__header) {
      background: #fef0f0;
    }
  }
}

// 问题详情弹窗样式
.question-detail-dialog {
  .detail-content {
    max-height: 70vh;
    overflow-y: auto;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .question-detail-dialog {
    width: 95% !important;
  }
}
</style>