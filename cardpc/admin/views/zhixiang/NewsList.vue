<template>
  <div>
    <ns-form ref="searchForm" v-model="searchFormdata" :schema="$api.cardpc.zhixiang.getNewsSearchForm" inline>
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" icon="el-icon-plus" @click="$router.push({ name: 'zhixiang-news-new' })">创建新闻</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column prop="author_name" label="作者姓名" width="120" />
      <el-table-column prop="publish_time" label="发布时间" width="150">
        <template slot-scope="scope">
          {{ formatTime(scope.row.publish_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="title" label="新闻标题" />
      <el-table-column label="操作" width="100">
        <template slot-scope="scope">
          <el-link
            type="primary"
            @click="$router.push({ name: 'zhixiang-news-edit', params: { id: scope.row.id }})"
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
      listDataApi: this.$api.cardpc.zhixiang.listNews,
      deleteDataApi: this.$api.cardpc.zhixiang.deleteNews,
    }
  },
  methods: {
    formatTime (time) {
      return moment(time).format('YYYY-MM-DD HH:mm:ss')
    },
  },
}
</script>
