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


def create_notification(user, notification_type, title, message, link=''):
    """Helper function to create notifications"""
    from courses.models import Notification
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )


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
                enrollment = Enrollment.objects.create(user=request.user, course=course)
                messages.success(request, f'Вы успешно записались на курс "{course.title}"')
                
                # Create notification
                create_notification(
                    user=request.user,
                    notification_type='enrollment',
                    title=f'Вы записались на курс',
                    message=f'Вы успешно записались на курс "{course.title}". Начните обучение прямо сейчас!',
                    link=f'/courses/{course.slug}/'
                )
                
                # Notify instructor
                create_notification(
                    user=course.instructor,
                    notification_type='enrollment',
                    title=f'Новый студент',
                    message=f'{request.user.get_full_name() or request.user.username} записался на ваш курс "{course.title}"',
                    link=f'/instructor/'
                )
                
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
    from courses.models import LessonProgress
    
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')
    
    # Add next lesson info to each enrollment
    for enrollment in enrollments:
        # Get all lessons for this course
        all_lessons = Lesson.objects.filter(module__course=enrollment.course).order_by('module__order', 'order')
        
        # Get completed lesson IDs
        completed_ids = LessonProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).values_list('lesson_id', flat=True)
        
        # Find first incomplete lesson
        next_lesson = None
        for lesson in all_lessons:
            if lesson.id not in completed_ids:
                next_lesson = lesson
                break
        
        enrollment.next_lesson = next_lesson if next_lesson else (all_lessons.first() if all_lessons.exists() else None)
    
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


@login_required
def notifications_view(request):
    from courses.models import Notification
    from django.core.paginator import Paginator
    
    # Mark as read if coming from a notification link
    mark_read_id = request.GET.get('mark_read')
    if mark_read_id:
        Notification.objects.filter(id=mark_read_id, user=request.user).update(is_read=True)
    
    notifications_list = Notification.objects.filter(user=request.user)
    paginator = Paginator(notifications_list, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def mark_all_notifications_read(request):
    from courses.models import Notification
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'Все уведомления отмечены как прочитанные')
    return redirect('notifications')


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
        
        # Update course progress (optimized with single aggregation query)
        from django.db.models import Count, Q
        lesson_stats = Lesson.objects.filter(module__course=course).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(
                lessonprogress__enrollment=enrollment,
                lessonprogress__completed=True
            ))
        )
        total_lessons = lesson_stats['total']
        completed_lessons = lesson_stats['completed']
        enrollment.progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        # Check if course is completed
        if enrollment.progress == 100 and not enrollment.completed:
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
            
            # Generate certificate
            from courses.models import Certificate
            try:
                cert = enrollment.certificate
            except Certificate.DoesNotExist:
                cert = Certificate.objects.create(enrollment=enrollment)
                
                # Create notification
                create_notification(
                    user=request.user,
                    notification_type='certificate',
                    title='🎉 Сертификат получен!',
                    message=f'Поздравляем! Вы завершили курс "{course.title}" и получили сертификат #{cert.certificate_number}',
                    link=f'/certificate/{cert.certificate_number}/'
                )
                
                messages.success(request, '🎉 Поздравляем! Вы завершили курс и получили сертификат!')
            else:
                messages.success(request, 'Урок отмечен как завершённый!')
        else:
            messages.success(request, 'Урок отмечен как завершённый!')
        
        enrollment.save()
        return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
    
    # Find previous and next lessons (optimized with single query)
    all_lessons = list(Lesson.objects.filter(
        module__course=course
    ).select_related('module').order_by('module__order', 'order'))
    
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
