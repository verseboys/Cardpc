from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from natureself.django.core.managers import InheritanceQueryManager

from model_utils import Choices
from model_utils.managers import InheritanceManager
import jsonfield
import json
import os

from natureself.django.media.models import AbstractFile
from natureself.django.core.model_mixins import Orderable
from natureself.django.core.utils import get_pagination, serialize_datetime
from natureself.admin.forms import Form, panels, choices

from cardpc.panels import ProjectGalleryEditorPanel, ProjectCarouselEditorPanel, ProjectPageAttachmentPanel

class Project(models.Model):
    # 专题名称
    title = models.TextField(verbose_name='项目名称')
    # 主题颜色，目前需要指定3个颜色，color1, color2, color3
    theme_colors = jsonfield.JSONField(default=dict, verbose_name='主题颜色')
    # 主题模板
    theme = models.TextField(default='default', verbose_name='主题模板名称')
    # 专题 Banner 图片
    banner = models.ForeignKey('media.Image', models.PROTECT, verbose_name='Banner 图片', related_name='+')
    # 如果指定 banner_background，则 banner 背景使用该图片，否则使用 theme_colors.color3
    banner_background = models.ForeignKey('media.Image', models.SET_NULL, null=True, verbose_name='Banner 背景图片', related_name='+', help_text='如果不设置该图片，则 banner 背景使用主题颜色')
    # 专题项目介绍，富文本内容
    introduction = models.TextField(verbose_name='项目介绍')
    # 专题 URL 为：www.cardpc.org/project/{slug}/
    slug = models.TextField(verbose_name='项目地址', unique=True)
    # 专题导航菜单，注意我们可能先创建专题后创建菜单，因此菜单应该允许为空
    menu = models.OneToOneField('ProjectNavMenu', models.PROTECT, verbose_name='导航菜单', related_name='project')

    @property
    def colors(self):
        return self.theme_colors

    def serialize(self, to_dict=True, with_menu=False):
        data = dict(
                id = self.id,
                title = self.title,
                theme_colors = self.theme_colors,
                theme = self.theme,
                banner = self.banner.serialize(),
                banner_background = self.banner_background.serialize() if self.banner_background else None,
                introduction = self.introduction,
                slug = self.slug,
                )
        if with_menu:
            data['menu'] = self.menu.serialize()
        else:
            data['menu'] = dict(id=self.menu_id)

        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ProjectNavMenu(Orderable, models.Model):
    """
    专题导航菜单

    目前暂时仅支持一级菜单，即每个菜单项都对应一个页面或外部地址，
    不支持子菜单（任何形式的子菜单，包括静态配置的、动态发现的）。

    不过我们在实现时，预留对将来对子菜单的支持。
    """
    # 父节点，如果 parent 为 null，则表示该节点为根节点
    parent = models.ForeignKey('self', models.CASCADE, null=True, related_name='children')

    LINK_TYPES = Choices(
        ('external', 'external', '链接到外部地址'),
        ('page', 'page', '链接到内部页面'),
        ## 以下两个为子菜单相关的选项，现在暂时不支持
        # ('nolink', 'nolink', '无连接'),
        ## 当一个节点有多个子页面时，链接到第一个子页面的地址
        # ('firstchild', 'firstchild', '链接到首个子页面'),
    )
    link_type = models.TextField(choices=LINK_TYPES, verbose_name='链接类型')
    link_url = models.TextField(blank=True, verbose_name='链接地址')
    link_page = models.ForeignKey('ProjectPage', models.CASCADE, null=True, verbose_name='链接页面')
    text = models.TextField(blank=True, verbose_name='菜单文字')

    @cached_property
    def root(self):
        # TODO optomize
        if not self.parent:
            return self
        else:
            return self.parent.root

    def get_text(self):
        if self.text:
            return self.text

        if not self.parent:
            # 根节点没有 text 值，根节点不应该被渲染
            return 'ROOT'

        if self.link_type == self.LINK_TYPES.page:
            if self.link_page:
                return self.link_page.page_title
            else:
                # TODO 需要抛出 warning
                return 'NO-TEXT'
        elif self.link_type == self.LINK_TYPES.external:
            # TODO 需要抛出 warning
            return 'NO-TEXT'

    def get_url(self):
        if not self.parent:
            return None
        if self.link_type == self.LINK_TYPES.external:
            return self.link_url
        elif self.link_type == self.LINK_TYPES.page:
            return self.link_page.url

    def get_children(self):
        if not hasattr(self, '_cached_children'):
            # TODO 现在我们只支持一级菜单，将来这里需要支持多级菜单
            if self.parent_id:
                self._cached_children = list()
            else:
                self._cached_children = list(self.children.all().prefetch_related(
                    models.Prefetch('link_page', queryset=ProjectPage.published.select_subclasses())
                    ))
        return self._cached_children

    def get_active(self, page):
        """
        根据页面判断当前导航项是否为 active
        """
        if self.link_type != self.LINK_TYPES.page:
            # 如果链接类型不是内部页面，则一定非 active
            return False

        return self.link_page.is_subpage(page)

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                sort_order = self.sort_order,
                parent = dict(id=self.parent_id),
                project = self.project.serialize(with_menu=False) if not self.parent else None,
                children = [child.serialize() for child in self.get_children()],
                link_type = self.link_type,
                link_url = self.link_url,
                link_page = self.link_page.serialize(simple=True) if self.link_page else None,
                text = self.text,
                display_text = self.get_text(),
                url = self.get_url(),
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ProjectDocument(models.Model):
    project = models.ForeignKey('Project', models.PROTECT, verbose_name='项目')
    document = models.ForeignKey('media.Document', models.PROTECT, verbose_name='文件')

    subject = models.TextField(verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    publish_time = models.DateTimeField(verbose_name='发布时间')
    # 标签，只能填一个。前端可以提供下拉框选择，也可以用户自行创建，取值如 哮喘、间质性肺炎
    tag = models.TextField(verbose_name='标签')

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                project = self.project.serialize(),
                document = self.document.serialize(),
                subject = self.subject,
                description = self.description,
                publish_time = serialize_datetime(self.publish_time),
                tag = self.tag,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ProjectPage(models.Model):
    """
    专题页面基类

    专题中所有页面都需要继承这个类。

    撇开 cms，仅从开发的角度，有些页面不需要专门创建一个 Model，
    比如新闻列表页，并不需要记录额外的信息。但是我们在管理导航
    菜单时，需要获取页面列表，并且可以选择这样的页面，最简单的
    实现方法就是让这些页面也都有专门的 Model。

    这个基类存在的一个最大的作用是可以方便的列取所有页面。

    既然存在这个类，那么我们顺便可以将一些公共的字段放在这个类里实现。

    此外，专题所有页面的地址都为 /project/{slug}/{ProjectPage.id}/
    其中专题首页除外，专题首页是 /project/{slug}/
    """
    # 页面类型，用于前后端沟通时的标志
    PAGE_TYPE = None
    # 页面类型名字，每一个子类都应该重载，用户在创建页面时，展示给用户选择
    PAGE_NAME = None
    # 页面模板名字，每一个子类都应该重载，渲染页面时需要该信息
    TEMPLATE_NAME = None
    # page_title 默认值
    PAGE_TITLE_DEFAULT_VALUE = ''
    # 每个项目中该页面的数量限制，0为不限制。常见一些单例页面为 1
    PAGES_LIMITE_PER_PROJECT = 0
    # 如果该页面是容器型页面，那么可以罗列子页面的类型。
    # 该字段仅在 is_subpage() 中使用，如果某页面重载了 is_subpage()，
    # 那么该字段就没有用了。
    SUB_PAGE_TYPES = []

    # 该页面所属的专题
    project = models.ForeignKey('Project', models.CASCADE, verbose_name='项目')

    STATUSES = Choices(
            ('published', 'published', '已发布'),
            ('draft', 'draft', '草稿'),
            )
    status = models.TextField(choices=STATUSES, default=STATUSES.draft, verbose_name='状态')

    # 页面标题
    page_title = models.TextField(verbose_name='网页标题')

    # 附件，目前虽然只有新闻页有附件，但将来可能其他页面也可能需要附件，因此统一放在基类上
    attachments = models.ManyToManyField('media.Document', verbose_name='附件')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # InheritanceManager 文档：https://django-model-utils.readthedocs.io/en/latest/managers.html#inheritancemanager
    # pages = Page.objects.filter(...).select_subclasses()
    # pages[n] -> Page 的某个具体的子类
    objects = InheritanceManager()
    published = InheritanceQueryManager(status=STATUSES.published)

    def get_context(self, request):
        page = self
        project = self.project
        menu = self.project.menu.get_children()
        for child in menu:
            child.active = child.get_active(self)
        attachments = list(self.attachments.all())

        return dict(page=page, project=project, menu=menu, attachments=attachments)

    def get_template(self, request):
        return f'cardpc/project/{self.project.theme}/{self.TEMPLATE_NAME}'

    @property
    def url(self):
        return reverse('project-page', kwargs=dict(project_slug=self.project.slug, page_id=self.id))

    def serialize(self, to_dict=True, simple=False):
        # simple 模式是给菜单序列化用的
        data = dict(
                id = self.id,
                page_title = self.page_title,
                pagetype = dict(type=self.PAGE_TYPE, name=self.PAGE_NAME),
                url = self.url,
                status = self.status,
                )
        if not simple:
            data.update(dict(
                page_name = self.PAGE_NAME,
                project = self.project.serialize(),
                attachments = [att.serialize() for att in self.attachments.all()],
                created_at = serialize_datetime(self.created_at),
                updated_at = serialize_datetime(self.updated_at),
                ))
        return data if to_dict else json.dumps(data, ensure_ascii=False)

    @classmethod
    def serialize_pagetypes(cls, project_id=None):
        data = []
        for type, model in cls.PAGE_TYPES.items():
            disabled = False
            if project_id:
                if model.PAGES_LIMITE_PER_PROJECT:
                    page_count = model.objects.filter(project_id=project_id).count()
                    disabled = page_count >= model.PAGES_LIMITE_PER_PROJECT
            item = dict(type=type, name=model.PAGE_NAME, disabled=disabled)
            data.append(item)
        return data

    @classmethod
    def get_edit_panels(cls):
        edit_panels = [
                panels.SelectPanel('status'),
                panels.TextPanel('page_title', default_value=cls.PAGE_TITLE_DEFAULT_VALUE),
                # panels.DocumentUploaderPanel(attachments')
                ]

        return edit_panels

    def is_subpage(self, other):
        # 判断 other 这个页面是否为当前页面或当前页面的子页面，用于判断导航菜单项是否标记为 active
        if self.id == other.id:
            return True

        if other.PAGE_TYPE in self.SUB_PAGE_TYPES:
            return True

        return False

class ProjectHomepage(ProjectPage):
    """
    专题首页
    """
    PAGE_TYPE = 'homepage'
    PAGE_NAME = '专题首页'
    TEMPLATE_NAME = 'homepage.html'
    PAGE_TITLE_DEFAULT_VALUE = '专题首页'
    PAGES_LIMITE_PER_PROJECT = 1

    carousel_items = models.ManyToManyField('ProjectCarouselItem', related_name='project_homepage')

    @classmethod
    def get_edit_panels(cls):
        return super().get_edit_panels() + [
                ProjectCarouselEditorPanel('carousel_items'),
                ]

    @property
    def url(self):
        return reverse('project-homepage', kwargs=dict(project_slug=self.project.slug))

    def get_context(self, request):
        context = super().get_context(request)

        news_list = ProjectNews.published.filter(project_id=self.project_id).order_by('-publish_time')
        page, paginator, pagination = get_pagination(request, news_list, page_size=7)
        news_list_page = ProjectNewsList.published.filter(project_id=self.project_id).first()
        context.update(dict(news_list=page, news_list_page=news_list_page))

        images = ProjectGalleryImage.objects.filter(gallery__project_id=self.project_id).order_by('sort_order')
        page, paginator, pagination = get_pagination(request, images, page_size=4)
        gallery_page = ProjectGallery.published.filter(project_id=self.project_id).first()
        context.update(dict(gallery_images=page, gallery_page=gallery_page))

        return context

    def serialize(self, to_dict=True, simple=False):
        data = super().serialize(to_dict=True, simple=simple)
        if not simple:
            data.update(dict(
                carousel_items = [item.serialize() for item in self.carousel_items.all()]
                ))
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ProjectCarouselItem(Orderable):
    """
    目前只有首页有轮播图，但是考虑到轮播图本身具有一定的通用性，所以这里就实现为通用的，
    每个页面可以通过 ManyToManyField 来引入轮播图
    """
    class Meta:
        ordering = ['sort_order']

    image = models.ForeignKey('media.Image', models.PROTECT, related_name='+', verbose_name='图片')
    title = models.TextField(verbose_name='标题')
    link_url = models.TextField(verbose_name='链接地址', blank=True)

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                image = self.image.serialize(),
                title = self.title,
                link_url = self.link_url,
                sort_order = self.sort_order,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ProjectNews(ProjectPage):
    """
    新闻详情页
    """
    PAGE_TYPE = 'news'
    PAGE_NAME = '新闻'
    TEMPLATE_NAME = 'news.html'

    # 新闻标题
    title = models.TextField(verbose_name='标题')
    # 新闻摘要，显示在新闻列表页，富文本
    excerpt = models.TextField(verbose_name='摘要', help_text='在新闻列表页中显示')
    # 新闻正文，富文本
    content = models.TextField(verbose_name='正文')
    # 作者姓名
    author_name = models.TextField(verbose_name='作者姓名')
    # 封面图片
    cover_picture = models.ForeignKey('media.Image', models.PROTECT, verbose_name='封面图片')
    # 发表时间
    publish_time = models.DateTimeField(verbose_name='发表时间')

    def get_context(self, request):
        context = super().get_context(request)
        # 所有 Page 页面都有 page 指向 self，这里添加一个别名 news，方便使用
        context['news'] = self
        return context

    def serialize(self, to_dict=True, simple=False):
        data = super().serialize(to_dict=True, simple=simple)
        if not simple:
            data.update(dict(
                title = self.title,
                excerpt = self.excerpt,
                content = self.content,
                author_name = self.author_name,
                cover_picture = self.cover_picture.serialize(),
                publish_time = serialize_datetime(self.publish_time),
                ))
        return data if to_dict else json.dumps(data, ensure_ascii=False)

    @classmethod
    def get_edit_panels(cls):
        return super().get_edit_panels() + [
            panels.TextPanel('title'),
            panels.TextPanel('author_name'),
            panels.ImageUploaderPanel('cover_picture', bucket='project'),
            panels.DateTimePickerPanel('publish_time'),
            ProjectPageAttachmentPanel('attachments', bucket='project-attachments'),
            panels.RichTextPanel('excerpt'),
            panels.RichTextPanel('content'),
        ]

class ProjectNewsList(ProjectPage):
    """
    新闻列表页
    """
    PAGE_TYPE = 'news-list'
    PAGE_NAME = '新闻资讯'
    TEMPLATE_NAME = 'news-list.html'
    PAGE_TITLE_DEFAULT_VALUE = '新闻资讯'
    PAGES_LIMITE_PER_PROJECT = 1
    SUB_PAGE_TYPES = ['news']

    def get_context(self, request):
        context = super().get_context(request)

        news_list = ProjectNews.published.filter(project_id=self.project_id).order_by('-publish_time')
        page, paginator, pagination = get_pagination(request, news_list)

        context.update(dict(news_list=page, pagination=pagination))

        return context

class ProjectGallery(ProjectPage):
    """
    花絮集锦

    关于单词命名，花絮一词有许多翻译，如：
    * outtakes，备用镜头，未被采用的镜头
    * featurettes，电影幕后花絮
    * titbit，趣闻，花絮
    * blooper，一般指拍电影时失败的镜头，比如成龙的电影后面经常有这类花絮

    但我感觉这些单词都不能准确表达这个场景中的意思。这个场景中的花絮集锦
    主要指的是活动图片，因此我觉得 gallery 比较合适。gallery 一般指相册、
    画库，也是 IT 产品中常用来表达许多图片集合的一个数据结构。
    """
    PAGE_TYPE = 'gallery'
    PAGE_NAME = '花絮集锦'
    TEMPLATE_NAME = 'gallery.html'
    PAGE_TITLE_DEFAULT_VALUE = '花絮集锦'
    PAGES_LIMITE_PER_PROJECT = 1

    def get_context(self, request):
        context = super().get_context(request)

        images = self.images.order_by('sort_order')
        # 强制设置 page_size 为 8
        page, paginator, pagination = get_pagination(request, images, page_size=8)

        context.update(dict(images=page, pagination=pagination))

        return context

    def serialize(self, to_dict=True, simple=False):
        data = super().serialize(to_dict=True, simple=simple)
        if not simple:
            data.update(dict(
                images = [image.serialize() for image in self.images.all()],
                ))

        return data if to_dict else json.dumps(data, ensure_ascii=False)

    @classmethod
    def get_edit_panels(cls):
        return super().get_edit_panels() + [
            ProjectGalleryEditorPanel('images', form_field_property='id'),
        ]

class ProjectGalleryImage(Orderable, AbstractFile):
    """
    花絮集锦中的图片
    """
    STORAGE_ROOT = 'project/images/'

    # 在管理后台中，先上传图片（不设置所属的专题页面），在保存花絮集锦页面时，在处理所有图片
    gallery = models.ForeignKey('ProjectGallery', models.SET_NULL, null=True, related_name='images', verbose_name='花絮锦集')

    def serialize(self, to_dict=True, **kwargs):
        data = super().serialize(to_dict=True, **kwargs)
        data['sort_order'] = self.sort_order

        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ProjectDownload(ProjectPage):
    """
    文件下载页
    """
    PAGE_TYPE = 'download'
    PAGE_NAME = '文件下载页'
    TEMPLATE_NAME = 'download.html'
    PAGE_TITLE_DEFAULT_VALUE = '文件下载'
    PAGES_LIMITE_PER_PROJECT = 1

    def get_context(self, request):
        context = super().get_context(request)

        documents = list(ProjectDocument.objects.filter(project_id=self.project_id))

        tags = {}
        for doc in documents:
            if doc.tag in tags:
                tags[doc.tag].append(doc)
            else:
                tags[doc.tag] = [doc]

        context.update(dict(documents=documents, tags=tags))

        return context

class ProjectRichtextPage(ProjectPage):
    PAGE_TYPE = 'richtext'
    PAGE_NAME = '一般富文本页面'
    TEMPLATE_NAME = 'richtext.html'

    # 标题
    title = models.TextField(verbose_name='标题')
    # 正文内容，富文本
    content = models.TextField(verbose_name='正文')

    def serialize(self, to_dict=True, simple=False):
        data = super().serialize(to_dict=True, simple=simple)
        if not simple:
            data.update(dict(
                title = self.title,
                content = self.content,
                ))

        return data if to_dict else json.dumps(data, ensure_ascii=False)

    @classmethod
    def get_edit_panels(cls):
        return super().get_edit_panels() + [
            panels.TextPanel('title'),
            panels.RichTextPanel('content'),
        ]

class ProjectVideo(ProjectPage):
    """
    视频播放页
    """
    PAGE_TYPE = 'video'
    PAGE_NAME = '视频'
    TEMPLATE_NAME = 'video.html'

    video = models.ForeignKey('media.PolyvVideo', models.PROTECT, verbose_name='保利威视频')

    # title, thumbnail 从 PolyvVideo 中获取

    # 讲师姓名和单位，纯文本
    teacher_name = models.TextField(verbose_name='讲师姓名')
    teacher_organization = models.TextField(verbose_name='讲师单位')
    # 内容简介 富文本
    introduction = models.TextField(verbose_name='内容简介')
    # 讲者简介 富文本
    teacher_introduction = models.TextField(verbose_name='讲者简介')

    def serialize(self, to_dict=True, simple=False):
        data = super().serialize(to_dict=True, simple=simple)
        if not simple:
            data.update(dict(
                video = self.video.serialize(),
                teacher_name = self.teacher_name,
                teacher_organization = self.teacher_organization,
                introduction = self.introduction,
                teacher_introduction = self.teacher_introduction,
                ))
        return data if to_dict else json.dumps(data, ensure_ascii=False)

    @classmethod
    def get_edit_panels(cls):
        return super().get_edit_panels() + [
            panels.SelectPanel('video', choices=choices.ApiChoices('api-media-videos', label_field='title')),
            panels.TextPanel('teacher_name'),
            panels.TextPanel('teacher_organization'),
            panels.RichTextPanel('introduction'),
            panels.RichTextPanel('teacher_introduction'),
        ]

class ProjectVideoList(ProjectPage):
    """
    视频列表页
    """
    PAGE_TYPE = 'video-list'
    PAGE_NAME = '视频列表'
    TEMPLATE_NAME = 'video-list.html'
    PAGE_TITLE_DEFAULT_VALUE = '视频'
    PAGES_LIMITE_PER_PROJECT = 1
    SUB_PAGE_TYPES = ['video']

    def get_context(self, request):
        context = super().get_context(request)

        videos = ProjectVideo.published \
                .select_related('video', 'video__thumbnail') \
                .filter(project_id=self.project_id) \
                .order_by('-id')
        page, paginator, pagination = get_pagination(request, videos)

        context.update(dict(videos=page, pagination=pagination))

        return context
