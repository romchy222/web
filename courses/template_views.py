from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count
from .models import (Course, Category, Enrollment, Module, Lesson, Review, LessonProgress,
                     ModuleProgress, Assignment, AssignmentSubmission, Quiz, QuizAttempt, QuestionAnswer, Certificate)
from users.models import User


def can_complete_lesson(enrollment, lesson):
    """Проверяет, может ли студент завершить урок (пройдены ли предыдущие уроки в модуле)"""
    # Получаем все предыдущие уроки в том же модуле
    previous_lessons = lesson.module.lessons.filter(
        order__lt=lesson.order,
        is_required=True
    )
    
    # Проверяем, что все предыдущие обязательные уроки завершены
    for prev_lesson in previous_lessons:
        prev_progress = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson=prev_lesson,
            completed=True
        ).exists()
        if not prev_progress:
            return False
    
    return True


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
        
        # Добавляем информацию о прогрессе по модулям
        if is_enrolled:
            for module in modules:
                module_progress, created = ModuleProgress.objects.get_or_create(
                    enrollment=enrollment,
                    module=module
                )
                module.progress = module_progress
        
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
    
    # Для каждого курса определяем последний изученный урок
    for enrollment in enrollments:
        if not enrollment.completed:
            # Находим последний просмотренный урок
            last_completed = LessonProgress.objects.filter(
                enrollment=enrollment,
                completed=True
            ).order_by('lesson__module__order', 'lesson__order').last()
            
            if last_completed:
                # Следующий урок после последнего завершенного
                all_lessons = list(Lesson.objects.filter(
                    module__course=enrollment.course
                ).order_by('module__order', 'order'))
                
                try:
                    current_index = all_lessons.index(last_completed.lesson)
                    if current_index + 1 < len(all_lessons):
                        enrollment.last_lesson = all_lessons[current_index + 1]
                    else:
                        enrollment.last_lesson = last_completed.lesson
                except ValueError:
                    enrollment.last_lesson = None
            else:
                # Если нет завершенных уроков, берем первый
                enrollment.last_lesson = None
    
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


@login_required
def lesson_view(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    # Проверяем, записан ли пользователь на курс
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Получаем все уроки курса для навигации
    all_lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
    lessons_list = list(all_lessons)
    
    current_index = None
    for i, l in enumerate(lessons_list):
        if l.id == lesson.id:
            current_index = i
            break
    
    prev_lesson = lessons_list[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = lessons_list[current_index + 1] if current_index is not None and current_index < len(lessons_list) - 1 else None
    
    # Получаем или создаем прогресс по уроку
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    # Получаем информацию о задании, если урок типа assignment
    user_submission = None
    if lesson.lesson_type == 'assignment' and hasattr(lesson, 'assignment'):
        user_submission = AssignmentSubmission.objects.filter(
            user=request.user, 
            assignment=lesson.assignment
        ).first()
    
    # Обработка POST запросов
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'complete':
            if not lesson_progress.completed:
                # Проверяем, можно ли завершить урок (пройдены ли предыдущие обязательные уроки)
                if can_complete_lesson(enrollment, lesson):
                    lesson_progress.completed = True
                    lesson_progress.completed_at = timezone.now()
                    lesson_progress.save()
                    
                    # Обновляем прогресс по курсу через новую систему
                    enrollment.update_progress()
                    
                    messages.success(request, 'Урок отмечен как завершенный!')
                else:
                    messages.error(request, 'Необходимо сначала завершить все предыдущие обязательные уроки в модуле.')
            
            return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
        
        elif action == 'submit_assignment' and lesson.lesson_type == 'assignment':
            if hasattr(lesson, 'assignment') and not user_submission:
                assignment_file = request.FILES.get('assignment_file')
                assignment_comment = request.POST.get('assignment_comment', '')
                
                if assignment_file:
                    # Проверяем размер файла
                    if assignment_file.size > lesson.assignment.max_file_size * 1024 * 1024:
                        messages.error(request, f'Файл слишком большой. Максимальный размер: {lesson.assignment.max_file_size} МБ')
                    else:
                        # Создаем отправку задания
                        AssignmentSubmission.objects.create(
                            user=request.user,
                            assignment=lesson.assignment,
                            file=assignment_file,
                            comment=assignment_comment
                        )
                        
                        # Автоматически отмечаем урок как завершенный, если можно
                        if can_complete_lesson(enrollment, lesson):
                            if not lesson_progress.completed:
                                lesson_progress.completed = True
                                lesson_progress.completed_at = timezone.now()
                                lesson_progress.save()
                                
                                # Обновляем общий прогресс
                                enrollment.update_progress()
                        
                        messages.success(request, 'Задание успешно отправлено!')
                else:
                    messages.error(request, 'Пожалуйста, выберите файл для отправки.')
            
            return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
    
    # Получаем прогресс по всем урокам для отображения
    lesson_progresses = LessonProgress.objects.filter(
        enrollment=enrollment
    ).select_related('lesson').values_list('lesson_id', 'completed')
    
    progress_dict = dict(lesson_progresses)
    
    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'all_lessons': lessons_list,
        'progress_dict': progress_dict,
        'user_submission': user_submission,
    }
    
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def create_course_view(request):
    if request.user.role not in ['instructor', 'admin']:
        messages.error(request, 'У вас нет доступа к созданию курсов')
        return redirect('home')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Базовые данные курса
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_type = request.POST.get('type')
        category_id = request.POST.get('category')
        price = request.POST.get('price', 0)
        
        # Данные для офлайн курсов
        location = request.POST.get('location', '')
        max_students = request.POST.get('max_students', None)
        
        # Данные для вебинаров
        webinar_link = request.POST.get('webinar_link', '')
        start_date = request.POST.get('start_date', None)
        
        # Валидация
        if not title or not description or not course_type:
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'instructor/create_course.html', {
                'categories': categories,
                'form_data': request.POST
            })
        
        try:
            # Создаем slug из названия
            from django.utils.text import slugify
            import time
            slug = slugify(title)
            # Добавляем timestamp если slug уже существует
            if Course.objects.filter(slug=slug).exists():
                slug = f"{slug}-{int(time.time())}"
            
            category = None
            if category_id:
                category = Category.objects.get(id=category_id)
            
            course = Course.objects.create(
                title=title,
                slug=slug,
                description=description,
                type=course_type,
                category=category,
                instructor=request.user,
                price=float(price) if price else 0,
                location=location if course_type == 'offline' else '',
                max_students=int(max_students) if max_students and course_type == 'offline' else None,
                webinar_link=webinar_link if course_type == 'webinar' else '',
                start_date=start_date if start_date else None,
                is_published=False  # Создаем как черновик
            )
            
            messages.success(request, f'Курс "{title}" успешно создан! Добавьте модули и уроки в админ-панели.')
            return redirect('instructor_dashboard')
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании курса: {str(e)}')
    
    context = {
        'categories': categories,
    }
    return render(request, 'instructor/create_course.html', context)


@login_required
def quiz_view(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course, lesson_type='quiz')
    
    # Проверяем, записан ли пользователь на курс
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Проверяем, есть ли квиз для этого урока
    if not hasattr(lesson, 'quiz'):
        messages.error(request, 'Квиз не настроен для этого урока.')
        return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
    
    quiz = lesson.quiz
    
    # Проверяем количество попыток
    attempts_count = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    if attempts_count >= quiz.max_attempts:
        messages.error(request, f'Вы исчерпали все попытки ({quiz.max_attempts}).')
        return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
    
    # Получаем все попытки пользователя
    user_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at')
    best_attempt = user_attempts.filter(is_passed=True).first()
    
    if request.method == 'POST':
        # Создаем новую попытку
        questions = quiz.questions.all()
        total_score = 0
        max_score = sum(q.points for q in questions)
        
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=0,
            max_score=max_score
        )
        
        # Обрабатываем ответы
        for question in questions:
            if question.question_type in ['single', 'multiple']:
                selected_option_ids = request.POST.getlist(f'question_{question.id}')
                answer = QuestionAnswer.objects.create(
                    attempt=attempt,
                    question=question
                )
                
                if selected_option_ids:
                    selected_options = question.options.filter(id__in=selected_option_ids)
                    answer.selected_options.set(selected_options)
                    
                    # Проверяем правильность ответа
                    if question.question_type == 'single':
                        correct_options = question.options.filter(is_correct=True)
                        if selected_options.count() == 1 and selected_options.first() in correct_options:
                            answer.is_correct = True
                            total_score += question.points
                    else:  # multiple
                        correct_options = set(question.options.filter(is_correct=True))
                        selected_options_set = set(selected_options)
                        if correct_options == selected_options_set:
                            answer.is_correct = True
                            total_score += question.points
                    
                    answer.save()
            
            elif question.question_type in ['text', 'number']:
                text_answer = request.POST.get(f'question_{question.id}', '').strip()
                answer = QuestionAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer=text_answer
                )
                
                # Простая проверка для текстовых ответов
                if question.correct_answer and text_answer.lower() == question.correct_answer.lower():
                    answer.is_correct = True
                    total_score += question.points
                    answer.save()
        
        # Обновляем результат попытки
        attempt.score = total_score
        attempt.completed_at = timezone.now()
        attempt.is_passed = (total_score / max_score * 100) >= quiz.passing_score
        attempt.save()
        
        # Если квиз пройден, отмечаем урок как завершенный
        if attempt.is_passed:
            if can_complete_lesson(enrollment, lesson):
                lesson_progress, created = LessonProgress.objects.get_or_create(
                    enrollment=enrollment,
                    lesson=lesson
                )
                if not lesson_progress.completed:
                    lesson_progress.completed = True
                    lesson_progress.completed_at = timezone.now()
                    lesson_progress.save()
                    
                    # Обновляем общий прогресс
                    enrollment.update_progress()
                
                messages.success(request, f'Поздравляем! Вы прошли квиз с результатом {total_score}/{max_score} ({total_score/max_score*100:.1f}%)')
            else:
                messages.warning(request, f'Квиз пройден ({total_score}/{max_score}), но необходимо завершить предыдущие уроки в модуле.')
        else:
            messages.warning(request, f'Квиз не пройден. Результат: {total_score}/{max_score} ({total_score/max_score*100:.1f}%). Необходимо: {quiz.passing_score}%')
        
        return redirect('lesson_detail', course_slug=course_slug, lesson_id=lesson_id)
    
    context = {
        'course': course,
        'lesson': lesson,
        'quiz': quiz,
        'attempts_count': attempts_count,
        'user_attempts': user_attempts[:5],  # Показываем только последние 5 попыток
        'best_attempt': best_attempt,
    }
    
    return render(request, 'courses/quiz_take.html', context)


@login_required 
def certificate_view(request, certificate_id):
    """Просмотр сертификата студентом"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, user=request.user)
    
    # Если PDF не существует, генерируем его
    if not certificate.pdf_file:
        certificate.generate_pdf()
    
    if certificate.pdf_file:
        # Возвращаем PDF файл для просмотра
        from django.http import HttpResponse
        response = HttpResponse(certificate.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="certificate_{certificate.certificate_id}.pdf"'
        return response
    else:
        messages.error(request, 'Ошибка при генерации сертификата. Попробуйте позже.')
        return redirect('my_courses')


def certificate_verify_view(request, certificate_id):
    """Публичная страница верификации сертификата"""
    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)
        context = {
            'certificate': certificate,
            'verified': True,
        }
    except Certificate.DoesNotExist:
        context = {
            'verified': False,
            'certificate_id': certificate_id,
        }
    
    return render(request, 'courses/certificate_verify.html', context)
