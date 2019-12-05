<template>
  <div v-loading.fullscreen.lock="!ready">
    <el-card v-if="root && project" class="preview">
      <div class="nav" :style="`background-color: ${project.theme_colors.color1};`">
        <div v-for="(menu, index) in items || []" :key="index" class="nav-item">{{ menu.display_text }}</div>
      </div>
    </el-card>
    <draggable :list="items" handle=".handle" class="editor">
      <div v-for="(item, index) in items" :key="index" class="item-row">
        <div class="handle"><svg-icon name="drag-handle" /></div>
        <nav-menu-edit-item
          v-if="panels"
          :panels="panels"
          :item.sync="item"
          :project-id="root.project.id"
          class="edit-item"
        />
        <div class="delete-item" @click="deleteItem(index)"><i class="el-icon-close" /></div>
      </div>
      <div slot="footer" class="item-row">
        <div class="add-item" @click="addItem"><i class="el-icon-plus" /></div>
      </div>
    </draggable>
    <el-button type="danger" size="mini" @click="cancel">取消</el-button>
    <el-button type="success" size="mini" @click="submitData">保存</el-button>
  </div>
</template>

<script>
import _ from 'lodash'
import draggable from 'vuedraggable'
import NavMenuEditItem from './NavMenuEditItem.vue'

export default {
  components: {
    draggable,
    NavMenuEditItem,
  },
  data () {
    return {
      root: null,
      project: null,
      items: null,
      panels: null,
    }
  },
  computed: {
    ready () {
      return this.root && this.panels
    },
  },
  created () {
    let vm = this
    vm.$api.cardpc.project.getMenu({ id: vm.$route.params.id }).then(res => {
      if (res.status !== 200 || res.data.code !== 0) {
        vm.$message.error('菜单数据加载失败')
      } else {
        vm.items = _.cloneDeep(res.data.data.children)
        vm.project = res.data.data.project
        vm.root = res.data.data
      }
    })

    vm.$api.cardpc.project.getMenuForm('edit').then(res => {
      if (res.status !== 200 || res.data.code !== 0) {
        vm.$message.error('菜单编辑 schema 加载失败')
      } else {
        let panels = {}
        _.forEach(res.data.data.panels, panel => {
          panels[panel.field_name] = panel
        })
        vm.panels = panels
      }
    })
  },
  methods: {
    addItem () {
      this.items.push({
        id: null,
        link_page: null,
        link_type: 'page',
        link_url: '',
        text: '',
        display_text: '!ERROR!',
      })
    },

    deleteItem (index) {
      this.items.splice(index, 1)
    },

    cancel () {
      this.$router.go(-1)
    },

    submitData () {
      let children = []
      _.forEach(this.items, item => {
        children.push({
          id: item.id,
          parent: item.parent ? item.parent.id : this.root.id,
          link_type: item.link_type,
          link_page: item.link_page ? item.link_page.id : null,
          link_url: item.link_url,
          text: item.text,
          sort_order: children.length + 1,
        })
      })
      let data = {
        id: this.root.id,
        children,
      }
      let vm = this
      vm.$api.cardpc.project.patchMenu(this.root.id, data).then(res => {
        if (res.status !== 200 || res.data.code !== 0) {
          vm.$message.error('保存失败')
        } else {
          vm.$message.success('保存成功')
          vm.$router.go(-1)
        }
      })
    },
  },
}
</script>

<style lang="scss" scoped>
// stylelint-disable-next-line
::v-deep .el-card__body {
  padding: 0;
}

.preview {
  min-width: 500px;
  max-width: 1000px;

  .nav {
    width: 100%;
    height: 50px;
    color: white;
    padding-left: 10px;
    padding-right: 10px;
    display: flex;
    justify-content: start;
    align-items: center;
  }

  .nav-item {
    height: 50px;
    width: 100px;
    line-height: 50px;
    text-align: center;
    vertical-align: middle;
  }
}

.editor {
  margin-top: 1em;
  margin-bottom: 1em;

  .item-row {
    border: 1px dashed #eee;
    height: 50px;
    margin-top: 1px;
    display: flex;
    align-items: center;

    .handle {
      width: 48px;
      font-size: 24px;
      display: flex;
      justify-content: center;
      border-right: 1px dashed #eee;

      &:hover {
        cursor: move;
      }
    }

    .edit-item {
      flex-grow: 1;
    }

    .delete-item {
      width: 48px;
      font-size: 24px;
      display: flex;
      justify-content: center;
      border-left: 1px dashed #eee;

      &:hover {
        cursor: pointer;
      }
    }

    .add-item {
      width: 48px;
      font-size: 24px;
      display: flex;
      justify-content: center;
      border-right: 1px dashed #eee;

      &:hover {
        cursor: pointer;
      }
    }
  }
}
</style>
