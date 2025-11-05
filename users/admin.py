from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'role', 'email_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'email_verified', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['role', 'email_verified']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar')}),
        ('Роли и права', {'fields': ('role', 'email_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'first_name', 'last_name', 'email', 'phone')
        }),
    )
    
    actions = ['make_instructor', 'make_student', 'verify_email']
    
    def make_instructor(self, request, queryset):
        updated = queryset.update(role='instructor')
        self.message_user(request, f'{updated} пользователей назначено преподавателями.')
    make_instructor.short_description = "Назначить преподавателями"
    
    def make_student(self, request, queryset):
        updated = queryset.update(role='student')
        self.message_user(request, f'{updated} пользователей назначено студентами.')
    make_student.short_description = "Назначить студентами"
    
    def verify_email(self, request, queryset):
        updated = queryset.update(email_verified=True)
        self.message_user(request, f'Email подтвержден для {updated} пользователей.')
    verify_email.short_description = "Подтвердить email"
