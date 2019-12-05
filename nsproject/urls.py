"""nsproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

urlpatterns = [
    path('', include('cardpc.urls')),

    path('', include('natureself.django.media.urls')),
    path('', include('natureself.django.notification.urls')),
    path('', include('natureself.django.account.urls')),
    path('', include('natureself.django.course.urls')),
]

from django.conf import settings
if settings.DEBUG:
    import os
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/admin/', document_root=os.path.join(settings.BUILD_DIR, 'admin'))
