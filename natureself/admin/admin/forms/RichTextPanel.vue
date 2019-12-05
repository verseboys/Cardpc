<template>
  <ckeditor
    :editor="editor"
    :config="config"
    :value="editorData"
    v-bind="$attrs"
    v-on="$listeners"
    @input="(val) => $emit('input', val)"
    @ready="onEditorReady"
  />
</template>

<script>
import CKEditor from '@ckeditor/ckeditor5-vue'
// import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
import DecoupledEditor from '@ckeditor/ckeditor5-build-decoupled-document'
import api from '@admin/api'

class UploadAdapter {
  constructor (loader) {
    this.loader = loader
  }

  upload () {
    return new Promise((resolve, reject) => {
      this.loader.file.then(file => {
        api.media.uploadImageTo('richtext')({ file }).then(response => {
          if (response.data.code === 0) {
            resolve({ default: response.data.data[0].url })
          } else {
            reject(response)
          }
        })
      })
    })
  }

  abort () {}
}

export default {
  components: {
    ckeditor: CKEditor.component,
  },
  props: {
    schema: { type: Object, required: true },
    value: { type: String, required: false, default: null },
  },
  data () {
    return {
      // editor: ClassicEditor,
      editor: DecoupledEditor,
      editorData: this.value,

      config: {
        language: 'zh-cn',
      },
    }
  },
  methods: {
    onEditorReady (editor) {
      //  used for DecoupledEditor
      editor.ui.getEditableElement().parentElement.insertBefore(
        editor.ui.view.toolbar.element,
        editor.ui.getEditableElement()
      )

      editor.plugins.get('FileRepository').createUploadAdapter = function (loader) {
        return new UploadAdapter(loader)
      }
    },
  },
}
</script>

<style :lang="scss" scoped>
.ck.ck-editor__editable:not(.ck-focused) {
  border-color: var(--ck-color-base-border) !important;
}
</style>
