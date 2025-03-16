<script setup lang="ts">
import groupService from '@renderer/services/group'
import { onMounted, ref } from 'vue'

const selectMenuTag = ref<number>(0)
const groupList = ref<Group[]>([])
const createGroupDialogRef = ref()

function handleNewGroup() {
  openModal()
}

function openModal() {
  createGroupDialogRef.value?.openModal()
}

function getGroupList() {
  groupService.invokeGetAllGroups().then((res: ApiResponse<Group[]>) => {
    if (res.success && res.data) {
      groupList.value = res.data
    }
  })
}

function refreshGroupList() {
  getGroupList()
  if (groupList.value.length > 0) {
    selectMenuTag.value = groupList.value.length - 1
  }
}

onMounted(() => {
  getGroupList()
})
</script>

<template>
  <a-layout class="layout">
    <a-layout-header class="layout-header">
      <MenuTag v-for="group in groupList" :key="group.id" :title="group.name" />
      <MenuTag
        v-if="groupList.length == 0"
        title="组管理"
        :active="selectMenuTag == 0"
        :closeable="false"
      />
      <MenuTag tag-type="corner" @click="handleNewGroup" />
    </a-layout-header>
    <a-layout-content class="layout-content">
      <GroupPage v-if="groupList.length > 0" :group-info="groupList[selectMenuTag]" />
      <GroupPage v-else />
    </a-layout-content>
    <CreateGroupDialog
      ref="createGroupDialogRef"
      @open-modal="openModal"
      @handle-ok="getGroupList"
    />
  </a-layout>
</template>

<style scoped lang="less">
.layout {
  height: 100vh;

  .layout-sider {
    line-height: 120px;
  }

  .layout-header {
    background: #fff;
    padding: 0;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
    z-index: 1;
    height: 2rem;
    display: flex;
    flex-direction: row;
  }
  .layout-content {
    padding: 20px;
    .text-avatar {
      width: 40%;
    }
    .gutter-box-avatar {
      display: flex;
      justify-content: center; /* 默认居中 */
      align-items: center;
      height: 100%; /* 确保垂直居中 */
    }
    @media (min-width: 770px) {
      .text-avatar {
        width: 100%;
      }
    }
  }
}
</style>
