from django.db import models


class PlatformSettings(models.Model):
    """
    Singleton model to store platform-wide settings.
    Only one instance should exist.
    """
    MODE_CHOICES = (
        ('lms', 'LMS Mode - Full Learning Platform'),
        ('applications', 'Applications Mode - Pre-registration Landing Page'),
    )
    
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='lms',
        verbose_name='Platform Mode',
        help_text='Select the platform operation mode'
    )
    
    # Landing page settings for application mode
    landing_page_title = models.CharField(
        max_length=200,
        default='Скоро открытие!',
        verbose_name='Landing Page Title'
    )
    landing_page_description = models.TextField(
        default='Мы готовим для вас лучшую платформу для обучения. Оставьте заявку, и мы уведомим вас о старте.',
        verbose_name='Landing Page Description'
    )
    application_form_enabled = models.BooleanField(
        default=True,
        verbose_name='Enable Application Form'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Platform Settings'
        verbose_name_plural = 'Platform Settings'
    
    def __str__(self):
        return f"Platform Settings - {self.get_mode_display()}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and PlatformSettings.objects.exists():
            # If instance exists, update it instead of creating new
            existing = PlatformSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={'mode': 'lms'}
        )
        return settings


class CourseApplication(models.Model):
    """
    Model to store pre-registration applications when platform is in application mode
    """
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    course_interest = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Интересующий курс'
    )
    message = models.TextField(blank=True, verbose_name='Сообщение')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи')
    processed = models.BooleanField(default=False, verbose_name='Обработано')
    notes = models.TextField(blank=True, verbose_name='Заметки администратора')
    
    class Meta:
        verbose_name = 'Course Application'
        verbose_name_plural = 'Course Applications'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
