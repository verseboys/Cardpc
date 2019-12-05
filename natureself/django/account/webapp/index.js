import Vue from 'vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import BootstrapVue from 'bootstrap-vue'

import '@natureself/icons'

import api from './api'

import Login from './views/Login.vue'
Vue.use(BootstrapVue)
Vue.prototype.$api = api

Vue({
  el: '#app',
  components: {
    'ns-login': Login,
  },
})
