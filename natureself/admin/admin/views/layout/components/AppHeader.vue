<template>
  <el-header
    id="app-header"
    height="50px"
  >
    <div
      class="toggler-container"
      @click="ToggleSidebar"
    >
      <svg-icon
        class="toggler"
        name="hamburger"
      />
    </div>

    <el-breadcrumb separator="/">
      <el-breadcrumb-item
        v-for="(item, index) in breadcrumbItems"
        :key="item.path"
      >
        <span v-if="item.redirect==='noredirect' || index===breadcrumbItems.length-1">
          {{ item.meta.title }}
        </span>
        <a
          v-else
          @click.prevent="handleBreadcrumbLink(item)"
        >{{ item.meta.title }}</a>
      </el-breadcrumb-item>
    </el-breadcrumb>

    <div class="tray">
      <el-dropdown
        trigger="click"
        @command="handleCommand"
      >
        <div class="avatar">
          <img :src="avatarUrl">
        </div>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item command="logout">
            退出
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script>
import pathToRegexp from 'path-to-regexp'
import { mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ...mapGetters([
      'avatarUrl',
    ]),

    breadcrumbItems () {
      return this.$route.matched.filter(
        item => item.meta && item.meta.title && (item.meta.breadcrumb === undefined || item.meta.breadcrumb)
      )
    },
  },
  methods: {
    ...mapActions([
      'ToggleSidebar',
    ]),

    compilePath (path) {
      const { params } = this.$route
      return pathToRegexp.compile(path)(params)
    },

    handleBreadcrumbLink (item) {
      const { redirect, path } = item
      if (redirect) {
        this.$router.push(redirect)
      } else {
        this.$router.push(this.compilePath(path))
      }
    },

    handleCommand (command) {
      if (command === 'logout') {
        this.logout()
      }
    },

    logout () {
      let vm = this
      vm.$store.dispatch('Logout').then(() => {
        vm.$router.push({ name: 'login', query: { redirect: vm.$route.path } })
      })
    },
  },
}
</script>

<style lanb="scss" scoped>
@import '~element-ui/packages/theme-chalk/src/common/var.scss';

#app-header {
  display: flex;
  align-content: center;
  box-shadow: $--box-shadow-light;
}

.toggler-container {
  margin-left: -20px;
  cursor: pointer;
  text-align: center;
  width: 50px;
  font-size: 20px;
  line-height: 50px;
  transition: background 0.3s;

  &:hover {
    background: rgba(0, 0, 0, 0.025);
  }
}

.el-breadcrumb {
  margin: auto 0 auto 10px;
  font-size: 14px;
}

.tray {
  margin: auto 0 auto auto;

  .avatar {
    cursor: pointer;

    img {
      height: 36px;
    }
  }
}
</style>
