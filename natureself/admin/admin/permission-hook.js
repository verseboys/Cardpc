import router from './router'
import store from './store'
import { Message } from 'element-ui'

// 通过 meta.roles 判断当前用户是否有权访问
function hasPermission (route, roles) {
  if (route.meta && route.meta.roles) {
    return roles.some(role => route.meta.roles.includes(role))
  } else {
    return true
  }
}

router.beforeEach((to, from, next) => {
  if (store.getters.authenticated) {
    // already signed in, check if user has permission to the route
    if (!hasPermission(to, store.getters.roles)) {
      next({ name: 'notfound' })
    } else {
      next()
    }
  } else {
    if (to.meta.allowAnonymous) {
      // e.g. login page, 404 page, ...
      next()
    } else {
      store.dispatch('GetUserInfo').then(response => {
        store.dispatch('GenerateRoutes').then(addRoutes => {
          router.addRoutes(addRoutes)
          next({ ...to, replace: true })
        })
      }).catch(err => {
        if (err.status === 401) {
          next({ name: 'login', query: { redirect: to.path } })
        } else {
          Message.error('网络错误')
        }
      })
    }
  }
})
