import Layout from '@admin/views/layout/index.vue'

const roles = ['admin']

export default [
  {
    path: '/media',
    name: 'media',
    component: Layout,
    meta: { title: '媒体资源管理', roles, icon: '多媒体' },
    children: [
      {
        path: 'presentation',
        name: 'media-presentation-list',
        component: () => import('./views/PresentationList.vue'),
        meta: { title: 'PPT 管理', roles, icon: 'PPT' },
      },
      {
        path: 'presentation/new',
        name: 'media-presentation-new',
        hidden: true,
        component: () => import('./views/PresentationEdit.vue'),
        props: { mode: 'new' },
        meta: { title: '新建 PPT', roles },
      },
      {
        path: 'presentation/edit/:id',
        name: 'media-presentation-edit',
        hidden: true,
        component: () => import('./views/PresentationEdit.vue'),
        props: { mode: 'edit' },
        meta: { title: '编辑 PPT', roles },
      },
      {
        path: 'video',
        name: 'media-video-list',
        component: () => import('./views/VideoList.vue'),
        meta: { title: '视频管理', roles, icon: '视频' },
      },
      {
        path: 'video/new',
        name: 'media-video-new',
        hidden: true,
        component: () => import('./views/VideoEdit.vue'),
        props: { mode: 'new' },
        meta: { title: '新建视频', roles },
      },
      {
        path: 'video/edit/:id',
        name: 'media-video-edit',
        hidden: true,
        component: () => import('./views/VideoEdit.vue'),
        props: { mode: 'edit' },
        meta: { title: '编辑视频', roles },
      },
    ],
  },
]
