<template>
  <div>
    <ns-form ref="searchForm" v-model="searchFormdata" :schema="$api.media.getPresentationSearchForm" inline>
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" icon="el-icon-plus" @click="$router.push({ name: 'media-presentation-new' })">创建 PPT</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column prop="owner" label="创建者" width="120">
        <template slot-scope="scope">
          {{ scope.row.owner.username }}
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column label="操作" width="100">
        <template slot-scope="scope">
          <el-link
            type="primary"
            @click="$router.push({ name: 'media-presentation-edit', params: { id: scope.row.id }})"
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

export default {
  mixins: [ListPageMixin],
  data () {
    return {
      listDataApi: this.$api.media.listPresentation,
      deleteDataApi: this.$api.media.deletePresentation,
    }
  },
}
</script>
