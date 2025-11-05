from django.db import models
from django.conf import settings
import uuid


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
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(help_text='Duration in minutes', null=True, blank=True)
    
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


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title}"
    
    class Meta:
        unique_together = ['enrollment', 'lesson']


class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    present = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.date}"
    
    class Meta:
        unique_together = ['enrollment', 'date']


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


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70, help_text='Minimum percentage to pass')
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('text', 'Text Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single')
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"
    
    class Meta:
        ordering = ['order']


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.quiz.title} - {self.text[:50]}"


class QuizAttempt(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.quiz.title} ({self.score}%)"
    
    class Meta:
        ordering = ['-completed_at']


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.attempt.enrollment.user.username} - {self.question.text[:50]}"


class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Certificate #{self.certificate_number} - {self.enrollment.user.username}"
    
    def generate_certificate_number(self):
        return f"CERT-{uuid.uuid4().hex[:8].upper()}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('enrollment', 'Enrollment'),
        ('completion', 'Course Completion'),
        ('certificate', 'Certificate Issued'),
        ('review', 'New Review'),
        ('announcement', 'Announcement'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']
