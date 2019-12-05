import Vue from 'vue'
import Router from 'vue-router'

// import MockMenus from './mock'

import Layout from '@admin/views/layout/index.vue'
Vue.use(Router)

/**
 * Route object options (non vue-router options):
 *
 * hidden: false            don't show in sidebar if true (default: false)
 * redirect: 'noredirect'   TODO
 * promote: true            if a route has children and children length is 1, that children will be rendered as
 *                          root in sidebar, if promote is false, the root route is always rendered, default is false
 * meta: {
 *   roles: ['admin']       determine whether the current user is allowed to access this route by role
 *   title: 'some-title'    show in breadcrumb
 *   icon: 'svg-icon-name'
 *   breadcrumb: false      whether show in breadcrumb (default: true)
 * }
**/

export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [{
      path: '/redirect/:path*',
      component: import('@admin/views/misc/ForceRefresh.vue'),
    }],
    meta: { allowAnonymous: true },
  },

  {
    path: '/login/',
    name: 'login',
    component: () => import('@admin/views/misc/Login.vue'),
    hidden: true,
    meta: { allowAnonymous: true },
  },

  // MockMenus,
]

export const asyncRoutes = []

export const notFoundRoute = [
  { path: '*', name: 'notfound', redirect: '/404/', hidden: true, meta: { allowAnonymous: true } },
]

export const registerRoutes = (moduleRoutes) => {
  if (moduleRoutes) {
    asyncRoutes.push(...moduleRoutes)
  }
}

export default new Router({
  mode: 'hash',
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes,
})
