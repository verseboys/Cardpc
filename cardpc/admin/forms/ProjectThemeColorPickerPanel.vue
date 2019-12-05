<template>
  <div style="display: flex;">
    <div>
      <el-color-picker v-model="colors.color1" @active-change="(val) => onActiveChange(val, 'color1')" />
      <el-color-picker v-model="colors.color2" @active-change="(val) => onActiveChange(val, 'color2')" />
      <el-color-picker v-model="colors.color3" @active-change="(val) => onActiveChange(val, 'color3')" />
    </div>
    <el-card class="preview" style="margin-left: auto;">
      <div class="header">
        <div class="banner" :style="`background-color: ${activeColors.color3};`">
          <div class="el-image banner-image">
            <div slot="error" class="el-image__error">Banner 图片</div>
          </div>
        </div>
        <div class="nav" :style="`background-color: ${activeColors.color1};`">
          <div class="nav-item">导航1</div>
          <div class="nav-item active" :style="`background-color: ${activeColors.color2};`">导航2</div>
          <div class="nav-item">导航3</div>
          <div class="nav-item">导航4</div>
        </div>
      </div>
      <div class="main" :style="`background-color: ${activeColors.color3};`">
        <div class="content">
          <p>
            颜色 1: 主色调，用于导航条背景、按钮背景、边框颜色等，当前值：{{ activeColors.color1 }}<br>
            颜色 2: 主色调激活色，导航条激活条目背景，当前值：{{ activeColors.color2 }}<br>
            颜色 3: 网页背景色，当前值：{{ activeColors.color3 }}
          </p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
// https://gist.github.com/jedfoster/7939513
const rgb2hex = function (rgb) {
  // A very ugly regex that parses a string such as 'rgb(191, 0, 46)' and produces an array
  // eslint-disable-next-line no-useless-escape
  rgb = rgb.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d\.]+))?\)$/)

  // another way to convert a decimal to hex
  function hex (x) { return ('0' + parseInt(x).toString(16)).slice(-2) }

  // concatenate the pairs and return them lower cased
  return '#' + (hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3])).toLowerCase()
}

export default {
  props: {
    schema: { type: Object, required: true },
    value: { type: Object, required: false, default: () => {} },
  },
  data () {
    return {
      colors: {
        color1: '#eea842',
        color2: '#e6832d',
        color3: '#faf5e4',
        ...this.value,
      },
      activeColors: {
        color1: '#eea842',
        color2: '#e6832d',
        color3: '#faf5e4',
        ...this.value,
      },
    }
  },
  watch: {
    colors: {
      deep: true,
      handler: function (val) {
        this.activeColors = { ...val }
        this.$emit('input', val)
      },
    },
  },
  mounted () {
    this.$emit('input', this.colors)
  },
  methods: {
    onActiveChange (val, colorName) {
      this.activeColors = { ...this.activeColors, [colorName]: rgb2hex(val) }
    },
  },
}
</script>

<style lang="scss" scoped>
.preview {
  width: 500px;
}

// stylelint-disable-next-line
::v-deep .el-card__body {
  padding: 0;
}

.banner {
  width: 100%;
  height: 80px;
  display: flex;
}

.banner-image {
  width: 80%;
  height: 80px;
  margin-left: auto;
  margin-right: auto;
}

.nav {
  width: 100%;
  height: 50px;
  color: white;
  padding-left: 10%;
  padding-right: 10%;
  display: flex;
  justify-content: center;
}

.nav-item {
  height: 50px;
  flex-grow: 1;
  line-height: 50px;
  text-align: center;
  vertical-align: middle;
}

.main {
  width: 100%;
  height: 250px;
  display: flex;
}

.content {
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 1em;
  margin-bottom: 1em;
  padding: 1em;
  background-color: white;
}
</style>
