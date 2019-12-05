from django.urls import path

from . import views

urlpatterns = [
    path('account/login/', views.page_login, name='page_login'),
    path('account/logout/', views.page_logout, name='page_logout'),
    path('account/reset_password/', views.page_reset_password, name='page_reset_password'),
]
