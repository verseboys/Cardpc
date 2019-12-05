<template>
  <el-input :type="schema.options.widget_type || 'text'" v-bind="$attrs" v-on="$listeners" />
</template>

<script>
export default {
  props: {
    schema: { type: Object, required: true },
  },
}
</script>
