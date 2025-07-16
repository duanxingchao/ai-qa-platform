<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 侧边栏 -->
      <el-aside width="250px" class="app-aside">
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
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/questions">
            <el-icon><ChatDotRound /></el-icon>
            <span>问题管理</span>
          </el-menu-item>
          <el-menu-item index="/answers">
            <el-icon><Document /></el-icon>
            <span>答案对比</span>
          </el-menu-item>
          <el-menu-item index="/scores">
            <el-icon><DataLine /></el-icon>
            <span>评分分析</span>
          </el-menu-item>
          <el-menu-item index="/monitor">
            <el-icon><View /></el-icon>
            <span>系统监控</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
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
            <el-dropdown>
              <span class="user-info">
                <el-icon><User /></el-icon>
                管理员
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>用户设置</el-dropdown-item>
                  <el-dropdown-item divided>退出登录</el-dropdown-item>
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()

    const breadcrumbs = computed(() => {
      const routeMap = {
        '/dashboard': [{ title: '数据概览', path: '/dashboard' }],
        '/questions': [{ title: '问题管理', path: '/questions' }],
        '/answers': [{ title: '答案对比', path: '/answers' }],
        '/scores': [{ title: '评分分析', path: '/scores' }],
        '/monitor': [{ title: '系统监控', path: '/monitor' }],
        '/settings': [{ title: '系统配置', path: '/settings' }]
      }
      return routeMap[route.path] || []
    })

    return {
      breadcrumbs
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
        &:hover {
          background-color: #434a50 !important;
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
        font-size: 14px;
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