<template>
  <el-card class="badcase-list-card">
    <template #header>
      <div class="card-header">
        <span>Badcase案例列表</span>
        <div class="header-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索问题内容..."
            style="width: 200px; margin-right: 10px;"
            clearable
            @change="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select
            v-model="statusFilter"
            placeholder="筛选状态"
            style="width: 120px; margin-right: 10px;"
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="待处理" value="pending" />
            <el-option label="已复核" value="reviewed" />
          </el-select>

          <el-select
            v-model="categoryFilter"
            placeholder="筛选分类"
            style="width: 140px;"
            clearable
            @change="handleCategoryFilter"
          >
            <el-option
              v-for="category in categories"
              :key="category.value"
              :label="category.label"
              :value="category.value"
            />
          </el-select>
        </div>
      </div>
    </template>

    <el-table
      :data="badcaseList"
      :loading="loading"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="query" label="问题内容" min-width="250" show-overflow-tooltip />
      
      <el-table-column label="YOYO答案" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.yoyo_answer || '暂无答案' }}
        </template>
      </el-table-column>

      <el-table-column label="低分维度" min-width="200">
        <template #default="{ row }">
          <div class="low-dimensions">
            <el-tag
              v-for="dim in (row.low_score_dimensions || [])"
              :key="dim.dimension_name"
              type="danger"
              size="small"
              class="dimension-tag"
            >
              {{ dim.dimension_name }}: {{ dim.score }}/5
            </el-tag>
            <span v-if="!row.low_score_dimensions || row.low_score_dimensions.length === 0" class="no-data">
              暂无数据
            </span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="classification" label="分类" width="120" />
      
      <el-table-column label="复核状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.review_status)">
            {{ getStatusText(row.review_status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="复核人员" width="120">
        <template #default="{ row }">
          <span v-if="row.reviewer_name" class="reviewer-name">
            {{ row.reviewer_name }}
          </span>
          <span v-else class="no-reviewer">-</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="detected_at" label="检测时间" width="150">
        <template #default="{ row }">
          {{ formatDate(row.detected_at) }}
        </template>
      </el-table-column>
      
      <!-- 复核时间：仅在已复核筛选时显示 -->
      <el-table-column v-if="statusFilter === 'reviewed'" prop="reviewed_at" label="复核时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.reviewed_at) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">
            详情
          </el-button>
          <el-button 
            v-if="row.review_status === 'pending'"
            type="warning" 
            size="small" 
            @click="reviewCase(row)"
          >
            复核
          </el-button>
          <el-button 
            v-else
            type="success" 
            size="small" 
            @click="viewReview(row)"
          >
            查看复核
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </el-card>
</template>

<script>
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'BadcaseList',
  components: {
    Search
  },
  props: {
    badcaseList: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    total: {
      type: Number,
      default: 0
    },
    categories: {
      type: Array,
      default: () => []
    }
  },
  emits: ['search', 'status-filter', 'category-filter', 'page-change', 'page-size-change', 'view-detail', 'review-case', 'view-review'],
  data() {
    return {
      searchKeyword: '',
      statusFilter: '',
      categoryFilter: '',
      currentPage: 1,
      pageSize: 20
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', this.searchKeyword)
    },
    
    handleStatusFilter() {
      this.$emit('status-filter', this.statusFilter)
    },

    handleCategoryFilter() {
      this.$emit('category-filter', this.categoryFilter)
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.$emit('page-change', page)
    },
    
    handlePageSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.$emit('page-size-change', size)
    },
    
    viewDetail(row) {
      this.$emit('view-detail', row)
    },
    
    reviewCase(row) {
      this.$emit('review-case', row)
    },
    
    viewReview(row) {
      this.$emit('view-review', row)
    },
    
    getStatusTagType(status) {
      const typeMap = {
        pending: 'warning',
        reviewed: 'primary',
        optimized: 'success'
      }
      return typeMap[status] || 'info'
    },
    
    getStatusText(status) {
      const textMap = {
        pending: '待处理',
        reviewed: '已复核',
        optimized: '已优化'
      }
      return textMap[status] || status
    },
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style lang="scss" scoped>
.badcase-list-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    span {
      font-weight: bold;
      color: #303133;
    }

    .header-actions {
      display: flex;
      align-items: center;
    }
  }

  .low-dimensions {
    .dimension-tag {
      margin-right: 5px;
      margin-bottom: 3px;
    }
  }

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }

  .reviewer-name {
    color: #409EFF;
    font-weight: 500;
  }

  .no-reviewer {
    color: #C0C4CC;
  }
}
</style>
