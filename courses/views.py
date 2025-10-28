from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (Category, Course, Module, Lesson, Enrollment, 
                     LessonProgress, Attendance, Review)
from .serializers import (CategorySerializer, CourseListSerializer, CourseDetailSerializer,
                          CourseCreateUpdateSerializer, ModuleSerializer, LessonSerializer,
                          EnrollmentSerializer, LessonProgressSerializer, AttendanceSerializer,
                          ReviewSerializer)


class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.instructor == request.user or request.user.role == 'admin'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'category', 'instructor']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'price']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseDetailSerializer
    
    def get_queryset(self):
        queryset = Course.objects.all()
        if self.request.user.is_authenticated and self.request.user.role in ['instructor', 'admin']:
            return queryset
        return queryset.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, slug=None):
        course = self.get_object()
        if course.type == 'offline' and course.max_students:
            if course.enrollments.count() >= course.max_students:
                return Response({'error': 'Course is full'}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        if created:
            return Response({'message': 'Successfully enrolled'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already enrolled'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def my_progress(self, request, slug=None):
        course = self.get_object()
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            return Response(EnrollmentSerializer(enrollment).data)
        except Enrollment.DoesNotExist:
            return Response({'error': 'Not enrolled'}, status=status.HTTP_404_NOT_FOUND)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsInstructorOrReadOnly]
    
    def get_queryset(self):
        course_slug = self.request.query_params.get('course', None)
        if course_slug:
            return Module.objects.filter(course__slug=course_slug)
        return Module.objects.all()


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        lesson = self.get_object()
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=lesson.module.course
        ).first()
        
        if not enrollment:
            return Response({'error': 'Not enrolled in this course'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        # Update course progress
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()
        enrollment.progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        enrollment.save()
        
        return Response({'message': 'Lesson marked as complete', 'progress': enrollment.progress})


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        course_slug = self.request.query_params.get('course', None)
        if course_slug:
            return Review.objects.filter(course__slug=course_slug)
        return Review.objects.all()
