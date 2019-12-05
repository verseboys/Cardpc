<template>
  <div>
    <el-form size="mini" hide-required-asterisk inline>
      <ns-data-panel v-model="item.link_type" :schema="panels.link_type" class="link-type" />
      <ns-data-panel
        v-show="item.link_type === 'external'"
        v-model="item.link_url"
        :schema="panels.link_url"
        class="link-url"
        placeholder="https://..."
      />
      <ns-data-panel
        v-show="item.link_type === 'page'"
        v-model="item.link_page"
        :schema="panels.link_page"
        :api-params="pageSelectApiParams"
        class="link-page"
        placeholder="请选择页面"
      />
      <ns-data-panel
        v-model="item.text"
        :schema="panels.text"
        class="text"
        :placeholder="textPlaceholder"
      />
    </el-form>
  </div>
</template>

<script>
import NsDataPanel from '@admin/forms/DataPanel.vue'

export default {
  components: {
    NsDataPanel,
  },
  props: {
    panels: { type: Object, required: true },
    item: { type: Object, required: true },
    projectId: { type: Number, required: true },
  },
  data () {
    return {
      pageSelectApiParams: { project: this.projectId, simple: true },
    }
  },
  computed: {
    textPlaceholder () {
      if (this.item.link_type === 'page' && this.item.link_page) {
        return this.item.link_page.page_title
      } else {
        return '请输入名称'
      }
    },
  },
  watch: {
    item: {
      deep: true,
      handler (val) {
        if (val.text) {
          val.display_text = val.text
        } else if (val.link_type === 'external') {
          val.display_text = '!ERROR!'
        } else if (val.link_type === 'page') {
          val.display_text = val.link_page ? val.link_page.page_title : '!ERROR!'
        }
        this.$emit('update:item', val)
      },
    },
  },
}
</script>

<style :lang="scss" scoped>
.el-form-item {
  margin-bottom: 0;

  ::v-deep .el-form-item__label {
    display: none;
  }
}

.link-type {
  ::v-deep .el-select {
    width: 140px;
  }
}

.link-page {
  ::v-deep .el-select {
    width: 180px;
  }
}

.link-url {
  ::v-deep .el-input {
    width: 180px;
  }
}

.text {
  ::v-deep .el-input {
    width: 150px;
  }
}
</style>
