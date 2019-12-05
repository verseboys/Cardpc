<template>
  <div>
    <ns-form
      ref="editForm"
      v-model="editFormdata"
      :schema="editFormSchema"
      :initial-data="editFormInitialData"
    >
      <template slot="header">
        <ns-panel
          v-if="projectPanelSchema"
          v-model="projectAndPagetype"
          :schema="projectPanelSchema"
          :mode="mode"
          :disabled="mode === 'edit'"
        />
        <ns-panel
          v-if="pagetypePanelSchema"
          v-model="projectAndPagetype"
          :schema="pagetypePanelSchema"
          :mode="mode"
          :disabled="mode === 'edit'"
          :disable-api="mode === 'new' && !projectAndPagetype.project"
          disable-api-message="请先选择项目"
          :api-params="pagetypePanelApiParams"
        />
      </template>
      <el-form-item>
        <el-button type="danger" size="mini" @click="cancel">取消</el-button>
        <el-button type="success" size="mini" :disabled="submitButtonDisabled" @click="submitData">
          {{ mode === 'new' ? '新建' : '保存' }}
        </el-button>
      </el-form-item>
    </ns-form>
  </div>
</template>

<script>
import EditPageMixin from '@admin/mixins/edit-page.js'
import NsPanel from '@admin/forms/Panel.vue'

export default {
  components: {
    NsPanel,
  },
  mixins: [EditPageMixin],
  data () {
    return {
      createDataApi: this.$api.cardpc.project.createPage,
      patchDataApi: (data) => this.$api.cardpc.project.patchPage(this.$route.params.id, data),
      getDataApi: () => this.$api.cardpc.project.getPage({ id: this.$route.params.id }),

      projectAndPagetype: {},
      projectPanelSchema: null,
      pagetypePanelSchema: null,

      editFormSchema: { object: 'form', panels: [], form_mode: 'edit' },
      editFormInitialData: null,
    }
  },
  computed: {
    pagetypePanelApiParams () {
      return {
        project: this.mode === 'edit'
          ? this.$route.params.id
          : this.projectAndPagetype.project ? this.projectAndPagetype.project.id : null,
      }
    },

    extraEditFormdata () {
      let project = this.projectAndPagetype.project
      let pagetype = this.projectAndPagetype.pagetype
      return {
        project: project ? project.id : null,
        pagetype: pagetype ? pagetype.type : null,
      }
    },
  },
  watch: {
    projectAndPagetype: {
      deep: true,
      handler (val) {
        let vm = this

        vm.$api.cardpc.project.getPageEditForm(val.pagetype ? val.pagetype.type : null).then(res => {
          if (res.status !== 200 || res.data.code !== 0) {
            this.$message.error('请求表单 schema 失败')
          } else {
            vm.editFormSchema = res.data.data
          }
        })
      },
    },
  },
  created () {
    let vm = this

    vm.$api.cardpc.project.getPagePanel('project').then(res => {
      vm.projectPanelSchema = res.data.data
    })
    vm.$api.cardpc.project.getPagePanel('pagetype').then(res => {
      vm.pagetypePanelSchema = res.data.data
    })

    if (vm.mode === 'edit') {
      vm.getDataApi().then(res => {
        if (res.status !== 200 || res.data.code !== 0) {
          vm.$message.error('请求数据失败')
        } else {
          vm.editFormInitialData = res.data.data
          vm.projectAndPagetype = {
            project: res.data.data.project,
            pagetype: res.data.data.pagetype,
          }
        }
      })
    }
  },
}
</script>
