<template>
  <div class="statistics-cards">
    <el-row :gutter="20">
      <!-- 本周评分总数 -->
      <el-col :span="3">
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
      </el-col>

      <!-- 本周badcase总数 -->
      <el-col :span="3">
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
      </el-col>
      
      <!-- Badcase占比 -->
      <el-col :span="3">
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
      </el-col>
      
      <!-- 待处理案例 -->
      <el-col :span="4">
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
      </el-col>
      
      <!-- 已复核案例 -->
      <el-col :span="3">
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
      </el-col>

      <!-- 复核率 -->
      <el-col :span="3">
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
      </el-col>

      <!-- 误判修正数 -->
      <el-col :span="3">
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
      </el-col>
    </el-row>
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
  
  .stat-card {
    height: 100px;
    
    .stat-content {
      display: flex;
      align-items: center;
      height: 100%;
      
      .stat-icon {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-size: 24px;
        
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
        
        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
          line-height: 1;
          margin-bottom: 5px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #606266;
          line-height: 1;
        }
      }
    }
  }
}
</style>
