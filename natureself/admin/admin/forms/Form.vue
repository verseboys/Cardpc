<template>
  <el-form
    ref="form"
    v-loading="loading || !ready"
    v-bind="$attrs"
    label-width="auto"
    label-position="right"
    size="mini"
    :model="formdata"
  >
    <slot name="header" />
    <template v-if="ready">
      <ns-panel
        v-for="(panel, index) in computedSchema.panels"
        :key="index"
        v-model="formdata"
        :schema="panel"
        :mode="mode"
      />
    </template>
    <slot />
  </el-form>
</template>

<script>
import utils from './utils.js'
import NsPanel from './Panel.vue'

export default {
  components: {
    NsPanel,
  },
  props: {
    schema: { type: [Object, Function], required: true },
    initialData: { type: [Object, Function], default: null },
    value: { type: [Object, Array], default: null },
    mode: { type: String, default: 'edit' },
  },
  data () {
    return {
      formdata: null,
      computedSchema: null,
      computedInitialData: null,
      loading: false,
    }
  },
  computed: {
    ready () {
      return (!!this.computedSchema && !!this.computedInitialData && !!this.formdata)
    },
  },
  watch: {
    computedSchema (val) {
      this.formdata = utils.buildFormdata(this.computedSchema, this.computedInitialData)
    },

    computedInitialData (val) {
      this.formdata = utils.buildFormdata(this.computedSchema, this.computedInitialData)
    },

    formdata: {
      deep: true,
      handler (val) {
        this.$emit('input', utils.prepareSubmitFormdata(this.computedSchema, this.formdata))
      },
    },

    schema: {
      deep: true,
      handler (val) {
        this.computeSchema()
      },
    },

    initialData: {
      deep: true,
      handler (val) {
        this.computeInitialData()
      },
    },
  },
  created () {
    this.computeSchema()
    this.computeInitialData()
  },
  methods: {
    computeInitialData () {
      if (this.initialData instanceof Function) {
        this.initialData().then(response => {
          if ((response.status !== 200) || (response.data.code !== 0)) {
            this.$message.error('请求初始数据失败')
          } else {
            this.computedInitialData = response.data.data
          }
        })
      } else if (this.initialData instanceof Object) {
        this.computedInitialData = { ...this.initialData }
      } else {
        this.computedInitialData = {}
      }
    },

    computeSchema () {
      let vm = this

      if (vm.schema instanceof Function) {
        vm.schema().then(response => {
          if ((response.status !== 200) || (response.data.code !== 0)) {
            vm.$message.error('请求 schema 失败')
          } else {
            vm.computedSchema = response.data.data
          }
        })
      } else {
        vm.computedSchema = { ...vm.schema }
      }
    },

    validate (...args) {
      return this.$refs.form.validate(...args)
    },

    validateField (...args) {
      return this.$refs.form.validateField(...args)
    },

    resetFields (...args) {
      return this.$refs.form.resetFields(...args)
    },

    clearValidate (...args) {
      return this.$refs.form.clearValidate(...args)
    },
  },
}
</script>
