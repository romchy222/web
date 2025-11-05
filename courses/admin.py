from django.contrib import admin
from .models import (Category, Course, Module, Lesson, LessonAttachment,
                     Enrollment, LessonProgress, Attendance, Review,
                     Quiz, Question, Answer, QuizAttempt, QuizAnswer, Certificate)


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
