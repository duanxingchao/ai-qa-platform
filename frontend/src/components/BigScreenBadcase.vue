<template>
  <div class="bigscreen-badcase">
    <!-- 标题区域 -->
    <div class="header">
      <div class="title">
        <i class="icon">🔍</i>
        <span>badcase 分析及复核</span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content">
      <!-- 仪表盘和指标区域 -->
      <div class="dashboard-section">
        <!-- 左侧：圆形仪表盘 -->
        <div class="gauge-container">
          <div class="gauge-wrapper">
            <svg class="gauge-svg" viewBox="0 0 200 200">
              <circle
                class="gauge-bg"
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="rgba(255, 255, 255, 0.1)"
                stroke-width="8"
              />
              <circle
                class="gauge-fill"
                cx="100"
                cy="100"
                r="80"
                fill="none"
                :stroke="getGaugeColor(statistics.badcaseRate)"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="gaugeOffset"
                transform="rotate(-90 100 100)"
              />
            </svg>
            <div class="gauge-text">
              <div class="gauge-value">{{ statistics.badcaseRate }}%</div>
              <div class="gauge-label">问题率</div>
            </div>
          </div>
        </div>

        <!-- 右侧：核心指标垂直排列 -->
        <div class="metrics-panel">
          <div class="metric-item">
            <div class="metric-icon">📊</div>
            <div class="metric-content">
              <div class="metric-label">总问题</div>
              <div class="metric-value">{{ formatNumber(statistics.totalQuestions) }}</div>
            </div>
          </div>
          <div class="metric-item">
            <div class="metric-icon">⚠️</div>
            <div class="metric-content">
              <div class="metric-label">Badcase</div>
              <div class="metric-value danger">{{ formatNumber(statistics.badcaseCount) }}</div>
            </div>
          </div>
          <div class="metric-item">
            <div class="metric-icon">✅</div>
            <div class="metric-content">
              <div class="metric-label">复核率</div>
              <div class="metric-value success">{{ statistics.optimizationRate }}%</div>
            </div>
          </div>
          <div class="metric-item">
            <div class="metric-icon">📈</div>
            <div class="metric-content">
              <div class="metric-label">本周趋势</div>
              <div class="metric-value" :class="getTrendClass(trendValue)">
                <i :class="getTrendIcon(trendValue)"></i>
                {{ Math.abs(trendValue) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 热点分类区域 -->
      <div class="categories-section">
        <div class="section-title">热点分类 (Top3 评分维度)</div>
        <div class="categories-grid">
          <div 
            v-for="category in topCategories" 
            :key="category.category_id"
            class="category-card"
          >
            <div class="card-header">
              <span class="category-name">{{ category.category_name }}</span>
              <span class="badcase-count">{{ category.total_badcase }}</span>
            </div>
            <div class="dimensions-list">
              <div 
                v-for="dimension in category.lowest_dimensions" 
                :key="dimension.dimension_code"
                class="dimension-item"
              >
                <span class="dimension-name">{{ dimension.dimension_name }}:</span>
                <span 
                  class="dimension-score"
                  :class="getScoreClass(dimension.avg_score)"
                >
                  {{ dimension.avg_score }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getBadcaseStatistics, getTopCategoriesAnalysis } from '@/api/badcase'

export default {
  name: 'BigScreenBadcase',
  setup() {
    // 响应式数据
    const statistics = ref({
      totalQuestions: 0,
      badcaseCount: 0,
      badcaseRate: 0,
      optimizationRate: 0
    })
    
    const topCategories = ref([])
    const trendValue = ref(0)

    // 圆形进度条计算
    const circumference = 2 * Math.PI * 80 // r=80
    const gaugeOffset = computed(() => {
      const progress = statistics.value.badcaseRate / 100
      return circumference * (1 - progress)
    })

    // 格式化数字显示
    const formatNumber = (num) => {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k'
      }
      return num.toString()
    }

    // 获取仪表盘颜色
    const getGaugeColor = (rate) => {
      if (rate >= 50) return '#ff4757' // 红色 - 严重
      if (rate >= 30) return '#ff6348' // 橙色 - 高
      if (rate >= 20) return '#ffb800' // 黄色 - 中等
      return '#00d4aa' // 绿色 - 良好
    }

    // 获取评分颜色类
    const getScoreClass = (score) => {
      if (score < 2.0) return 'score-critical'
      if (score < 2.5) return 'score-poor'
      if (score < 3.0) return 'score-below'
      if (score < 3.5) return 'score-average'
      return 'score-good'
    }

    // 获取趋势类
    const getTrendClass = (value) => {
      if (value > 0) return 'trend-up'
      if (value < 0) return 'trend-down'
      return 'trend-stable'
    }

    // 获取趋势图标
    const getTrendIcon = (value) => {
      if (value > 0) return 'trend-icon-up'
      if (value < 0) return 'trend-icon-down'
      return 'trend-icon-stable'
    }

    // 加载统计数据
    const loadStatistics = async () => {
      try {
        const response = await getBadcaseStatistics({ time_range: 'week' })
        if (response.success) {
          statistics.value = {
            totalQuestions: response.data.total_questions || 0,
            badcaseCount: response.data.badcase_count || 0,
            badcaseRate: response.data.badcase_ratio || 0,
            optimizationRate: (response.data.review_rate || 0).toFixed(1)
          }
          
          if (response.data.trend) {
            trendValue.value = response.data.trend.percentage || 0
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        // 使用模拟数据
        statistics.value = {
          totalQuestions: 1234,
          badcaseCount: 456,
          badcaseRate: 37.0,
          optimizationRate: 78.5
        }
        trendValue.value = 8.2
      }
    }

    // 加载Top3分类分析数据
    const loadTopCategoriesAnalysis = async () => {
      try {
        const response = await getTopCategoriesAnalysis()
        if (response.success && response.data) {
          topCategories.value = response.data.top_categories || []
        }
      } catch (error) {
        console.error('加载分类分析数据失败:', error)
        // 使用模拟数据
        topCategories.value = [
          {
            category_id: 1,
            category_name: '技术问题',
            total_badcase: 156,
            lowest_dimensions: [
              { dimension_name: '有用性', dimension_code: 'usefulness', avg_score: 2.0 },
              { dimension_name: '准确性', dimension_code: 'accuracy', avg_score: 2.1 }
            ]
          },
          {
            category_id: 2,
            category_name: '故障排查',
            total_badcase: 124,
            lowest_dimensions: [
              { dimension_name: '时效性', dimension_code: 'timeliness', avg_score: 2.2 },
              { dimension_name: '完整性', dimension_code: 'completeness', avg_score: 2.3 }
            ]
          },
          {
            category_id: 3,
            category_name: '业务咨询',
            total_badcase: 98,
            lowest_dimensions: [
              { dimension_name: '满意度', dimension_code: 'satisfaction', avg_score: 2.1 },
              { dimension_name: '相关性', dimension_code: 'relevance', avg_score: 2.4 }
            ]
          }
        ]
      }
    }

    // 数据刷新
    const refreshData = () => {
      loadStatistics()
      loadTopCategoriesAnalysis()
    }

    let refreshInterval = null

    onMounted(() => {
      refreshData()
      // 每30秒刷新一次数据
      refreshInterval = setInterval(refreshData, 30000)
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })

    return {
      statistics,
      topCategories,
      trendValue,
      circumference,
      gaugeOffset,
      formatNumber,
      getGaugeColor,
      getScoreClass,
      getTrendClass,
      getTrendIcon
    }
  }
}
</script>

<style lang="scss" scoped>
.bigscreen-badcase {
  width: 100%;
  height: 100%;
  background: transparent; // 使用透明背景，让外层容器控制背景
  border-radius: 0; // 移除内部圆角，使用外层容器的圆角
  padding: 16px;
  color: #ffffff;
  font-family: 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  flex-direction: column;

  .header {
    margin-bottom: 16px;

    .title {
      display: flex;
      align-items: center;
      font-size: 18px;
      font-weight: 600;
      color: #ffffff;

      .icon {
        margin-right: 8px;
        font-size: 20px;
      }
    }
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px; // 减小间距
  }

  // 仪表盘和指标区域
  .dashboard-section {
    display: flex;
    align-items: center;
    gap: 20px;
    height: 140px; // 增加高度以容纳5个指标

    // 左侧圆环容器
    .gauge-container {
      flex-shrink: 0;
      width: 150px; // 固定宽度

      .gauge-wrapper {
        position: relative;
        width: 120px;
        height: 120px;

        .gauge-svg {
          width: 100%;
          height: 100%;
        }

        .gauge-fill {
          transition: stroke-dashoffset 1.5s ease-in-out;
        }

        .gauge-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;

          .gauge-value {
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            line-height: 1;
          }

          .gauge-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 4px;
          }
        }
      }
    }

    // 右侧指标面板
    .metrics-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 6px; // 减小间距以容纳5个指标
      height: 140px; // 与容器高度一致
      justify-content: center; // 垂直居中

      .metric-item {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 6px 12px; // 减小垂直内边距
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        height: 26px; // 减小每个卡片高度以容纳5个
        flex-shrink: 0; // 防止被压缩

        .metric-icon {
          font-size: 16px; // 减小图标尺寸
          margin-right: 10px;
          flex-shrink: 0;
        }

        .metric-content {
          flex: 1;
          display: flex;
          justify-content: space-between;
          align-items: center;

          .metric-label {
            font-size: 11px; // 减小标签字体
            color: rgba(255, 255, 255, 0.8);
          }

          .metric-value {
            font-size: 14px; // 减小数值字体
            font-weight: bold;
            color: #ffffff;

            &.danger {
              color: #ff4757;
            }

            &.success {
              color: #4ade80; // 复核率使用绿色
            }

            &.trend-up {
              color: #00d4aa;
            }

            &.trend-down {
              color: #ff4757;
            }

            &.trend-stable {
              color: rgba(255, 255, 255, 0.8);
            }

            .trend-icon-up::before {
              content: '↗';
              margin-right: 4px;
            }

            .trend-icon-down::before {
              content: '↘';
              margin-right: 4px;
            }

            .trend-icon-stable::before {
              content: '→';
              margin-right: 4px;
            }
          }
        }
      }
    }
  }

  // 分类区域
  .categories-section {
    flex: 1;

    .section-title {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 12px;
      color: rgba(255, 255, 255, 0.9);
    }

    .categories-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      height: calc(100% - 32px);

      .category-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        flex-direction: column;

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .category-name {
            font-size: 13px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
          }

          .badcase-count {
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
          }
        }

        .dimensions-list {
          flex: 1;

          .dimension-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;

            .dimension-name {
              font-size: 11px;
              color: rgba(255, 255, 255, 0.8);
            }

            .dimension-score {
              font-size: 12px;
              font-weight: 600;
              padding: 2px 6px;
              border-radius: 4px;

              &.score-critical {
                color: #ff4757;
                background: rgba(255, 71, 87, 0.15);
              }

              &.score-poor {
                color: #ff6348;
                background: rgba(255, 99, 72, 0.15);
              }

              &.score-below {
                color: #ffb800;
                background: rgba(255, 184, 0, 0.15);
              }

              &.score-average {
                color: #00d4ff;
                background: rgba(0, 212, 255, 0.15);
              }

              &.score-good {
                color: #00d4aa;
                background: rgba(0, 212, 170, 0.15);
              }
            }
          }
        }
      }
    }
  }
}

// 响应式适配
@media (max-width: 1366px) {
  .bigscreen-badcase {
    padding: 12px;

    .header .title {
      font-size: 16px;

      .icon {
        font-size: 18px;
      }
    }

    .dashboard-section {
      height: 120px; // 小屏幕下适当减小高度
      gap: 16px;

      .gauge-container {
        width: 120px; // 小屏幕下减小宽度

        .gauge-wrapper {
          width: 100px;
          height: 100px;

          .gauge-text {
            .gauge-value {
              font-size: 18px;
            }

            .gauge-label {
              font-size: 10px;
            }
          }
        }
      }

      .metrics-panel {
        height: 120px; // 与圆环高度一致
        gap: 4px; // 进一步减小间距

        .metric-item {
          padding: 4px 8px; // 减小内边距
          height: 22px; // 减小卡片高度以容纳5个

          .metric-icon {
            font-size: 14px;
            margin-right: 8px;
          }

          .metric-content {
            .metric-label {
              font-size: 10px;
            }

            .metric-value {
              font-size: 12px;
            }
          }
        }
      }
    }

    .categories-section {
      .section-title {
        font-size: 13px;
      }

      .categories-grid {
        gap: 10px;

        .category-card {
          padding: 10px;

          .card-header {
            .category-name {
              font-size: 12px;
            }

            .badcase-count {
              font-size: 14px;
            }
          }

          .dimensions-list .dimension-item {
            .dimension-name {
              font-size: 10px;
            }

            .dimension-score {
              font-size: 11px;
            }
          }
        }
      }
    }
  }
}
</style>
