import adminAppsConfig from '@nsproject/admin.js'
import defaultLogo from '@natureself/assets/logo/natureself.svg'

export default {
  state: {
    sidebar: {
      collapsed: false,
      animation: true,
    },
    // 'device' 仅仅表示屏幕大小，当屏幕宽度大于等于 992 时（element-ui 中的 md），我们认为是桌面端，反之为移动端
    device: 'desktop',
    logo: adminAppsConfig.logo || defaultLogo,
    title: adminAppsConfig.title || '管理后台',
  },

  getters: {
    sidebar: state => state.sidebar,
    device: state => state.device,
    appLogo: state => state.logo,
    appTitle: state => state.title,
  },

  mutations: {
    TOGGLE_SIDEBAR: (state, animation) => {
      state.sidebar.collapsed = !state.sidebar.collapsed
      state.sidebar.animation = animation !== undefined ? animation : true
    },
    CLOSE_SIDEBAR: (state, animation) => {
      state.sidebar.collapsed = true
      state.sidebar.animation = animation !== undefined ? animation : true
    },
    SET_DEVICE: (state, device) => {
      state.device = device
    },
  },

  actions: {
    ToggleSidebar ({ commit }, animation) {
      commit('TOGGLE_SIDEBAR', animation)
    },
    CloseSidebar ({ commit }, animation) {
      commit('CLOSE_SIDEBAR', animation)
    },
    SetDevice ({ commit }, device) {
      commit('SET_DEVICE', device)
    },
  },
}
