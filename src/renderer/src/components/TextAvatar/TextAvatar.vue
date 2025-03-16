<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  displayType: {
    type: String,
    default: 'head', // 默认展示前两个字
    validator: (value) => ['head', 'foot'].includes(value)
  },
  bgType: {
    type: String,
    default: 'fix', // 默认固定背景色
    validator: (value) => ['fix', 'gradient'].includes(value)
  },
  fgType: {
    type: String,
    default: 'fix', // 默认固定前景色
    validator: (value) => ['fix', 'gradient'].includes(value)
  }
})

// 计算头像显示的文本
const avatarText = computed(() => {
  if (!props.title) return '?'
  return props.displayType === 'head' ? props.title.slice(0, 2) : props.title.slice(-2)
})

// 生成随机颜色（用于渐变）
const randomColor = () => `hsl(${Math.random() * 360}, 70%, 60%)`

// 计算背景色
const backgroundColor = computed(() => {
  return props.bgType === 'fix'
    ? `background-color: ${randomColor()};` // 固定蓝色背景
    : `background: linear-gradient(135deg, ${randomColor()}, ${randomColor()})`
})

// 计算前景色
const foregroundColor = computed(() => {
  return props.fgType === 'fix'
    ? 'color: white;'
    : 'background: -webkit-linear-gradient(135deg, #3b82f6, #93c5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'
})
</script>

<template>
  <div class="text-avatar" :style="backgroundColor">
    <div class="inner-text" :style="foregroundColor">
      {{ avatarText }}
    </div>
  </div>
</template>

<style scoped>
.text-avatar {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  .inner-text {
    font-weight: bold;
    font-size: 5vw;
  }
}

.text-transparent {
  -webkit-background-clip: text;
  background-clip: text;
}
</style>
