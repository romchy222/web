"""
Скрипт для тестирования системы сертификатов
"""
import os
import sys
import django

# Настройка Django окружения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_platform.settings')
django.setup()

from courses.models import Course, Enrollment, Certificate
from users.models import User

def test_certificate_system():
    """Тестирует систему сертификатов"""
    
    # Создаем тестового пользователя
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'student@test.com',
            'first_name': 'Иван',
            'last_name': 'Петров'
        }
    )
    
    # Получаем курс
    try:
        course = Course.objects.first()
        if not course:
            print("Курсы не найдены. Сначала создайте тестовые данные с помощью: python manage.py create_sample_data")
            return
        
        # Создаем запись на курс
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'progress': 100,
                'completed': True
            }
        )
        
        # Если курс не завершен, завершаем его принудительно для теста
        if not enrollment.completed:
            enrollment.completed = True
            enrollment.progress = 100
            enrollment.save()
            
            # Принудительно создаем сертификат для теста
            enrollment.create_certificate()
        
        # Проверяем сертификат
        if hasattr(enrollment, 'certificate'):
            certificate = enrollment.certificate
            print(f"✅ Сертификат создан: {certificate.certificate_id}")
            print(f"📅 Дата выдачи: {certificate.issued_at}")
            print(f"🎓 Курс: {certificate.course.title}")
            print(f"👤 Студент: {certificate.user.get_full_name()}")
            print(f"📄 PDF файл: {'✅ Создан' if certificate.pdf_file else '❌ Не создан'}")
            print(f"🔗 Ссылка для проверки: http://127.0.0.1:8000{certificate.verification_url}")
            
            if certificate.grade:
                print(f"📊 Оценка: {certificate.grade}")
            if certificate.total_hours:
                print(f"⏰ Часов: {certificate.total_hours}")
                
        else:
            print("❌ Сертификат не создан")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_certificate_system()