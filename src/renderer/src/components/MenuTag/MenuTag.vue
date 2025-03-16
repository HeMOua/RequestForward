<script setup lang="ts">
import { CloseOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { PropType } from 'vue'

defineOptions({ name: 'MenuTag' })

defineProps({
  title: {
    type: String,
    require: true
  },
  tagType: {
    type: String as PropType<MenuTagType>,
    default: 'normal'
  },
  active: {
    type: Boolean,
    default: false
  },
  closeable: {
    type: Boolean,
    default: true
  }
})
</script>

<template>
  <div v-if="tagType == 'normal'" class="menu-tag" :class="{ active: active }">
    <span>{{ title }}</span>
    <span v-if="closeable" class="close-icon">
      <CloseOutlined />
    </span>
  </div>
  <div v-else class="menu-tag corner">
    <PlusOutlined />
  </div>
</template>

<style lang="less" scoped>
.menu-tag {
  height: 2rem;
  line-height: 2rem;
  flex: 1;
  text-align: center;
  background-color: #dddddd;
  user-select: none;
  position: relative;
  &:not(:last-of-type) {
    border-right: 1px solid #c2c2c2;
  }
  &:hover {
    &:not(.active) {
      background-color: #d7d7d7;
      cursor: pointer;
    }

    .close-icon {
      display: inline-block;
    }
  }
  &.active {
    background-color: #fff;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
  }
  &.corner {
    flex: none;
    width: 2rem;
  }

  .close-icon {
    display: none;
    height: 1rem;
    line-height: 1rem;
    position: absolute;
    top: 0.5rem;
    right: 8px;
    &:hover {
      background-color: #e3e3e3;
      border-radius: 2px;
    }
  }
}
</style>
