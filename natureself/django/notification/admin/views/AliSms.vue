<template>
  <el-container>
    <el-header height="auto">
      <el-form
        label-width="5em"
        label-position="right"
        size="mini"
      >
        <el-col :span="7">
          <el-form-item label="手机号">
            <el-input
              v-model="filters.phone"
              @change="handleFiltersChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="7">
          <el-form-item label="内容">
            <el-input
              v-model="filters.content"
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
              @click="listAliSms"
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
            <div class="alisms-details-container">
              <el-form
                class="alisms-details"
                label-position="right"
                label-width="150px"
                size="mini"
              >
                <el-form-item label="手机号：">
                  <el-tag
                    v-for="(number, index) in scope.row.phone_numbers"
                    :key="number + index"
                  >
                    {{ number }}
                  </el-tag>
                </el-form-item>
                <el-form-item label="内容：">
                  <span>{{ scope.row.content }}</span>
                </el-form-item>
                <el-form-item label="阿里云 BizId：">
                  <span>{{ scope.row.ali_bizid || '-' }}</span>
                </el-form-item>
                <el-form-item label="阿里云 Code：">
                  <span>{{ scope.row.ali_code || '-' }}</span>
                </el-form-item>
                <el-form-item label="阿里云 Message：">
                  <span>{{ scope.row.ali_message || '-' }}</span>
                </el-form-item>
              </el-form>
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
            :type="$api.notification.getAliSmsStatus(scope.row.status).type"
          >
            {{ $api.notification.getAliSmsStatus(scope.row.status).display }}
          </el-tag>
        </el-table-column>
        <el-table-column
          prop="phone_numbers"
          label="手机号"
          width="200"
        >
          <template slot-scope="scope">
            <el-tag
              v-for="(number, index) in scope.row.phone_numbers"
              :key="number + index"
            >
              {{ number }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="content"
          label="短信内容"
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
        phone: '',
        content: '',
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
    this.listAliSms()
  },
  methods: {
    formatTime (time) {
      return moment(time).format('YYYY-MM-DD HH:mm:ss')
    },

    handlePageChange (page) {
      this.listAliSms()
    },

    handleFiltersChange () {
      this.listAliSms()
    },

    listAliSms () {
      let vm = this
      this.$api.notification.listAliSms({ ...this.filters, page: this.pagination.page }).then(response => {
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

.alisms-details {
  .el-form-item--mini.el-form-item {
    margin-bottom: 5px;
  }
}

.alisms-details-container {
  border: 1px solid #ebeef5;
}

.alisms-content-container {
  border-top: 1px solid #ebeef5;
  padding: 1em;
}
</style>
