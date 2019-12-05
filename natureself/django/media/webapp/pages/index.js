import { activators, registerPageJs } from '@webapp/page.js'

registerPageJs(() => import('./presentation-player.js'), activators.elementExists('#presentation-player'))
registerPageJs(() => import('./media-share-widget.js'), activators.elementExists('#media-share-widget'))
