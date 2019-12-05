from django.views import View
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property

from natureself.django.account.decorators import role_required
from natureself.django.core import api
from natureself.django.core.utils import get_pagination
from natureself.admin.forms import Form, panels
from natureself.admin.views import AdminView

from natureself.django.media.models import Image, Document, Slide, Presentation, PolyvVideo
from natureself.django.media.panels import SlidesUploaderPanel, TimeSliderPanel

@method_decorator(role_required(['admin']), name='dispatch')
class AbstractFileView(View):
    Model = None

    def __init__(self, *args, **kwargs):
        if not self.Model:
            raise Exception(f'"Model" is not configured on class {self.__class__}')
        super().__init__(*args, **kwargs)

    def get(self, request, id=None):
        if id is not None:
            return get_file(request, self.Model, id)
        else:
            return list_file(request, self.Model)

    def post(self, request, id=None):
        if id is not None:
            return api.invalid_endpoint()
        else:
            return create_file(request, self.Model)

    def delete(self, request, id=None):
        if id is not None:
            return delete_file(request, self.Model, id)
        else:
            return api.invalid_endpoint()

    def patch(self, request, id=None):
        if id is not None:
            return patch_file(request, self.Model, id)
        else:
            return api.invalid_endpoint()

class ImageView(AbstractFileView):
    Model = Image

class DocumentView(AbstractFileView):
    Model = Document

class SlideView(AbstractFileView):
    Model = Slide

"""
获取所有图片/文件列表，支持分页

GET /api/admin/media/images
GET /api/admin/media/documents

Query: (所有参数都可选)
  * owner: int，用户 id，筛选指定用户上传的文件
  * filename: string，搜索文件名（大小写不敏感、包含式）
  * size_lt, size_gt: int，筛选尺寸小于/大于指定值的文件
  * bucket: string, 搜索指定 bucket 的文件（大小写敏感，完全匹配）
  * order_by: size/-size, id/-id, 默认为 -id
  * page, page_size: 分页参数
"""
def list_file(request, Model):
    queryset = Model.objects.filter(deleted_at__isnull=True)

    if 'owner' in request.GET:
        queryset = queryset.filter(owner_id=request.GET['owner'])

    if 'filename' in request.GET:
        queryset = queryset.filter(filename__icontains=request.GET['filename'])

    if 'size_lt' in request.GET:
        queryset = queryset.filter(size__lt=request.GET['size_lt'])

    if 'size_gt' in request.GET:
        queryset = queryset.filter(size__gt=request.GET['size_gt'])

    if 'bucket' in request.GET:
        queryset = queryset.filter(bucket=request.GET['bucket'])

    order_by = request.GET.get('order_by', '-id')
    if order_by not in ['size', '-size', 'id', '-id']:
        order_by = '-id'
    queryset = queryset.order_by(order_by)

    page, paginator, pagination = get_pagination(request, queryset)
    return api.ok(data=[file.serialize(request=request) for file in page], pagination=pagination)

"""
获取指定的图片/文件

GET /api/admin/media/images/<int:id>
GET /api/admin/media/documents/<int:id>
Return:
    * 如果图片/文件存在，则返回该图片/文件
    * 否则返回404
"""
def get_file(request, Model, id):
    try:
        file = Model.objects.filter(deleted_at__isnull=True).get(id=id)
        return api.ok(data=file.serialize(request=request))
    except Model.DoesNotExist:
        return api.not_found()

"""
创建文件
**注意** 该请求的 body 不使用 json，而是使用 x-www-form-urlencoded 格式（以方便前端上传文件）

POST /api/admin/media/images
POST /api/admin/media/documents

Body(x-www-form-urlencoded):
    * bucket: string，表示上传到哪一个目录中，理论上可以随意指定，但我们尽量按用途来区分
    * 可以上传单个或多个文件

Return:
    如果没有提供 bucket 或者 bucket 非法，则返回 400
    否则，正确上传文件后，返回 200，data 是一个数组，每一个元素是一个 Image/Document 对象，
          如果只上传一个文件，返回的也是数组（只有一个元素）。
"""
def create_file(request, Model):
    bucket = request.POST.get('bucket')
    if not bucket:
        return api.bad_request(message=f'无效的 "bucket": {bucket}')

    if not request.FILES:
        return api.bad_request(message=f'没有上传文件')

    files = []
    for file in request.FILES.values():
        files.append(Model.objects.create(bucket, file, owner=request.user))

    return api.ok(data=[file.serialize(request=request) for file in files])

"""
修改文件（只能修改文件名和title）

PATCH /api/admin/media/images/<int:id>
PATCH /api/admin/media/documents/<int:id>

Body:
    * filename: string, 在下载文件时显示的文件名
    * title: string

Return:
    * 如果指定的文件不存在，返回 404
    * 如果没有提供 filename 参数，或者 filename 参数有误，返回 400
    * 否则返回 200，内容会更新后的图片/文件
"""
def patch_file(request, Model, id):
    try:
        file = Model.objects.filter(deleted_at__isnull=True).get(id=id)
    except Model.DoesNotExist:
        return api.not_found()

    update_fields = []

    for field in ['filename', 'title']:
        if field in request.json:
            value = request.json[field]
            if not value:
                return api.bad_request(message=f'无效的 {field}: {value}')
            update_fields.append(field)
            setattr(file, field, value)

    file.save(update_fields=update_fields)

    return api.ok(data=file, message='文件修改成功')

"""
删除文件

DELETE /api/admin/media/images/<int:id>
DELETE /api/admin/media/documents/<int:id>

Return:
    * 如果文件不存在，返回 404
    * 如果存在，并且成功删除，返回 200，data 为文件被删除前的值
    * 如果存在，但删除失败（可能有其他资源引用时做了保护），返回 400
"""
def delete_file(request, Model, id):
    try:
        file = Model.objects.filter(deleted_at__isnull=True).get(id=id)
        file.delete()
        return api.ok(data=file)
    except Model.DoesNotExist:
        return api.not_found()
    except Exception as e:
        # NOTE 可能是由于其他资源依赖该文件，而相应资源上设置了 on_delete=models.PROTECT
        # 由于该请求仅在管理后台使用，所以可以直接把 exception 输出
        return api.bad_request(message=f'删除失败：{e}')

@method_decorator(role_required(['admin']), name='dispatch')
class PresentationAdminView(AdminView):
    MODEL = Presentation
    ORDER_BY = ['-id']
    USE_PAGINATION = True
    QUERYSET_SELECT_RELATED = [
            'owner',
            'thumbnail',
            'thumbnail__owner',
            ]
    QUERYSET_PREFETCH_RELATED = ['slides']

    SEARCH_FORM = Form([
        panels.TextPanel('title', search_op='icontains')
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.TextPanel('title'),
        TimeSliderPanel('min_watch_seconds'),
        panels.ImageUploaderPanel('thumbnail', bucket='thumbnails'),
        SlidesUploaderPanel('slides'),
    ], model=MODEL, form_mode='edit')

    def get_extra_create_kwargs(self, request):
        return dict(owner=request.user)

    def set_slides(self, presentation, slide_ids):
        # 对于PPT的图片，我们做如下处理：
        # * 获取当前所有的图片（对于 create 来说，应该是空的）
        # * 将所有图片的 presentation 置为空，sort_order 置为 null
        # * 获取用户提交的所有图片列表
        # * 将用户提交的所有图片设置正确的 presentation 以及 sort_order
        # * 保存所有涉及到的图片的修改
        # 我们维护一个 slides_to_update 字典，key 为 slide 的 id，方便记录

        slides_to_update = list(presentation.slides.all())
        slides_to_update = { slide.id: slide for slide in slides_to_update }

        slides = list(Slide.objects.filter(id__in=slide_ids))
        for slide in slides:
            slides_to_update[slide.id] = slide

        for slide in slides_to_update.values():
            slide.presentation = None
            slide.sort_order = None

        sort_order = 1
        for slide_id in slide_ids:
            # TODO if slide_id does not exist, it means the frontend passed in a non-exist slide id
            slide = slides_to_update[slide_id]
            slide.presentation = presentation
            slide.sort_order = sort_order
            sort_order += 1

        Slide.objects.bulk_update(slides_to_update.values(), ['presentation', 'sort_order'])

    def create_model(self, request):
        create_args = super().create_model(request, no_save=True)
        model = self.MODEL.objects.create(**create_args)
        self.set_slides(model, request.json.get('slides', []))
        return api.ok(data=model)

    def patch_model(self, request, pk):
        model = super().patch_model(request, pk, no_save=True)
        model.save()
        self.set_slides(model, request.json.get('slides', []))
        return api.ok(data=model)

class PolyvVideoAdminView(AdminView):
    MODEL = PolyvVideo
    ORDER_BY = ['-id']
    USE_PAGINATION = True
    QUERYSET_SELECT_RELATED = [
        'owner',
        'thumbnail',
        'thumbnail__owner',
    ]

    SEARCH_FORM = Form([
        panels.TextPanel('title', search_op='icontains'),
        panels.TextPanel('vid'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.TextPanel('title'),
        panels.TextPanel('vid'),
        panels.TextPanel('duration'),
        panels.SwitchPanel('login_required'),
        panels.ImageUploaderPanel('thumbnail', bucket='thumbnails'),
    ], model=MODEL, form_mode='edit')

    def get_extra_create_kwargs(self, request):
        return dict(owner=request.user)
