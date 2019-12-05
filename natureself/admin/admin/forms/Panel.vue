<template>
  <div v-if="schema.hide_on_new && mode === 'new'" />
  <div v-else-if="schema.hide_on_edit && mode === 'edit'" />
  <ns-data-panel
    v-else-if="schema.data_panel"
    v-model="formdata[schema.form_field_name]"
    :schema="schema"
    v-bind="$attrs"
  />
  <div v-else-if="schema.type === 'inline'" class="el-form--inline">
    <ns-panel
      v-for="(panel, index) in schema.panels"
      :key="index"
      v-model="formdata"
      :schema="panel"
      v-bind="$attrs"
    />
  </div>
  <el-tabs v-else-if="schema.type === 'tab'">
    <el-tab-pane
      v-for="tab in schema.tabs"
      :key="tab.title"
      :label="tab.title"
    >
      <ns-panel
        v-for="(panel, index) in tab.panels"
        :key="index"
        v-model="formdata"
        :schema="panel"
        v-bind="$attrs"
      />
    </el-tab-pane>
  </el-tabs>
  <el-divider v-else-if="schema.type === 'divider'" content-position="left">
    {{ schema.title }}
  </el-divider>
</template>

<script>
import NsDataPanel from './DataPanel.vue'

export default {
  name: 'NsPanel',
  components: {
    NsDataPanel,
  },
  props: {
    schema: { type: Object, required: false, default: null },
    value: { type: Object, default: null },
    mode: { type: String, required: true },
  },
  data () {
    return {
      formdata: this.value,
    }
  },
  watch: {
    formdata: {
      deep: true,
      handler (val) {
        this.$emit('input', this.formdata)
      },
    },
    value: {
      deep: true,
      handler (val) {
        this.formdata = val
      },
    },
  },
}
</script>

<style lang="scss" scoped>
// el-form 中，当设置了 label-width 之后，会强制给 el-form-item 添加 margin-left，
// 这导致 inline-form 中排版不正常。而我们的场景中，Form.vue 里面总是会设置 label-width，
// 因此这里我们强制去掉这个 margin-left。
.el-form--inline::v-deep .el-form-item__content {
  margin-left: 0 !important;
}
</style>
