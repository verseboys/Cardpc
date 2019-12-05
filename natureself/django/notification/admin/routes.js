import Layout from '@admin/views/layout/index.vue'
const roles = ['admin']

export default [
  {
    path: '/notification',
    name: 'notification',
    component: Layout,
    redirect: '/notification/email',
    meta: { title: '通知管理', roles, icon: 'bell' },
    children: [
      {
        path: 'email',
        name: 'notification-email',
        component: () => import('./views/Email.vue'),
        meta: { title: '邮件管理', roles, icon: 'email' },
      },
      {
        path: 'alisms',
        name: 'notification-alisms',
        component: () => import('./views/AliSms.vue'),
        meta: { title: '短信管理', roles, icon: 'sms' },
      },
    ],
  },
]
