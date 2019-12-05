from django.urls import path, include

from . import views

urlpatterns = [
    path('api/account/', include([
        path('login', views.api_login, name='api-login'),
        path('logout', views.api_logout, name='api-logout'),
        path('info', views.api_get_info, name='api-get-info'),
        path('send-code', views.api_send_code, name='api-send-code'),
        path('verify-code', views.api_verify_code, name='api-verify-code'),
        path('reset-password', views.api_reset_password, name='api-reset-password'),
        path('register', views.api_register, name='api-register'),
    ])),
]
