<template>
  <el-upload
    action="dummy"
    :http-request="$api.media.uploadImageTo(schema.options.bucket)"
    :show-file-list="false"
    :on-success="onUploadSuccess"
    :before-upload="onBeforeUpload"
    :accept="schema.options.accept"
  >
    <img v-if="imageUrl" :src="imageUrl" class="image-preview">
    <i v-else class="el-icon-plus image-uploader-icon" />
    <div slot="tip" class="el-upload__tip">
      只能上传 {{ humanAcceptImageTypes }} 文件
      <template v-if="humanSizeLimit">
        ，且不超过 {{ humanSizeLimit }}
      </template>
    </div>
  </el-upload>
</template>

<script>
import _ from 'lodash'

export default {
  props: {
    schema: { type: Object, required: true },
    value: { type: Object, required: false, default: null },
  },
  data () {
    return {
      imageUrl: this.value ? this.value.url : '',
      humanAcceptImageTypes: this.schema.options.accept
        ? _.map(this.schema.options.accept.split(','), (item) => item.trim().replace(/^image\//, '')).join('/')
        : '',
      humanSizeLimit: this.schema.options.size_limit
        ? this.humanFileSize(this.schema.options.size_limit)
        : null,
    }
  },
  methods: {
    onUploadSuccess (res, file) {
      this.imageUrl = res.data.data[0].url
      this.$emit('input', res.data.data[0])
    },

    onBeforeUpload (file) {
      let ok = true

      if (this.schema.options.size_limit && file.size > this.schema.options.size_limit) {
        this.$message.error(`上传图片大小不能超过 ${this.humanSizeLimit}}`)
        ok = false
      }

      return ok
    },

    // https://stackoverflow.com/a/20732091
    humanFileSize (size) {
      let i = Math.floor(Math.log(size) / Math.log(1024))
      return (size / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i]
    },
  },
}
</script>

<style lang="scss" scoped>
::v-deep .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

::v-deep .el-upload:hover {
  border-color: #409eff;
}

::v-deep .image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

::v-deep .image-preview {
  width: auto;
  height: 178px;
  display: block;
}
</style>
