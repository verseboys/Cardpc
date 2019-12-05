<template>
  <div>
    <draggable
      :list="items"
      :animation="200"
    >
      <div v-for="(item, index) in items" :key="index" class="item-box">
        <carousel-edit-item v-if="editPanels" :item.sync="item" :panels="editPanels" />
        <i class="delete-button el-icon-delete" @click="deleteCarouselItem(index)" />
      </div>
    </draggable>
    <el-button icon="el-icon-plus" @click="addCarouselItem" />
  </div>
</template>

<script>
import CarouselEditItem from './ProjectCarouselEditItem.vue'
import draggable from 'vuedraggable'
import _ from 'lodash'

export default {
  components: {
    draggable,
    CarouselEditItem,
  },
  props: {
    schema: { type: Object, required: true },
    value: { type: Array, required: false, default: () => [] },
  },
  data () {
    return {
      items: _.isEmpty(this.value) ? [] : this.value,
      uploadingCount: 0,

      editPanels: null,
    }
  },
  watch: {
    items: {
      deep: true,
      handler (val) {
        this.$emit('input', val)
      },
    },
  },
  created () {
    let vm = this
    vm.$api.cardpc.project.getCarouselEditForm().then(res => {
      if (res.status !== 200 || res.data.code !== 0) {
        vm.$message.error('表单 schema 加载失败')
      } else {
        let panels = {}
        _.forEach(res.data.data.panels, panel => {
          panels[panel.field_name] = panel
        })
        vm.editPanels = panels
      }
    })
  },
  methods: {
    deleteCarouselItem (index) {
      this.items.splice(index, 1)
    },
    addCarouselItem (index) {
      this.items.push({ id: null, image: null, title: '', link_url: '' })
    },
  },
}
</script>

<style lang="scss" scoped>
.item-box {
  width: 600px;
  position: relative;
  padding: 5px;
  box-sizing: border-box;

  .delete-button {
    transition: 0.5s ease;
    opacity: 1;
    position: absolute;
    top: 5px;
    right: 5px;
    cursor: pointer;
    color: #409eff;
    font-size: 20px;
  }

  &:hover {
    cursor: move;
    background-color: #f8fafc;

    .delete-button {
      opacity: 1;
    }
  }
}
</style>
