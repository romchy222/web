from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count
from .models import Course, Category, Enrollment, Module, Lesson, Review
from users.models import User


def home_view(request):
    popular_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:6]
    upcoming_webinars = Course.objects.filter(
        type='webinar',
        is_published=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')[:4]
    
    context = {
        'popular_courses': popular_courses,
        'upcoming_webinars': upcoming_webinars,
    }
    return render(request, 'home.html', context)


def course_list_view(request):
    courses = Course.objects.filter(is_published=True)
    categories = Category.objects.all()
    
    # Фильтрация
    course_type = request.GET.get('type')
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    if course_type:
        courses = courses.filter(type=course_type)
    if category_id:
        courses = courses.filter(category_id=category_id)
    if search:
        courses = courses.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(courses, 9)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    context = {
        'courses': courses,
        'categories': categories,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    modules = course.modules.prefetch_related('lessons').all()
    reviews = course.reviews.select_related('user').all()[:10]
    
    is_enrolled = False
    enrollment = None
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        is_enrolled = enrollment is not None
        
        # Запись на курс
        if request.method == 'POST':
            if not is_enrolled:
                Enrollment.objects.create(user=request.user, course=course)
                messages.success(request, f'Вы успешно записались на курс "{course.title}"')
                return redirect('course_detail', slug=slug)
    
    lessons_count = Lesson.objects.filter(module__course=course).count()
    enrollments_count = course.enrollments.count()
    
    context = {
        'course': course,
        'modules': modules,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'lessons_count': lessons_count,
        'enrollments_count': enrollments_count,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def my_courses_view(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')
    
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'my_courses.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'auth/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'student')
        
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email уже используется')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('home')
    
    return render(request, 'auth/register.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def profile_view(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.bio = request.POST.get('bio', '')
        
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, 'Профиль успешно обновлён')
        return redirect('profile')
    
    stats = {
        'total_courses': enrollments.count(),
        'completed_courses': enrollments.filter(completed=True).count(),
        'in_progress': enrollments.filter(completed=False).count(),
    }
    
    instructor_stats = {}
    if request.user.role == 'instructor':
        from django.db.models import Avg
        courses = Course.objects.filter(instructor=request.user)
        instructor_stats = {
            'courses_created': courses.count(),
            'active_courses': courses.filter(is_published=True).count(),
            'total_students': Enrollment.objects.filter(course__instructor=request.user).count(),
            'avg_rating': Review.objects.filter(course__instructor=request.user).aggregate(Avg('rating'))['rating__avg'] or 0,
        }
    
    context = {
        'enrollments': enrollments[:6],
        'stats': stats,
        'instructor_stats': instructor_stats,
    }
    return render(request, 'profile.html', context)


@login_required
def instructor_dashboard_view(request):
    if request.user.role not in ['instructor', 'admin']:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    from django.db.models import Avg, Count
    
    courses = Course.objects.filter(instructor=request.user).annotate(student_count=Count('enrollments'))
    enrollments = Enrollment.objects.filter(course__instructor=request.user).select_related('user', 'course').order_by('-enrolled_at')[:20]
    reviews = Review.objects.filter(course__instructor=request.user).select_related('user', 'course').order_by('-created_at')[:10]
    
    stats = {
        'total_courses': courses.count(),
        'total_students': Enrollment.objects.filter(course__instructor=request.user).values('user').distinct().count(),
        'active_students': Enrollment.objects.filter(course__instructor=request.user, completed=False).count(),
        'avg_rating': Review.objects.filter(course__instructor=request.user).aggregate(Avg('rating'))['rating__avg'] or 0,
    }
    
    context = {
        'courses': courses,
        'enrollments': enrollments,
        'reviews': reviews,
        'stats': stats,
    }
    return render(request, 'instructor_dashboard.html', context)


def about_view(request):
    return render(request, 'about.html')
