import NsForm from '@admin/forms/Form.vue'
import NsConfirmButton from '@admin/widgets/ConfirmButton.vue'

export default {
  components: {
    NsForm,
    NsConfirmButton,
  },
  data () {
    return {
      loadingData: false,
      searchFormdata: {},
      initialSearchFormdata: this.$store.getters.searchForms[this.$route.name] || {},
      cachedData: null,
      pagination: {
        page: 1,
        page_size: 10,
        total: 0,
      },
    }
  },
  methods: {
    refreshData () {
      let vm = this
      vm.loadingData = true
      vm.listDataApi({
        ...vm.searchFormdata,
        page: this.pagination.page,
        page_size: this.pagination.page_size,
      }).then(response => {
        vm.loadingData = false
        if (response.status === 200) {
          if (this.parseListData) {
            vm.cachedData = this.parseListData(response.data.data)
          } else {
            vm.cachedData = response.data.data
          }
          vm.pagination.page = response.data.pagination.page
          vm.pagination.total = response.data.pagination.total
        } else {
          vm.$message.error('获取数据失败')
        }
      })
    },

    handlePageChange () {
      this.refreshData()
    },

    deleteRow (row) {
      let vm = this
      vm.deleteDataApi({ id: row.id }).then(response => {
        if (response.status === 200) {
          vm.$message.success('删除成功')
          vm.refreshData()
        } else {
          vm.$message.error('删除失败')
        }
      })
    },
  },
  mounted () {
    this.refreshData()
  },
  watch: {
    searchFormdata: {
      handler (val, old) {
        this.$store.commit('CACHE_FORM_DATA', { pageName: this.$route.name, data: val })
        this.refreshData()
      },
      deep: true,
    },
  },
}
