<template>
  <div>
    <ns-form
      ref="searchForm"
      v-model="searchFormdata"
      :schema="$api.cardpc.zhixiang.getTrainingSearchForm"
      :initial-data="initialSearchFormdata"
      inline
    >
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" :icon="exportDisabled ? 'el-icon-loading' : 'el-icon-download'" :disabled="exportDisabled" @click="exportData">导出数据</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column prop="id" label="用户ID" width="60">
        <template slot-scope="scope">
          {{ scope.row.user.id }}
        </template>
      </el-table-column>

      <el-table-column prop="user" label="用户名" width="120">
        <template slot-scope="scope">
          <el-popover title="用户信息" width="300" trigger="hover">
            <el-form label-position="right" label-width="auto" size="mini">
              用户ID：{{ scope.row.user.id }}<br>
              用户名：{{ scope.row.user.username }}<br>
              手机号：{{ scope.row.user.phone }}<br>
              邮箱：{{ scope.row.user.email }}
            </el-form>
            <span slot="reference">{{ scope.row.user.username }}</span>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column label="课程" width="150">
        <template slot-scope="scope">
          {{ scope.row.examination ? scope.row.examination.course.title : '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="a_status" label="课程调研状态" width="100">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.a_status == 1" type="danger">未参加调研</el-tag>
          <el-tag v-else-if="scope.row.a_status == 2" type="success">已完成调研</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="b_status" label="课程学习状态" width="100">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.b_status == 1" type="warning">未学完课程</el-tag>
          <el-tag v-else-if="scope.row.b_status == 2" type="success">已学完课程</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="c_status" label="资格认证状态" width="180">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.c_status == 1" type="danger">未参加认证</el-tag>
          <el-tag v-else-if="scope.row.c_status == 2" type="yellow">资格待审核</el-tag>
          <el-tag v-else-if="scope.row.c_status == 3" type="success">已认证通过</el-tag>
          <el-tag v-else-if="scope.row.c_status == 4" type="danger">审核失败</el-tag>

          <el-popover :ref="`passPopover${scope.row.id}`" placement="top">
            <el-form :ref="`passForm${scope.row.id}`" :model="scope.row.passFormData" size="mini" inline>
              <el-form-item prop="examination" :rules="{ required: true, message: '必须选择考试', trigger: 'blur' }">
                <el-select v-model="scope.row.passFormData.examination" placeholder="选择关联的考试">
                  <el-option v-for="exam in exams" :key="exam.id" :label="exam.title" :value="exam.id" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button size="mini" type="success" @click="passQualification(scope.row)">通过</el-button>
              </el-form-item>
            </el-form>
            <el-link slot="reference" type="primary">通过</el-link>
          </el-popover>

          <el-popover :ref="`rejectPopover${scope.row.id}`" placement="top">
            <div style="text-align: center;">
              <el-button size="mini" type="danger" @click="rejectQualification(scope.row)">确认驳回</el-button>
            </div>
            <el-link slot="reference" type="primary">驳回</el-link>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column label="考试" width="150" prop="examination">
        <template slot-scope="scope">
          {{ scope.row.examination ? scope.row.examination.title : '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="c_status" label="考试评定状态" width="100">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.d_status == 1" type="danger">未参加考试</el-tag>
          <el-tag v-if="scope.row.d_status == 2">已完成考试</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-link
            type="primary"
            @click="$router.push({ name: 'zhixiang-training-edit', params: { id: scope.row.id }})"
          >
            高级设置
          </el-link>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      :current-page.sync="pagination.page"
      :page-size="pagination.page_size"
      layout="total, prev, pager, next"
      :total="pagination.total"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script>
import ListPageMixin from '@admin/mixins/list-page.js'
import moment from 'moment'
import fileDownload from 'js-file-download'
import contentDisposition from 'content-disposition'
import _ from 'lodash'

export default {
  mixins: [ListPageMixin],
  data () {
    return {
      listDataApi: this.$api.cardpc.zhixiang.listTraining,
      exams: [],
      exportDisabled: false,
    }
  },
  created () {
    let vm = this
    vm.$api.cardpc.zhixiang.listExamination().then(response => {
      if (response.data.code === 0) {
        vm.exams = response.data.data
      }
    })
  },
  methods: {
    formatTime (time) {
      return moment(time).format('YYYY-MM-DD HH:mm:ss')
    },

    passQualification (row) {
      let vm = this
      let form = this.$refs[`passForm${row.id}`]
      let popover = this.$refs[`passPopover${row.id}`]
      form.validate().then(() => {
        vm.$api.cardpc.zhixiang.trainingPassQualification(row.id, row.passFormData.examination).then(response => {
          if (response.data.code === 0) {
            vm.$message.success('设置成功')
          } else {
            vm.$message.error('设置失败')
          }
          vm.refreshData()
        })
        popover.doClose()
      }).catch(() => {})
    },

    rejectQualification (row) {
      let vm = this
      let popover = this.$refs[`rejectPopover${row.id}`]
      vm.$api.cardpc.zhixiang.trainingRejectQualification(row.id).then(response => {
        if (response.data.code === 0) {
          vm.$message.success('设置成功')
        } else {
          vm.$message.error('设置失败')
        }
        vm.refreshData()
      })
      popover.doClose()
    },

    parseListData (data) {
      _.map(data, item => {
        item.passFormData = {
          examination: item.examination ? item.examination.id : null,
        }
      })
      return data
    },

    exportData () {
      let vm = this
      vm.exportDisabled = true

      vm.$api.cardpc.zhixiang.exportTrainingData().then(res => {
        vm.exportDisabled = false
        let disposition = contentDisposition.parse(res.headers['content-disposition'])
        fileDownload(res.data, disposition.parameters.filename)
      })
    },
  },
}
</script>
