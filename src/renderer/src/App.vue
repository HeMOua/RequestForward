<script setup lang="ts">
import {
  PieChartOutlined,
  DesktopOutlined,
  UserOutlined,
  TeamOutlined,
  FileOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons-vue'
import { ref } from 'vue'

const selectedKeys = ref(['1'])
const collapsed = ref(false)
</script>

<template>
  <a-layout class="layout">
    <a-layout-sider
      v-model:collapsed="collapsed"
      class="layout-sider"
      :trigger="null"
      :collapsed-width="60"
      collapsible
    >
      <a-menu v-model:selected-keys="selectedKeys" theme="dark" mode="inline">
        <a-menu-item key="1">
          <pie-chart-outlined />
          <span>Option 1</span>
        </a-menu-item>
        <a-menu-item key="2">
          <desktop-outlined />
          <span>Option 2</span>
        </a-menu-item>
        <a-sub-menu key="sub1">
          <template #title>
            <span>
              <user-outlined />
              <span>User</span>
            </span>
          </template>
          <a-menu-item key="3">Tom</a-menu-item>
          <a-menu-item key="4">Bill</a-menu-item>
          <a-menu-item key="5">Alex</a-menu-item>
        </a-sub-menu>
        <a-sub-menu key="sub2">
          <template #title>
            <span>
              <team-outlined />
              <span>Team</span>
            </span>
          </template>
          <a-menu-item key="6">Team 1</a-menu-item>
          <a-menu-item key="8">Team 2</a-menu-item>
        </a-sub-menu>
        <a-menu-item key="9">
          <file-outlined />
          <span>File</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="layout-header">
        <menu-unfold-outlined
          v-if="collapsed"
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        <menu-fold-outlined v-else class="trigger" @click="() => (collapsed = !collapsed)" />
      </a-layout-header>
      <a-layout-content>Contentasdf</a-layout-content>
    </a-layout>
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
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1;
    .trigger {
      font-size: 18px;
      line-height: 64px;
      padding: 0 24px;
      cursor: pointer;
      transition: color 0.3s;
      &:hover {
        color: #1890ff;
      }
    }
  }
}
</style>
