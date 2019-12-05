// NOTES
// 我们使用 Session 来登录，因此无需记录、也没有 jwt token。我们在每一次加载新页面前（router.beforeEach），
// 通过判断 state.roles 是否为 null 来判断是否登录过（注意，只在前端是无法百分之百判断用户是否已经登录，
// 所以我们只能 try best effort）。如果用户没有登录（roles === null），则跳转到登录页面。
//
// 在任何 API 请求时如果服务器返回了 401，则表示用户没有登录（或之前的 session 已经失效），我们将 roles
// 重新设置为 null，这样在下一次加载页面时，就会跳转到登录页面。
//
// 在每一次网页加载前（主 Vue 的 beforeMount hook），我们执行一次 user.GetInfo，获取用户信息，
// 如果成功，则表示用户已经登录了，我们可以更新 state。因此，state 无需持久化存储。持久化存储反而会导致
// 一些麻烦。

import defaultAvatar from '@natureself/assets/img/avatar-default.svg'
import api from '@ns-account/webapp/api'

export default {
  state: {
    username: '',
    email: '',
    displayName: '',
    avatarUrl: '',
    roles: null,
  },

  getters: {
    username: state => state.username,
    email: state => state.email,
    displayName: state => state.displayName,
    avatarUrl: state => state.avatarUrl || defaultAvatar,
    // 无论用户是否登录，roles 总是返回一个数组，方便使用
    roles: state => state.roles || [],
    // 这里 authenticated 只表示用户已经登录过（当前页面曾经执行过 GetInfo()）
    authenticated: state => state.roles !== undefined && state.roles !== null,
  },

  mutations: {
    // userdata is api response of GET /account/user_info
    SET_USER (state, userdata) {
      state.username = userdata.username
      state.email = userdata.email
      state.displayName = userdata.display_name || userdata.username
      state.avatarUrl = userdata.avatar_url || defaultAvatar
      state.roles = userdata.roles
    },
  },

  actions: {
    Login ({ commit }, form) {
      let { username, password, role = 'admin' } = form
      return new Promise((resolve, reject) => {
        api.account.login({ username, password, role }).then(response => {
          if (response.status === 200) {
            commit('SET_USER', response.data.data)
            resolve(response)
          } else {
            reject(response)
          }
        })
      })
    },

    GetUserInfo ({ commit }) {
      return new Promise((resolve, reject) => {
        api.account.getInfo().then(response => {
          if (response.status === 200) {
            commit('SET_USER', response.data.data)
            resolve(response)
          } else if (response.status === 401) {
            commit('SET_USER', {})
            reject(response)
          } else {
            commit('SET_USER', {})
            reject(response)
          }
        }).catch(err => {
          reject(err)
        })
      })
    },

    Logout ({ commit }) {
      return new Promise((resolve, reject) => {
        api.account.logout().then(response => {
          commit('SET_USER', {})
          resolve(response)
        })
      })
    },
  },
}
