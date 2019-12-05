<template>
  <div>
    <div style="margin-bottom: 1em;">
      <ul class="el-upload-list el-upload-list--text">
        <li v-if="file" class="el-upload-list__item is-success">
          <a class="el-upload-list__item-name">
            <i class="el-icon-document" />{{ file.filename }}
          </a>
          <label class="el-upload-list__item-status-label">
            <i class="el-icon-upload-success el-icon-circle-check" />
          </label>
          <i class="el-icon-close" @click="removeFile" />
        </li>
      </ul>
    </div>
    <el-upload
      action="dummy"
      :http-request="$api.media.uploadDocumentTo(schema.options.bucket)"
      :show-file-list="false"
      :on-success="onUploadSuccess"
      :before-upload="onBeforeUpload"
      :accept="schema.options.accept"
      drag
    >
      <i class="el-icon-upload" />
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div slot="tip" class="el-upload__tip">
        <template v-if="humanSizeLimit">
          文件大小不超过 {{ humanSizeLimit }}
        </template>
      </div>
    </el-upload>
  </div>
</template>

<script>
export default {
  props: {
    schema: { type: Object, required: true },
    value: { type: Object, required: false, default: null },
  },
  data () {
    return {
      file: this.value ? this.value : null,
      humanSizeLimit: this.schema.options.size_limit
        ? this.humanFileSize(this.schema.options.size_limit)
        : null,
    }
  },
  methods: {
    onUploadSuccess (res, file, fileList) {
      this.file = res.data.data[0]
      this.$emit('input', res.data.data[0])
    },

    onBeforeUpload (file) {
      let ok = true

      if (this.schema.options.size_limit && file.size > this.schema.options.size_limit) {
        this.$message.error(`上传文件大小不能超过 ${this.humanSizeLimit}}`)
        ok = false
      }

      return ok
    },

    removeFile () {
      this.file = null
      this.$emit('input', null)
    },

    // https://stackoverflow.com/a/20732091
    humanFileSize (size) {
      let i = Math.floor(Math.log(size) / Math.log(1024))
      return (size / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i]
    },
  },
}
</script>
