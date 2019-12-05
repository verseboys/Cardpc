import { registerPanelComponent } from '@admin/forms/panels.js'

import ProjectThemeColorPickerPanel from './ProjectThemeColorPickerPanel.vue'
import ProjectGalleryEditorPanel from './ProjectGalleryEditorPanel.vue'
import ProjectCarouselEditorPanel from './ProjectCarouselEditorPanel.vue'
import ProjectPageAttachmentPanel from './ProjectPageAttachmentPanel.vue'

registerPanelComponent('project-theme-color-picker', ProjectThemeColorPickerPanel)
registerPanelComponent('project-gallery-editor', ProjectGalleryEditorPanel)
registerPanelComponent('project-carousel-editor', ProjectCarouselEditorPanel)
registerPanelComponent('project-page-attachment', ProjectPageAttachmentPanel)
