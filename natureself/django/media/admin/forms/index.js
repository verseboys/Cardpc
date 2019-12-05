import { registerPanelComponent } from '@admin/forms/panels.js'

import SlidesUploaderPanel from './SlidesUploaderPanel.vue'
import TimeSliderPanel from './TimeSliderPanel.vue'

registerPanelComponent('slides-uploader', SlidesUploaderPanel)
registerPanelComponent('time-slider', TimeSliderPanel)
