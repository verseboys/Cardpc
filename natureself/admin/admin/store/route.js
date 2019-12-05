import { constantRoutes, asyncRoutes, notFoundRoute } from '@admin/router'

// 通过 meta.roles 判断当前用户是否有权访问
function hasPermission (route, roles) {
  if (route.meta && route.meta.roles) {
    return roles.some(role => route.meta.roles.includes(role))
  } else {
    return true
  }
}

// 递归过滤异步路由表，仅返回当前用户有权限的条目
export function filterAsyncRoutes (routes, roles) {
  const res = []

  routes.forEach(route => {
    const tmp = { ...route }
    if (hasPermission(tmp, roles)) {
      if (tmp.children) {
        tmp.children = filterAsyncRoutes(tmp.children, roles)
      }
      res.push(tmp)
    }
  })

  return res
}

export default {
  state: {
    routes: [],
    addRoutes: [],
  },

  getters: {
    routes: state => state.routes,
    addRoutes: state => state.addRoutes,
  },

  mutations: {
    SET_ROUTES: (state, routes) => {
      state.addRoutes = routes
      state.routes = constantRoutes.concat(routes, notFoundRoute)
    },
  },

  actions: {
    GenerateRoutes: ({ commit, getters }) => {
      return new Promise(resolve => {
        commit('SET_ROUTES', filterAsyncRoutes(asyncRoutes, getters.roles))
        resolve(getters.addRoutes)
      })
    },
  },
}
