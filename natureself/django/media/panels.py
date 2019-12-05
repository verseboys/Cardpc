from natureself.admin.forms import panels

class SlidesUploaderPanel(panels.Panel):
    TYPE = 'slides-uploader'
    DEFAULT_OPTIONS = {
            'accept': 'image/png, image/jpeg',
            }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', 'PPT 图片')
        kwargs.setdefault('help_text', '')
        kwargs.setdefault('default_value', None)
        super().__init__(*args, **kwargs)

    def get_edit_kwargs(self, request):
        # don't let AdminView process this automatically
        return None

class TimeSliderPanel(panels.Panel):
    TYPE = 'time-slider'
