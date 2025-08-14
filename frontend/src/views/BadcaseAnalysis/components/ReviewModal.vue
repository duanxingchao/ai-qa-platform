<template>
  <el-dialog
    :model-value="visible"
    title="Badcase复核"
    width="800px"
    :before-close="handleClose"
    @update:model-value="handleClose"
  >
    <div v-if="badcaseData" class="review-content">
      <!-- 问题信息 -->
      <el-card class="question-card" shadow="never">
        <template #header>
          <span>问题信息</span>
        </template>
        <div class="question-info">
          <p><strong>问题内容:</strong> {{ badcaseData.query }}</p>
          <p><strong>YOYO答案:</strong> {{ badcaseData.yoyo_answer || '暂无答案' }}</p>
          <p><strong>当前状态:</strong> 
            <el-tag :type="getStatusTagType(badcaseData.review_status)">
              {{ getStatusText(badcaseData.review_status) }}
            </el-tag>
          </p>
        </div>
      </el-card>

      <!-- 原始评分 -->
      <el-card class="original-scores-card" shadow="never">
        <template #header>
          <span>原始评分 (导致badcase的评分)</span>
        </template>
        <el-row :gutter="16">
          <el-col :span="8" v-for="dim in originalScores" :key="dim.dimension_name">
            <div class="original-score-item">
              <div class="score-name">{{ dim.dimension_name }}</div>
              <div class="score-value" :class="{ 'low-score': dim.score < 2.5 }">
                {{ dim.score }}/5
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 重新评分界面 -->
      <el-card class="review-scores-card" shadow="never">
        <template #header>
          <span>重新评分</span>
        </template>
        <el-form :model="reviewForm" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12" v-for="(score, index) in reviewForm.scores" :key="score.dimension_name">
              <el-form-item :label="score.dimension_name">
                <el-rate
                  v-model="score.score"
                  :max="5"
                  show-score
                  score-template="{value}/5"
                  style="margin-right: 10px;"
                />
                <el-input-number
                  v-model="score.score"
                  :min="1"
                  :max="5"
                  :step="0.1"
                  :precision="1"
                  size="small"
                  style="width: 80px;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="复核理由">
            <el-input
              v-model="reviewForm.comment"
              type="textarea"
              :rows="4"
              placeholder="请输入复核理由和评分依据..."
            />
          </el-form-item>
          
          <el-form-item label="复核结果">
            <el-radio-group v-model="reviewForm.reviewResult">
              <el-radio label="confirmed">确认为badcase</el-radio>
              <el-radio label="rejected">误判，非badcase（需修改评分）</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 评分预览 -->
      <el-card class="preview-card" shadow="never">
        <template #header>
          <span>评分预览</span>
        </template>
        <div class="score-preview">
          <div class="average-score">
            <el-statistic 
              title="新平均分" 
              :value="averageScore" 
              :precision="2" 
              suffix="/5"
              :value-style="{ color: averageScore >= 2.5 ? '#67C23A' : '#F56C6C' }"
            />
          </div>
          <div class="threshold-info">
            <p>当前阈值: <strong>{{ threshold }}</strong></p>
            <p>预测结果: 
              <el-tag :type="averageScore >= threshold ? 'success' : 'danger'">
                {{ averageScore >= threshold ? '非badcase' : 'badcase' }}
              </el-tag>
            </p>
          </div>
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button @click="resetScores">重置评分</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">
          提交复核
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
export default {
  name: 'ReviewModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    badcaseData: {
      type: Object,
      default: null
    },
    threshold: {
      type: Number,
      default: 2.5
    }
  },
  emits: ['update:visible', 'submit-review'],
  data() {
    return {
      submitting: false,
      reviewForm: {
        scores: [],
        comment: '',
        reviewResult: 'confirmed'
      },
      originalScores: []
    }
  },
  computed: {
    averageScore() {
      if (this.reviewForm.scores.length === 0) return 0
      const total = this.reviewForm.scores.reduce((sum, score) => sum + score.score, 0)
      return total / this.reviewForm.scores.length
    }
  },
  watch: {
    badcaseData: {
      handler(newData) {
        if (newData) {
          this.initializeScores()
        }
      },
      immediate: true
    }
  },
  methods: {
    initializeScores() {
      if (!this.badcaseData) return

      // 初始化原始评分
      this.originalScores = this.badcaseData.low_score_dimensions || []

      // 根据问题分类动态获取评分维度
      let dimensions = ['准确性', '完整性', '清晰度', '实用性', '创新性'] // 默认维度

      // 如果有原始评分数据，使用原始评分的维度
      if (this.badcaseData.yoyo_scores && this.badcaseData.yoyo_scores.dimensions) {
        dimensions = this.badcaseData.yoyo_scores.dimensions.map(score => score.dimension_name)
      }

      // 初始化复核评分表单
      this.reviewForm.scores = dimensions.map(dim => ({
        dimension_name: dim,
        score: 3.0 // 默认分数
      }))

      // 如果有原始评分，使用原始评分作为初始值
      if (this.badcaseData.yoyo_scores && this.badcaseData.yoyo_scores.dimensions) {
        this.badcaseData.yoyo_scores.dimensions.forEach(originalScore => {
          const reviewScore = this.reviewForm.scores.find(s => s.dimension_name === originalScore.dimension_name)
          if (reviewScore) {
            reviewScore.score = originalScore.score
          }
        })
      }
    },
    
    resetScores() {
      this.initializeScores()
      this.reviewForm.comment = ''
      this.reviewForm.reviewResult = 'confirmed'
    },
    
    async submitReview() {
      if (!this.reviewForm.comment.trim()) {
        this.$message.warning('请填写复核理由')
        return
      }

      // 如果选择误判，必须修改评分
      if (this.reviewForm.reviewResult === 'rejected') {
        const hasScoreChanged = this.reviewForm.scores.some((score, index) => {
          const originalScore = this.badcaseData.original_scores?.[index]?.score || 0
          return Math.abs(score.score - originalScore) > 0.01
        })

        if (!hasScoreChanged) {
          this.$message.warning('选择误判时必须修改评分')
          return
        }
      }

      this.submitting = true
      try {
        const reviewData = {
          question_id: this.badcaseData.id,
          scores: this.reviewForm.scores,
          comment: this.reviewForm.comment,
          review_result: this.reviewForm.reviewResult,
          average_score: this.averageScore
        }

        this.$emit('submit-review', reviewData)
      } finally {
        this.submitting = false
      }
    },
    
    handleClose() {
      this.$emit('update:visible', false)
    },
    
    getStatusTagType(status) {
      const typeMap = {
        pending: 'warning',
        reviewed: 'success'
      }
      return typeMap[status] || 'info'
    },

    getStatusText(status) {
      const textMap = {
        pending: '待处理',
        reviewed: '已复核'
      }
      return textMap[status] || status
    }
  }
}
</script>

<style lang="scss" scoped>
.review-content {
  .question-card, .original-scores-card, .review-scores-card, .preview-card {
    margin-bottom: 20px;
  }
  
  .question-info {
    p {
      margin: 10px 0;
      line-height: 1.6;
    }
  }
  
  .original-score-item {
    text-align: center;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 4px;
    margin-bottom: 10px;
    
    .score-name {
      font-size: 12px;
      color: #606266;
      margin-bottom: 5px;
    }
    
    .score-value {
      font-size: 18px;
      font-weight: bold;
      color: #409EFF;
      
      &.low-score {
        color: #F56C6C;
      }
    }
  }
  
  .score-preview {
    display: flex;
    align-items: center;
    
    .average-score {
      margin-right: 30px;
    }
    
    .threshold-info {
      p {
        margin: 5px 0;
      }
    }
  }
}
</style>
