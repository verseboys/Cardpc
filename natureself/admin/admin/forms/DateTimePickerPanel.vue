<template>
  <el-date-picker
    type="datetime"
    :value-format="schema.options.datetime_format"
    v-bind="$attrs"
    v-on="$listeners"
  />
</template>

<script>
export default {
  props: {
    schema: { type: Object, required: true },
  },
}
</script>
