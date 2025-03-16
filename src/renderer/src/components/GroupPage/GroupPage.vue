<script lang="ts" setup>
import { computed, onMounted, PropType } from 'vue'
import EmptyPng from '@renderer/assets/icons/empty.png'

const emits = defineEmits(['openModal'])

const props = defineProps({
  groupInfo: {
    type: Object as PropType<Group>,
    default: () => undefined
  }
})

const proxyAddress = computed(() => {
  if (props.groupInfo?.address && props.groupInfo?.port) {
    return `${props.groupInfo.address}:${props.groupInfo.port}`
  } else {
    return '未配置代理地址'
  }
})

const handleCreateGroup = () => {
  emits('openModal')
}

onMounted(() => {})
</script>

<template>
  <div style="height: 100%">
    <div v-if="groupInfo" class="group-page-wrapper">
      <a-row :gutter="{ xs: 12, sm: 12, md: 24, lg: 24 }">
        <!-- 第一列：小屏占满（100%），大屏占25% -->
        <a-col class="gutter-row" :xs="24" :sm="24" :md="4" :lg="4">
          <div class="gutter-box-avatar">
            <TextAvatar :title="groupInfo.name" :fg-type="'gradient'" :bg-type="'gradient'" />
          </div>
        </a-col>
        <!-- 第二列：小屏占满（100%），大屏占75% -->
        <a-col class="gutter-row" :xs="24" :sm="24" :md="20" :lg="20">
          <a-descriptions>
            <template #title>
              <a-typography-title>分组信息</a-typography-title>
            </template>
            <a-descriptions-item>
              <template #label>
                <a-typography-text strong>名称</a-typography-text>
              </template>
              {{ groupInfo.name }}
            </a-descriptions-item>
            <a-descriptions-item>
              <template #label>
                <a-typography-text strong>别名</a-typography-text>
                <QuestionTooltip title="英文，可用于配置代理路径" />
              </template>
              {{ groupInfo.alias }}
            </a-descriptions-item>
            <a-descriptions-item>
              <template #label>
                <a-typography-text strong>创建时间</a-typography-text>
              </template>
              {{ groupInfo.createTime }}
            </a-descriptions-item>
            <a-descriptions-item>
              <template #label>
                <a-typography-text strong>代理地址</a-typography-text>
              </template>
              {{ proxyAddress }}
            </a-descriptions-item>
          </a-descriptions>
        </a-col>
      </a-row>
      <div>wocao</div>
    </div>
    <div v-else class="group-page-empty-wrapper">
      <a-empty
        :image="EmptyPng"
        :image-style="{
          height: '60px'
        }"
      >
        <template #description>
          <span> 当前没有分组 </span>
        </template>
        <a-button type="primary" @click="handleCreateGroup">立即创建</a-button>
      </a-empty>
    </div>
  </div>
</template>

<style scoped lang="less">
.group-page-empty-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
