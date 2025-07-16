<template>
  <div class="scores">
    <div class="page-header">
      <h1>评分分析</h1>
      <p class="page-description">AI模型评分结果分析</p>
    </div>

    <el-card>
      <div style="text-align: center; padding: 60px 0;">
        <el-icon size="64" color="#909399">
          <DataLine />
        </el-icon>
        <p style="margin: 20px 0; color: #909399; font-size: 16px;">
          评分分析功能开发中...
        </p>
        <el-button type="primary" @click="comingSoon">
          敬请期待
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'Scores',
  setup() {
    const comingSoon = () => {
      ElMessage.info('功能开发中，敬请期待！')
    }

    return {
      comingSoon
    }
  }
}
</script> 