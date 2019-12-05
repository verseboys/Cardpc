from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db import transaction
from django.urls import path

from natureself.django.core import api
from natureself.django.core.utils import get_boolean_query
from natureself.django.core.shortcuts import render_for_ua
from natureself.django.account.decorators import role_required
from natureself.django.media.views.admin import AbstractFileView
from natureself.django.media.models import Document
from natureself.admin.forms import Form, panels, choices
from natureself.admin.views import AdminView

from cardpc.models import Project, ProjectNavMenu, ProjectDocument, ProjectPage
from cardpc.models import ProjectHomepage, ProjectNews, ProjectNewsList
from cardpc.models import ProjectGallery, ProjectGalleryImage, ProjectRichtextPage
from cardpc.models import ProjectCarouselItem
from cardpc.panels import ProjectThemeColorPickerPanel

@require_http_methods(['GET'])
def page(request, project_slug, page_id=None):
    try:
        if page_id is None:
            page = ProjectHomepage.objects \
                    .select_related('project', 'project__banner', 'project__menu') \
                    .get(project__slug=project_slug)
        else:
            page = ProjectPage.objects \
                    .select_related('project', 'project__banner', 'project__menu') \
                    .get_subclass(project__slug=project_slug, id=page_id)
    except ProjectPage.DoesNotExist:
        return api.not_found()

    preview = get_boolean_query(request, 'preview', False)
    if page.status != page.STATUSES.published and not preview:
        return api.not_found()

    context = page.get_context(request)
    template = page.get_template(request)

    return render_for_ua(request, template, context=context)

@method_decorator(role_required(['admin']), name='dispatch')
class ProjectAdminView(AdminView):
    MODEL = Project
    QUERYSET_SELECT_RELATED = [
            'banner',
            'menu',
            'menu__link_page',
            ]
    QUERYSET_PREFETCH_RELATED = [
            'menu__children',
            'menu__children__link_page',
            ]

    SEARCH_FORM = Form([
        panels.TextPanel('title'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.TextPanel('title'),
        panels.TextPanel('slug'),
        panels.RichTextPanel('introduction'),
        panels.ImageUploaderPanel('banner', bucket='banner'),
        panels.ImageUploaderPanel('banner_background', bucket='banner'),
        ProjectThemeColorPickerPanel('theme_colors'),
    ], model=MODEL, form_mode='edit')

    @transaction.atomic
    def create_model(self, request):
        create_args = super().create_model(request, no_save=True)

        # 创建菜单
        create_args['menu'] = ProjectNavMenu.objects.create()

        project = self.MODEL.objects.create(**create_args)

        # 创建首页
        ProjectHomepage.objects.create(project=project, status=ProjectHomepage.STATUSES.published)

        return api.ok(data=project)

    @transaction.atomic
    def delete_model(self, request, pk):
        try:
            model = self.get_queryset(request).get(pk=pk)
            data = model.serialize()
            model.delete()
            # 删除关联的菜单
            model.menu.delete()
            return api.ok(data=data)
        except self.MODEL.DoesNotExist:
            return api.not_found()

    def get(self, request, pk=None, menu=None, *args, **kwargs):
        if pk and menu:
            try:
                project = self.get_queryset(request).get(pk=pk)
                return api.ok(data=project.menu)
            except self.MODEL.DoesNotExist:
                return api.not_found()
        return super().get(request, pk=pk, **kwargs)

    @classmethod
    def urls(cls, base, app):
        return super().urls(base, app) + [
            path(f'{base}/<int:pk>/menu', cls.as_view(), name=f'{app}-{base}-menu', kwargs=dict(menu=True)),
        ]

@method_decorator(role_required(['admin']), name='dispatch')
class ProjectDocumentAdminView(AdminView):
    MODEL = ProjectDocument
    QUERYSET_SELECT_RELATED = [
            'project',
            'document',
            ]

    SEARCH_FORM = Form([
        panels.SelectPanel('project', choices=choices.ApiChoices('api-project-projects', label_field='title')),
        panels.SelectPanel('tag',
            choices=choices.ApiChoices('api-project-documents-tags', value_field=None, label_field=None),
            ),
        panels.TextPanel('subject', search_op='icontains'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.SelectPanel('project', choices=choices.ApiChoices('api-project-projects', label_field='title')),
        panels.TextPanel('subject'),
        panels.TextPanel('description'),
        panels.DateTimePickerPanel('publish_time'),
        panels.SelectPanel('tag',
            choices=choices.ApiChoices('api-project-documents-tags', value_field=None, label_field=None),
            allow_create=True,
            placeholder='选择或创建新的标签',
            ),
        panels.DocumentUploaderPanel('document', bucket='project'),
    ], model=MODEL, form_mode='edit')

    def get(self, request, pk=None, form_name=None, tags=False):
        if not tags:
            return super().get(request, pk=pk, form_name=form_name)

        tags = [val['tag'] for val in self.MODEL.objects.all().distinct('tag').values('tag')]

        return api.ok(data=tags)

    @classmethod
    def urls(cls, base, app):
        return super().urls(base, app) + [
            path(f'{base}/tags', cls.as_view(), name=f'{app}-{base}-tags', kwargs=dict(tags=True)),
        ]

@method_decorator(role_required(['admin']), name='dispatch')
class ProjectPageAdminView(AdminView):
    MODEL = ProjectPage

    # API: .../forms?page_type=xxx
    # API: .../pagetypes (should contain creatable info (e.g. single instance))

    PROJECT_SELECT_PANEL = panels.SelectPanel(
            'project',
            choices=choices.ApiChoices('api-project-projects',
            label_field='title'),
            )
    PAGETYPE_SELECT_PANEL = panels.SelectPanel(
            None,
            form_field_name='pagetype',
            form_field_property='type',
            label='页面类型',
            choices=choices.ApiChoices('api-project-pages-pagetypes', label_field='name', value_field='type'),
            )

    SEARCH_FORM = Form([
        PROJECT_SELECT_PANEL,
        PAGETYPE_SELECT_PANEL,
        panels.TextPanel('page_title'),
        panels.SelectPanel('status'),
        ], model=MODEL, form_mode='search')

    def get_serialize_kwargs(self, request):
        simple = get_boolean_query(request, 'simple', False)
        return dict(simple=simple)

    def get(self, request, menu=None, pagetypes=None, form_name=None, panel=None, **kwargs):
        if pagetypes:
            project = request.GET.get('project', None)
            return api.ok(data=ProjectPage.serialize_pagetypes(project))
        if form_name == 'edit':
            pagetype = request.GET.get('pagetype')
            Page = ProjectPage.PAGE_TYPES.get(pagetype)
            if not Page:
                return api.ok(data=Form().serialize())
            form = Form(Page.get_edit_panels(), model=Page, form_mode='edit')
            return api.ok(data=form.serialize())
        if form_name == 'empty':
            return api.ok(data=Form().serialize())
        if panel:
            if panel == 'project':
                return api.ok(data=self.PROJECT_SELECT_PANEL.serialize())
            elif panel == 'pagetype':
                return api.ok(data=self.PAGETYPE_SELECT_PANEL.serialize())
            else:
                return api.not_found()
        return super().get(request, form_name=form_name, **kwargs)

    def get_queryset(self, request):
        if request.method == 'GET':
            pagetype = request.GET.get('pagetype')
        else:
            pagetype = request.json.get('pagetype')

        if pagetype:
            Page = ProjectPage.PAGE_TYPES.get(pagetype)
            if not Page:
                return ProjectPage.objects.none()
            queryset = Page.objects.all()
        else:
            queryset = ProjectPage.objects.all().select_subclasses()

        if self.ORDER_BY:
            queryset = queryset.order_by(*self.ORDER_BY)

        if self.QUERYSET_SELECT_RELATED:
            queryset = queryset.select_related(*self.QUERYSET_SELECT_RELATED)

        if self.QUERYSET_PREFETCH_RELATED:
            queryset = queryset.prefetch_related(*self.QUERYSET_PREFETCH_RELATED)

        return queryset

    def get_edit_panels(self, request):
        pagetype = request.json.get('pagetype')
        Page = ProjectPage.PAGE_TYPES.get(pagetype)
        form = Form(Page.get_edit_panels(), model=Page, form_mode='edit')
        for panel in form.data_panels:
            yield panel

    def create_model(self, request):
        create_args = super().create_model(request, no_save=True)

        project_id = request.json.get('project')
        if not project_id:
            return api.bad_request(message='missing project id')
        create_args['project_id'] = project_id

        pagetype = request.json.get('pagetype')
        Page = ProjectPage.PAGE_TYPES.get(pagetype)
        if not Page:
            return api.bad_request(message=f'invalid pagetype: {pagetype}')

        page = Page.objects.create(**create_args)

        if pagetype == 'gallery':
            self.set_gallery_images(page, request.json.get('images', []))

        if pagetype == 'homepage':
            self.set_homepage_carousel_items(page, request.json.get('carousel_items', []))

        self.set_attachments(page, request.json.get('attachments', []))

        return api.ok(data=page)

    def patch_model(self, request, pk):
        model = super().patch_model(request, pk, no_save=True)

        if 'project' in request.json:
            model.project_id = request.json['project']

        if 'pagetype' in request.json:
            pagetype = request.json['pagetype']
            if pagetype != model.PAGE_TYPE:
                return api.bad_request(message=f'不能修改页面类型')

        model.save()

        if model.PAGE_TYPE == 'gallery':
            self.set_gallery_images(model, request.json.get('images', []))

        if pagetype == 'homepage':
            self.set_homepage_carousel_items(model, request.json.get('carousel_items', []))

        self.set_attachments(model, request.json.get('attachments', []))

        return api.ok(data=model)

    def set_attachments(self, model, attachment_ids):
        model.attachments.set(attachment_ids)

    def set_homepage_carousel_items(self, model, carousel_item_ids):
        items = ProjectCarouselItem.objects.filter(id__in=carousel_item_ids)
        items = { item.id: item for item in items }
        sort_order = 1
        for id in carousel_item_ids:
            items[id].sort_order = sort_order
            sort_order += 1
        ProjectCarouselItem.objects.bulk_update(items.values(), ['sort_order'])

        model.carousel_items.set(carousel_item_ids)

    def set_gallery_images(self, model, image_ids):
        images_to_update = list(model.images.all())
        images_to_update = { image.id: image for image in images_to_update }

        images = list(ProjectGalleryImage.objects.filter(id__in=image_ids))
        for image in images:
            images_to_update[image.id] = image

        for image in images_to_update.values():
            image.gallery = None
            image.sort_order = None

        sort_order = 1
        for image_id in image_ids:
            image = images_to_update[image_id]
            image.gallery = model
            image.sort_order = sort_order
            sort_order += 1

        ProjectGalleryImage.objects.bulk_update(images_to_update.values(), ['gallery', 'sort_order'])

    @classmethod
    def urls(cls, base, app):
        return super().urls(base, app) + [
            path(f'{base}/pagetypes', cls.as_view(), name=f'{app}-{base}-pagetypes', kwargs=dict(pagetypes=True)),
            path(f'{base}/panels/<str:panel>', cls.as_view(), name=f'{app}-{base}-panels'),
        ]

@method_decorator(role_required(['admin']), name='dispatch')
class ProjectNavMenuAdminView(AdminView):
    MODEL = ProjectNavMenu
    QUERYSET_SELECT_RELATED = [
            'link_page',
            ]
    QUERYSET_PREFETCH_RELATED = [
            'children',
            'children__link_page',
            ]

    """
    菜单管理比较特殊，我们将菜单分为两大类：根节点、非根节点。
    在管理API中，我们仅提供 GET、PATCH 操作，这两个操作都只能针对
    根节点进行。（创建操作是在创建项目时一起创建的，删除也是。）

    这里不提供 SEARCH_FORM，EDIT_FORM 实质上仅仅是为前端提供 panel
    的 schema，前端并不直接使用 <ns-form> 来构造表单，而是手动构造。
    """
    LIST_METHOD = None
    CREATE_METHOD = None
    UPDATE_METHOD = None
    DELETE_METHOD = None

    SEARCH_FORM = Form()
    EDIT_FORM = Form([
        panels.SelectPanel('link_type'),
        panels.TextPanel('link_url'),
        panels.SelectPanel('link_page', choices=choices.ApiChoices('api-project-pages', label_field='page_title')),
        panels.TextPanel('text'),
    ], model=MODEL, form_mode='edit')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent=None)

    @transaction.atomic
    def patch_model(self, request, pk):
        children = request.json.get('children', [])
        try:
            root = self.get_queryset(request).get(pk=pk)
        except self.MODEL.DoesNotExist:
            return api.not_found()

        old_children = list(root.children.all())
        old_ids = { child.id for child in old_children }
        new_ids = { child['id'] for child in children if child['id']}

        children_to_delete = [child for child in old_children if child.id not in new_ids]
        children_to_update = [child for child in old_children if child.id in new_ids]
        children_to_create = [ProjectNavMenu(
                                id = None,
                                parent_id = child['parent'],
                                link_type = child['link_type'],
                                link_page_id = child['link_page'] if child['link_type'] == 'page' else None,
                                link_url = child['link_url'] if child['link_type'] == 'external' else '',
                                text = child['text'],
                                sort_order = child['sort_order'],
                            ) for child in children if not child['id']]
        children_to_update_data = { child['id']: child for child in children if child['id']}
        for child in children_to_update:
            data = children_to_update_data[child.id]
            child.link_type = data['link_type']
            child.link_page_id = data['link_page'] if data['link_type'] == 'page' else None
            child.link_url = data['link_url'] if data['link_url'] == 'external' else ''
            child.text = data['text']
            child.sort_order = data['sort_order']

        for child in children_to_delete:
            child.delete()
        for child in children_to_update:
            child.save()
        for child in children_to_create:
            child.save()

        root.refresh_from_db()
        return api.ok(data=root.serialize())

class ProjectGalleryImageAdminView(AbstractFileView):
    Model = ProjectGalleryImage

class ProjectCarouselItemAdminView(AdminView):
    MODEL = ProjectCarouselItem
    QUERYSET_PREFETCH_RELATED = [
        'image',
    ]

    SEARCH_FORM = Form([
        panels.SelectPanel('project_homepage', label='', help_text=''),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.ImageUploaderPanel('image', bucket='carousel'),
        panels.TextPanel('title'),
        panels.TextPanel('link_url'),
    ], model=MODEL, form_mode='edit')
