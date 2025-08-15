<template>
  <div class="application-management">
    <div class="page-header">
      <h2>📋 用户申请审核</h2>
      <p>管理用户注册申请，审核通过后用户可正常使用系统</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.username"
            placeholder="搜索用户名"
            prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="searchForm.apply_role"
            placeholder="申请角色"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="searchForm.status"
            placeholder="申请状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="待审核" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 批量操作 -->
    <el-card class="batch-operations" shadow="never" v-if="selectedApplications.length > 0">
      <el-alert
        :title="`已选择 ${selectedApplications.length} 个申请`"
        type="info"
        show-icon
        :closable="false"
      >
        <template #default>
          <div class="batch-buttons">
            <el-button type="success" size="small" @click="batchApprove">
              <el-icon><Check /></el-icon>
              批量批准
            </el-button>
            <el-button type="danger" size="small" @click="batchReject">
              <el-icon><Close /></el-icon>
              批量拒绝
            </el-button>
          </div>
        </template>
      </el-alert>
    </el-card>

    <!-- 申请列表 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>申请列表</span>
          <el-button type="text" @click="loadApplications">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="applications"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="username" label="登录账号" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.username }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="display_name" label="用户名" width="150">
          <template #default="{ row }">
            <span class="display-name">{{ row.display_name || row.username }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="apply_role" label="申请角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.apply_role === 'admin' ? 'danger' : 'primary'">
              {{ row.apply_role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              effect="light"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="{ row }">
            {{ row.created_at ? formatDateTime(row.created_at) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="processed_at" label="处理时间" width="180">
          <template #default="{ row }">
            {{ row.processed_at ? formatDateTime(row.processed_at) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                v-if="row.status === 'pending'"
                type="success"
                size="small"
                @click="approveApplication(row)"
              >
                <el-icon><Check /></el-icon>
                批准
              </el-button>
              <el-button
                v-if="row.status === 'pending'"
                type="danger"
                size="small"
                @click="rejectApplication(row)"
              >
                <el-icon><Close /></el-icon>
                拒绝
              </el-button>
              <el-button
                type="info"
                size="small"
                @click="viewApplication(row)"
              >
                <el-icon><View /></el-icon>
                详情
              </el-button>
            </div>
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

    <!-- 申请详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="申请详情"
      width="600px"
    >
      <div v-if="currentApplication" class="application-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="登录账号">
            {{ currentApplication.username }}
          </el-descriptions-item>
          <el-descriptions-item label="用户名">
            {{ currentApplication.display_name || currentApplication.username }}
          </el-descriptions-item>
          <el-descriptions-item label="申请角色">
            <el-tag :type="currentApplication.apply_role === 'admin' ? 'danger' : 'primary'">
              {{ currentApplication.apply_role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申请状态">
            <el-tag :type="getStatusType(currentApplication.status)">
              {{ getStatusText(currentApplication.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申请时间">
            {{ formatDateTime(currentApplication.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="处理时间" v-if="currentApplication.processed_at">
            {{ formatDateTime(currentApplication.processed_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button
            v-if="currentApplication?.status === 'pending'"
            type="success"
            @click="approveApplication(currentApplication)"
          >
            批准申请
          </el-button>
          <el-button
            v-if="currentApplication?.status === 'pending'"
            type="danger"
            @click="rejectApplication(currentApplication)"
          >
            拒绝申请
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Check,
  Close,
  View
} from '@element-plus/icons-vue'
import { getApplications, approveApplication as approveApp, rejectApplication as rejectApp } from '@/api/admin'
import { formatDateTime } from '@/utils/datetime'

export default {
  name: 'ApplicationManagement',
  components: {
    Search,
    Refresh,
    Check,
    Close,
    View
  },
  setup() {
    const loading = ref(false)
    const applications = ref([])
    const selectedApplications = ref([])
    const detailDialogVisible = ref(false)
    const currentApplication = ref(null)
    
    // 搜索表单
    const searchForm = reactive({
      username: '',
      apply_role: '',
      status: ''
    })
    
    // 分页
    const pagination = reactive({
      page: 1,
      pageSize: 20,
      total: 0
    })
    
    // 加载申请列表
    const loadApplications = async () => {
      try {
        loading.value = true
        console.log('开始加载申请列表...')
        const response = await getApplications({
          ...searchForm,
          page: pagination.page,
          page_size: pagination.pageSize
        })

        console.log('API响应:', response)

        if (response.success) {
          applications.value = response.data.applications || []
          pagination.total = response.data.total || 0
          console.log('加载成功，申请数量:', applications.value.length)
        } else {
          console.error('API返回失败:', response.message)
          ElMessage.error('加载申请列表失败: ' + response.message)
        }
      } catch (error) {
        console.error('加载申请列表失败:', error)
        ElMessage.error('加载申请列表失败: ' + (error.message || '网络错误'))
      } finally {
        loading.value = false
      }
    }
    
    // 搜索处理
    const handleSearch = () => {
      pagination.page = 1
      loadApplications()
    }
    
    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      handleSearch()
    }
    
    // 选择变化
    const handleSelectionChange = (selection) => {
      selectedApplications.value = selection
    }
    
    // 批准申请
    const approveApplication = async (application) => {
      try {
        await ElMessageBox.confirm(
          `确认批准用户 "${application.display_name || application.username}" (${application.username}) 的${application.apply_role === 'admin' ? '管理员' : '普通用户'}申请？`,
          '确认批准',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'success'
          }
        )
        
        const response = await approveApp(application.id)
        if (response.success) {
          ElMessage.success('申请已批准')
          detailDialogVisible.value = false
          loadApplications()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批准申请失败:', error)
        }
      }
    }
    
    // 拒绝申请
    const rejectApplication = async (application) => {
      try {
        await ElMessageBox.confirm(
          `确认拒绝用户 "${application.username}" 的申请？`,
          '确认拒绝',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await rejectApp(application.id)
        if (response.success) {
          ElMessage.success('申请已拒绝')
          detailDialogVisible.value = false
          loadApplications()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('拒绝申请失败:', error)
        }
      }
    }
    
    // 批量批准
    const batchApprove = async () => {
      const pendingApps = selectedApplications.value.filter(app => app.status === 'pending')
      if (pendingApps.length === 0) {
        ElMessage.warning('请选择待审核的申请')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          `确认批准选中的 ${pendingApps.length} 个申请？`,
          '批量批准',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'success'
          }
        )
        
        for (const app of pendingApps) {
          await approveApp(app.id)
        }
        
        ElMessage.success(`已批准 ${pendingApps.length} 个申请`)
        selectedApplications.value = []
        loadApplications()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量批准失败:', error)
        }
      }
    }
    
    // 批量拒绝
    const batchReject = async () => {
      const pendingApps = selectedApplications.value.filter(app => app.status === 'pending')
      if (pendingApps.length === 0) {
        ElMessage.warning('请选择待审核的申请')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          `确认拒绝选中的 ${pendingApps.length} 个申请？`,
          '批量拒绝',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        for (const app of pendingApps) {
          await rejectApp(app.id)
        }
        
        ElMessage.success(`已拒绝 ${pendingApps.length} 个申请`)
        selectedApplications.value = []
        loadApplications()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量拒绝失败:', error)
        }
      }
    }
    
    // 查看详情
    const viewApplication = (application) => {
      currentApplication.value = application
      detailDialogVisible.value = true
    }
    
    // 分页处理
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      pagination.page = 1
      loadApplications()
    }
    
    const handleCurrentChange = (page) => {
      pagination.page = page
      loadApplications()
    }
    
    // 工具函数
    const getStatusType = (status) => {
      const statusMap = {
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return statusMap[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        pending: '待审核',
        approved: '已批准',
        rejected: '已拒绝'
      }
      return statusMap[status] || status
    }
    
    // 时间格式化函数已通过import导入
    
    // 初始化
    onMounted(() => {
      loadApplications()
    })
    
    return {
      loading,
      applications,
      selectedApplications,
      detailDialogVisible,
      currentApplication,
      searchForm,
      pagination,
      loadApplications,
      handleSearch,
      resetSearch,
      handleSelectionChange,
      approveApplication,
      rejectApplication,
      batchApprove,
      batchReject,
      viewApplication,
      handleSizeChange,
      handleCurrentChange,
      getStatusType,
      getStatusText,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.application-management {
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

.search-card {
  margin-bottom: 20px;
}

.batch-operations {
  margin-bottom: 20px;
}

.batch-buttons {
  margin-top: 10px;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.application-detail {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
