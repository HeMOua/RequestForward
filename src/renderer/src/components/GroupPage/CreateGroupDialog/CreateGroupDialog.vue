<script setup lang="ts">
import { ref, computed, CSSProperties, watch, watchEffect, reactive, toRaw } from 'vue'
import { useDraggable } from '@vueuse/core'
import { Rule } from 'ant-design-vue/es/form'
import groupService from '@renderer/services/group'

const emits = defineEmits(['handleOk'])

const open = ref<boolean>(false)
const modalTitleRef = ref()
const { x, y, isDragging } = useDraggable(modalTitleRef)
const openModal = () => (open.value = true)
const closeModal = () => (open.value = false)
const startX = ref<number>(0)
const startY = ref<number>(0)
const startedDrag = ref(false)
const transformX = ref(0)
const transformY = ref(0)
const preTransformX = ref(0)
const preTransformY = ref(0)
const dragRect = ref({ left: 0, right: 0, top: 0, bottom: 0 })
watch([x, y], () => {
  if (!startedDrag.value) {
    startX.value = x.value
    startY.value = y.value
    const bodyRect = document.body.getBoundingClientRect()
    const titleRect = modalTitleRef.value.getBoundingClientRect()
    dragRect.value.right = bodyRect.width - titleRect.width
    dragRect.value.bottom = bodyRect.height - titleRect.height
    preTransformX.value = transformX.value
    preTransformY.value = transformY.value
  }
  startedDrag.value = true
})
watch(isDragging, () => {
  if (!isDragging) {
    startedDrag.value = false
  }
})

watchEffect(() => {
  if (startedDrag.value) {
    transformX.value =
      preTransformX.value +
      Math.min(Math.max(dragRect.value.left, x.value), dragRect.value.right) -
      startX.value
    transformY.value =
      preTransformY.value +
      Math.min(Math.max(dragRect.value.top, y.value), dragRect.value.bottom) -
      startY.value
  }
})
const transformStyle = computed<CSSProperties>(() => {
  return {
    transform: `translate(${transformX.value}px, ${transformY.value}px)`
  }
})

const formState = reactive<Partial<CreateGroupDto>>({
  name: '',
  alias: '',
  address: '',
  port: undefined,
  status: undefined,
  refresh: true,
  refreshInterval: undefined,
  comment: ''
})

const rules: Record<string, Rule[]> = {
  name: [{ required: true, message: '请输入分组名', trigger: 'change' }],
  address: [{ required: true, message: '请输入代理地址', trigger: 'change' }],
  port: [{ required: true, message: '请输入代理端口', trigger: 'change' }],
  status: [{ required: true, message: '请选择启用状态', trigger: 'change' }]
}

const formRef = ref()

const handleOk = () => {
  formRef.value.validate().then((valid) => {
    if (valid) {
      groupService.invokeAddGroup(toRaw(formState)).then((res: ApiResponse) => {
        if (res.success) {
          closeModal()
          emits('handleOk')
        }
      })
    }
  })
}

defineExpose({
  openModal,
  closeModal
})
</script>

<template>
  <a-modal ref="modalRef" v-model:open="open" :wrap-style="{ overflow: 'hidden' }" @ok="handleOk">
    <a-form
      ref="formRef"
      name="basic"
      :model="formState"
      :rules="rules"
      :label-col="{ span: 8 }"
      :wrapper-col="{ span: 16 }"
      autocomplete="off"
    >
      <a-form-item label="名称" name="name">
        <a-input v-model:value="formState.name" />
      </a-form-item>

      <a-form-item label="别名" name="alias">
        <a-input v-model:value="formState.alias" />
      </a-form-item>

      <a-form-item label="地址" name="address">
        <a-input v-model:value="formState.address" />
      </a-form-item>

      <a-form-item label="端口" name="port">
        <a-input-number v-model:value="formState.port" />
      </a-form-item>

      <a-form-item label="启用状态" name="status">
        <a-switch
          v-model:checked="formState.status"
          checked-children="启用"
          un-checked-children="禁用"
        />
      </a-form-item>

      <a-form-item label="是否刷新" name="refresh">
        <a-switch
          v-model:checked="formState.refresh"
          checked-children="是"
          un-checked-children="否"
        />
      </a-form-item>

      <a-form-item label="刷新间隔" name="refreshInterval">
        <a-input-number v-model:value="formState.refreshInterval" />
      </a-form-item>

      <a-form-item label="备注" name="comment">
        <a-textarea v-model:value="formState.comment" />
      </a-form-item>
    </a-form>
    <template #title>
      <div ref="modalTitleRef" style="width: 100%; cursor: move">创建分组</div>
    </template>
    <template #modalRender="{ originVNode }">
      <div :style="transformStyle">
        <component :is="originVNode" />
      </div>
    </template>
  </a-modal>
</template>
