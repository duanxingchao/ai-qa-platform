<template>
  <div class="responsive-test">
    <div class="test-header">
      <h1>响应式测试页面</h1>
      <div class="screen-info">
        <span>当前分辨率: {{ screenWidth }} x {{ screenHeight }}</span>
        <span>设备类型: {{ deviceType }}</span>
      </div>
    </div>

    <div class="test-controls">
      <h3>快速测试分辨率</h3>
      <div class="resolution-buttons">
        <button 
          v-for="resolution in testResolutions" 
          :key="resolution.name"
          @click="setTestResolution(resolution)"
          :class="{ active: currentResolution?.name === resolution.name }"
        >
          {{ resolution.name }}
          <small>{{ resolution.width }}x{{ resolution.height }}</small>
        </button>
      </div>
    </div>

    <div class="test-content">
      <div class="test-section">
        <h3>字体大小测试</h3>
        <div class="font-test">
          <p class="responsive-title">响应式标题 (24px-48px)</p>
          <p class="responsive-subtitle">响应式副标题 (18px-24px)</p>
          <p class="responsive-text">响应式正文 (14px-18px)</p>
        </div>
      </div>

      <div class="test-section">
        <h3>网格布局测试</h3>
        <div class="responsive-grid">
          <div class="grid-item">卡片 1</div>
          <div class="grid-item">卡片 2</div>
          <div class="grid-item">卡片 3</div>
          <div class="grid-item">卡片 4</div>
        </div>
      </div>

      <div class="test-section">
        <h3>Flex布局测试</h3>
        <div class="responsive-flex">
          <div class="flex-item">项目 1</div>
          <div class="flex-item">项目 2</div>
          <div class="flex-item">项目 3</div>
        </div>
      </div>

      <div class="test-section">
        <h3>显示/隐藏测试</h3>
        <div class="visibility-test">
          <div class="hide-mobile">桌面端显示</div>
          <div class="show-mobile">移动端显示</div>
          <div class="hide-desktop">移动端显示</div>
          <div class="show-desktop">桌面端显示</div>
        </div>
      </div>

      <div class="test-section">
        <h3>大屏组件预览</h3>
        <div class="bigscreen-preview">
          <div class="preview-header">
            <h2>AI自动化测试中心实时监控大屏</h2>
          </div>
          <div class="preview-metrics">
            <div class="preview-metric">
              <span class="metric-icon">📊</span>
              <div class="metric-content">
                <div class="metric-value">1170</div>
                <div class="metric-label">总问题数</div>
              </div>
            </div>
            <div class="preview-metric">
              <span class="metric-icon">🎯</span>
              <div class="metric-content">
                <div class="metric-value">270</div>
                <div class="metric-label">已分类</div>
              </div>
            </div>
            <div class="preview-metric">
              <span class="metric-icon">⚡</span>
              <div class="metric-content">
                <div class="metric-value">171</div>
                <div class="metric-label">已评分</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const screenWidth = ref(window.innerWidth)
const screenHeight = ref(window.innerHeight)
const currentResolution = ref(null)

const deviceType = computed(() => {
  const width = screenWidth.value
  if (width <= 480) return '手机'
  if (width <= 768) return '平板'
  if (width <= 1024) return '笔记本'
  if (width <= 1366) return '桌面'
  if (width <= 1920) return '大屏'
  return '超大屏'
})

const testResolutions = [
  { name: '手机', width: 375, height: 667 },
  { name: '平板', width: 768, height: 1024 },
  { name: '笔记本', width: 1024, height: 768 },
  { name: '桌面', width: 1366, height: 768 },
  { name: '大屏', width: 1920, height: 1080 },
  { name: '4K', width: 2560, height: 1440 }
]

const updateScreenSize = () => {
  screenWidth.value = window.innerWidth
  screenHeight.value = window.innerHeight
}

const setTestResolution = (resolution) => {
  currentResolution.value = resolution
  // 这里只是模拟，实际需要开发者工具来改变视口大小
  alert(`请在浏览器开发者工具中设置视口为 ${resolution.width}x${resolution.height}`)
}

onMounted(() => {
  window.addEventListener('resize', updateScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
})
</script>

<style lang="scss" scoped>
.responsive-test {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;

  .test-header {
    text-align: center;
    margin-bottom: 30px;
    
    h1 {
      font-size: clamp(24px, 4vw, 36px);
      margin-bottom: 10px;
    }
    
    .screen-info {
      display: flex;
      justify-content: center;
      gap: 20px;
      font-size: 14px;
      color: #666;
      
      @media (max-width: 768px) {
        flex-direction: column;
        gap: 5px;
      }
    }
  }

  .test-controls {
    margin-bottom: 30px;
    
    .resolution-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 15px;
      
      button {
        padding: 10px 15px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 5px;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        
        &:hover {
          background: #f5f5f5;
        }
        
        &.active {
          background: #007bff;
          color: white;
        }
        
        small {
          font-size: 12px;
          opacity: 0.8;
        }
      }
    }
  }

  .test-content {
    .test-section {
      margin-bottom: 40px;
      padding: 20px;
      border: 1px solid #eee;
      border-radius: 8px;
      
      h3 {
        margin-bottom: 20px;
        color: #333;
      }
    }
  }

  .font-test {
    p {
      margin-bottom: 15px;
      padding: 10px;
      background: #f8f9fa;
      border-radius: 4px;
    }
  }

  .grid-item, .flex-item {
    padding: 20px;
    background: #e9ecef;
    border-radius: 4px;
    text-align: center;
    margin-bottom: 10px;
  }

  .visibility-test {
    div {
      padding: 10px;
      margin: 5px 0;
      background: #d4edda;
      border-radius: 4px;
      text-align: center;
    }
  }

  .bigscreen-preview {
    background: linear-gradient(135deg, #0a1628 0%, #112A43 30%, #1B4A73 100%);
    color: white;
    padding: 20px;
    border-radius: 8px;
    
    .preview-header {
      text-align: center;
      margin-bottom: 20px;
      
      h2 {
        font-size: clamp(18px, 3vw, 24px);
      }
    }
    
    .preview-metrics {
      display: flex;
      justify-content: space-around;
      flex-wrap: wrap;
      gap: 15px;
      
      .preview-metric {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        min-width: 150px;
        
        .metric-icon {
          font-size: clamp(20px, 3vw, 28px);
        }
        
        .metric-content {
          .metric-value {
            font-size: clamp(18px, 2.5vw, 24px);
            font-weight: bold;
            color: #00d4ff;
          }
          
          .metric-label {
            font-size: clamp(12px, 1.5vw, 14px);
            color: #8892b0;
          }
        }
      }
    }
  }
}
</style>
