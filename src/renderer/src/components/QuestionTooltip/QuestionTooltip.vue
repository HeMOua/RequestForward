<script lang="ts" setup>
import { QuestionCircleTwoTone } from '@ant-design/icons-vue'

defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<template>
  <a-tooltip placement="right">
    <template #title>
      <span>{{ title }}</span>
    </template>
    <question-circle-two-tone style="margin-left: 5px" />
  </a-tooltip>
</template>
