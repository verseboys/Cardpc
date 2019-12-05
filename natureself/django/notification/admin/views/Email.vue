<template>
  <el-container>
    <el-header height="auto">
      <el-form
        label-width="5em"
        label-position="right"
        size="mini"
      >
        <el-col :span="6">
          <el-form-item label="发件人">
            <el-input
              v-model="filters.from"
              @change="handleFiltersChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="收件人">
            <el-input
              v-model="filters.recipient"
              @change="handleFiltersChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="标题">
            <el-input
              v-model="filters.subject"
              @change="handleFiltersChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="发送日期">
            <el-date-picker
              v-model="filters.sentRange"
              type="daterange"
              align="right"
              unlink-panels
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :picker-options="sentRangeOptions"
              value-format="yyyy-MM-dd"
              @change="handleFiltersChange"
            />
          </el-form-item>
        </el-col>
        <el-col>
          <el-form-item>
            <el-button
              type="primary"
              @click="listEmail"
            >
              刷新
            </el-button>
          </el-form-item>
        </el-col>
      </el-form>
    </el-header>

    <el-main class="table-container">
      <el-table :data="cachedData">
        <el-table-column type="expand">
          <template slot-scope="scope">
            <div class="email-details-container">
              <el-form
                class="email-details"
                label-position="right"
                label-width="100px"
                size="mini"
              >
                <el-form-item label="邮件标题：">
                  <span><b>{{ scope.row.subject }}</b></span>
                </el-form-item>
                <el-form-item label="发件人：">
                  <el-tag>{{ scope.row.from_email.display }}</el-tag>
                </el-form-item>
                <el-form-item label="收件人：">
                  <el-tag
                    v-for="email in scope.row.recipients"
                    :key="email.address"
                  >
                    {{ email.display }}
                  </el-tag>
                </el-form-item>
              </el-form>
              <div class="email-content-container">
                <!-- eslint-disable-next-line -->
                <div v-html="scope.row.content"></div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="sent_at"
          label="发送时间"
          width="150"
        >
          <template slot-scope="scope">
            {{ formatTime(scope.row.sent_at) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="发送状态"
          width="100"
        >
          <el-tag
            slot-scope="scope"
            :type="$api.notification.getEmailStatus(scope.row.status).type"
          >
            {{ $api.notification.getEmailStatus(scope.row.status).display }}
          </el-tag>
        </el-table-column>
        <el-table-column
          prop="from_email"
          label="发件人"
          width="100"
        >
          <el-tag slot-scope="scope">
            {{ scope.row.from_email.name || scope.row.from_email.address }}
          </el-tag>
        </el-table-column>
        <el-table-column
          prop="recipients"
          label="收件人"
          width="200"
        >
          <template slot-scope="scope">
            <el-tag
              v-for="email in scope.row.recipients"
              :key="email.address"
            >
              {{ email.name || email.address }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="subject"
          label="邮件标题"
        />
      </el-table>
    </el-main>

    <el-footer>
      <el-pagination
        :current-page.sync="pagination.page"
        :page-size="10"
        layout="total, prev, pager, next"
        :total="pagination.total"
        @current-change="handlePageChange"
      />
    </el-footer>
  </el-container>
</template>

<script>
import moment from 'moment'

export default {
  data () {
    return {
      cachedData: null,
      filters: {
        subject: '',
        from: '',
        recipient: '',
        sentRange: null,
        status: '',
      },
      sentRangeOptions: {
        shortcuts: [
          {
            text: '最近一周',
            onClick (picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
              picker.$emit('pick', [start, end])
            },
          },
          {
            text: '最近一月',
            onClick (picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
              picker.$emit('pick', [start, end])
            },
          },
        ],
      },
      pagination: {
        page: 1,
        total: 0,
      },
    }
  },
  mounted () {
    this.listEmail()
  },
  methods: {
    formatTime (time) {
      return moment(time).format('YYYY-MM-DD HH:mm:ss')
    },

    handlePageChange (page) {
      this.listEmail()
    },

    handleFiltersChange () {
      this.listEmail()
    },

    listEmail () {
      let vm = this
      this.$api.notification.listEmail({ ...this.filters, page: this.pagination.page }).then(response => {
        if (response.status === 200) {
          vm.cachedData = response.data.data
          vm.pagination.page = response.data.pagination.page
          vm.pagination.total = response.data.pagination.total
        }
      })
    },
  },
}
</script>

<style lang="scss">
.el-tag + .el-tag {
  margin-left: 0.3em;
}

.table-container {
  padding-top: 0;
}

.email-details {
  .el-form-item--mini.el-form-item {
    margin-bottom: 5px;
  }
}

.email-details-container {
  border: 1px solid #ebeef5;
}

.email-content-container {
  border-top: 1px solid #ebeef5;
  padding: 1em;
}
</style>
