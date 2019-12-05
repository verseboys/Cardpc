import 'bootstrap'

import layout from './layout.js'
import './pages/index.js'
import './styles/index.scss'

import '@ns-course/webapp/index.js'
import '@ns-media/webapp/index.js'

import { runPageJs } from '@webapp/page.js'

(function () {
  runPageJs()
  layout.setupResponsiveLayoutSizes()
})()
