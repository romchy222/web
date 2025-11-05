from django.contrib import admin
from .models import (Category, Course, Module, Lesson, LessonAttachment,
                     Enrollment, LessonProgress, ModuleProgress, Attendance, Review, Quiz, Question,
                     QuestionOption, Assignment, QuizAttempt, AssignmentSubmission, Certificate)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class LessonAttachmentInline(admin.TabularInline):
    model = LessonAttachment
    extra = 1


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'instructor', 'price', 'is_published', 'enrollments_count', 'created_at']
    list_filter = ['type', 'is_published', 'category', 'instructor']
    search_fields = ['title', 'description', 'instructor__username', 'instructor__first_name', 'instructor__last_name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    raw_id_fields = ['instructor']
    list_editable = ['is_published', 'price']
    readonly_fields = ['created_at', 'updated_at', 'enrollments_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'category', 'instructor', 'image')
        }),
        ('Настройки курса', {
            'fields': ('type', 'price', 'is_published')
        }),
        ('Для офлайн курсов', {
            'fields': ('location', 'max_students'),
            'classes': ('collapse',)
        }),
        ('Для вебинаров', {
            'fields': ('webinar_link', 'start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('enrollments_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def enrollments_count(self, obj):
        return obj.enrollments.count()
    enrollments_count.short_description = 'Записано студентов'
    
    actions = ['make_published', 'make_unpublished']
    
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} курсов опубликовано.')
    make_published.short_description = "Опубликовать выбранные курсы"
    
    def make_unpublished(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} курсов скрыто.')
    make_unpublished.short_description = "Скрыть выбранные курсы"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson_type', 'module', 'order', 'duration', 'is_required']
    list_filter = ['lesson_type', 'is_required', 'module__course']
    list_editable = ['lesson_type', 'order', 'is_required']
    inlines = [LessonAttachmentInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'lesson_type', 'module', 'order', 'is_required')
        }),
        ('Контент', {
            'fields': ('content', 'duration')
        }),
        ('Медиа', {
            'fields': ('video_url', 'video_file'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'completed', 'completed_at']
    list_filter = ['completed', 'course__type', 'course__category', 'enrolled_at']
    search_fields = ['user__username', 'user__email', 'course__title']
    raw_id_fields = ['user', 'course']
    readonly_fields = ['enrolled_at', 'completed_at']
    list_editable = ['progress', 'completed']
    date_hierarchy = 'enrolled_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'course', 'enrolled_at')
        }),
        ('Прогресс', {
            'fields': ('progress', 'completed', 'completed_at')
        }),
    )
    
    actions = ['mark_completed', 'reset_progress']
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(completed=True, progress=100, completed_at=timezone.now())
        self.message_user(request, f'{updated} записей отмечено как завершенные.')
    mark_completed.short_description = "Отметить как завершенные"
    
    def reset_progress(self, request, queryset):
        updated = queryset.update(progress=0, completed=False, completed_at=None)
        self.message_user(request, f'Прогресс сброшен для {updated} записей.')
    reset_progress.short_description = "Сбросить прогресс"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed']


# Удалена дублированная регистрация ModuleProgress - см. ниже


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'date', 'present']
    list_filter = ['present', 'date']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'passing_score', 'max_attempts', 'time_limit']
    list_filter = ['lesson__module__course', 'passing_score']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'quiz', 'points']
    list_filter = ['question_type', 'quiz__lesson__module__course']
    inlines = [QuestionOptionInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'due_date', 'max_file_size']
    list_filter = ['lesson__module__course', 'due_date']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'max_score', 'is_passed', 'completed_at']
    list_filter = ['is_passed', 'quiz__lesson__module__course', 'completed_at']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment', 'status', 'grade', 'submitted_at']
    list_filter = ['status', 'assignment__lesson__module__course', 'submitted_at']
    list_editable = ['status', 'grade']
    readonly_fields = ['submitted_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'assignment', 'file', 'comment', 'submitted_at')
        }),
        ('Проверка', {
            'fields': ('status', 'grade', 'instructor_feedback', 'reviewed_at')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'user__username']


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'module', 'get_completed_lessons', 'get_total_lessons', 'progress_percentage', 'completed', 'completed_at']
    list_filter = ['completed', 'completed_at', 'module__course']
    search_fields = ['enrollment__user__username', 'enrollment__user__email', 'module__title']
    readonly_fields = ['progress_percentage', 'completed_at', 'get_completed_lessons', 'get_total_lessons']
    
    def get_completed_lessons(self, obj):
        return obj.completed_lessons
    get_completed_lessons.short_description = "Завершено уроков"
    
    def get_total_lessons(self, obj):
        return obj.total_lessons
    get_total_lessons.short_description = "Всего уроков"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'user', 'course', 'grade', 'total_hours', 'issued_at']
    list_filter = ['issued_at', 'course', 'course__type']
    search_fields = ['certificate_id', 'user__username', 'user__email', 'course__title']
    readonly_fields = ['certificate_id', 'issued_at', 'verification_url']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'course', 'enrollment', 'certificate_id', 'issued_at')
        }),
        ('Детали завершения', {
            'fields': ('completion_date', 'grade', 'total_hours')
        }),
        ('Файлы и проверка', {
            'fields': ('pdf_file', 'verification_url')
        }),
    )
    
    def has_add_permission(self, request):
        # Сертификаты создаются автоматически, не разрешаем ручное создание
        return False
