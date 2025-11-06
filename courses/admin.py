from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Course, Module, Lesson, LessonAttachment,
                     Enrollment, LessonProgress, Attendance, Review,
                     Quiz, Question, Answer, QuizAttempt, QuizAnswer, Certificate,
                     Notification)
from .models_settings import PlatformSettings, CourseApplication


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for platform mode toggle.
    Displayed prominently at the top of admin.
    """
    def has_add_permission(self, request):
        # Only one instance allowed (singleton)
        return not PlatformSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Cannot delete the settings
        return False
    
    list_display = ['mode_display', 'landing_page_title', 'application_form_enabled', 'updated_at']
    fields = [
        'mode',
        'landing_page_title',
        'landing_page_description',
        'application_form_enabled',
    ]
    
    def mode_display(self, obj):
        if obj.mode == 'lms':
            color = '#28a745'  # green
            icon = '🎓'
        else:
            color = '#ffc107'  # yellow
            icon = '📝'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{} {}</span>',
            color, icon, obj.get_mode_display()
        )
    mode_display.short_description = 'Current Mode'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '⚙️ Platform Mode Settings'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CourseApplication)
class CourseApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing course pre-registration applications
    """
    list_display = ['first_name', 'last_name', 'email', 'phone', 'course_interest', 'submitted_at', 'processed_badge']
    list_filter = ['processed', 'submitted_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'course_interest']
    readonly_fields = ['submitted_at']
    list_editable = []
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Application Details', {
            'fields': ('course_interest', 'message', 'submitted_at')
        }),
        ('Processing', {
            'fields': ('processed', 'notes')
        }),
    )
    
    def processed_badge(self, obj):
        if obj.processed:
            return format_html('<span style="color: green;">✓ Processed</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    processed_badge.short_description = 'Status'
    
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    def mark_as_processed(self, request, queryset):
        count = queryset.update(processed=True)
        self.message_user(request, f'{count} application(s) marked as processed.')
    mark_as_processed.short_description = 'Mark selected as processed'
    
    def mark_as_unprocessed(self, request, queryset):
        count = queryset.update(processed=False)
        self.message_user(request, f'{count} application(s) marked as unprocessed.')
    mark_as_unprocessed.short_description = 'Mark selected as unprocessed'


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class LessonAttachmentInline(admin.TabularInline):
    model = LessonAttachment
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'instructor', 'price', 'is_published', 'created_at']
    list_filter = ['type', 'is_published', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    raw_id_fields = ['instructor']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'duration']
    list_filter = ['module__course']
    inlines = [LessonAttachmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'completed']
    list_filter = ['completed', 'course__type']
    search_fields = ['user__username', 'course__title']
    raw_id_fields = ['user', 'course']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'date', 'present']
    list_filter = ['present', 'date']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'user__username']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score']
    list_filter = ['lesson__module__course']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text', 'question_type', 'points', 'order']
    list_filter = ['question_type']
    inlines = [AnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'quiz', 'score', 'passed', 'completed_at']
    list_filter = ['passed', 'completed_at']
    search_fields = ['enrollment__user__username', 'quiz__title']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'enrollment', 'issued_at']
    search_fields = ['certificate_number', 'enrollment__user__username', 'enrollment__course__title']
    readonly_fields = ['certificate_number', 'issued_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
