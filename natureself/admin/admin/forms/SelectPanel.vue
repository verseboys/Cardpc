<template>
  <el-select
    v-model="model"
    v-loading="loading"
    :clearable="!schema.required"
    :filterable="filterable"
    :allow-create="schema.options.allow_create || false"
    :default-first-option="schema.options.allow_create || false"
    :placeholder="placeholder"
    :disabled="computedDisabled"
    @change="onSelectChange"
  >
    <el-option
      v-for="choice in choices"
      :key="choice.value"
      :label="choice.label"
      :value="choice.value"
      :disabled="choice.disabled"
    />
  </el-select>
</template>

<script>
import _ from 'lodash'

export default {
  props: {
    schema: { type: Object, required: true },
    value: { type: [Object, Number, String], required: false, default: null },
    apiParams: { type: Object, required: false, default: null },
    disabled: { type: Boolean, required: false, default: false },
    disableApi: { type: Boolean, required: false, default: false },
    disableApiMessage: { type: String, required: false, default: null },
  },
  data () {
    return {
      choices: [],
      model: null,
      loading: false,
    }
  },
  computed: {
    filterable () {
      if (this.schema.options.filterable) {
        return true
      }
      if (this.schema.options.allow_create) {
        return true
      }
      return false
    },
    computedDisabled () {
      if (this.schema.options.choices.type === 'url' && this.disableApi) {
        return true
      }
      return this.disabled
    },
    placeholder () {
      return this.disableApi ? this.disableApiMessage : this.schema.options.placeholder
    },
  },
  watch: {
    apiParams: {
      deep: true,
      handler (val, oldVal) {
        this.refreshApi()
      },
    },
    disableApi (val) {
      this.refreshApi()
    },
    value: {
      deep: true,
      handler (val) {
        let choicesOption = this.schema.options.choices
        this.model = val
          ? choicesOption.value_field ? val[choicesOption.value_field] : val
          : null
      },
    },
  },
  created () {
    let vm = this
    let choicesOption = this.schema.options.choices

    if (choicesOption.type === 'list') {
      vm.choices = choicesOption.choices
      vm.model = vm.value
    } else if (choicesOption.type === 'url') {
      this.refreshApi()
    }
  },
  methods: {
    onSelectChange (val) {
      if (val === null) {
        this.$emit('input', val)
      } else if (this.schema.options.choices.value_field) {
        const idx = _.findIndex(this.choices, obj => obj.value === val)
        this.$emit('input', this.choices[idx].obj)
      } else {
        this.$emit('input', val)
      }
    },

    refreshApi () {
      // TODO 后面需要支持搜索
      if (this.disableApi) {
        this.choices = []
        this.model = null
        this.$emit('input', null)
        return
      }

      let choicesOption = this.schema.options.choices
      if (choicesOption.type !== 'url') {
        return
      }

      let vm = this
      let url = choicesOption.url
      let params = vm.apiParams ? { ...vm.apiParams } : {}
      params = { ...params, page_size: 1000 }
      vm.loading = true
      vm.$api.request({ url, params }).then((response) => {
        vm.loading = false
        if ((response.status !== 200) || (response.data.code !== 0)) {
          vm.$message.error('请求下拉选项失败')
        } else {
          let choices = []
          response.data.data.forEach((elem) => {
            if (typeof elem === 'string' || elem instanceof String) {
              choices.push({
                value: elem,
                label: elem,
                obj: elem,
              })
            } else {
              choices.push({
                value: elem[choicesOption.value_field],
                label: elem[choicesOption.label_field],
                disabled: elem.disabled,
                obj: elem,
              })
            }
          })
          vm.choices = choices
          vm.model = vm.value
            ? choicesOption.value_field ? vm.value[choicesOption.value_field] : vm.value
            : null
        }
      })
    },
  },
}
</script>
