import NsForm from '@admin/forms/Form.vue'

export default {
  components: {
    NsForm,
  },
  props: {
    mode: { type: String, default: 'new' },
  },
  data () {
    return {
      submitButtonDisabled: false,
      editFormdata: {},
    }
  },
  methods: {
    submitData () {
      let vm = this
      vm.submitButtonDisabled = true
      let api = vm.mode === 'new' ? vm.createDataApi : vm.patchDataApi

      vm.$refs.editForm.validate().then(() => {
        vm.$refs.editForm.loading = true
        let extraEditFormdata = this.extraEditFormdata || {}
        api({ ...vm.editFormdata, ...extraEditFormdata }).then(response => {
          vm.submitButtonDisabled = false
          vm.$refs.editForm.loading = false
          if (response.status === 200) {
            vm.$message.success('保存成功')
            vm.$router.go(-1)
          } else if (response.status === 400) {
            // TODO check form error
          } else {
            // TODO report unknown error
          }
        })
      }).catch(() => {
        vm.submitButtonDisabled = false
        // validate error, do nothing, the ui will show validation errors
      })
    },
    cancel () {
      // TODO check if form is dirty and warn
      this.$router.go(-1)
    },
  },
}
