<template>
  <div>
    <ns-form ref="searchForm" v-model="searchFormdata" :schema="$api.cardpc.project.getProjectSearchForm" inline>
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" icon="el-icon-plus" @click="$router.push({ name: 'project-project-new' })">创建专题</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column prop="slug" label="slug" width="100" />
      <el-table-column prop="title" label="标题" />

      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-link
            type="primary"
            icon="el-icon-edit"
            @click="$router.push({ name: 'project-project-edit', params: { id: scope.row.id }})"
          >
            编辑
          </el-link>
          <el-link
            type="primary"
            icon="el-icon-menu"
            @click="$router.push({ name: 'project-menu-edit', params: { id: scope.row.menu.id }})"
          >
            菜单管理
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
      listDataApi: this.$api.cardpc.project.listProject,
      deleteDataApi: this.$api.cardpc.project.deleteProject,
    }
  },
}
</script>
