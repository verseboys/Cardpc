<template>
  <div>
    <draggable
      v-model="images"
      :animation="200"
    >
      <div v-for="(image, index) in images" :key="image.id" class="imgbox">
        <el-image :src="image.url" fit="contain" />
        <div class="overlay"></div>
        <i class="delete-button el-icon-delete" @click="deleteImage(index)" />
        <el-input v-model="image.title" size="mini" placeholder="请输入标题" @change="(val) => updateImageTitle(val, index)" />
      </div>
    </draggable>
    <el-upload
      action="dummy"
      :http-request="$api.cardpc.project.uploadGalleryImage"
      :show-file-list="false"
      :on-success="onUploadSuccess"
      :before-upload="beforeUpload"
      :accept="schema.options.accept"
      multiple
      drag
    >
      <i class="el-icon-upload" />
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div v-if="uploadingCount">
        文件上传中：{{ uploadingCount }}
      </div>
    </el-upload>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import _ from 'lodash'

export default {
  components: {
    draggable,
  },
  props: {
    schema: { type: Object, required: true },
    value: { type: Array, required: false, default: () => [] },
  },
  data () {
    return {
      images: _.isEmpty(this.value) ? [] : this.value,
      uploadingCount: 0,
    }
  },
  watch: {
    images: {
      deep: true,
      handler (val) {
        this.$emit('input', val)
      },
    },
  },
  methods: {
    onUploadSuccess (res, file, fileList) {
      this.uploadingCount--
      this.images.push(res.data.data[0])
    },

    beforeUpload (file) {
      this.uploadingCount++
    },

    deleteImage (index) {
      this.images.splice(index, 1)
    },

    updateImageTitle (val, index) {
      let vm = this
      let image = this.images[index]
      vm.$api.cardpc.project.patchGalleryImage({ id: image.id, title: val }).then(res => {
        if (res.status === 200 && res.data.code === 0) {
          vm.$message.success(`保存成功: ${val}`)
        } else {
          vm.$message.error(`保存失败: ${val}`)
        }
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.imgbox {
  display: inline-block;
  position: relative;
  width: 200px;
  margin: 5px;

  .el-image {
    transition: 0.5s ease;
    opacity: 1;
    width: 100%;
    height: auto;
  }

  .overlay {
    transition: 0.5s ease;
    opacity: 0;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    -ms-transform: translate(-50%, -50%);
    text-align: center;

    span {
      font-size: 64px;
      color: white;
      text-shadow: 2px 2px black;
    }
  }

  .delete-button {
    transition: 0.5s ease;
    opacity: 0;
    position: absolute;
    top: 5px;
    right: 5px;
    cursor: pointer;
    color: #409eff;
    font-size: 20px;
  }

  &:hover {
    cursor: move;

    .el-image {
      opacity: 0.8;
    }

    .overlay {
      opacity: 1;
    }

    .delete-button {
      opacity: 1;
    }
  }
}
</style>
