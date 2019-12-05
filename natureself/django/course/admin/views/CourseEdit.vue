<template>
  <div>
    <ns-form
      ref="editForm"
      v-model="editFormdata"
      :schema="$api.course.getCourseEditForm"
      :initial-data="mode === 'new' ? null : getDataApi"
    >
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

export default {
  mixins: [EditPageMixin],
  data () {
    return {
      createDataApi: this.$api.course.createCourse,
      patchDataApi: (data) => this.$api.course.patchCourse(this.$route.params.id, data),
      getDataApi: () => this.$api.course.getCourse({ id: this.$route.params.id }),
    }
  },
}
</script>
