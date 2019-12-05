from django.views import View
from django.db.models import Q
from django.urls import path, include
from django.utils.functional import cached_property

from natureself.django.core import api
from natureself.django.core.utils import get_pagination
from .forms import Form, panels

class AdminView(View):
    """
    提供基础的 CRUD 操作

    GET /api/admin/{model}                -> 获取资源列表
    GET /api/admin/{model}/panels/search  -> 获取新建/编辑表单定义
    GET /api/admin/{model}/panels/edit    -> 获取新建/编辑表单定义
    GET /api/admin/{model}/<int:id>       -> 获取单个资源
    POST /api/admin/{model}               -> 创建新资源
    PUT /api/admin/{model}/<int:id>       -> 更新单个资源
    PATCH /api/admin/{model}/<int:id>     -> 更新单个资源
    DELETE /api/admin/{model}/<int:id>    -> 删除单个资源
    """

    # CRUD 所操作的 model 类
    MODEL = None
    # list 请求中用于排序的字段
    ORDER_BY = ['-id']
    # list 请求是否需要分页
    USE_PAGINATION = True

    QUERYSET_SELECT_RELATED = None
    QUERYSET_PREFETCH_RELATED = None

    SEARCH_FORM = Form()
    EDIT_FORM = Form()

    GET_METHOD = 'get_model'
    LIST_METHOD = 'list_model'
    CREATE_METHOD = 'create_model'
    UPDATE_METHOD = None
    PATCH_METHOD = 'patch_model'
    DELETE_METHOD = 'delete_model'

    def get_queryset(self, request=None):
        queryset = self.MODEL.objects.all()

        if self.ORDER_BY:
            queryset = queryset.order_by(*self.ORDER_BY)

        if self.QUERYSET_SELECT_RELATED:
            queryset = queryset.select_related(*self.QUERYSET_SELECT_RELATED)

        if self.QUERYSET_PREFETCH_RELATED:
            queryset = queryset.prefetch_related(*self.QUERYSET_PREFETCH_RELATED)

        return queryset

    def get_search_panels(self):
        for panel in self.SEARCH_FORM.data_panels:
            yield panel

    def get_edit_panels(self, request=None):
        for panel in self.EDIT_FORM.data_panels:
            yield panel

    @cached_property
    def forms(self):
        return dict(search=self.SEARCH_FORM, edit=self.EDIT_FORM)

    # ---------- 8< ----------
    # 以下代码可以重载，也可以通过 xx_METHOD 来指定自己实现的函数名
    # ---------- 8< ----------
    def get_serialize_kwargs(self, request):
        """
        在调用 serialize() 时，会通过该函数来获取 serialize() 的参数
        """
        return {}

    def get_extra_create_kwargs(self, request):
        """
        在 create_model() 中，会调用该函数来获取更多的自定义参数，例如设置 owner
        """
        return {}

    def get_model(self, request, pk):
        """
        GET /api/admin/.../{model}/<pk>
        """
        try:
            model = self.get_queryset(request).get(pk=pk)
            return api.ok(data=model.serialize(**self.get_serialize_kwargs(request)))
        except self.MODEL.DoesNotExist:
            return api.not_found()

    def list_model(self, request):
        """
        GET /api/admin/.../{model}
        """
        queryset = self.get_queryset(request)

        for panel in self.get_search_panels():
            kwargs = panel.get_filter_kwargs(request)
            if kwargs:
                if isinstance(kwargs, Q):
                    queryset = queryset.filter(kwargs)
                else:
                    queryset = queryset.filter(**kwargs)

        if self.USE_PAGINATION:
            page, paginator, pagination = get_pagination(request, queryset)
            return api.ok(data=[model.serialize(**self.get_serialize_kwargs(request)) for model in page], pagination=pagination)
        else:
            return api.ok(data=[model.serialize(**self.get_serialize_kwargs(request)) for model in queryset])

    def create_model(self, request, no_save=False):
        """
        POST /api/admin/.../{model}
        """
        create_args = {}
        for panel in self.get_edit_panels(request):
            kwargs = panel.get_edit_kwargs(request)
            if kwargs:
                create_args.update(kwargs)

        extra_kwargs = self.get_extra_create_kwargs(request)
        if extra_kwargs:
            create_args.update(extra_kwargs)

        if no_save:
            return create_args
        else:
            model = self.MODEL.objects.create(**create_args)
            return api.ok(data=model.serialize(**self.get_serialize_kwargs(request)))

    def delete_model(self, request, pk):
        """
        DELETE /api/admin/.../{model}/<pk>
        """
        try:
            model = self.get_queryset(request).get(pk=pk)
            # 在删除前序列化。在 multitable-inheritance 的场景中，
            # 删除资源后会导致无法序列化（父类关联的子类已经被删除）。
            data = model.serialize(**self.get_serialize_kwargs(request))
            model.delete()
            return api.ok(data=data)
        except self.MODEL.DoesNotExist:
            return api.not_found()

    def patch_model(self, request, pk, no_save=False):
        """
        PATCH /adpi/admin/.../{model}/<pk>
        """
        try:
            model = self.get_queryset(request).get(pk=pk)
        except self.MODEL.DoesNotExist:
            return api.not_found()

        update_fields = []
        for panel in self.get_edit_panels(request):
            kwargs = panel.get_edit_kwargs(request)
            if kwargs:
                for key, value in kwargs.items():
                    setattr(model, key, value)
                    update_fields.append(key)

        if not update_fields:
            return api.bad_request(message='No field to update')

        if hasattr(model, 'updated_at'):
            update_fields.append('updated_at')

        if no_save:
            return model
        else:
            model.save()
            return api.ok(data=model.serialize(**self.get_serialize_kwargs(request)))

    # ---------- 8< ----------
    # 以下代码不建议重载
    # ---------- 8< ----------

    @classmethod
    def urls(cls, base, app):
        return [
            path(f'{base}', cls.as_view(), name=f'{app}-{base}'),
            path(f'{base}/<int:pk>', cls.as_view(), name=f'{app}-{base}-single'),
            path(f'{base}/forms/<str:form_name>', cls.as_view(), name=f'{app}-{base}-forms'),
        ]

    def get(self, request, pk=None, form_name=None):
        if form_name is not None:
            if form_name in self.forms:
                return api.ok(data=self.forms[form_name].serialize())
            else:
                return api.not_found()
        if pk is not None:
            return self._get_method(request, pk)
        else:
            return self._list_method(request)

    def post(self, request, pk=None):
        if pk is not None:
            return api.invalid_endpoint()
        return self._create_method(request)

    def delete(self, request, pk=None):
        if pk is not None:
            return self._delete_method(request, pk)
        else:
            return api.invalid_endpoint()

    def patch(self, request, pk=None):
        if pk is not None:
            return self._patch_method(request, pk)
        else:
            return api.invalid_endpoint()

    def put(self, request, pk=None):
        if pk is not None:
            return self._update_method(request, pk)
        else:
            return api.invalid_endpoint()

    @classmethod
    def as_view(cls, *args, **kwargs):
        cls._get_method = getattr(cls, cls.GET_METHOD) if cls.GET_METHOD else cls._not_implemented
        cls._list_method = getattr(cls, cls.LIST_METHOD) if cls.LIST_METHOD else cls._not_implemented
        cls._create_method = getattr(cls, cls.CREATE_METHOD) if cls.CREATE_METHOD else cls._not_implemented
        cls._update_method = getattr(cls, cls.UPDATE_METHOD) if cls.UPDATE_METHOD else cls._not_implemented
        cls._patch_method = getattr(cls, cls.PATCH_METHOD) if cls.PATCH_METHOD else cls._not_implemented
        cls._delete_method = getattr(cls, cls.DELETE_METHOD) if cls.DELETE_METHOD else cls._not_implemented

        return super().as_view(*args, **kwargs)

    def _not_implemented(request, *args, **kwargs):
        return api.invalid_endpoint()
