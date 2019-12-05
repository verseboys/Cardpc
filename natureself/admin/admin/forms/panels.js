import TextPanel from './TextPanel.vue'
import SwitchPanel from './SwitchPanel.vue'
import SelectPanel from './SelectPanel.vue'
import DateRangePanel from './DateRangePanel.vue'
import DateTimePickerPanel from './DateTimePickerPanel.vue'
import ImageUploaderPanel from './ImageUploaderPanel.vue'
import DocumentUploaderPanel from './DocumentUploaderPanel.vue'
const RichTextPanel = () => import('./RichTextPanel.vue')

export const components = {
  'ns-panel-text': TextPanel,
  'ns-panel-richtext': RichTextPanel,
  'ns-panel-switch': SwitchPanel,
  'ns-panel-select': SelectPanel,
  'ns-panel-date-range': DateRangePanel,
  'ns-panel-datetime-picker': DateTimePickerPanel,
  'ns-panel-image-uploader': ImageUploaderPanel,
  'ns-panel-document-uploader': DocumentUploaderPanel,
}

export const registerPanelComponent = (name, component) => {
  components[`ns-panel-${name}`] = component
}
