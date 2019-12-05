import store from '@admin/store'

export default {
  watch: {
    $route (route) {
      // force close sidebar on mobile device on route change
      if (this.$store.getters.device === 'mobile' && !this.$store.getters.sidebar.collapsed) {
        store.dispatch('CloseSidebar')
      }
    },
  },
  created () {
    window.addEventListener('resize', this.resizeHandler)
    this.resizeHandler()
  },
  destroyed () {
    window.removeEventListener('resize', this.resizeHandler)
  },
  mounted () {
    let isMobile = this.isMobile()
    store.dispatch('SetDevice', isMobile ? 'mobile' : 'desktop')
    // if device is mobile, ensures sidebar is collapsed on app mount
    if (isMobile) {
      store.dispatch('CloseSidebar', false)
    }
  },
  methods: {
    isMobile () {
      // element-ui xs breakpoint: <768px
      return window.innerWidth < 768
    },

    resizeHandler () {
      if (!document.hidden) {
        let isMobile = this.isMobile()
        store.dispatch('SetDevice', isMobile ? 'mobile' : 'desktop')
        // if device is mobile, ensures sidebar is collapsed on app mount
        if (isMobile) {
          store.dispatch('CloseSidebar', false)
        }
      }
    },
  },
}
