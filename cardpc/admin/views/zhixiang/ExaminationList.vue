<template>
  <div>
    <ns-form ref="searchForm" v-model="searchFormdata" :schema="$api.cardpc.zhixiang.getExaminationSearchForm">
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" icon="el-icon-plus" @click="$router.push({ name: 'zhixiang-examination-new' })">新增考试</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column prop="title" label="名称" width="300">
        <template slot-scope="scope">
          {{ scope.row.title }}
          <el-tag v-if="!scope.row.wjx_url" type="danger" size="mini" style="margin-left: 1em;">
            问卷星地址未填
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="course" label="关联课程">
        <template slot-scope="scope">
          {{ scope.row.course.title }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-link
            type="primary"
            @click="$router.push({ name: 'zhixiang-examination-edit', params: { id: scope.row.id }})"
          >
            编辑
          </el-link>
          <ns-confirm-button @click="deleteRow(scope.row)">
            <el-link type="danger">删除</el-link>
          </ns-confirm-button>
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

export default {
  mixins: [ListPageMixin],
  data () {
    return {
      listDataApi: this.$api.cardpc.zhixiang.listExamination,
      deleteDataApi: this.$api.cardpc.zhixiang.deleteExamination,
    }
  },
  methods: {
    formatTime (time) {
      return moment(time).format('YYYY-MM-DD HH:mm:ss')
    },
  },
}
</script>
