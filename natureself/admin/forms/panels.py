from django.apps import apps

from natureself.django.core.utils import get_boolean_query, get_datetime_query, get_datetime_range_query, parse_datetime
from .choices import TupleChoices
from .validators import RequiredValidator, TextLengthValidator

import re
from collections import namedtuple

class Panel:
    TYPE = None

    # 序列化时提供的默认 options 的值
    DEFAULT_OPTIONS = {}
    # 必须提供的配置项，在初始化 panel 时，如果没有提供，会报错，阻止程序启动
    REQUIRED_OPTION_NAMES = []

    # 是否为数据型 Panel
    DATA_PANEL = True

    def __init__(self,
            field_name = None,
            form_field_name = None,
            form_field_property = 'AUTO',
            required = None,
            disabled = False,
            disabled_on_search = 'AUTO',
            disabled_on_new = 'AUTO',
            disabled_on_edit = 'AUTO',
            hide_on_new = False,
            hide_on_edit = False,
            choices = None,
            validators = None,
            search_op = None,
            form_mode = 'edit',
            model = None,
            **kwargs,
            ):
        if not self.TYPE:
            raise Exception(f'You should not use Panel directly, use a specific class')

        self.model = model
        self.form_mode = form_mode
        self.field_name = field_name
        self.form_field_name = form_field_name or field_name
        self.form_field_property = form_field_property
        self.required = required
        self.disabled = disabled
        self.disabled_on_search = disabled_on_search
        self.disabled_on_edit = disabled_on_edit
        self.disabled_on_new = disabled_on_new
        self.hide_on_new = hide_on_new
        self.hide_on_edit = hide_on_edit
        self.choices = choices
        self.search_op = search_op
        self._init_kwargs = kwargs
        self._validators = validators

        for opt_name in self.REQUIRED_OPTION_NAMES:
            if opt_name not in self._init_kwargs:
                raise ValueError(f'Missing required option: {opt_name}')

    @property
    def model(self):
        return getattr(self, '_model', None)

    @model.setter
    def model(self, value):
        if isinstance(value, str):
            self._model = apps.get_model(*value.split('.'))
        else:
           self._model = value

        for panel in getattr(self, 'children', []):
            panel.model = self._model

    @property
    def field(self):
        if getattr(self, 'model', None) and getattr(self, 'field_name', None):
            return self.model._meta.get_field(self.field_name)
        return None

    @property
    def form_mode(self):
        return getattr(self, '_form_mode', 'edit')

    @form_mode.setter
    def form_mode(self, value):
        self._form_mode = value

        for panel in getattr(self, 'children', []):
            panel.form_mode = self._form_mode

    @property
    def required(self):
        if hasattr(self, '_required') and self._required is not None:
            return self._required

        if self.form_mode == 'search':
            return False

        if self.field and not self.field.null and not self.field.blank:
            return True

        return False

    @property
    def form_field_property(self):
        if hasattr(self, '_form_field_property'):
            return self._form_field_property

        if not self.field:
            return None

        if self.field.many_to_one:
            # ForeignKey
            return 'id'
        elif self.field.many_to_many:
            # ManyToManyField
            return 'id'
        elif self.field.one_to_many:
            # target of ForeignKey
            return 'id'
        elif self.field.one_to_one:
            # OneToOneField
            return 'id'

        return None

    @form_field_property.setter
    def form_field_property(self, value):
        if value != 'AUTO':
            self._form_field_property = value

    @property
    def disabled_on_search(self):
        if hasattr(self, '_disabled_on_search'):
            return self._disabled_on_search

        return self.disabled

    @disabled_on_search.setter
    def disabled_on_search(self, value):
        if value != 'AUTO':
            self._disabled_on_search = value

    @property
    def disabled_on_new(self):
        if hasattr(self, '_disabled_on_new'):
            return self._disabled_on_new

        return self.disabled

    @disabled_on_new.setter
    def disabled_on_new(self, value):
        if value != 'AUTO':
            self._disabled_on_new = value

    @property
    def disabled_on_edit(self):
        if hasattr(self, '_disabled_on_edit'):
            return self._disabled_on_edit

        return self.disabled

    @disabled_on_edit.setter
    def disabled_on_edit(self, value):
        if value != 'AUTO':
            self._disabled_on_edit = value

    @property
    def many_field(self):
        return self.field and (self.field.one_to_many or self.field.many_to_many)

    @required.setter
    def required(self, value):
        self._required = value

    @property
    def options(self):
        opts = {**self.DEFAULT_OPTIONS, **self._init_kwargs}
        if 'label' not in opts:
            opts['label'] = self.field.verbose_name if self.field else ''
        if 'help_text' not in opts:
            opts['help_text'] = self.field.help_text if self.field else ''
        if 'default_value' not in opts:
            if self.form_mode == 'search':
                opts['default_value'] = None
            else:
                opts['default_value'] = self.field.get_default() if self.field else None
        if self.choices:
            opts['choices'] = self.choices.serialize()
        elif self.field and hasattr(self.field, 'choices') and self.field.choices:
            opts['choices'] = TupleChoices(self.field.get_choices()).serialize()

        return opts

    @property
    def validators(self):
        vlds = []
        if self._validators:
            vlds.extend(self._validators)

        if self.required:
            vlds.append(RequiredValidator())

        return vlds

    @property
    def data_panels(self):
        if self.DATA_PANEL:
            yield self
        else:
            for panel in self.children:
                yield from panel.data_panels

    def serialize(self):
        data = dict(
                object = 'panel',
                data_panel = self.DATA_PANEL,
                type = self.TYPE,
                field_name = self.field_name,
                form_field_name = self.form_field_name,
                form_field_property = self.form_field_property,
                required = self.required,
                disabled = self.disabled,
                disabled_on_new = self.disabled_on_new,
                disabled_on_edit = self.disabled_on_edit,
                disabled_on_search = self.disabled_on_search,
                hide_on_new = self.hide_on_new,
                hide_on_edit = self.hide_on_edit,
                options = self.options,
                many_field = self.many_field,
                validators = [vld.serialize() for vld in self.validators],
                )
        return data

    def get_querystring_value(self, request):
        return request.GET.get(self.form_field_name, None)

    def get_filter_kwargs(self, request):
        if not self.field:
            return None
        value = self.get_querystring_value(request)
        search_name = f'{self.field_name}__{self.search_op}' if self.search_op else self.field_name
        return { search_name: value } if value else None

    def get_edit_kwargs(self, request):
        if not self.field:
            return None
        # TODO consider ManyToManyField
        if self.form_field_name not in request.json:
            return None
        value = request.json[self.form_field_name]
        return {
                self.field.get_attname(): value,
                }

Tab = namedtuple('Tab', ['title', 'panels'])

class TabPanel(Panel):
    TYPE = 'tab'
    DATA_PANEL = False

    def __init__(self, tabs, *args, **kwargs):
        """
        panels = TabPanel(tabs=[
            Tab(title='first', panels=[
                TextPanel(...),
                TextPanel(...),
            ]),
            Tab(title='second', panels=[
                TextPanel(...),
                TextPanel(...),
            ]),
        ])
        """
        self.tabs = []
        for tab in tabs:
            if isinstance(tab.panels, Panel):
                self.tabs.append(Tab(title=tab.title, panels=[tab.panels]))
            else:
                self.tabs.append(tab)
        super().__init__(*args, **kwargs)

    @property
    def children(self):
        ret = []
        for tab in self.tabs:
            ret.extend(tab.panels)
        return ret

    def serialize(self):
        data = dict(
                object = 'panel',
                data_panel = False,
                type = self.TYPE,
                tabs = [
                    { 'title': tab.title, 'panels': [panel.serialize() for panel in tab.panels] } \
                    for tab in self.tabs
                    ],
                )
        return data

class InlinePanel(Panel):
    TYPE = 'inline'
    DATA_PANEL = False

    def __init__(self, panels, *args, **kwargs):
        if isinstance(panels, Panel):
            self.panels = [panels]
        elif panels:
            self.panels = panels
        else:
            self.panels = []
        super().__init__(*args, **kwargs)

    @property
    def children(self):
        return self.panels

    def serialize(self):
        data = dict(
                object = 'panel',
                data_panel = False,
                type = self.TYPE,
                panels = [ panel.serialize() for panel in self.panels ]
                )
        return data

class DividerPanel(Panel):
    TYPE = 'divider'
    DATA_PANEL = False

    def __init__(self, title, *args, **kwargs):
        self.title = title
        super().__init__(*args, **kwargs)

    @property
    def children(self):
        return []

    def serialize(self):
        data = dict(
                object = 'panel',
                data_panel = False,
                type = self.TYPE,
                title = self.title,
                panels = [],
                )
        return data

class TextPanel(Panel):
    TYPE = 'text'

class RichTextPanel(Panel):
    TYPE = 'richtext'

class SwitchPanel(Panel):
    TYPE = 'switch'

    def get_querystring_value(self, request):
        return get_boolean_query(request, self.form_field_name, None)

class DropdownPanel(Panel):
    TYPE = 'dropdown'

class SelectPanel(Panel):
    TYPE = 'select'

class _DateTimePickerBase(Panel):
    """
    Base class for datetime related panels
    """
    # set TYPE to None to prevent user directly use this base class
    TYPE = None

    # python time format: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    # element-ui time format: https://element.eleme.cn/#/zh-CN/component/date-picker#ri-qi-ge-shi
    PY_TO_ELEMENTUI_MAPPING = {
            '%Y': 'yyyy',
            '%m': 'MM',
            '%d': 'dd',
            '%H': 'HH',
            '%M': 'mm',
            '%S': 'ss',
            }
    PY_FMT_PATTERN = re.compile(r'(?P<fmt>%.)')
    def _to_elementui_format(self, py_format):
        return self.PY_FMT_PATTERN.sub(lambda m: self.PY_TO_ELEMENTUI_MAPPING[m.group('fmt')], py_format)

    def __init__(self, *args, **kwargs):
        self.datetime_format = kwargs.pop('datetime_format', self.DEFAULT_DATETIME_FORMAT)
        super().__init__(*args, **kwargs)

    @property
    def options(self):
        opts = super().options
        opts['datetime_format'] = self._to_elementui_format(self.datetime_format)
        return opts

    def get_querystring_value(self, request):
        if not self.field:
            return None
        return get_datetime_query(request, self.form_field_name, format=self.datetime_format)

    def get_edit_kwargs(self, request):
        if not self.field:
            return None
        if self.form_field_name not in request.json:
            return None
        value = request.json[self.form_field_name]
        value = parse_datetime(value, format=self.datetime_format, raise_value_error=True)
        return {
                self.field.get_attname(): value,
                }

class _DateTimeRangeBase(_DateTimePickerBase):
    ALIGN_DATE = False

    def __init__(self, *args, **kwargs):
        self.align_date = kwargs.pop('align_date', self.ALIGN_DATE)
        super().__init__(*args, **kwargs)

    def get_querystring_value(self, request):
        if not self.field:
            return None
        return get_datetime_range_query(request, self.form_field_name, format=self.datetime_format, align_date=self.align_date)

    def get_filter_kwargs(self, request):
        if not self.field:
            return None
        start, end = self.get_querystring_value(request)
        kwargs = {}
        if start:
            kwargs[f'{self.field_name}__gte'] = start
        if end:
            kwargs[f'{self.field_name}__lte'] = end
        return kwargs

class DateTimePickerPanel(_DateTimePickerBase):
    TYPE = 'datetime-picker'
    DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class TimePickerPanel(_DateTimePickerBase):
    TYPE = 'time-picker'
    DEFAULT_DATETIME_FORMAT = '%H:%M:%S'

class DatePickerPanel(_DateTimePickerBase):
    TYPE = 'date-picker'
    DEFAULT_DATETIME_FORMAT = '%Y-%m-%d'

class DateTimeRangePanel(_DateTimeRangeBase):
    TYPE = 'datetime-range'
    DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    ALIGN_DATE = False

class TimeRangePanel(_DateTimeRangeBase):
    TYPE = 'time-range'
    DEFAULT_DATETIME_FORMAT = '%H:%M:%S'
    ALIGN_DATE = False

class DateRangePanel(_DateTimeRangeBase):
    TYPE = 'date-range'
    DEFAULT_DATETIME_FORMAT = '%Y-%m-%d'
    ALIGN_DATE = True

class ImageChooserPanel(Panel):
    TYPE = 'image-chooser'
    REQUIRED_OPTION_NAMES = ['bucket']
    DEFAULT_OPTIONS = {
            'accept': 'image/png, image/jpeg',
            }

class ImageUploaderPanel(Panel):
    TYPE = 'image-uploader'
    REQUIRED_OPTION_NAMES = ['bucket']
    DEFAULT_OPTIONS = {
            'accept': 'image/png, image/jpeg',
            # 默认 5M
            'size_limit': 1024*1024*5,
            }

class DocumentUploaderPanel(Panel):
    TYPE = 'document-uploader'
    REQUIRED_OPTION_NAMES = ['bucket']
    DEFAULT_OPTIONS = {
            'accept': '*',
            # 默认 20M
            'size_limit': 1024*1024*20,
            }
