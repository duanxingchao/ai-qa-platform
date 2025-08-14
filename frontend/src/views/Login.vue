<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>🔐 AI问答平台登录</h2>
        <p>请使用您的员工号码和密码登录</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入员工号码"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            style="width: 100%" 
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="text" 
            size="large"
            style="width: 100%" 
            @click="goToRegister"
          >
            没有账号？申请注册
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { setToken, clearAuth } from '@/utils/auth'
import { updateUserInfo } from '@/stores/user'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const loginFormRef = ref()
    
    // 表单数据
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    // 表单验证规则
    const loginRules = {
      username: [
        { required: true, message: '请输入员工号码', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }
    
    // 处理登录
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      try {
        const valid = await loginFormRef.value.validate()
        if (!valid) return
        
        loading.value = true
        
        const response = await login(loginForm)
        
        if (response.success) {
          // 先清除旧的认证信息，确保不会有缓存问题
          clearAuth()

          // 保存新的token和用户信息
          setToken(response.data.token, response.data.user)
          updateUserInfo(response.data.user)

          console.log('登录成功，用户信息:', response.data.user)

          ElMessage.success('登录成功')

          // 跳转到首页
          router.push('/')
        }
      } catch (error) {
        console.error('登录失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 跳转到注册页面
    const goToRegister = () => {
      router.push('/register')
    }
    
    return {
      loginForm,
      loginRules,
      loginFormRef,
      loading,
      handleLogin,
      goToRegister
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-header {
  text-align: center;
  padding: 40px 30px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.login-header h2 {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.login-form {
  padding: 30px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.login-form :deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
}

.login-form :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.login-form :deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}
</style>
