<template>
  <div class="user-management">
    <div class="page-header">
      <h2>👥 用户管理</h2>
      <p>管理系统用户，包括用户状态控制和权限管理</p>
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
            v-model="searchForm.role"
            placeholder="用户角色"
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
            placeholder="用户状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="激活" value="active" />
            <el-option label="禁用" value="inactive" />
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
    <el-card class="batch-operations" shadow="never" v-if="selectedUsers.length > 0">
      <el-alert
        :title="`已选择 ${selectedUsers.length} 个用户`"
        type="info"
        show-icon
        :closable="false"
      >
        <template #default>
          <div class="batch-buttons">
            <el-button type="success" size="small" @click="batchUpdateStatus('active')">
              <el-icon><Check /></el-icon>
              批量激活
            </el-button>
            <el-button type="warning" size="small" @click="batchUpdateStatus('inactive')">
              <el-icon><Lock /></el-icon>
              批量禁用
            </el-button>
            <el-button type="danger" size="small" @click="batchDeleteUsers">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </template>
      </el-alert>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="text" @click="loadUsers">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="users"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="username" label="用户名" width="120">
          <template #default="{ row }">
            <span class="username">{{ row.username }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'warning'"
              effect="light"
            >
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ row.created_at ? formatDateTime(row.created_at) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="last_login_at" label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login_at ? formatDateTime(row.last_login_at) : '从未登录' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                :type="row.status === 'active' ? 'warning' : 'success'"
                size="small"
                @click="toggleUserStatus(row)"
              >
                <el-icon><Lock v-if="row.status === 'active'" /><Unlock v-else /></el-icon>
                {{ row.status === 'active' ? '禁用' : '激活' }}
              </el-button>
              <el-button
                type="info"
                size="small"
                @click="viewUser(row)"
              >
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteUser(row)"
                :disabled="row.username === 'admin'"
              >
                <el-icon><Delete /></el-icon>
                删除
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

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="600px"
    >
      <div v-if="currentUser" class="user-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">
            {{ currentUser.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="currentUser.role === 'admin' ? 'danger' : 'primary'">
              {{ currentUser.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentUser.status === 'active' ? 'success' : 'warning'">
              {{ currentUser.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ currentUser.created_at ? formatDateTime(currentUser.created_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="最后登录" v-if="currentUser.last_login_at">
            {{ formatDateTime(currentUser.last_login_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="登录次数" v-if="currentUser.login_count">
            {{ currentUser.login_count }} 次
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button
            :type="currentUser?.status === 'active' ? 'warning' : 'success'"
            @click="toggleUserStatus(currentUser)"
          >
            {{ currentUser?.status === 'active' ? '禁用用户' : '激活用户' }}
          </el-button>
          <el-button
            type="danger"
            @click="deleteUser(currentUser)"
            :disabled="currentUser?.username === 'admin'"
          >
            删除用户
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
  Lock,
  Unlock,
  Delete,
  View
} from '@element-plus/icons-vue'
import { getUsers, updateUserStatus, deleteUser as deleteUserApi } from '@/api/admin'
import { formatDateTime } from '@/utils/datetime'

export default {
  name: 'UserManagement',
  components: {
    Search,
    Refresh,
    Check,
    Lock,
    Unlock,
    Delete,
    View
  },
  setup() {
    const loading = ref(false)
    const users = ref([])
    const selectedUsers = ref([])
    const detailDialogVisible = ref(false)
    const currentUser = ref(null)
    
    // 搜索表单
    const searchForm = reactive({
      username: '',
      role: '',
      status: ''
    })
    
    // 分页
    const pagination = reactive({
      page: 1,
      pageSize: 20,
      total: 0
    })
    
    // 加载用户列表
    const loadUsers = async () => {
      try {
        loading.value = true
        console.log('开始加载用户列表...')
        const response = await getUsers({
          ...searchForm,
          page: pagination.page,
          page_size: pagination.pageSize
        })

        console.log('用户API响应:', response)

        if (response.success) {
          users.value = response.data.users || []
          pagination.total = response.data.total || 0
          console.log('加载成功，用户数量:', users.value.length)
        } else {
          console.error('API返回失败:', response.message)
          ElMessage.error('加载用户列表失败: ' + response.message)
        }
      } catch (error) {
        console.error('加载用户列表失败:', error)
        ElMessage.error('加载用户列表失败: ' + (error.message || '网络错误'))
      } finally {
        loading.value = false
      }
    }
    
    // 搜索处理
    const handleSearch = () => {
      pagination.page = 1
      loadUsers()
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
      selectedUsers.value = selection
    }
    
    // 切换用户状态
    const toggleUserStatus = async (user) => {
      const newStatus = user.status === 'active' ? 'inactive' : 'active'
      const action = newStatus === 'active' ? '激活' : '禁用'
      
      try {
        await ElMessageBox.confirm(
          `确认${action}用户 "${user.username}"？`,
          `确认${action}`,
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: newStatus === 'active' ? 'success' : 'warning'
          }
        )
        
        const response = await updateUserStatus(user.id, newStatus)
        if (response.success) {
          ElMessage.success(`用户已${action}`)
          detailDialogVisible.value = false
          loadUsers()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('更新用户状态失败:', error)
        }
      }
    }
    
    // 删除用户
    const deleteUser = async (user) => {
      if (user.username === 'admin') {
        ElMessage.warning('不能删除管理员账户')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          `确认删除用户 "${user.username}"？此操作不可恢复！`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'error'
          }
        )
        
        const response = await deleteUserApi(user.id)
        if (response.success) {
          ElMessage.success('用户已删除')
          detailDialogVisible.value = false
          loadUsers()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除用户失败:', error)
        }
      }
    }
    
    // 批量更新状态
    const batchUpdateStatus = async (status) => {
      const action = status === 'active' ? '激活' : '禁用'
      
      try {
        await ElMessageBox.confirm(
          `确认${action}选中的 ${selectedUsers.value.length} 个用户？`,
          `批量${action}`,
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: status === 'active' ? 'success' : 'warning'
          }
        )
        
        for (const user of selectedUsers.value) {
          await updateUserStatus(user.id, status)
        }
        
        ElMessage.success(`已${action} ${selectedUsers.value.length} 个用户`)
        selectedUsers.value = []
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量更新状态失败:', error)
        }
      }
    }
    
    // 批量删除用户
    const batchDeleteUsers = async () => {
      const deletableUsers = selectedUsers.value.filter(user => user.username !== 'admin')
      
      if (deletableUsers.length === 0) {
        ElMessage.warning('没有可删除的用户')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          `确认删除选中的 ${deletableUsers.length} 个用户？此操作不可恢复！`,
          '批量删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'error'
          }
        )
        
        for (const user of deletableUsers) {
          await deleteUserApi(user.id)
        }
        
        ElMessage.success(`已删除 ${deletableUsers.length} 个用户`)
        selectedUsers.value = []
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量删除失败:', error)
        }
      }
    }
    
    // 查看详情
    const viewUser = (user) => {
      currentUser.value = user
      detailDialogVisible.value = true
    }
    
    // 分页处理
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      pagination.page = 1
      loadUsers()
    }
    
    const handleCurrentChange = (page) => {
      pagination.page = page
      loadUsers()
    }
    
    // 工具函数
    
    // 时间格式化函数已通过import导入
    
    // 初始化
    onMounted(() => {
      loadUsers()
    })
    
    return {
      loading,
      users,
      selectedUsers,
      detailDialogVisible,
      currentUser,
      searchForm,
      pagination,
      loadUsers,
      handleSearch,
      resetSearch,
      handleSelectionChange,
      toggleUserStatus,
      deleteUser,
      batchUpdateStatus,
      batchDeleteUsers,
      viewUser,
      handleSizeChange,
      handleCurrentChange,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.user-management {
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

.username {
  font-weight: 500;
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

.user-detail {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
