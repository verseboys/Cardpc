<template>
  <div class="carousel-edit-item">
    <el-upload
      action="dummy"
      :http-request="$api.media.uploadImageTo('carousel')"
      :show-file-list="false"
      :on-success="onUploadSuccess"
    >
      <img v-if="item.image && item.image.url" :src="item.image.url" class="image-preview" />
      <i v-else class="el-icon-plus image-uploader-icon" />
    </el-upload>
    <el-form label-width="auto" label-position="right" hide-required-asterisk>
      <el-form-item label="标题">
        <el-input v-model="item.title" @input="dirty=true" />
      </el-form-item>
      <el-form-item label="链接">
        <el-input v-model="item.link_url" @input="dirty=true" />
      </el-form-item>
      <el-form-item>
        <el-button
          type="success"
          :disabled="!dirty"
          @click="onSave"
        >
          保存
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  props: {
    item: { type: Object, required: true },
    panels: { type: Object, required: true },
  },
  data () {
    return {
      dirty: false,
    }
  },
  methods: {
    onUploadSuccess (res, file, fileList) {
      this.item.image = res.data.data[0]
      this.dirty = true
    },

    onSave () {
      let vm = this
      let api = null
      let data = {
        title: vm.item.title,
        link_url: vm.item.link_url,
        image: vm.item.image.id,
      }
      if (vm.item.id) {
        api = () => vm.$api.cardpc.project.patchCarouselItem(vm.item.id, data)
      } else {
        api = () => vm.$api.cardpc.project.createCarouselItem(data)
      }
      api().then(res => {
        if (res.status !== 200 || res.data.code !== 0) {
          vm.$message.error('保存失败')
        } else {
          vm.item.id = res.data.data.id
          vm.dirty = false
          vm.$message.success('保存成功')
        }
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.carousel-edit-item {
  display: flex;

  .el-form {
    margin-left: 1em;
  }

  .el-form-item {
    margin-bottom: 10px;
  }

  ::v-deep .el-form-item__label::before {
    content: '' !important;
  }

  .el-input {
    min-width: 250px;
  }
}

::v-deep .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;

  &:hover {
    border-color: #409eff;
  }

  .image-preview {
    width: auto;
    height: 120px;
    display: block;
  }

  .image-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    height: 120px;
    line-height: 178px;
    text-align: center;
  }
}
</style>
