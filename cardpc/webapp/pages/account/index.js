import Vue from 'vue'
import Login from './Login.vue'
import Register from './Register.vue'
import ResetPassword from './ResetPassword.vue'
// 滚动条包
import PerfectScrollbar from 'perfect-scrollbar'
// 滚动条包的css
import 'perfect-scrollbar/css/perfect-scrollbar.css'

const el_scrollBar = (el) => {
  if (el._ps_ instanceof PerfectScrollbar) {
    el._ps_.update()
  } else {
    el._ps_ = new PerfectScrollbar(el, { suppressScrollX: true })
  }
}
// 自定义滚动条指令
Vue.directive('scrollBar', {
  inserted (el, binding, vnode) {
    el_scrollBar(el)
  },
  // 更新dom的时候
  componentUpdated (el, binding, vnode, oldVnode) {
    try {
      vnode.context.$nextTick(
        () => {
          el_scrollBar(el)
        }
      )
    } catch (error) {
      el_scrollBar(el)
    }
  },
})
// eslint-disable-next-line no-new
new Vue({
  el: '#account-app',
  components: {
    Login,
    Register,
    ResetPassword,
  },
  computed: {
    component () {
      return document.querySelector('#account-app').dataset.app
    },
  },
})
