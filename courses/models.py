from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'


class Course(models.Model):
    TYPE_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('webinar', 'Webinar'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teaching_courses')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    
    # For offline courses
    location = models.CharField(max_length=255, blank=True)
    max_students = models.PositiveIntegerField(null=True, blank=True)
    
    # For webinars
    webinar_link = models.URLField(blank=True)
    
    # Dates
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
    
    class Meta:
        ordering = ['-created_at']


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    LESSON_TYPES = (
        ('text', 'Текстовый урок'),
        ('video', 'Видео урок'),
        ('quiz', 'Квиз'),
        ('assignment', 'Домашнее задание'),
    )
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='text')
    content = models.TextField()
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(help_text='Duration in minutes', null=True, blank=True)
    is_required = models.BooleanField(default=True, help_text='Обязательный ли урок для завершения курса')
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    class Meta:
        ordering = ['order']


class LessonAttachment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='lessons/attachments/')
    title = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)  # Progress percentage
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        unique_together = ['user', 'course']
    
    def update_progress(self):
        """Обновляет общий прогресс по курсу на основе завершенных модулей"""
        modules = self.course.modules.all()
        completed_modules = 0
        
        for module in modules:
            module_progress, created = ModuleProgress.objects.get_or_create(
                enrollment=self,
                module=module
            )
            if module_progress.update_progress():
                completed_modules += 1
        
        if modules.count() == 0:
            self.progress = 100
        else:
            self.progress = int((completed_modules / modules.count()) * 100)
        
        # Курс считается завершенным только если все модули завершены
        if self.progress == 100 and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            
            # Создаем сертификат при завершении курса
            self.create_certificate()
            
        elif self.progress < 100:
            self.completed = False
            self.completed_at = None
            self.save()
        else:
            self.save()
        
        return self.completed
    
    def create_certificate(self):
        """Создает сертификат для завершенного курса"""
        if not self.completed:
            return None
            
        # Проверяем, не создан ли уже сертификат
        if hasattr(self, 'certificate'):
            return self.certificate
            
        # Вычисляем общую оценку на основе квизов и заданий
        grade = self.calculate_final_grade()
        
        # Вычисляем общее время курса
        total_hours = self.course.modules.aggregate(
            total_duration=models.Sum('lessons__duration')
        )['total_duration'] or 0
        total_hours = round(total_hours / 60, 1)  # Конвертируем минуты в часы
        
        certificate = Certificate.objects.create(
            user=self.user,
            course=self.course,
            enrollment=self,
            completion_date=self.completed_at,
            grade=grade,
            total_hours=total_hours
        )
        
        return certificate
    
    def calculate_final_grade(self):
        """Вычисляет итоговую оценку студента по курсу"""
        quiz_scores = []
        assignment_scores = []
        
        # Получаем оценки за квизы
        for module in self.course.modules.all():
            for lesson in module.lessons.filter(lesson_type='quiz'):
                quiz = getattr(lesson, 'quiz', None)
                if quiz:
                    attempt = QuizAttempt.objects.filter(
                        user=self.user,
                        quiz=quiz,
                        is_passed=True
                    ).first()
                    if attempt:
                        quiz_scores.append(attempt.score)
        
        # Получаем оценки за задания
        assignments = AssignmentSubmission.objects.filter(
            user=self.user,
            assignment__lesson__module__course=self.course,
            grade__isnull=False
        )
        assignment_scores = [sub.grade for sub in assignments]
        
        # Вычисляем среднюю оценку
        all_scores = quiz_scores + assignment_scores
        if all_scores:
            return sum(all_scores) / len(all_scores)
        
        return None
    
    def get_next_lesson(self):
        """Возвращает следующий незавершенный урок"""
        for module in self.course.modules.all():
            for lesson in module.lessons.all():
                lesson_progress = LessonProgress.objects.filter(
                    enrollment=self,
                    lesson=lesson,
                    completed=True
                ).first()
                if not lesson_progress:
                    return lesson
        return None


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title}"
    
    class Meta:
        unique_together = ['enrollment', 'lesson']


class ModuleProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.module.title}"
    
    class Meta:
        unique_together = ['enrollment', 'module']
    
    def update_progress(self):
        """Обновляет прогресс по модулю на основе завершенных уроков"""
        required_lessons = self.module.lessons.filter(is_required=True)
        completed_required_lessons = LessonProgress.objects.filter(
            enrollment=self.enrollment,
            lesson__in=required_lessons,
            completed=True
        ).count()
        
        if required_lessons.count() == 0:
            self.progress_percentage = 100
            self.completed = True
        else:
            self.progress_percentage = int((completed_required_lessons / required_lessons.count()) * 100)
            self.completed = self.progress_percentage == 100
        
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
            
        self.save()
        return self.completed


class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    present = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.date}"
    
    class Meta:
        unique_together = ['enrollment', 'date']


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    passing_score = models.PositiveIntegerField(default=70, help_text='Проходной балл в процентах')
    max_attempts = models.PositiveIntegerField(default=3, help_text='Максимальное количество попыток')
    time_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Лимит времени в минутах')
    
    def __str__(self):
        return f"Квиз: {self.lesson.title}"


class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Одиночный выбор'),
        ('multiple', 'Множественный выбор'),
        ('text', 'Текстовый ответ'),
        ('number', 'Числовой ответ'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    correct_answer = models.TextField(blank=True, help_text='Правильный ответ для текстовых/числовых вопросов')
    
    def __str__(self):
        return f"{self.quiz.lesson.title} - {self.question_text[:50]}"
    
    class Meta:
        ordering = ['order']


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.option_text[:30]}"
    
    class Meta:
        ordering = ['order']


class Assignment(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment')
    instructions = models.TextField(help_text='Инструкции к заданию')
    due_date = models.DateTimeField(null=True, blank=True, help_text='Срок сдачи')
    max_file_size = models.PositiveIntegerField(default=10, help_text='Максимальный размер файла в МБ')
    allowed_file_types = models.CharField(max_length=200, default='.pdf,.doc,.docx,.txt', 
                                        help_text='Разрешенные типы файлов через запятую')
    
    def __str__(self):
        return f"Задание: {self.lesson.title}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.lesson.title} ({self.score}/{self.max_score})"
    
    class Meta:
        ordering = ['-started_at']


class QuestionAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(QuestionOption, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.question_text[:30]}"


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Отправлено'),
        ('reviewed', 'Проверено'),
        ('approved', 'Принято'),
        ('rejected', 'Отклонено'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='assignments/')
    comment = models.TextField(blank=True, help_text='Комментарий студента')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    grade = models.PositiveIntegerField(null=True, blank=True, help_text='Оценка от 0 до 100')
    instructor_feedback = models.TextField(blank=True, help_text='Отзыв преподавателя')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.assignment.lesson.title}"
    
    class Meta:
        unique_together = ['user', 'assignment']
        ordering = ['-submitted_at']


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}★)"
    
    class Meta:
        unique_together = ['course', 'user']


class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField('Enrollment', on_delete=models.CASCADE, related_name='certificate')
    certificate_id = models.CharField(max_length=32, unique=True)  # Уникальный номер сертификата
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    
    # Дополнительные поля для сертификата
    completion_date = models.DateTimeField()
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Итоговая оценка
    total_hours = models.PositiveIntegerField(null=True, blank=True)  # Общее количество часов
    
    def __str__(self):
        return f"Сертификат {self.certificate_id} - {self.user.get_full_name()} ({self.course.title})"
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = uuid.uuid4().hex[:16].upper()
        
        if not self.completion_date:
            self.completion_date = timezone.now()
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Генерируем PDF для нового сертификата
        if is_new and not self.pdf_file:
            self.generate_pdf()
    
    def generate_pdf(self):
        """Генерирует PDF сертификата"""
        try:
            from .russian_certificate_generator import generate_certificate_for_enrollment
            generate_certificate_for_enrollment(self)
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Ошибка при генерации PDF сертификата: {e}")
    
    @property
    def verification_url(self):
        from django.urls import reverse
        return reverse('certificate_verify', kwargs={'certificate_id': self.certificate_id})
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-issued_at']
