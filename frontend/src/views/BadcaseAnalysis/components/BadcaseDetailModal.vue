<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="handleClose"
    title="📋 Badcase详情"
    width="80%"
    :before-close="handleClose"
    class="badcase-detail-modal"
  >
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>
    
    <div v-else-if="badcaseData" class="detail-content">
      <!-- 基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">📋 基本信息</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="info-item">
              <span class="label">问题ID：</span>
              <span class="value">{{ badcaseData.business_id }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ badcaseData.created_at }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <span class="label">分类：</span>
              <span class="value">{{ badcaseData.classification || '未分类' }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <span class="label">检测时间：</span>
              <span class="value">{{ badcaseData.badcase_detected_at }}</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 问题内容 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">❓ 问题内容</span>
        </template>
        <div class="question-content">
          {{ badcaseData.query }}
        </div>
      </el-card>

      <!-- AI模型回答 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">🤖 AI模型回答</span>
        </template>
        <div class="answers-container">
          <div v-for="answer in badcaseData.answers" :key="answer.id" class="answer-item">
            <div class="answer-header">
              <el-tag :type="getAssistantTagType(answer.assistant_type)">
                {{ getAssistantName(answer.assistant_type) }}
              </el-tag>
              <span class="answer-time">{{ answer.answer_time }}</span>
            </div>
            <div class="answer-content">
              {{ answer.answer_text }}
            </div>
          </div>
        </div>
      </el-card>

      <!-- 原始AI评分 -->
      <el-card class="info-card ai-scoring" shadow="never">
        <template #header>
          <span class="card-title">✨ 原始AI评分</span>
        </template>
        <div v-if="badcaseData.original_ai_scoring" class="scoring-content">
          <!-- 评分详情 -->
          <div class="scores-grid">
            <div 
              v-for="dimension in badcaseData.original_ai_scoring.dimensions" 
              :key="dimension.dimension_name"
              class="score-item"
            >
              <span class="dimension-name">{{ dimension.dimension_name }}</span>
              <span class="score-value" :class="getScoreClass(dimension.score)">
                {{ dimension.score }}/5
              </span>
            </div>
          </div>
          
          <!-- 平均分 -->
          <div class="average-score">
            <span class="label">平均分：</span>
            <span class="value" :class="getScoreClass(badcaseData.original_ai_scoring.average_score)">
              {{ badcaseData.original_ai_scoring.average_score }}/5
            </span>
          </div>
          
          <!-- AI评分理由 -->
          <div class="ai-reasoning">
            <span class="label">AI评分理由：</span>
            <div class="reasoning-content">
              {{ badcaseData.original_ai_scoring.comment || '暂无评分理由' }}
            </div>
          </div>
          
          <!-- 检测结果 -->
          <div class="detection-result">
            <span class="label">检测结果：</span>
            <el-tag type="danger">确认为badcase</el-tag>
            <span class="threshold-info">（阈值：{{ badcaseData.detection_threshold }}）</span>
          </div>
        </div>
      </el-card>

      <!-- 人工复核结果 -->
      <el-card class="info-card review-info" shadow="never">
        <template #header>
          <span class="card-title">👤 人工复核结果</span>
        </template>
        <div class="review-content">
          <div v-if="!badcaseData.review_info" class="no-review">
            <el-empty description="暂未复核" />
          </div>
          <div v-else class="review-details">
            <!-- 复核状态 -->
            <div class="review-item">
              <span class="label">复核状态：</span>
              <el-tag :type="badcaseData.review_info.status === 'reviewed' ? 'success' : 'warning'">
                {{ badcaseData.review_info.status === 'reviewed' ? '已复核' : '待复核' }}
              </el-tag>
            </div>
            
            <!-- 复核结果 -->
            <div v-if="badcaseData.review_info.review_result" class="review-item">
              <span class="label">复核结果：</span>
              <el-tag :type="getReviewResultType(badcaseData.review_info.review_result)">
                {{ getReviewResultText(badcaseData.review_info.review_result) }}
              </el-tag>
            </div>
            
            <!-- 复核后评分对比 -->
            <div v-if="badcaseData.review_info.modified_scores" class="score-comparison">
              <div class="comparison-title">复核后评分：</div>
              <div class="comparison-grid">
                <div 
                  v-for="(newScore, index) in badcaseData.review_info.modified_scores" 
                  :key="index"
                  class="comparison-item"
                >
                  <span class="dimension-name">{{ newScore.dimension_name }}：</span>
                  <span class="score-change">
                    <span class="old-score">{{ formatScore(getOriginalScore(newScore.dimension_name)) }}/5</span>
                    <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                    <span class="new-score" :class="getScoreClass(newScore.score)">{{ formatScore(newScore.score) }}/5</span>
                    <span class="change-indicator" :class="getChangeClass(getOriginalScore(newScore.dimension_name), newScore.score)">
                      {{ getChangeIcon(getOriginalScore(newScore.dimension_name), newScore.score) }}
                    </span>
                  </span>
                </div>
              </div>
              
              <!-- 新平均分 -->
              <div class="new-average">
                <span class="label">新平均分：</span>
                <span class="score-change">
                  <span class="old-score">{{ formatScore(badcaseData.original_ai_scoring.average_score) }}/5</span>
                  <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                  <span class="new-score" :class="getScoreClass(badcaseData.review_info.new_average_score)">
                    {{ formatScore(badcaseData.review_info.new_average_score) }}/5
                  </span>
                  <span class="change-indicator" :class="getChangeClass(badcaseData.original_ai_scoring.average_score, badcaseData.review_info.new_average_score)">
                    {{ getChangeIcon(badcaseData.original_ai_scoring.average_score, badcaseData.review_info.new_average_score) }}
                  </span>
                </span>
              </div>
            </div>
            
            <!-- 复核理由 -->
            <div v-if="badcaseData.review_info.review_comment" class="review-item">
              <span class="label">复核理由：</span>
              <div class="review-comment">
                {{ badcaseData.review_info.review_comment }}
              </div>
            </div>
            
            <!-- 复核时间 -->
            <div class="review-item">
              <span class="label">复核时间：</span>
              <span class="value">{{ badcaseData.review_info.reviewed_at }}</span>
            </div>
            
            <!-- 复核人员（预留） -->
            <div class="review-item">
              <span class="label">复核人员：</span>
              <span class="value">{{ badcaseData.review_info.reviewer_id || '系统用户' }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script>
import { ArrowRight } from '@element-plus/icons-vue'

export default {
  name: 'BadcaseDetailModal',
  components: {
    ArrowRight
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    questionId: {
      type: Number,
      default: null
    }
  },
  emits: ['update:visible'],
  data() {
    return {
      loading: false,
      badcaseData: null
    }
  },
  watch: {
    visible(newVal) {
      if (newVal && this.questionId) {
        this.loadBadcaseDetail()
      }
    }
  },
  methods: {
    async loadBadcaseDetail() {
      this.loading = true
      try {
        const { getBadcaseDetail } = await import('@/api/badcase')
        const response = await getBadcaseDetail(this.questionId)

        if (response.success) {
          this.badcaseData = response.data
        } else {
          this.$message.error(response.message || '获取详情失败')
        }
      } catch (error) {
        console.error('加载badcase详情失败:', error)
        this.$message.error('加载详情失败')
      } finally {
        this.loading = false
      }
    },
    
    handleClose() {
      this.$emit('update:visible', false)
    },
    
    getAssistantTagType(type) {
      const typeMap = {
        'yoyo': 'primary',
        'doubao': 'success',
        'xiaotian': 'warning'
      }
      return typeMap[type] || 'info'
    },
    
    getAssistantName(type) {
      const nameMap = {
        'yoyo': 'YOYO',
        'doubao': '豆包',
        'xiaotian': '小天'
      }
      return nameMap[type] || type
    },
    
    getScoreClass(score) {
      if (score >= 4) return 'score-high'
      if (score >= 3) return 'score-medium'
      return 'score-low'
    },
    
    getReviewResultType(result) {
      const typeMap = {
        'confirmed': 'danger',
        'rejected': 'success'
      }
      return typeMap[result] || 'info'
    },
    
    getReviewResultText(result) {
      const textMap = {
        'confirmed': '确认badcase',
        'rejected': '误判，非badcase'
      }
      return textMap[result] || result
    },
    
    getOriginalScore(dimensionName) {
      // 优先从original_ai_scoring获取
      if (this.badcaseData.original_ai_scoring && this.badcaseData.original_ai_scoring.dimensions) {
        const dimension = this.badcaseData.original_ai_scoring.dimensions.find(
          d => d.dimension_name === dimensionName
        )
        if (dimension) {
          return parseFloat(dimension.score) || 0
        }
      }

      // 备用：从low_score_dimensions获取
      if (this.badcaseData.low_score_dimensions) {
        const dimension = this.badcaseData.low_score_dimensions.find(
          d => d.dimension_name === dimensionName
        )
        if (dimension) {
          return parseFloat(dimension.score) || 0
        }
      }

      return 0
    },
    
    getChangeClass(oldScore, newScore) {
      if (newScore > oldScore) return 'score-up'
      if (newScore < oldScore) return 'score-down'
      return 'score-same'
    },
    
    getChangeIcon(oldScore, newScore) {
      if (newScore > oldScore) return '⬆️'
      if (newScore < oldScore) return '⬇️'
      return '➡️'
    },

    formatScore(score) {
      // 格式化分数，确保显示精度正确
      if (score === null || score === undefined) return '0'
      const numScore = parseFloat(score)
      return isNaN(numScore) ? '0' : numScore.toFixed(1)
    }
  }
}
</script>

<style scoped>
.badcase-detail-modal {
  .detail-content {
    max-height: 70vh;
    overflow-y: auto;
  }

  .info-card {
    margin-bottom: 20px;

    .card-title {
      font-weight: bold;
      font-size: 16px;
    }
  }

  .info-item {
    margin-bottom: 10px;

    .label {
      font-weight: 500;
      color: #606266;
    }

    .value {
      color: #303133;
    }
  }

  .question-content {
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 6px;
    line-height: 1.6;
    color: #303133;
  }

  .answers-container {
    .answer-item {
      margin-bottom: 15px;
      border: 1px solid #e4e7ed;
      border-radius: 6px;
      padding: 15px;

      .answer-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        .answer-time {
          color: #909399;
          font-size: 12px;
        }
      }

      .answer-content {
        line-height: 1.6;
        color: #303133;
      }
    }
  }

  .ai-scoring {
    border-left: 4px solid #409eff;

    .scoring-content {
      .scores-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 20px;

        .score-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background-color: #f8f9fa;
          border-radius: 6px;

          .dimension-name {
            font-weight: 500;
          }

          .score-value {
            font-weight: bold;

            &.score-high { color: #67c23a; }
            &.score-medium { color: #e6a23c; }
            &.score-low { color: #f56c6c; }
          }
        }
      }

      .average-score, .ai-reasoning, .detection-result {
        margin-bottom: 15px;

        .label {
          font-weight: 500;
          color: #606266;
        }

        .value {
          font-weight: bold;

          &.score-high { color: #67c23a; }
          &.score-medium { color: #e6a23c; }
          &.score-low { color: #f56c6c; }
        }

        .threshold-info {
          color: #909399;
          font-size: 12px;
          margin-left: 10px;
        }
      }

      .reasoning-content {
        margin-top: 8px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 6px;
        line-height: 1.6;
      }
    }
  }

  .review-info {
    border-left: 4px solid #67c23a;

    .review-content {
      .no-review {
        text-align: center;
        padding: 20px;
      }

      .review-details {
        .review-item {
          margin-bottom: 15px;

          .label {
            font-weight: 500;
            color: #606266;
          }

          .value {
            color: #303133;
          }

          .review-comment {
            margin-top: 8px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
            line-height: 1.6;
          }
        }

        .score-comparison {
          margin: 20px 0;

          .comparison-title {
            font-weight: 500;
            margin-bottom: 15px;
            color: #606266;
          }

          .comparison-grid {
            display: grid;
            gap: 10px;
            margin-bottom: 15px;

            .comparison-item {
              display: flex;
              align-items: center;
              padding: 10px;
              background-color: #f8f9fa;
              border-radius: 6px;

              .dimension-name {
                font-weight: 500;
                min-width: 80px;
              }

              .score-change {
                display: flex;
                align-items: center;
                gap: 8px;

                .old-score {
                  color: #909399;
                }

                .arrow-icon {
                  color: #909399;
                }

                .new-score {
                  font-weight: bold;

                  &.score-high { color: #67c23a; }
                  &.score-medium { color: #e6a23c; }
                  &.score-low { color: #f56c6c; }
                }

                .change-indicator {
                  &.score-up { color: #67c23a; }
                  &.score-down { color: #f56c6c; }
                  &.score-same { color: #909399; }
                }
              }
            }
          }

          .new-average {
            padding: 15px;
            background-color: #e8f4fd;
            border-radius: 6px;
            border-left: 4px solid #409eff;

            .label {
              font-weight: 500;
              color: #606266;
            }
          }
        }
      }
    }
  }

  .loading-container {
    padding: 20px;
  }
}
</style>
