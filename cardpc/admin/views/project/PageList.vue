<template>
  <div>
    <ns-form ref="searchForm" v-model="searchFormdata" :schema="$api.cardpc.project.getPageSearchForm" inline>
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" icon="el-icon-plus" @click="$router.push({ name: 'project-page-new' })">创建页面</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column v-if="!searchFormdata.project" label="项目" width="150">
        <template slot-scope="scope">
          <el-tag size="mini">{{ scope.row.project.title }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="!searchFormdata.pagetype" label="类型" width="150">
        <template slot-scope="scope">
          <el-tag size="mini">{{ scope.row.pagetype.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.status === 'published'" size="mini" type="success">已发布</el-tag>
          <el-tag v-else-if="scope.row.status === 'draft'" size="mini" type="warning">草稿</el-tag>
          <el-tag v-else size="mini" type="danger">未知</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="page_title" label="页面标题" />

      <el-table-column label="操作" width="180">
        <template slot-scope="scope">
          <el-link
            type="primary"
            icon="el-icon-link"
            :href="`${scope.row.url}?preview=1`"
          >
            访问
          </el-link>
          <el-link
            type="primary"
            icon="el-icon-edit"
            @click="$router.push({ name: 'project-page-edit', params: { id: scope.row.id }})"
          >
            编辑
          </el-link>
          <ns-confirm-button @click="deleteRow(scope.row)">
            <el-link type="danger" icon="el-icon-delete">删除</el-link>
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

export default {
  mixins: [ListPageMixin],
  data () {
    return {
      listDataApi: this.$api.cardpc.project.listPage,
      deleteDataApi: this.$api.cardpc.project.deletePage,
    }
  },
}
</script>
