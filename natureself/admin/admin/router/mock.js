import Layout from '@admin/views/layout/index.vue'
const NotImplemented = () => import('@admin/views/misc/NotImplemented.vue')

export default {
  path: '/mock',
  component: Layout,
  meta: { title: 'Mock Menu', icon: 'user' },
  redirect: '/mock/1/1',
  children: [
    {
      path: '1',
      name: 'menu-1',
      component: NotImplemented,
      meta: { title: 'Menu 1', icon: 'user' },
      children: [
        {
          path: '1',
          name: 'menu-1-1',
          component: NotImplemented,
          meta: { title: 'Menu 1-1', icon: 'user' },
        },
        {
          path: '2',
          component: NotImplemented,
          meta: { title: 'Menu 1-2', icon: 'user' },
        },
      ],
    },
    {
      path: '2',
      component: NotImplemented,
      meta: { title: 'Menu 2' },
      children: [
        {
          path: '1',
          component: NotImplemented,
          meta: { title: 'Menu 2-1', icon: 'user' },
        },
        {
          path: '2',
          component: NotImplemented,
          meta: { title: 'Menu 2-2', icon: 'user' },
        },
      ],
    },
    {
      path: '3',
      component: NotImplemented,
      meta: { title: 'Menu 3' },
      children: [
        {
          path: '1',
          component: NotImplemented,
          meta: { title: 'Menu 3-1', icon: 'user' },
          children: [
            {
              path: '1',
              component: NotImplemented,
              meta: { title: 'Menu 3-1-1', icon: 'user' },
              children: [
                {
                  path: '1',
                  component: NotImplemented,
                  meta: { title: 'Menu 3-1-1-1', icon: 'user' },
                },
                {
                  path: '2',
                  component: NotImplemented,
                  meta: { title: 'Menu 3-1-1-2', icon: 'user' },
                },
                {
                  path: '3',
                  component: NotImplemented,
                  meta: { title: 'Menu 3-1-1-3', icon: 'user' },
                },
              ],
            },
            {
              path: '2',
              component: NotImplemented,
              meta: { title: 'Menu 3-1-2', icon: 'user' },
            },
            {
              path: '3',
              component: NotImplemented,
              meta: { title: 'Menu 3-1-3', icon: 'user' },
            },
          ],
        },
        {
          path: '2',
          component: NotImplemented,
          meta: { title: 'Menu 3-2', icon: 'user' },
        },
      ],
    },
  ],
}
