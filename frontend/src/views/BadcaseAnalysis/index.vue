<template>
  <div class="badcase-analysis">
    <div class="page-header">
      <h1>🔍 Badcase 分析及优化</h1>
      <p class="page-description">基于YOYO模型评分的问题案例分析与人工复核</p>
    </div>

    <!-- 统计概览 -->
    <StatisticsCard :statistics="statistics" />

    <!-- 维度分析 -->
    <DimensionAnalysis
      :categories="categories"
    />

    <!-- Badcase列表 -->
    <BadcaseList
      :badcase-list="badcaseList"
      :loading="loading"
      :total="total"
      :categories="categories"
      @search="handleSearch"
      @status-filter="handleStatusFilter"
      @category-filter="handleCategoryFilter"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
      @view-detail="handleViewDetail"
      @review-case="handleReviewCase"
      @view-review="handleViewReview"
    />

    <!-- 详情弹窗 -->
    <DetailModal
      v-model:visible="detailVisible"
      :badcase-detail="currentDetail"
      @start-review="handleStartReview"
    />

    <!-- 复核弹窗 -->
    <ReviewModal
      v-model:visible="reviewVisible"
      :badcase-data="currentReviewData"
      :threshold="badcaseThreshold"
      @submit-review="handleSubmitReview"
    />

    <!-- Badcase详情弹窗 -->
    <BadcaseDetailModal
      v-model:visible="detailVisible"
      :question-id="currentDetailId"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import StatisticsCard from './components/StatisticsCard.vue'
import DimensionAnalysis from './components/DimensionAnalysis.vue'
import BadcaseList from './components/BadcaseList.vue'
import DetailModal from './components/DetailModal.vue'
import ReviewModal from './components/ReviewModal.vue'
import BadcaseDetailModal from './components/BadcaseDetailModal.vue'
import { getBadcaseStatistics, getBadcaseList, getBadcaseDetail, submitBadcaseReview, getBadcaseCategories } from '@/api/badcase'

export default {
  name: 'BadcaseAnalysis',
  components: {
    StatisticsCard,
    DimensionAnalysis,
    BadcaseList,
    DetailModal,
    ReviewModal,
    BadcaseDetailModal
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const statistics = ref({
      totalQuestions: 0,
      badcaseCount: 0,
      badcaseRatio: 0,
      pendingCount: 0,
      reviewedCount: 0,
      misjudgedCount: 0,
      reviewRate: 0
    })
    
    const badcaseList = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const searchKeyword = ref('')
    const statusFilter = ref('')
    const categoryFilter = ref('')
    const categories = ref([])
    
    // 弹窗相关
    const detailVisible = ref(false)
    const reviewVisible = ref(false)
    const currentDetail = ref(null)
    const currentReviewData = ref(null)
    const currentDetailId = ref(null)
    const badcaseThreshold = ref(2.5)

    // 加载本周统计数据
    const loadWeeklyStatistics = async () => {
      try {
        const response = await getBadcaseStatistics({ time_range: 'week' })
        if (response.success) {
          const data = response.data
          statistics.value = {
            totalQuestions: data.total_questions || 0,
            badcaseCount: data.badcase_count || 0,
            badcaseRatio: data.badcase_ratio || 0,
            pendingCount: data.pending_count || 0,
            reviewedCount: data.reviewed_count || 0,
            misjudgedCount: data.misjudged_count || 0,
            reviewRate: data.review_rate || 0
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      }
    }

    // 加载分类数据
    const loadCategories = async () => {
      try {
        const response = await getBadcaseCategories()
        if (response.success) {
          categories.value = response.data || []
        }
      } catch (error) {
        console.error('加载分类数据失败:', error)
        // 使用默认的16个分类
        categories.value = [
          { value: '技术问题', label: '技术问题' },
          { value: '产品使用', label: '产品使用' },
          { value: '业务咨询', label: '业务咨询' },
          { value: '功能建议', label: '功能建议' },
          { value: '故障排查', label: '故障排查' },
          { value: '其他', label: '其他' },
          { value: '工程问题', label: '工程问题' },
          { value: '科学问题', label: '科学问题' },
          { value: '教育问题', label: '教育问题' },
          { value: '经济问题', label: '经济问题' },
          { value: '账户管理', label: '账户管理' },
          { value: '系统优化', label: '系统优化' },
          { value: '安全设置', label: '安全设置' },
          { value: '数据分析', label: '数据分析' },
          { value: '用户体验', label: '用户体验' },
          { value: '性能优化', label: '性能优化' }
        ]
      }
    }

    // 加载badcase列表
    const loadBadcaseList = async () => {
      try {
        loading.value = true
        const params = {
          time_range: 'all', // 显示所有时间的badcase
          page: currentPage.value,
          page_size: pageSize.value
        }
        
        if (statusFilter.value) {
          params.status = statusFilter.value
        }

        if (categoryFilter.value) {
          params.category = categoryFilter.value
        }

        if (searchKeyword.value.trim()) {
          params.search = searchKeyword.value.trim()
        }
        
        const response = await getBadcaseList(params)
        if (response.success) {
          const data = response.data
          badcaseList.value = data.list || []
          total.value = data.total || 0
        }
      } catch (error) {
        console.error('加载badcase列表失败:', error)
        ElMessage.error('加载badcase列表失败')
      } finally {
        loading.value = false
      }
    }

    // 事件处理
    const handleSearch = (keyword) => {
      searchKeyword.value = keyword
      currentPage.value = 1
      loadBadcaseList()
    }

    const handleStatusFilter = (status) => {
      statusFilter.value = status
      currentPage.value = 1
      loadBadcaseList()
    }

    const handleCategoryFilter = (category) => {
      categoryFilter.value = category
      currentPage.value = 1
      loadBadcaseList()
    }

    const handlePageChange = (page) => {
      currentPage.value = page
      loadBadcaseList()
    }

    const handlePageSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      loadBadcaseList()
    }

    const handleViewDetail = (row) => {
      currentDetailId.value = row.id
      detailVisible.value = true
    }

    const handleViewReview = (row) => {
      currentDetailId.value = row.id
      detailVisible.value = true
    }

    const handleReviewCase = (row) => {
      currentReviewData.value = row
      reviewVisible.value = true
    }

    const handleStartReview = (badcaseDetail) => {
      detailVisible.value = false
      currentReviewData.value = badcaseDetail
      reviewVisible.value = true
    }

    const handleSubmitReview = async (reviewData) => {
      try {
        const response = await submitBadcaseReview(reviewData.question_id, {
          scores: reviewData.scores,
          comment: reviewData.comment,
          review_result: reviewData.review_result,
          average_score: reviewData.average_score
        })

        if (response.success) {
          ElMessage.success('复核提交成功')
          reviewVisible.value = false

          // 刷新列表和统计数据
          await Promise.all([
            loadBadcaseList(),
            loadWeeklyStatistics()
          ])
        } else {
          ElMessage.error(response.message || '复核提交失败')
        }
      } catch (error) {
        console.error('提交复核失败:', error)
        ElMessage.error('提交复核失败')
      }
    }

    // 生命周期
    onMounted(() => {
      loadWeeklyStatistics()
      loadBadcaseList()
      loadCategories()
    })

    return {
      loading,
      statistics,
      badcaseList,
      total,
      categories,
      detailVisible,
      reviewVisible,
      currentDetail,
      currentReviewData,
      currentDetailId,
      badcaseThreshold,
      handleSearch,
      handleStatusFilter,
      handleCategoryFilter,
      handlePageChange,
      handlePageSizeChange,
      handleViewDetail,
      handleReviewCase,
      handleViewReview,
      handleStartReview,
      handleSubmitReview
    }
  }
}
</script>

<style lang="scss" scoped>
.badcase-analysis {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #303133;
    }

    .page-description {
      margin: 0;
      color: #606266;
      font-size: 14px;
    }
  }
}
</style>
