import { activators, registerPageJs } from '@webapp/page.js'

registerPageJs(() => import('./partials/header.js'), activators.elementExists('.tab-menu'))
registerPageJs(() => import('./account/index.js'), activators.elementExists('#account-app'))
registerPageJs(() => import('./zhixiang/homepage.js'), activators.datajsContains('zhixiang-homepage'))
registerPageJs(() => import('./zhixiang/training.js'), activators.datajsContains('zhixiang-training'))
registerPageJs(() => import('./project/download.js'), activators.datajsContains('project-download'))
