<template>
  <el-upload
    action="dummy"
    :http-request="$api.media.uploadDocumentTo(schema.options.bucket)"
    :file-list="files"
    :on-success="onUploadSuccess"
    :on-remove="onRemove"
  >
    <el-button size="small" type="primary">点击上传</el-button>
    <div slot="tip" class="el-upload__tip">
      <template v-if="humanSizeLimit">
        可上传多个文件，单个文件尺寸不超过 {{ humanSizeLimit }}
      </template>
    </div>
  </el-upload>
</template>

<script>
import _ from 'lodash'

export default {
  props: {
    schema: { type: Object, required: true },
    value: { type: Array, required: false, default: null },
  },
  data () {
    return {
      files: _.map(this.value, file => { file.name = file.filename; return file }),
      humanAcceptImageTypes: this.schema.options.accept
        ? _.map(this.schema.options.accept.split(','), (item) => item.trim().replace(/^image\//, '')).join('/')
        : '',
      humanSizeLimit: this.schema.options.size_limit
        ? this.humanFileSize(this.schema.options.size_limit)
        : null,
    }
  },
  methods: {
    // https://stackoverflow.com/a/20732091
    humanFileSize (size) {
      let i = Math.floor(Math.log(size) / Math.log(1024))
      return (size / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i]
    },

    onUploadSuccess (res, file) {
      file = { ...file, ...res.data.data[0] }
      this.files.push(file)
      this.$emit('input', this.files)
    },

    onRemove (file) {
      _.remove(this.files, item => item.id === file.id)
      this.$emit('input', this.files)
    },
  },
}
</script>
