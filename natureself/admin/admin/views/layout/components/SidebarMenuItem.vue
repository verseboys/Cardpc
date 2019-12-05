<template>
  <router-link
    v-if="!root.hasChildren"
    :to="resolvePath(root.path)"
  >
    <el-menu-item
      :index="resolvePath(root.path)"
      :class="{ nested }"
    >
      <svg-icon :name="root.meta.icon || ' '" />
      <span
        v-if="root.meta.title"
        slot="title"
      >{{ root.meta.title }}</span>
    </el-menu-item>
  </router-link>
  <el-submenu
    v-else
    :index="resolvePath(root.path)"
    popper-append-to-body
    :class="{ nested }"
  >
    <template slot="title">
      <svg-icon :name="root.meta.icon || ' '" />
      <span v-if="root.meta.title">{{ root.meta.title }}</span>
    </template>
    <sidebar-menu-item
      v-for="child in root.visibleChildren"
      :key="child.path"
      :route="child"
      :base-path="resolvePath(root.path)"
      :nested="true"
    />
  </el-submenu>
</template>

<script>
import path from 'path'

export function isExternal (path) {
  return /^(https?:|mailto:|tel:)/.test(path)
}

export default {
  name: 'SidebarMenuItem',
  props: {
    route: {
      type: Object,
      required: true,
    },
    basePath: {
      type: String,
      default: '',
    },
    nested: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    root () {
      let _root = { ...this.route }
      _root.visibleChildren = (_root.children || []).filter(item => (item.hidden === undefined || !item.hidden))

      if (_root.visibleChildren.length === 1 && _root.promote) {
        _root = { ..._root.visibleChildren[0] }
        _root.visibleChildren = (_root.children || []).filter(item => (item.hidden === undefined || !item.hidden))
      }

      _root.meta = _root.meta || {}
      _root.hasChildren = _root.visibleChildren.length > 0
      return _root
    },
  },
  methods: {
    resolvePath (routePath) {
      if (isExternal(routePath)) {
        return routePath
      }
      return path.resolve(this.basePath, routePath)
    },
  },
}
</script>

<style lang="scss">
@import '~element-ui/packages/theme-chalk/src/common/var.scss';

.el-menu-item > span,
.el-submenu__title > span {
  margin-left: 0.5em;
}

.el-menu-item.nested {
  background-color: $--color-primary-light-8 !important;
}

.nested .el-submenu__title {
  background-color: $--color-primary-light-8 !important;
}
</style>
