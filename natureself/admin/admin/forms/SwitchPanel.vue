<template>
  <el-switch v-bind="$attrs" active-color="#13ce66" v-on="$listeners" />
</template>

<script>
export default {
  props: {
    schema: { type: Object, required: true },
  },
}
</script>
