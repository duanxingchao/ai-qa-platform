<template>
  <div class="statistics-cards">
    <div class="stats-grid">
      <!-- 本周评分总数 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon primary">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalQuestions || 0 }}</div>
            <div class="stat-label">本周评分总数</div>
          </div>
        </div>
      </el-card>

      <!-- 本周badcase总数 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon error">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.badcaseCount || 0 }}</div>
            <div class="stat-label">本周badcase总数</div>
          </div>
        </div>
      </el-card>

      <!-- Badcase占比 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><PieChart /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (statistics.badcaseRatio || 0).toFixed(1) }}%</div>
            <div class="stat-label">Badcase占比</div>
          </div>
        </div>
      </el-card>

      <!-- 待处理案例 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.pendingCount || 0 }}</div>
            <div class="stat-label">待处理案例</div>
          </div>
        </div>
      </el-card>

      <!-- 已复核案例 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon success">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.reviewedCount || 0 }}</div>
            <div class="stat-label">已复核案例</div>
          </div>
        </div>
      </el-card>

      <!-- 复核率 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon success">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (statistics.reviewRate || 0).toFixed(1) }}%</div>
            <div class="stat-label">复核率</div>
          </div>
        </div>
      </el-card>

      <!-- 误判修正数 -->
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.misjudgedCount || 0 }}</div>
            <div class="stat-label">误判修正数</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { Document, Warning, PieChart, Clock, Check, TrendCharts } from '@element-plus/icons-vue'

export default {
  name: 'StatisticsCard',
  components: {
    Document,
    Warning,
    PieChart,
    Clock,
    Check,
    TrendCharts
  },
  props: {
    statistics: {
      type: Object,
      default: () => ({
        totalQuestions: 0,
        badcaseCount: 0,
        badcaseRatio: 0,
        pendingCount: 0,
        optimizedCount: 0,
        optimizationRate: 0
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.statistics-cards {
  margin-bottom: 20px;

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 16px;

    // 响应式布局
    @media (max-width: 1400px) {
      grid-template-columns: repeat(4, 1fr);
    }

    @media (max-width: 992px) {
      grid-template-columns: repeat(3, 1fr);
    }

    @media (max-width: 768px) {
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    @media (max-width: 480px) {
      grid-template-columns: 1fr;
      gap: 10px;
    }
  }

  .stat-card {
    height: 100px;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
    }

    :deep(.el-card__body) {
      padding: 16px;
      height: 100%;
      display: flex;
      align-items: center;
    }

    .stat-content {
      display: flex;
      align-items: center;
      width: 100%;
      height: 100%;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-size: 22px;
        flex-shrink: 0;

        &.primary {
          background-color: #e3f2fd;
          color: #1976d2;
        }

        &.error {
          background-color: #ffebee;
          color: #d32f2f;
        }

        &.warning {
          background-color: #fff3e0;
          color: #f57c00;
        }

        &.success {
          background-color: #e8f5e8;
          color: #388e3c;
        }
      }

      .stat-info {
        flex: 1;
        min-width: 0;

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
          line-height: 1.2;
          margin-bottom: 4px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;

          @media (max-width: 768px) {
            font-size: 20px;
          }
        }

        .stat-label {
          font-size: 13px;
          color: #606266;
          line-height: 1.2;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;

          @media (max-width: 768px) {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>
