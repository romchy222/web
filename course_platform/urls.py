"""
URL configuration for course_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.template_views import (
    home_view, course_list_view, course_detail_view, lesson_detail_view,
    my_courses_view, login_view, register_view, logout_view,
    profile_view, instructor_dashboard_view, about_view, contact_view,
    add_review_view, certificate_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('courses/', course_list_view, name='course_list'),
    path('courses/<slug:slug>/', course_detail_view, name='course_detail'),
    path('courses/<slug:slug>/review/', add_review_view, name='add_review'),
    path('courses/<slug:course_slug>/lesson/<int:lesson_id>/', lesson_detail_view, name='lesson_detail'),
    path('my-courses/', my_courses_view, name='my_courses'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('certificate/<str:certificate_number>/', certificate_view, name='certificate'),
    path('instructor/', instructor_dashboard_view, name='instructor_dashboard'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/', include('courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
