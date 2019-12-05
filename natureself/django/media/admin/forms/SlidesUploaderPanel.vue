<template>
  <div>
    <div v-if="slides.length > 0" style="width: 300px;">
      <el-slider
        v-model="imageBoxWidth"
        :min="150" :max="600"
        :format-tooltip="(val) => `预览图片尺寸：${val}px`"
      />
    </div>
    <draggable
      v-model="slides"
      :animation="200"
      @start="autoSort = false"
    >
      <div v-for="(slide, index) in slides" :key="slide.id" class="imgbox" :style="'width: ' + imageBoxWidth + 'px;'">
        <el-image :src="slide.url" fit="contain" />
        <div class="overlay"><span>{{ index+1 }}</span></div>
        <i class="delete-button el-icon-delete" @click="deleteSlide(index)" />
      </div>
    </draggable>
    <el-upload
      action="dummy"
      :http-request="$api.media.uploadSlide"
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
      slides: _.isEmpty(this.value) ? [] : this.value,
      autoSort: _.isEmpty(this.value),

      imageBoxWidth: 350,
      uploadingCount: 0,
    }
  },
  watch: {
    slides (val) {
      this.$emit('input', val)
    },
  },
  methods: {
    onUploadSuccess (res, file, fileList) {
      this.uploadingCount--
      // 最初，我们直接用 el-upload 提供的 filelist。
      // 当我们在选择文件对话框中一次性选择多个文件、或一次性将多个文件拖拽到上传对话框中，
      // filelist 的顺序应该是由操作系统决定的，这个顺序一般符合用户的直觉。
      // 现在我们使用独立维护的 slides 数组，当一次性上传多个文件时，el-upload 会并行上传
      // 文件，上传完一个通知一次（onUploadSuccess），我们将上传完的文件追加到 slides 数组
      // 后面，因此 slides 就是乱序的。
      // 解决方法：
      // 考虑一般正常的场景，用户新建 PPT，会直接将所有文件一次性上传。在有拖拽排序之后，
      // 几乎不会再有批量上传的情况。
      // 因此，我们可以记录一个标记，如果用户没有拖拽过，那么总是自动排序，如果用户拖拽过，
      // 那么久不再自动排序。如果是编辑模式，则自动禁用自动排序。
      // 注意，如果文件名中不含数字，也应该尽量去排序（正常情况下，文件名应该都是有编号的）
      if (this.autoSort) {
        this.slides = _.sortBy([...this.slides, res.data.data[0]], slide => parseInt(slide.filename.match(/\d+/)))
      } else {
        this.slides.push(res.data.data[0])
      }
    },

    beforeUpload (file) {
      this.uploadingCount++
    },

    deleteSlide (index) {
      this.slides.splice(index, 1)
    },
  },
}
</script>

<style lang="scss" scoped>
.imgbox {
  display: inline-block;
  position: relative;
  // width: 200px;
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
      opacity: 0.5;
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
