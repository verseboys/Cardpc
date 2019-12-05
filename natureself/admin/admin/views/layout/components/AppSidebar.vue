<template>
  <el-aside
    id="app-sidebar"
    :width="sidebarWidth"
    :class="sidebarClass"
  >
    <el-container>
      <el-header
        class="brand-logo"
        height="50px"
      >
        <img :src="appLogo">
        <span class="brand-text">{{ appTitle }}</span>
      </el-header>

      <el-main class="menu-container">
        <el-scrollbar>
          <el-menu
            :default-active="$route.path"
            :collapse="sidebar.collapsed"
            mode="vertical"
          >
            <sidebar-menu-item
              v-for="route in visibleRoutes"
              :key="route.path"
              :route="route"
              :base-path="route.path"
            />
          </el-menu>
        </el-scrollbar>
      </el-main>
    </el-container>
  </el-aside>
</template>

<script>
import { mapGetters } from 'vuex'
import SidebarMenuItem from './SidebarMenuItem.vue'

export default {
  components: {
    SidebarMenuItem,
  },
  data: () => ({
  }),
  computed: {
    ...mapGetters([
      'sidebar',
      'appLogo',
      'appTitle',
      'routes',
    ]),

    visibleRoutes () {
      return this.routes.filter(item => (item.hidden === undefined || !item.hidden))
    },

    sidebarClass () {
      return {
        collapsed: this.sidebar.collapsed,
        'no-animation': !this.sidebar.animation,
      }
    },

    sidebarWidth () {
      return this.sidebar.collapsed ? '64px' : '210px'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '~element-ui/packages/theme-chalk/src/common/var.scss';

#app-sidebar {
  transition: width, 0.28s;
  background-color: $--color-primary-light-9;
  min-height: 100vh;
}

#app-sidebar.no-animation {
  transition: none !important;
}

.el-menu {
  background-color: $--color-primary-light-9;
}

.brand-logo {
  display: flex;
  align-content: center;
  // collapsed sidebar width: 64px, logo image width: 36px, to center image, padding left: (64-36)/2 = 14px
  padding-left: 14px;

  img {
    width: 36px;
    height: 36px;
    align-self: center;
  }

  box-shadow: $--box-shadow-light;

  .brand-text {
    align-self: center;
    font-size: 24px;
    margin-left: 0.5em;
    white-space: nowrap;
    color: $--color-primary;
  }
}

#app-sidebar.collapsed {
  .brand-text {
    display: none;
  }
}

.menu-container {
  padding: 0;
}
</style>
