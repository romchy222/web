#!/usr/bin/env python
"""
Тестирование генерации сертификатов с улучшенным дизайном
"""
import os
import sys
import django

# Настройка Django
sys.path.append('c:/Users/USER/web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_platform.settings')
django.setup()

from courses.models import Certificate, Course, Enrollment
from users.models import User
from courses.russian_certificate_generator import generate_certificate_for_enrollment
import random


def test_certificate_generation():
    """Тестирует генерацию сертификата с новым дизайном"""
    
    print("🧪 Начинаем тестирование генерации сертификатов...")
    
    # Получаем пользователя и курс для теста
    user = User.objects.first()
    course = Course.objects.first()
    
    if not user or not course:
        print("❌ Нет пользователей или курсов для тестирования")
        return
    
    # Проверяем или создаем запись о прохождении курса
    enrollment, created = Enrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            'completed': True,
            'progress': 100
        }
    )
    
    # Обновляем запись для корректного тестирования
    enrollment.completed = True
    enrollment.progress = 100
    enrollment.save()
    
    print(f"📚 Тестируем для пользователя: {user.get_full_name()}")
    print(f"🎓 Курс: {course.title}")
    
    # Создаем или обновляем сертификат
    certificate, cert_created = Certificate.objects.get_or_create(
        user=user,
        course=course,
        enrollment=enrollment,
        defaults={
            'grade': random.randint(80, 100),  # Случайная оценка от 80 до 100
            'total_hours': random.randint(20, 50)  # Случайное количество часов
        }
    )
    
    if cert_created:
        print(f"✅ Создан новый сертификат: {certificate.certificate_id}")
    else:
        print(f"📋 Используется существующий сертификат: {certificate.certificate_id}")
    
    # Генерируем PDF с улучшенным дизайном
    try:
        print("🎨 Генерируем PDF с улучшенным дизайном...")
        generate_certificate_for_enrollment(certificate)
        
        if certificate.pdf_file:
            print(f"✅ PDF сертификата создан: {certificate.pdf_file.name}")
            print(f"📁 Файл сохранен: {certificate.pdf_file.path}")
            
            # Проверяем размер файла
            if os.path.exists(certificate.pdf_file.path):
                size = os.path.getsize(certificate.pdf_file.path) / 1024  # KB
                print(f"📊 Размер файла: {size:.1f} KB")
            
            print(f"🔗 URL для верификации: {certificate.verification_url}")
            print(f"🆔 ID сертификата: {certificate.certificate_id}")
            
        else:
            print("❌ PDF файл не создан")
            
    except Exception as e:
        print(f"❌ Ошибка при генерации PDF: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Тестирование завершено!")
    return certificate


if __name__ == "__main__":
    certificate = test_certificate_generation()