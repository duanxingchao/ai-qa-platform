<template>
  <div class="questions">
    <div class="page-header">
      <h1>问题管理</h1>
      <p class="page-description">查看和管理所有问题数据</p>
    </div>

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
            <el-option label="已生成答案" value="answered" />
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
            type="primary"
            :disabled="selectedIds.length === 0"
            @click="handleBatchClassify"
          >
            <el-icon><Magic /></el-icon>
            批量重新分类
          </el-button>
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
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
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
              @click="handleReclassify(scope.row)"
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

    <!-- 问题详情抽屉 -->
    <el-drawer
      v-model="detailDrawer.visible"
      title="问题详情"
      direction="rtl"
      size="60%"
    >
      <div v-if="detailDrawer.data" class="detail-content">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="ID">
            {{ detailDrawer.data.id }}
          </el-descriptions-item>
          <el-descriptions-item label="业务ID">
            {{ detailDrawer.data.business_id }}
          </el-descriptions-item>
          <el-descriptions-item label="页面ID">
            {{ detailDrawer.data.pageid }}
          </el-descriptions-item>
          <el-descriptions-item label="设备类型">
            {{ detailDrawer.data.devicetypename }}
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag v-if="detailDrawer.data.classification">
              {{ detailDrawer.data.classification }}
            </el-tag>
            <span v-else>未分类</span>
          </el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <el-tag :type="getStatusType(detailDrawer.data.processing_status)">
              {{ getStatusText(detailDrawer.data.processing_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatTime(detailDrawer.data.sendmessagetime) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="question-detail">
          <h4>问题内容</h4>
          <div class="question-text">
            {{ detailDrawer.data.query }}
          </div>
        </div>

        <el-divider />

        <div class="answers-section">
          <h4>相关答案</h4>
          <el-empty v-if="detailDrawer.answers.length === 0" description="暂无答案数据" />
          <div v-else>
            <div
              v-for="answer in detailDrawer.answers"
              :key="answer.id"
              class="answer-item"
            >
              <div class="answer-header">
                <el-tag :type="getAnswerTagType(answer.assistant_type)">
                  {{ getAnswerTypeName(answer.assistant_type) }}
                </el-tag>
                <span class="answer-time">{{ formatTime(answer.created_at) }}</span>
              </div>
              <div class="answer-content">
                {{ answer.answer_text }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getQuestions,
  getQuestionDetail,
  reclassifyQuestion,
  batchUpdateQuestions,
  exportQuestions,
  getQuestionCategories
} from '@/api/questions'
import dayjs from 'dayjs'

export default {
  name: 'Questions',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const exportLoading = ref(false)
    const tableData = ref([])
    const selectedIds = ref([])
    const categories = ref([])

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

    // 详情抽屉
    const detailDrawer = reactive({
      visible: false,
      data: null,
      answers: []
    })

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
        const res = await getQuestionCategories()
        if (res.success) {
          categories.value = res.data || []
        }
      } catch (error) {
        console.error('加载分类列表失败:', error)
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

    // 选择变更
    const handleSelectionChange = (selection) => {
      selectedIds.value = selection.map(item => item.id)
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

    // 查看详情
    const handleViewDetail = async (row) => {
      try {
        const res = await getQuestionDetail(row.id)
        if (res.success) {
          detailDrawer.data = res.data
          detailDrawer.answers = res.data.answers || []
          detailDrawer.visible = true
        }
      } catch (error) {
        console.error('获取问题详情失败:', error)
        ElMessage.error('获取详情失败')
      }
    }

    // 重新分类
    const handleReclassify = async (row) => {
      try {
        row.reclassifying = true
        await reclassifyQuestion(row.id)
        ElMessage.success('重新分类成功')
        loadQuestions()
      } catch (error) {
        console.error('重新分类失败:', error)
        ElMessage.error('重新分类失败')
      } finally {
        row.reclassifying = false
      }
    }

    // 批量重新分类
    const handleBatchClassify = async () => {
      try {
        await ElMessageBox.confirm(
          `确定要对选中的 ${selectedIds.value.length} 个问题进行重新分类吗？`,
          '批量操作确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await batchUpdateQuestions({
          ids: selectedIds.value,
          action: 'reclassify'
        })

        ElMessage.success('批量重新分类成功')
        loadQuestions()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量重新分类失败:', error)
          ElMessage.error('批量操作失败')
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
        answered: 'primary',
        scored: 'success'
      }
      return statusMap[status] || 'info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        pending: '待处理',
        classified: '已分类',
        answered: '已生成答案',
        scored: '已评分'
      }
      return statusMap[status] || '未知'
    }

    // 获取答案类型标签颜色
    const getAnswerTagType = (type) => {
      const typeMap = {
        original: 'info',
        doubao: 'primary',
        xiaotian: 'success'
      }
      return typeMap[type] || 'info'
    }

    // 获取答案类型名称
    const getAnswerTypeName = (type) => {
      const nameMap = {
        original: '原始答案',
        doubao: '豆包答案',
        xiaotian: '小天答案'
      }
      return nameMap[type] || type
    }

    // 组件挂载
    onMounted(() => {
      loadQuestions()
      loadCategories()
    })

    return {
      loading,
      exportLoading,
      tableData,
      selectedIds,
      categories,
      searchForm,
      pagination,
      detailDrawer,
      loadQuestions,
      handleSearch,
      handleReset,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      handleViewDetail,
      handleReclassify,
      handleBatchClassify,
      handleExport,
      formatTime,
      getStatusType,
      getStatusText,
      getAnswerTagType,
      getAnswerTypeName
    }
  }
}
</script>

<style lang="scss" scoped>
.questions {
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
}
</style> 