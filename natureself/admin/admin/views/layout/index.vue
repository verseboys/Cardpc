<template>
  <el-container id="app-container">
    <div
      v-if="device==='mobile' && !sidebar.collapsed"
      class="drawer-bg"
      @click="handleClickOutside"
    />
    <app-sidebar />
    <el-container direction="vertical">
      <app-header />
      <app-main />
    </el-container>
  </el-container>
</template>

<script>
import { mapGetters } from 'vuex'

import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import AppMain from './components/AppMain.vue'
import ResizeHandlerMixin from './ResizeHandlerMixin.js'

export default {
  name: 'Layout',
  components: {
    AppHeader,
    AppSidebar,
    AppMain,
  },
  mixins: [ResizeHandlerMixin],
  computed: {
    ...mapGetters([
      'device',
      'sidebar',
    ]),
  },
  methods: {
    handleClickOutside () {
      this.$store.dispatch('CloseSidebar')
    },
  },
}
</script>

<style scoped>
.drawer-bg {
  background: #000;
  opacity: 0.3;
  top: 0;
  left: 210px;
  width: calc(100% - 210px);
  height: 100%;
  position: absolute;
  z-index: 999;
}
</style>
