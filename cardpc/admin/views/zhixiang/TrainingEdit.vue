<template>
  <div>
    <ns-form
      ref="editForm"
      v-model="editFormdata"
      :schema="$api.cardpc.zhixiang.getTrainingEditForm"
      :initial-data="getDataApi"
    >
      <el-form-item>
        <el-button type="danger" size="mini" @click="cancel">取消</el-button>
        <el-button type="success" size="mini" :disabled="submitButtonDisabled" @click="submitData">
          保存
        </el-button>
      </el-form-item>
    </ns-form>
  </div>
</template>

<script>
import EditPageMixin from '@admin/mixins/edit-page.js'

export default {
  mixins: [EditPageMixin],
  data () {
    return {
      patchDataApi: (data) => this.$api.cardpc.zhixiang.patchTraining(this.$route.params.id, data),
      getDataApi: () => this.$api.cardpc.zhixiang.getTraining({ id: this.$route.params.id }),
    }
  },
}
</script>
