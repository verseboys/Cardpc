from django.db.models import Q

from natureself.admin.forms import panels

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class UserSearchPanel(panels.TextPanel):
    def __init__(self, *args, **kwargs):
        # 由于 user 是一个外键，form_field_property 会被自动设置为 id 而非空
        # 这会导致前端不返回数据
        kwargs['form_field_property'] = None
        if 'placeholder' not in kwargs:
            kwargs['placeholder'] = '用户名/手机号/邮箱/id'
        return super().__init__(*args, **kwargs)

    def get_filter_kwargs(self, request):
        value = self.get_querystring_value(request)
        if value:
            condition = Q(**{f'{self.field_name}__username__icontains': value}) \
                    | Q(**{f'{self.field_name}__phone__icontains': value}) \
                    | Q(**{f'{self.field_name}__email__icontains': value})
            # https://sentry.evahealth.net/ns/cardpc/issues/749/events/28461/
            # 只有当 value 是 int 时，才能添加 Q(id=xx)
            if is_int(value):
                condition |= Q(**{f'{self.field_name}__id': value})
            return condition
        else:
            return None

class ProjectThemeColorPickerPanel(panels.Panel):
    TYPE = 'project-theme-color-picker'

class ProjectGalleryEditorPanel(panels.Panel):
    TYPE = 'project-gallery-editor'
    DEFAULT_OPTIONS = {
            'accept': 'image/png, image/jpeg',
            }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', '花絮图片')
        kwargs.setdefault('help_text', '')
        kwargs.setdefault('default_value', None)
        super().__init__(*args, **kwargs)

    def get_edit_kwargs(self, request):
        # don't let AdminView process this automatically
        return None

class ProjectCarouselEditorPanel(panels.Panel):
    TYPE = 'project-carousel-editor'
    DEFAULT_OPTIONS = {
            'accept': 'image/png, image/jpeg',
            }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', '轮播图')
        kwargs.setdefault('help_text', '')
        kwargs.setdefault('default_value', None)
        super().__init__(*args, **kwargs)

    def get_edit_kwargs(self, request):
        # don't let AdminView process this automatically
        return None

class ProjectPageAttachmentPanel(panels.Panel):
    TYPE = 'project-page-attachment'
    REQUIRED_OPTION_NAMES = ['bucket']
    DEFAULT_OPTIONS = {
            # 默认 20M
            'size_limit': 1024*1024*20,
            }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', '附件')
        kwargs.setdefault('help_text', '')
        kwargs.setdefault('default_value', None)
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def get_edit_kwargs(self, request):
        # don't let AdminView process this automatically
        return None
