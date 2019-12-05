<template>
  <el-date-picker
    type="daterange"
    :value-format="schema.options.datetime_format"
    unlink-panels
    range-separator="至"
    start-placeholder="开始日期"
    end-placeholder="结束日期"
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
