from django.urls import path, include

from .views import admin

urlpatterns = [
    path('api/admin/course/', include(admin.CourseAdminView.urls('courses', 'api-course'))),
    path('api/admin/course/', include(admin.PresentationLessonAdminView.urls('presentations', 'api-course'))),
]
