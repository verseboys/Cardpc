<template>
  <div>
    <ns-form
      ref="editForm"
      v-model="editFormdata"
      :schema="$api.media.getVideoEditForm"
      :initial-data="mode === 'new' ? null : getDataApi"
    >
      <el-form-item>
        <el-button type="danger" size="mini" @click="cancel">取消</el-button>
        <el-button type="success" size="mini" :disabled="submitButtonDisabled" @click="submitData">
          {{ mode === 'new' ? '新建' : '保存' }}
        </el-button>
      </el-form-item>
      <el-form-item label="视频预览">
        <div v-if="polyvScriptLoaded" id="player"></div>
        <div v-else>保利威 SDK 加载中...</div>
      </el-form-item>
    </ns-form>
  </div>
</template>

<script>
import EditPageMixin from '@admin/mixins/edit-page.js'

export default {
  mixins: [EditPageMixin],
  data () {
    return {
      createDataApi: this.$api.media.createVideo,
      patchDataApi: (data) => this.$api.media.patchVideo(this.$route.params.id, data),
      getDataApi: () => this.$api.media.getVideo({ id: this.$route.params.id }),

      polyvScriptLoaded: false,
      polyvPlayer: null,
    }
  },
  watch: {
    'editFormdata.vid' (val) {
      this.refreshPreviewPlayer(val)
    },

    polyvScriptLoaded (val) {
      if (val) {
        this.refreshPreviewPlayer(this.editFormdata.vid)
      }
    },
  },
  created () {
    let vm = this
    if (!window.polyvPlayer) {
      let script = document.createElement('script')
      script.onload = () => { vm.polyvScriptLoaded = true }
      script.src = '//player.polyv.net/script/player.js'
      document.head.appendChild(script)
    } else {
      vm.polyvScriptLoaded = true
    }
  },
  methods: {
    refreshPreviewPlayer (vid) {
      if (!this.polyvScriptLoaded) {
        return
      }
      if (!this.polyvPlayer && !vid) {
        return
      }
      if (this.polyvPlayer) {
        this.polyvPlayer.changeVid({ vid })
      } else {
        this.polyvPlayer = window.polyvPlayer({
          wrap: '#player',
          vid,
          width: '100%',
        })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
#player {
  width: 100%;
  max-width: 600px;
  min-width: 400px;
}
</style>
