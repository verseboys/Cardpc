from django.utils.decorators import method_decorator

from natureself.django.account.decorators import role_required
from natureself.admin.forms import Form, panels, choices, validators
from natureself.admin.views import AdminView

from natureself.django.course.models import Course, PresentationLesson

@method_decorator(role_required(['admin']), name='dispatch')
class CourseAdminView(AdminView):
    MODEL = Course
    ORDER_BY = ['-id']
    USE_PAGINATION = True
    QUERYSET_SELECT_RELATED = [
            'owner',
            'thumbnail',
            'thumbnail__owner',
            ]

    SEARCH_FORM = Form([
        panels.TextPanel('title', search_op='icontains'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.TextPanel('title'),
        panels.RichTextPanel('introduction'),
        panels.ImageUploaderPanel('thumbnail', bucket='thumbnails'),
    ], model=MODEL, form_mode='edit')

    def get_extra_create_kwargs(self, request):
        return dict(owner=request.user)

@method_decorator(role_required(['admin']), name='dispatch')
class PresentationLessonAdminView(AdminView):
    MODEL = PresentationLesson
    ORDER_BY = ['-id']
    USE_PAGINATION = True
    QUERYSET_SELECT_RELATED = [
            'course',
            'course__owner',
            'course__thumbnail',
            'course__thumbnail__owner',
            'teacher_picture',
            'teacher_picture__owner',
            'presentation',
            'presentation__owner',
            'presentation__thumbnail',
            'presentation__thumbnail__owner',
            ]
    QUERYSET_PREFETCH_RELATED = [
            'attachments',
            'presentation__slides',
            ]

    SEARCH_FORM = Form([
        panels.TextPanel('title', search_op='icontains'),
        panels.SelectPanel('status'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.DividerPanel('基本信息'),
        panels.SelectPanel('course', choices=choices.ApiChoices('api-course-courses', label_field='title')),
        panels.TextPanel('title', validators=[validators.TextLengthValidator(max=30)]),
        panels.RichTextPanel('summary'),
        panels.SelectPanel('status'),
        panels.SelectPanel('presentation', choices=choices.ApiChoices('api-media-presentations', label_field='title')),
        # TODO implement attachments (ManyToManyField Chooser)
        panels.DividerPanel('讲者信息'),
        panels.TextPanel('teacher_name', required=False),
        panels.TextPanel('teacher_organization', required=False),
        panels.ImageUploaderPanel('teacher_picture', bucket='thumbnails', required=False),
        panels.RichTextPanel('teacher_introduction', required=False),
    ], model=MODEL, form_mode='edit')
