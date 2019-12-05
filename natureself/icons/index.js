import Vue from 'vue'
import SvgIcon from './SvgIcon.vue'
import path from 'path'

// register globally
Vue.component('svg-icon', SvgIcon)

const iconFileNames = {}

// see https://webpack.js.org/guides/dependency-management/#context-module-api
const importAll = r => r.keys().forEach((file) => {
  let filename = path.basename(file)
  if (filename in iconFileNames) {
    throw Error(`Duplicate icon filename: ${filename}`)
  }
  iconFileNames[filename] = filename
  r(file)
})

const req = require.context('./svg', true, /\.svg$/)
importAll(req)

export default {
  importAll,
}
