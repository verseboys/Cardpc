<script>
// copied from vue-element-admin's 'redirect' view, named it as ForceRefresh
// https://github.com/PanJiaChen/vue-element-admin/blob/master/src/views/redirect/index.vue
export default {
  beforeCreate () {
    const { params, query } = this.$route
    const { path } = params
    this.$router.replace({ path: '/' + path, query })
  },
  render: function (h) {
    return h() // avoid warning message
  },
}
</script>
