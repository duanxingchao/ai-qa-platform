<template>
  <div id="app">
    <!-- 大屏展示页面，不显示布局 -->
    <router-view v-if="$route.meta.hideLayout" />
    
    <!-- 普通页面，显示完整布局 -->
    <el-container v-else class="app-container">
      <!-- 侧边栏 -->
      <el-aside width="200px" class="app-aside">
        <div class="logo">
          <h2>AI问答管理</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          class="app-menu"
          router
          unique-opened
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/questions">
            <el-icon><ChatDotRound /></el-icon>
            <span>问题管理</span>
          </el-menu-item>

          <el-menu-item index="/badcase">
            <el-icon><Warning /></el-icon>
            <span>badcase分析</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
          </el-menu-item>

          <!-- 管理员专用菜单 -->
          <template v-if="isAdmin">
            <el-menu-item index="/application-management">
              <el-icon><UserFilled /></el-icon>
              <span>申请审核</span>
            </el-menu-item>
            <el-menu-item index="/user-management">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/access-stats">
              <el-icon><DataAnalysis /></el-icon>
              <span>访问统计</span>
            </el-menu-item>
          </template>

          <el-menu-item index="/display">
            <el-icon><FullScreen /></el-icon>
            <span>大屏展示</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="app-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ userInfo?.username || '用户' }}
                <el-tag v-if="userInfo?.role === 'admin'" type="danger" size="small" style="margin-left: 8px;">
                  管理员
                </el-tag>
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 页面内容 -->
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor,
  ChatDotRound,
  Warning,
  View,
  Setting,
  UserFilled,
  User,
  DataAnalysis,
  FullScreen,
  ArrowDown
} from '@element-plus/icons-vue'
import { clearAuth, isLoggedIn as checkIsLoggedIn } from '@/utils/auth'
import { logout, verifyToken } from '@/api/auth'
import { userInfo, isAdmin, updateUserInfo, clearUserInfo } from '@/stores/user'

export default {
  name: 'App',
  components: {
    Monitor,
    ChatDotRound,
    Warning,
    View,
    Setting,
    UserFilled,
    User,
    DataAnalysis,
    FullScreen,
    ArrowDown
  },
  setup() {
    const route = useRoute()
    const router = useRouter()

    // 用户信息已经从stores导入，直接使用

    const breadcrumbs = computed(() => {
      const routeMap = {
        '/questions': [{ title: '问题管理', path: '/questions' }],
        '/badcase': [{ title: 'badcase分析', path: '/badcase' }],
        '/settings': [{ title: '系统配置', path: '/settings' }],
        '/display': [{ title: '大屏展示', path: '/display' }],
        '/user-management': [{ title: '用户管理', path: '/user-management' }],
        '/application-management': [{ title: '申请审核', path: '/application-management' }],
        '/access-stats': [{ title: '访问统计', path: '/access-stats' }]
      }
      return routeMap[route.path] || []
    })

    // 处理下拉菜单命令
    const handleCommand = async (command) => {
      switch (command) {
        case 'profile':
          ElMessage.info('个人信息功能开发中')
          break
        case 'logout':
          await handleLogout()
          break
      }
    }

    // 处理登出
    const handleLogout = async () => {
      try {
        await ElMessageBox.confirm('确认退出登录？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        // 调用登出API
        await logout()

        // 清除本地认证信息
        clearAuth()
        clearUserInfo()

        ElMessage.success('已退出登录')

        // 跳转到登录页
        router.push('/login')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('登出失败:', error)
        }
      }
    }

    // 应用启动时验证用户登录状态
    const validateUserSession = async () => {
      if (checkIsLoggedIn()) {
        try {
          // 验证token是否仍然有效
          const response = await verifyToken()
          console.log('用户会话验证成功')
          // 更新用户信息，确保显示正确的用户
          if (response.success && response.data.user) {
            updateUserInfo(response.data.user)
          }
        } catch (error) {
          console.log('用户会话已过期，清除登录信息')
          clearAuth()
          clearUserInfo()
          // 如果当前不在登录页，跳转到登录页
          if (route.path !== '/login') {
            router.push('/login')
          }
        }
      } else {
        clearUserInfo()
      }
    }

    // 组件挂载时验证用户会话
    onMounted(() => {
      validateUserSession()
    })

    return {
      breadcrumbs,
      userInfo,
      isAdmin,
      handleCommand
    }
  }
}
</script>

<style lang="scss">
.app-container {
  height: 100vh;

  .app-aside {
    background-color: #304156;
    
    .logo {
      padding: 20px;
      text-align: center;
      color: #fff;
      border-bottom: 1px solid #434a50;
      
      h2 {
        margin: 0;
        font-size: 18px;
      }
    }

    .app-menu {
      border: none;

      .el-menu-item {
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding-left: 30px;

        &:hover {
          background-color: #434a50 !important;
        }

        .el-icon {
          margin-right: 12px;
          font-size: 18px;
        }

        span {
          font-size: 16px;
          font-weight: 500;
        }
      }
    }
  }

  .app-header {
    background-color: #fff;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;

    .header-left {
      .el-breadcrumb {
        font-size: 16px;
      }
    }

    .header-right {
      .user-info {
        cursor: pointer;
        display: flex;
        align-items: center;
        color: #606266;
        
        .el-icon {
          margin: 0 4px;
        }
      }
    }
  }

  .app-main {
    background-color: #f0f2f5;
    padding: 20px;
  }
}
</style> 