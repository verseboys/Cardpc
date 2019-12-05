import Layout from '@admin/views/layout/index.vue'
const roles = ['admin']

export default [
  {
    path: '/course',
    name: 'course',
    component: Layout,
    meta: { title: '课程管理', roles, icon: '课程管理' },
    children: [
      {
        path: 'course',
        name: 'course-course',
        component: () => import('./views/CourseList.vue'),
        meta: { title: '课程管理', roles, icon: '课程' },
      },
      {
        path: 'course/new',
        name: 'course-course-new',
        hidden: true,
        component: () => import('./views/CourseEdit.vue'),
        props: { mode: 'new' },
        meta: { title: '新建课程', roles },
      },
      {
        path: 'course/edit/:id',
        name: 'course-course-edit',
        hidden: true,
        component: () => import('./views/CourseEdit.vue'),
        props: { mode: 'edit' },
        meta: { title: '编辑课程', roles },
      },
      {
        path: 'presentation',
        name: 'course-presentation',
        component: () => import('./views/PresentationList.vue'),
        meta: { title: 'PPT课管理', roles, icon: 'PPT' },
      },
      {
        path: 'presentation/new',
        name: 'course-presentation-new',
        hidden: true,
        component: () => import('./views/PresentationEdit.vue'),
        props: { mode: 'new' },
        meta: { title: '新建PPT课', roles },
      },
      {
        path: 'presentation/edit/:id',
        name: 'course-presentation-edit',
        hidden: true,
        component: () => import('./views/PresentationEdit.vue'),
        props: { mode: 'edit' },
        meta: { title: '编辑PPT课', roles },
      },
      {
        path: 'video',
        name: 'course-video',
        // 由于还没有实现，暂时隐藏
        hidden: true,
        component: () => import('./views/VideoList.vue'),
        meta: { title: '视频课管理', roles, icon: '视频课' },
      },
      {
        path: 'video/new',
        name: 'course-video-new',
        hidden: true,
        component: () => import('./views/VideoEdit.vue'),
        props: { mode: 'new' },
        meta: { title: '新建视频课', roles },
      },
      {
        path: 'video/edit/:id',
        name: 'course-video-edit',
        hidden: true,
        component: () => import('./views/VideoEdit.vue'),
        props: { mode: 'edit' },
        meta: { title: '编辑视频课', roles },
      },
    ],
  },
]
