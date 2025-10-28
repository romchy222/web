from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, CourseViewSet, ModuleViewSet, 
                    LessonViewSet, EnrollmentViewSet, ReviewViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
