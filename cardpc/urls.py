from django.urls import path, include
from django.views.generic.base import RedirectView

from .views import zhixiang, account, project, zhuanti

urlpatterns = [
    # 用户端网页
    path('zhixiang/', include([
        path('', zhixiang.homepage, name='zhixiang-homepage'),
        path('training/', zhixiang.training, name='zhixiang-training'),
        path('wjx/<str:action>/', zhixiang.wjx_callback),
        path('lesson/<int:id>/', zhixiang.lesson, name='zhixiang-lesson'),
        path('news/', zhixiang.news_list, name='zhixiang-news-list'),
        path('news/<int:id>/', zhixiang.news_detail, name='zhixiang-news-detail'),
    ])),

    path('account/', include([
        path('login/', account.page_login, name='login'),
        path('register/', account.page_register, name='register'),
        path('reset-password/', account.page_reset_password, name='reset_password'),
    ])),

    path('zhuanti/', include(
        [
            path('', zhuanti.homepage, name='zhuanti-homepage'),
            path('news/', zhuanti.news_list, name='zhuanti-news-list'),
            path('news/<int:id>', zhuanti.news_detail, name='zhuanti-news'),
            path('videos/', zhuanti.video_list, name='zhuanti-videos'),
            path('videos/<int:id>', zhuanti.video, name='zhuanti-video'),
            path('documents/', zhuanti.document_list, name='zhuanti-documents'),
            path('featurettes/', zhuanti.featurette_list, name='zhuanti-featurettes'),
            path('summary/', zhuanti.summary, name='zhuanti-summary')
            ]
        )),

    path('project/<str:project_slug>/', project.page, name='project-homepage'),
    path('project/<str:project_slug>/<int:page_id>/', project.page, name='project-page'),

    # 管理后台 API
    path('api/admin/cardpc/zhixiang/', include(zhixiang.NewsAdminView.urls('news', 'api-zhixiang'))),
    path('api/admin/cardpc/zhixiang/', include(zhixiang.ExaminationAdminView.urls('examinations', 'api-zhixiang'))),
    path('api/admin/cardpc/zhixiang/', include(zhixiang.TrainingAdminView.urls('training', 'api-zhixiang'))),
    path('api/admin/cardpc/zhixiang/training/export', zhixiang.api_export_training_data),
    path('api/admin/cardpc/project/', include(project.ProjectAdminView.urls('projects', 'api-project'))),
    path('api/admin/cardpc/project/', include(project.ProjectDocumentAdminView.urls('documents', 'api-project'))),
    path('api/admin/cardpc/project/', include(project.ProjectPageAdminView.urls('pages', 'api-project'))),
    path('api/admin/cardpc/project/', include(project.ProjectNavMenuAdminView.urls('menus', 'api-project'))),
    path('api/admin/cardpc/project/', include(project.ProjectCarouselItemAdminView.urls('carousel', 'api-project'))),
    path('api/admin/media/cardpcgalleryimages', project.ProjectGalleryImageAdminView.as_view()),
    path('api/admin/media/cardpcgalleryimages/<int:id>', project.ProjectGalleryImageAdminView.as_view()),
]
