<template>
  <el-slider
    v-bind="$attrs"
    :min="0"
    :max="3600"
    :step="60"
    :format-tooltip="toMinutes"
    v-on="$listeners"
  />
</template>

<script>
export default {
  props: {
    schema: { type: Object, required: true },
  },
  methods: {
    toMinutes (val) {
      if (val === 0) {
        return '不限制'
      } else {
        return `最少学习 ${val / 60} 分钟`
      }
    },
  },
}
</script>
