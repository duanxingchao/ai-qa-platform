<template>
  <div class="big-screen" :class="{ fullscreen: isFullscreen }">
    <!-- 大屏标题 -->
    <div class="screen-header" v-if="!isFullscreen">
      <h1 class="screen-title">AI实验室数据大屏</h1>
      <div class="screen-controls">
        <div class="screen-time">{{ currentTime }}</div>
        <button class="fullscreen-btn" @click="toggleFullscreen">
          <i class="icon">⛶</i>
          全屏
        </button>
      </div>
    </div>

    <!-- 大屏内容区域 -->
    <div class="screen-content">
      <!-- 左侧区域 -->
      <div class="left-section">
        <!-- 系统状态模块 -->
        <div class="module-card system-status">
          <div class="card-header">
            <h3>系统状态</h3>
            <div class="status-indicator online"></div>
          </div>
          <div class="status-grid">
            <div class="status-item">
              <span class="label">在线用户</span>
              <span class="value">{{ systemStatus.onlineUsers }}</span>
            </div>
            <div class="status-item">
              <span class="label">活跃会话</span>
              <span class="value">{{ systemStatus.activeSessions }}</span>
            </div>
            <div class="status-item">
              <span class="label">处理队列</span>
              <span class="value">{{ systemStatus.processingQueue }}</span>
            </div>
          </div>
        </div>
        
        <!-- 实时数据模块 -->
        <div class="module-card realtime-data">
          <div class="card-header">
            <h3>实时数据</h3>
            <div class="pulse-indicator"></div>
          </div>
          <div class="realtime-metrics">
            <div class="metric">
              <div class="metric-label">当前小时问题</div>
              <div class="metric-value">{{ realtimeData.currentHourQuestions }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">平均响应时间</div>
              <div class="metric-value">{{ realtimeData.avgResponseTime }}ms</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间区域 -->
      <div class="center-section">
        <!-- 主要展示区域 -->
        <div class="main-display">
          <div class="display-title">核心指标概览</div>
          <div class="main-metrics">
            <div class="main-metric-card">
              <div class="metric-icon">📊</div>
              <div class="metric-info">
                <div class="metric-value">{{ mainMetrics.totalQuestions }}</div>
                <div class="metric-label">总问题数</div>
              </div>
            </div>
            <div class="main-metric-card">
              <div class="metric-icon">🎯</div>
              <div class="metric-info">
                <div class="metric-value">{{ mainMetrics.accuracy }}%</div>
                <div class="metric-label">准确率</div>
              </div>
            </div>
            <div class="main-metric-card">
              <div class="metric-icon">⚡</div>
              <div class="metric-info">
                <div class="metric-value">{{ mainMetrics.avgResponseTime }}s</div>
                <div class="metric-label">平均响应时间</div>
              </div>
            </div>
            <div class="main-metric-card">
              <div class="metric-icon">👥</div>
              <div class="metric-info">
                <div class="metric-value">{{ mainMetrics.satisfaction }}%</div>
                <div class="metric-label">满意度</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 趋势图表区域 -->
        <div class="chart-display">
          <div class="chart-title">24小时趋势</div>
          <div class="chart-placeholder">
            <div class="chart-info">图表区域 - 可集成 ECharts</div>
          </div>
        </div>
      </div>

      <!-- 右侧区域 -->
      <div class="right-section">
        <!-- Badcase分析模块 -->
        <div class="badcase-module">
          <BigScreenBadcase />
        </div>
        
        <!-- AI助手对比模块 -->
        <div class="module-card assistant-comparison">
          <div class="card-header">
            <h3>AI助手对比</h3>
          </div>
          <div class="assistant-list">
            <div 
              v-for="assistant in assistants" 
              :key="assistant.name"
              class="assistant-item"
            >
              <div class="assistant-info">
                <span class="assistant-name">{{ assistant.name }}</span>
                <span class="assistant-score" :class="getScoreClass(assistant.score)">
                  {{ assistant.score }}%
                </span>
              </div>
              <div class="assistant-progress">
                <div 
                  class="progress-fill" 
                  :style="{ width: assistant.score + '%' }"
                  :class="getScoreClass(assistant.score)"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import BigScreenBadcase from '@/components/BigScreenBadcase.vue'

export default {
  name: 'BigScreen',
  components: {
    BigScreenBadcase
  },
  setup() {
    const currentTime = ref('')
    const isFullscreen = ref(false)
    
    // 系统状态数据
    const systemStatus = ref({
      onlineUsers: 1247,
      activeSessions: 328,
      processingQueue: 12
    })
    
    // 实时数据
    const realtimeData = ref({
      currentHourQuestions: 45,
      avgResponseTime: 1200
    })
    
    // 主要指标
    const mainMetrics = ref({
      totalQuestions: 12456,
      accuracy: 94.2,
      avgResponseTime: 1.8,
      satisfaction: 87.5
    })
    
    // AI助手数据
    const assistants = ref([
      { name: '小天', score: 91 },
      { name: '自研AI', score: 83 },
      { name: '豆包', score: 67 },
      { name: 'GPT-4', score: 89 }
    ])

    // 更新时间
    const updateTime = () => {
      const now = new Date()
      currentTime.value = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    // 切换全屏
    const toggleFullscreen = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
        isFullscreen.value = true
      } else {
        document.exitFullscreen()
        isFullscreen.value = false
      }
    }
    
    // 获取分数等级类
    const getScoreClass = (score) => {
      if (score >= 90) return 'excellent'
      if (score >= 80) return 'good'
      if (score >= 70) return 'average'
      return 'poor'
    }
    
    // 模拟数据更新
    const updateData = () => {
      // 更新实时数据
      realtimeData.value.currentHourQuestions += Math.floor(Math.random() * 3)
      realtimeData.value.avgResponseTime = 1000 + Math.floor(Math.random() * 500)
      
      // 更新系统状态
      systemStatus.value.onlineUsers += Math.floor(Math.random() * 10 - 5)
      systemStatus.value.activeSessions += Math.floor(Math.random() * 6 - 3)
      systemStatus.value.processingQueue = Math.max(0, systemStatus.value.processingQueue + Math.floor(Math.random() * 6 - 3))
    }

    let timeInterval = null
    let dataInterval = null

    onMounted(() => {
      updateTime()
      timeInterval = setInterval(updateTime, 1000)
      dataInterval = setInterval(updateData, 5000) // 每5秒更新一次数据
      
      // 监听全屏变化
      document.addEventListener('fullscreenchange', () => {
        isFullscreen.value = !!document.fullscreenElement
      })
    })

    onUnmounted(() => {
      if (timeInterval) clearInterval(timeInterval)
      if (dataInterval) clearInterval(dataInterval)
    })

    return {
      currentTime,
      isFullscreen,
      systemStatus,
      realtimeData,
      mainMetrics,
      assistants,
      toggleFullscreen,
      getScoreClass
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/bigscreen.scss';

.big-screen {
  width: 100vw;
  height: 100vh;
  background: var(--bigscreen-primary-bg);
  color: var(--bigscreen-text-primary);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .screen-header {
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    background: rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .screen-title {
      font-size: 32px;
      font-weight: bold;
      margin: 0;
      background: linear-gradient(45deg, #ffffff, #b3d4fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .screen-controls {
      display: flex;
      align-items: center;
      gap: 20px;

      .screen-time {
        font-size: 18px;
        color: var(--bigscreen-text-secondary);
        font-family: 'Courier New', monospace;
      }

      .fullscreen-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.3s ease;

        &:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .icon {
          font-size: 16px;
        }
      }
    }
  }

  .screen-content {
    flex: 1;
    display: grid;
    grid-template-columns: 300px 1fr 350px;
    gap: 20px;
    padding: 20px;

    .left-section,
    .right-section {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .center-section {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
  }

  // 模块卡片通用样式
  .module-card {
    background: var(--bigscreen-card-bg);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid var(--bigscreen-border);

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      h3 {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
        color: #ffffff;
      }
    }
  }

  // 系统状态模块
  .system-status {
    .status-grid {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .status-item {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .label {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.8);
        }

        .value {
          font-size: 16px;
          font-weight: 600;
          color: #ffffff;
        }
      }
    }
  }

  // 实时数据模块
  .realtime-data {
    .realtime-metrics {
      .metric {
        margin-bottom: 12px;

        .metric-label {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.8);
          margin-bottom: 4px;
        }

        .metric-value {
          font-size: 18px;
          font-weight: bold;
          color: var(--bigscreen-success);
        }
      }
    }
  }

  // 主展示区域
  .main-display {
    background: var(--bigscreen-card-bg);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(10px);
    border: 1px solid var(--bigscreen-border);

    .display-title {
      font-size: 20px;
      font-weight: 600;
      text-align: center;
      margin-bottom: 24px;
      color: #ffffff;
    }

    .main-metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;

      .main-metric-card {
        display: flex;
        align-items: center;
        gap: 16px;
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 8px;

        .metric-icon {
          font-size: 32px;
        }

        .metric-info {
          .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            line-height: 1;
          }

          .metric-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 4px;
          }
        }
      }
    }
  }

  // 图表展示区域
  .chart-display {
    background: var(--bigscreen-card-bg);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid var(--bigscreen-border);
    flex: 1;

    .chart-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      color: #ffffff;
    }

    .chart-placeholder {
      height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      border: 2px dashed rgba(255, 255, 255, 0.2);

      .chart-info {
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
      }
    }
  }

  // Badcase模块
  .badcase-module {
    height: 400px;
    min-height: 350px;
  }

  // AI助手对比模块
  .assistant-comparison {
    .assistant-list {
      .assistant-item {
        margin-bottom: 16px;

        .assistant-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;

          .assistant-name {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
          }

          .assistant-score {
            font-size: 14px;
            font-weight: 600;

            &.excellent { color: var(--bigscreen-success); }
            &.good { color: var(--bigscreen-accent); }
            &.average { color: var(--bigscreen-warning); }
            &.poor { color: var(--bigscreen-danger); }
          }
        }

        .assistant-progress {
          height: 6px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
          overflow: hidden;

          .progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 1s ease;

            &.excellent { background: var(--bigscreen-success); }
            &.good { background: var(--bigscreen-accent); }
            &.average { background: var(--bigscreen-warning); }
            &.poor { background: var(--bigscreen-danger); }
          }
        }
      }
    }
  }

  // 全屏模式
  &.fullscreen {
    .screen-content {
      padding: 10px;
      grid-template-columns: 280px 1fr 320px;
    }

    .module-card {
      padding: 16px;
    }

    .main-display {
      padding: 20px;
    }
  }
}

// 响应式适配
@media (max-width: 1920px) {
  .big-screen {
    .screen-header {
      height: 70px;
      padding: 0 30px;

      .screen-title {
        font-size: 28px;
      }

      .screen-controls .screen-time {
        font-size: 16px;
      }
    }

    .screen-content {
      padding: 15px;
      gap: 15px;
      grid-template-columns: 280px 1fr 320px;

      .badcase-module {
        height: 350px;
        min-height: 300px;
      }
    }
  }
}

@media (max-width: 1366px) {
  .big-screen {
    .screen-header {
      height: 60px;
      padding: 0 20px;

      .screen-title {
        font-size: 24px;
      }

      .screen-controls .screen-time {
        font-size: 14px;
      }
    }

    .screen-content {
      padding: 10px;
      gap: 10px;
      grid-template-columns: 260px 1fr 300px;

      .badcase-module {
        height: 300px;
        min-height: 250px;
      }

      .main-display .main-metrics {
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
      }
    }
  }
}
</style>
