<template>
  <div>
    <ns-form ref="searchForm" v-model="searchFormdata" :schema="$api.cardpc.project.getDocumentSearchForm" inline>
      <el-form-item>
        <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
        <el-button type="success" icon="el-icon-plus" @click="$router.push({ name: 'project-document-new' })">上传附件</el-button>
      </el-form-item>
    </ns-form>

    <el-table v-loading="loadingData" :data="cachedData">
      <el-table-column>
        <template slot-scope="scope">
          <div class="file-row">
            <div class="file-info">
              <div class="file-subject">
                {{ scope.row.subject }}
                <el-tag size="mini">{{ getFileExt(scope.row.document.filename) }}</el-tag>
                <el-tag size="mini" type="warning">{{ scope.row.tag }}</el-tag>
              </div>
              <div class="file-meta">
                <div class="file-publish-time">{{ formatDate(scope.row.publish_time) }}</div>
                <div class="file-description">{{ scope.row.description }}</div>
              </div>
            </div>
            <div class="file-action">
              <el-link type="success" :href="scope.row.document.download_url" icon="el-icon-download">下载</el-link>
              <el-link
                type="primary"
                icon="el-icon-edit"
                @click="$router.push({ name: 'project-document-edit', params: { id: scope.row.id }})"
              >
                编辑
              </el-link>
              <ns-confirm-button @click="deleteRow(scope.row)">
                <el-link type="danger" icon="el-icon-delete">删除</el-link>
              </ns-confirm-button>
            </div>
          </div>
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
      listDataApi: this.$api.cardpc.project.listDocument,
      deleteDataApi: this.$api.cardpc.project.deleteDocument,
    }
  },
  methods: {
    formatDate (time) {
      return moment(time).format('YYYY-MM-DD')
    },

    getFileExt (filename) {
      return filename.split('.').pop().toUpperCase()
    },
  },
}
</script>

<style lang="scss">
.file-row {
  display: flex;

  .file-info {
    flex-grow: 1;
    display: flex;
    flex-direction: column;

    .file-subject {
      font-size: 16px;
      color: #403f40;
    }

    .file-meta {
      display: flex;
      font-size: 14px;
      color: #9b9b9b;
      flex-wrap: nowrap;

      .file-publish-time {
        margin-right: 1em;
        flex-shrink: 0;
      }
    }
  }

  .file-action {
    width: 200px;
    display: flex;
    align-items: center;

    .el-link {
      margin-left: 1em;
    }
  }
}
</style>
