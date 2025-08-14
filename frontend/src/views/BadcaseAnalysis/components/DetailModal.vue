<template>
  <el-dialog
    :model-value="visible"
    title="Badcase详情"
    width="900px"
    :before-close="handleClose"
    @update:model-value="handleClose"
  >
    <div v-if="badcaseDetail" class="detail-content">
      <!-- 基本信息 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="问题ID">
          {{ badcaseDetail.business_id }}
        </el-descriptions-item>
        <el-descriptions-item label="检测时间">
          {{ formatDate(badcaseDetail.badcase_detected_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="复核状态">
          <el-tag :type="getStatusTagType(badcaseDetail.badcase_review_status)">
            {{ getStatusText(badcaseDetail.badcase_review_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          {{ badcaseDetail.classification || '未分类' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 问题内容 -->
      <el-divider content-position="left">问题内容</el-divider>
      <div class="question-content">
        {{ badcaseDetail.query }}
      </div>

      <!-- 三个AI模型回答 -->
      <el-divider content-position="left">AI模型回答</el-divider>
      <el-tabs v-model="activeTab" class="answer-tabs">
        <el-tab-pane 
          v-for="answer in badcaseDetail.answers" 
          :key="answer.assistant_type"
          :label="getModelName(answer.assistant_type)"
          :name="answer.assistant_type"
        >
          <div class="answer-content">
            <div class="answer-text">
              {{ answer.answer_text || '暂无回答' }}
            </div>
            <div class="answer-meta">
              <span>回答时间: {{ formatDate(answer.answer_time) }}</span>
              <span>是否已评分: {{ answer.is_scored ? '是' : '否' }}</span>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- YOYO模型五个维度评分 -->
      <el-divider content-position="left">YOYO模型评分详情</el-divider>
      <div v-if="badcaseDetail.yoyo_scores" class="score-details">
        <div class="score-summary">
          <el-statistic title="平均分" :value="badcaseDetail.yoyo_scores.average_score" :precision="2" suffix="/5" />
          <div class="score-comment">
            <strong>评分理由:</strong> {{ badcaseDetail.yoyo_scores.comment || '无' }}
          </div>
        </div>
        
        <el-row :gutter="16" class="score-dimensions">
          <el-col :span="8" v-for="score in badcaseDetail.yoyo_scores.dimensions" :key="score.dimension_name">
            <el-card class="score-card">
              <div class="score-item">
                <div class="score-name">{{ score.dimension_name }}</div>
                <div class="score-value" :class="{ 'low-score': score.score < 2.5 }">
                  {{ score.score }}/5
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 低分维度高亮 -->
      <el-divider content-position="left">低分维度分析</el-divider>
      <div class="low-dimensions-analysis">
        <div v-if="badcaseDetail.low_score_dimensions && badcaseDetail.low_score_dimensions.length > 0">
          <el-alert
            title="以下维度评分低于阈值，导致被标记为badcase"
            type="warning"
            :closable="false"
            show-icon
          />
          <div class="low-dimensions-list">
            <el-tag
              v-for="dim in badcaseDetail.low_score_dimensions"
              :key="dim.dimension_name"
              type="danger"
              size="large"
              class="dimension-tag"
            >
              {{ dim.dimension_name }}: {{ dim.score }}/5 (阈值: {{ dim.threshold }})
            </el-tag>
          </div>
        </div>
        <el-empty v-else description="无低分维度数据" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="badcaseDetail && badcaseDetail.badcase_review_status === 'pending'"
          type="warning" 
          @click="startReview"
        >
          开始复核
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
export default {
  name: 'DetailModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    badcaseDetail: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible', 'start-review'],
  data() {
    return {
      activeTab: 'yoyo'
    }
  },
  methods: {
    handleClose() {
      this.$emit('update:visible', false)
    },
    
    startReview() {
      this.$emit('start-review', this.badcaseDetail)
    },
    
    getModelName(model) {
      const nameMap = {
        yoyo: 'YOYO',
        doubao: '豆包',
        xiaotian: '小天',
        gpt: 'GPT',
        claude: 'Claude'
      }
      return nameMap[model] || model.toUpperCase()
    },
    
    getStatusTagType(status) {
      const typeMap = {
        pending: 'warning',
        reviewed: 'primary',
        optimized: 'success'
      }
      return typeMap[status] || 'info'
    },
    
    getStatusText(status) {
      const textMap = {
        pending: '待处理',
        reviewed: '已复核',
        optimized: '已优化'
      }
      return textMap[status] || status
    },
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style lang="scss" scoped>
.detail-content {
  .question-content {
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 6px;
    margin: 10px 0;
    line-height: 1.6;
    border-left: 4px solid #409EFF;
  }
  
  .answer-tabs {
    margin: 15px 0;
    
    .answer-content {
      .answer-text {
        padding: 15px;
        background-color: #fafafa;
        border-radius: 6px;
        line-height: 1.6;
        margin-bottom: 10px;
        min-height: 100px;
      }
      
      .answer-meta {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #909399;
      }
    }
  }
  
  .score-details {
    .score-summary {
      display: flex;
      align-items: center;
      margin-bottom: 20px;
      padding: 15px;
      background-color: #f8f9fa;
      border-radius: 6px;
      
      .score-comment {
        margin-left: 30px;
        flex: 1;
        color: #606266;
      }
    }
    
    .score-dimensions {
      .score-card {
        margin-bottom: 10px;
        
        .score-item {
          text-align: center;
          
          .score-name {
            font-size: 14px;
            color: #606266;
            margin-bottom: 8px;
          }
          
          .score-value {
            font-size: 24px;
            font-weight: bold;
            color: #409EFF;
            
            &.low-score {
              color: #F56C6C;
            }
          }
        }
      }
    }
  }
  
  .low-dimensions-analysis {
    .low-dimensions-list {
      margin-top: 15px;
      
      .dimension-tag {
        margin-right: 10px;
        margin-bottom: 10px;
        padding: 8px 12px;
        font-size: 14px;
      }
    }
  }
}
</style>
