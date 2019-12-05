from django.urls import path, include
from django.conf import settings

from .views import admin as admin_views
from .views import misc as misc_views

urlpatterns = [
    path('api/admin/notification/', include(admin_views.EmailView.urls('emails', 'notification'))),
    path('api/admin/notification/', include(admin_views.AliSmsView.urls('alisms', 'notification'))),
]

if settings.DEBUG:
    urlpatterns += [
        path('debug/preview-email/', misc_views.preview_email_template),
        ]
