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
    reviews = course.reviews.select_related('user').all()
    
    is_enrolled = False
    enrollment = None
    user_review = None
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        is_enrolled = enrollment is not None
        user_review = Review.objects.filter(user=request.user, course=course).first()
        
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
        'user_review': user_review,
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
    from courses.models import Certificate
    
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    certificates = Certificate.objects.filter(enrollment__user=request.user).select_related('enrollment__course')
    
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
        'certificates': certificates,
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


@login_required
def certificate_view(request, certificate_number):
    from courses.models import Certificate
    certificate = get_object_or_404(Certificate, certificate_number=certificate_number)
    
    # Check if user owns this certificate
    if certificate.enrollment.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этому сертификату')
        return redirect('profile')
    
    return render(request, 'certificate.html', {'certificate': certificate})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # In production, send email here
        # For now, just show success message
        messages.success(request, 'Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.')
        return redirect('contact')
    
    return render(request, 'contact.html')


@login_required
def add_review_view(request, slug):
    if request.method != 'POST':
        return redirect('course_detail', slug=slug)
    
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'Вы должны быть записаны на курс, чтобы оставить отзыв')
        return redirect('course_detail', slug=slug)
    
    # Check if user already reviewed
    if Review.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'Вы уже оставили отзыв на этот курс')
        return redirect('course_detail', slug=slug)
    
    rating = request.POST.get('rating')
    comment = request.POST.get('comment')
    
    if rating and comment:
        Review.objects.create(
            user=request.user,
            course=course,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, 'Спасибо за ваш отзыв!')
    else:
        messages.error(request, 'Пожалуйста, заполните все поля')
    
    return redirect('course_detail', slug=slug)


@login_required
def lesson_detail_view(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get all modules with lessons
    modules = course.modules.prefetch_related('lessons').all()
    
    # Get completed lesson IDs
    from courses.models import LessonProgress
    completed_lesson_ids = LessonProgress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).values_list('lesson_id', flat=True)
    
    # Check if current lesson is completed
    is_completed = lesson.id in completed_lesson_ids
    
    # Handle marking lesson as complete
    if request.method == 'POST':
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        # Update course progress
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()
        enrollment.progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        # Check if course is completed
        if enrollment.progress == 100 and not enrollment.completed:
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
            
            # Generate certificate
            from courses.models import Certificate
            if not hasattr(enrollment, 'certificate'):
                Certificate.objects.create(enrollment=enrollment)
                messages.success(request, '🎉 Поздравляем! Вы завершили курс и получили сертификат!')
            else:
                messages.success(request, 'Урок отмечен как завершённый!')
        else:
            messages.success(request, 'Урок отмечен как завершённый!')
        
        enrollment.save()
        return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
    
    # Find previous and next lessons
    all_lessons = []
    for module in modules:
        all_lessons.extend(module.lessons.all())
    
    current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), None)
    previous_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'modules': modules,
        'completed_lesson_ids': completed_lesson_ids,
        'is_completed': is_completed,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
    }
    return render(request, 'courses/lesson_detail.html', context)
