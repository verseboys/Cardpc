import logo from '@natureself/assets/logo/cardpc.png'
import Cardpc from 'cardpc/admin/app.js'
import NatureselfDjangoAccount from '@ns-account/admin/app.js'
import NatureselfDjangoMedia from '@ns-media/admin/app.js'
import NatureselfDjangoNotification from '@ns-notification/admin/app.js'
import NatureselfDjangoCourse from '@ns-course/admin/app.js'

export default {
  apps: {
    Cardpc,

    // NatureselfCms,
    NatureselfDjangoAccount,
    NatureselfDjangoMedia,
    NatureselfDjangoCourse,
    NatureselfDjangoNotification,
  },
  logo,
  title: '联盟官网',
}
