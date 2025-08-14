<template>
  <div class="debug-page">
    <el-card>
      <template #header>
        <h3>API调试页面</h3>
      </template>
      
      <el-space direction="vertical" size="large" style="width: 100%">
        <!-- 认证状态 -->
        <el-card>
          <template #header>认证状态</template>
          <p><strong>Token:</strong> {{ token ? '已设置' : '未设置' }}</p>
          <p><strong>用户信息:</strong> {{ userInfo ? JSON.stringify(userInfo) : '无' }}</p>
        </el-card>
        
        <!-- 测试按钮 -->
        <el-card>
          <template #header>API测试</template>
          <el-space>
            <el-button @click="testLogin" type="primary">测试登录</el-button>
            <el-button @click="testUsers" :disabled="!token">测试用户API</el-button>
            <el-button @click="testApplications" :disabled="!token">测试申请API</el-button>
            <el-button @click="testStats" :disabled="!token">测试统计API</el-button>
          </el-space>
        </el-card>
        
        <!-- 结果显示 -->
        <el-card>
          <template #header>测试结果</template>
          <pre>{{ result }}</pre>
        </el-card>
      </el-space>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAuthToken, getCurrentUser, setToken } from '@/utils/auth'
import { login } from '@/api/auth'
import { getUsers } from '@/api/admin'
import { getApplications } from '@/api/admin'
import { getAccessStats } from '@/api/stats'

export default {
  name: 'Debug',
  setup() {
    const token = ref('')
    const userInfo = ref(null)
    const result = ref('')
    
    const updateAuthInfo = () => {
      token.value = getAuthToken()
      userInfo.value = getCurrentUser()
    }
    
    const testLogin = async () => {
      try {
        result.value = '正在测试登录...'
        const response = await login({
          username: 'admin',
          password: 'admin123'
        })
        
        if (response.success) {
          setToken(response.data.token, response.data.user)
          updateAuthInfo()
          result.value = '登录成功:\n' + JSON.stringify(response, null, 2)
          ElMessage.success('登录成功')
        } else {
          result.value = '登录失败:\n' + JSON.stringify(response, null, 2)
        }
      } catch (error) {
        result.value = '登录错误:\n' + error.message
        console.error('登录错误:', error)
      }
    }
    
    const testUsers = async () => {
      try {
        result.value = '正在测试用户API...'
        const response = await getUsers()
        result.value = '用户API响应:\n' + JSON.stringify(response, null, 2)
      } catch (error) {
        result.value = '用户API错误:\n' + error.message
        console.error('用户API错误:', error)
      }
    }
    
    const testApplications = async () => {
      try {
        result.value = '正在测试申请API...'
        const response = await getApplications()
        result.value = '申请API响应:\n' + JSON.stringify(response, null, 2)
      } catch (error) {
        result.value = '申请API错误:\n' + error.message
        console.error('申请API错误:', error)
      }
    }
    
    const testStats = async () => {
      try {
        result.value = '正在测试统计API...'
        const response = await getAccessStats()
        result.value = '统计API响应:\n' + JSON.stringify(response, null, 2)
      } catch (error) {
        result.value = '统计API错误:\n' + error.message
        console.error('统计API错误:', error)
      }
    }
    
    onMounted(() => {
      updateAuthInfo()
    })
    
    return {
      token,
      userInfo,
      result,
      testLogin,
      testUsers,
      testApplications,
      testStats
    }
  }
}
</script>

<style scoped>
.debug-page {
  padding: 20px;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}
</style>
