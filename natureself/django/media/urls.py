from django.urls import path, include
from django.views.generic import TemplateView

from .views import admin, download, polyv

urlpatterns = [
    path('api/admin/media/', include([
        path('images', admin.ImageView.as_view()),
        path('images/<int:id>', admin.ImageView.as_view()),
        path('documents', admin.DocumentView.as_view()),
        path('documents/<int:id>', admin.DocumentView.as_view()),
        path('slides', admin.SlideView.as_view()),
        path('slides/<int:id>', admin.SlideView.as_view()),
    ])),

    path('video_validate/', polyv.polyv_validate),
    path('crossdomain.xml', TemplateView.as_view(template_name='media/crossdomain.xml', content_type='text/xml')),

    path('api/admin/media/', include(admin.PresentationAdminView.urls('presentations', 'api-media'))),
    path('api/admin/media/', include(admin.PolyvVideoAdminView.urls('videos', 'api-media'))),

    path('download/images/<str:key>', download.download_file, name='download-image',
        kwargs=dict(model='image')),
    path('download/documents/<str:key>', download.download_file, name='download-document',
        kwargs=dict(model='document')),
    path('download/slides/<str:key>', download.download_file, name='download-slide',
        kwargs=dict(model='slide')),
]
