import Vue from 'vue'

import 'normalize.css/normalize.css'

import ElementUI from 'element-ui'
import locale from 'element-ui/lib/locale/lang/zh-CN.js'

import App from './App.vue'
import store from './store'
import router, { registerRoutes } from './router'
import api, { registerApi } from './api'

import './styles/index.scss'
import '@natureself/icons'
import './permission-hook.js'

// -------- 8< --------
// register admin apps
// -------- 8< --------
import adminAppsConfig from '@nsproject/admin.js'

Vue.use(ElementUI, { locale, size: 'small' })
Vue.prototype.$api = api
const { apps = {} } = adminAppsConfig
Object.keys(apps).forEach(name => {
  registerApi(apps[name].api)
  registerRoutes(apps[name].routes)
})

const app = new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App),
})

if (process.ENV !== 'production') {
  window.app = app
}
