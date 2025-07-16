<template>
  <div class="answers">
    <div class="page-header">
      <h1>答案对比</h1>
      <p class="page-description">多AI模型答案对比分析</p>
    </div>

    <el-card>
      <div style="text-align: center; padding: 60px 0;">
        <el-icon size="64" color="#909399">
          <Document />
        </el-icon>
        <p style="margin: 20px 0; color: #909399; font-size: 16px;">
          答案对比功能开发中...
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
  name: 'Answers',
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