<template>
  <el-popover
    v-model="visible"
    placement="top"
  >
    <p v-if="prompt">{{ prompt }}</p>
    <div style="text-align: center; margin: 0;">
      <el-button size="mini" type="text" @click="visible=false">取消</el-button>
      <el-button size="mini" type="primary" @click="onConfirm">确定</el-button>
    </div>
    <slot slot="reference" />
  </el-popover>
</template>

<script>
export default {
  props: {
    prompt: { type: String, required: false, default: null },
  },
  data () {
    return {
      visible: false,
    }
  },
  methods: {
    onConfirm () {
      this.visible = false
      this.$emit('click')
    },
  },
}
</script>
