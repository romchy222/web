#!/usr/bin/env python
"""
Создание тестовых сертификатов с разными оценками для демонстрации дизайна
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


def create_sample_certificates():
    """Создает несколько образцов сертификатов с разными оценками"""
    
    print("🎨 Создаем образцы сертификатов с разным дизайном...")
    
    user = User.objects.first()
    courses = list(Course.objects.all()[:3])  # Берем до 3 курсов
    
    if not user or not courses:
        print("❌ Недостаточно данных для создания образцов")
        return
    
    # Разные варианты оценок для демонстрации цветов
    grade_samples = [
        (95, "Отличная оценка - золотой цвет"),
        (85, "Хорошая оценка - синий цвет"), 
        (75, "Удовлетворительная оценка - зеленый цвет")
    ]
    
    certificates = []
    
    for i, (grade, description) in enumerate(grade_samples):
        if i < len(courses):
            course = courses[i]
            
            # Создаем enrollment
            enrollment, _ = Enrollment.objects.get_or_create(
                user=user,
                course=course,
                defaults={'completed': True, 'progress': 100}
            )
            
            # Удаляем старый сертификат если есть
            Certificate.objects.filter(user=user, course=course).delete()
            
            # Создаем новый сертификат
            certificate = Certificate.objects.create(
                user=user,
                course=course,
                enrollment=enrollment,
                grade=grade,
                total_hours=30 + i * 10  # 30, 40, 50 часов
            )
            
            print(f"📜 {description}: {certificate.certificate_id} (оценка: {grade})")
            
            # Генерируем PDF
            try:
                generate_certificate_for_enrollment(certificate)
                if certificate.pdf_file:
                    print(f"   ✅ PDF создан: {certificate.pdf_file.name}")
                    certificates.append(certificate)
                else:
                    print(f"   ❌ Не удалось создать PDF")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
    
    print(f"\n🎉 Создано {len(certificates)} образцов сертификатов!")
    
    # Выводим информацию для проверки
    print("\n📋 Созданные сертификаты:")
    for cert in certificates:
        print(f"   🆔 {cert.certificate_id} - Оценка: {cert.grade} - {cert.course.title}")
        print(f"      🔗 Верификация: http://127.0.0.1:8000/verify/{cert.certificate_id}/")
    
    return certificates


if __name__ == "__main__":
    create_sample_certificates()