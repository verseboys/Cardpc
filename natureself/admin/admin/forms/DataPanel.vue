<template>
  <el-form-item
    :prop="schema.form_field_name || null"
    :rules="schema.validators"
  >
    <template slot="label">
      {{ schema.options.label }}
      <el-tooltip v-if="schema.options.help_text" :content="schema.options.help_text" placement="right">
        <svg-icon name="help-symbol" />
      </el-tooltip>
    </template>
    <component
      :is="`ns-panel-${schema.type}`"
      :schema="schema"
      :placeholder="computedPlaceholder"
      :disabled="computedDisabled"
      v-bind="$attrs"
      v-on="$listeners"
    />
    <div v-if="schema.options.help_text" class="help-text">说明：{{ schema.options.help_text }}</div>
  </el-form-item>
</template>

<script>
import { components } from './panels.js'

export default {
  name: 'NsDataPanel',
  components,
  props: {
    schema: { type: Object, required: true },
    disabled: { type: Boolean, required: false, default: null },
    placeholder: { type: String, required: false, default: null },
  },
  computed: {
    computedDisabled () {
      return this.disabled !== null ? this.disabled : this.schema.disabled
    },
    computedPlaceholder () {
      return this.placeholder ? this.placeholder : this.schema.options.placeholder
    },
  },
}
</script>

<style :lang="scss" scoped>
.help-text {
  color: #888;
  font-size: 12px;
}
</style>
