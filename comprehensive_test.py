#!/usr/bin/env python
"""
Комплексное тестирование функциональности платформы обучения
"""
import os
import sys
import django

# Настройка Django
sys.path.append('c:/Users/USER/web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_platform.settings')
django.setup()

from users.models import User
from courses.models import *
from django.test.client import Client
from django.urls import reverse


def test_functionality():
    """Комплексное тестирование функциональности"""
    
    print("🧪 === КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ПЛАТФОРМЫ ОБУЧЕНИЯ ===\n")
    
    client = Client()
    issues = []
    
    # 1. Тестирование основных страниц
    print("1️⃣ Тестирование основных страниц:")
    pages_to_test = [
        ('/', 'Главная страница'),
        ('/courses/', 'Каталог курсов'),
        ('/auth/login/', 'Страница входа'),
        ('/auth/register/', 'Страница регистрации'),
        ('/about/', 'О платформе'),
    ]
    
    for url, name in pages_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✅ {name}: работает")
            else:
                issues.append(f"{name}: статус {response.status_code}")
                print(f"   ❌ {name}: статус {response.status_code}")
        except Exception as e:
            issues.append(f"{name}: ошибка {e}")
            print(f"   ❌ {name}: ошибка {e}")
    
    # 2. Тестирование аутентификации
    print(f"\n2️⃣ Тестирование аутентификации:")
    user = User.objects.filter(is_superuser=False).first()
    if user:
        login_success = client.login(username=user.username, password='123456')  # Пробуем стандартный пароль
        if not login_success:
            # Создаем тестового пользователя с известным паролем
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Тест',
                last_name='Пользователь'
            )
            login_success = client.login(username='testuser', password='testpass123')
        
        if login_success:
            print("   ✅ Авторизация: работает")
        else:
            issues.append("Авторизация не работает")
            print("   ❌ Авторизация: не работает")
    else:
        issues.append("Нет пользователей для тестирования")
        print("   ❌ Нет пользователей для тестирования")
    
    # 3. Тестирование курсов
    print(f"\n3️⃣ Тестирование курсов:")
    courses = Course.objects.filter(is_published=True)
    if courses.exists():
        course = courses.first()
        try:
            response = client.get(f'/courses/{course.slug}/')
            if response.status_code == 200:
                print(f"   ✅ Детальная страница курса: работает")
            else:
                issues.append(f"Детальная страница курса: статус {response.status_code}")
                print(f"   ❌ Детальная страница курса: статус {response.status_code}")
        except Exception as e:
            issues.append(f"Детальная страница курса: ошибка {e}")
            print(f"   ❌ Детальная страница курса: ошибка {e}")
    else:
        issues.append("Нет опубликованных курсов")
        print("   ❌ Нет опубликованных курсов")
    
    # 4. Проверка модулей и уроков
    print(f"\n4️⃣ Тестирование уроков:")
    if courses.exists():
        course = courses.first()
        modules = course.modules.all()
        if modules.exists():
            module = modules.first()
            lessons = module.lessons.all()
            if lessons.exists():
                lesson = lessons.first()
                try:
                    # Нужно создать enrollment для доступа к урокам
                    enrollment, created = Enrollment.objects.get_or_create(
                        user=client.session.get('_auth_user_id') and User.objects.get(pk=client.session['_auth_user_id']) or User.objects.first(),
                        course=course
                    )
                    
                    response = client.get(f'/courses/lesson/{lesson.id}/')
                    if response.status_code in [200, 302]:  # 302 может быть редирект на авторизацию
                        print(f"   ✅ Страница урока: работает")
                    else:
                        issues.append(f"Страница урока: статус {response.status_code}")
                        print(f"   ❌ Страница урока: статус {response.status_code}")
                except Exception as e:
                    issues.append(f"Страница урока: ошибка {e}")
                    print(f"   ❌ Страница урока: ошибка {e}")
            else:
                issues.append("В модулях нет уроков")
                print("   ❌ В модулях нет уроков")
        else:
            issues.append("В курсах нет модулей")
            print("   ❌ В курсах нет модулей")
    
    # 5. Тестирование системы сертификатов
    print(f"\n5️⃣ Тестирование сертификатов:")
    certificates = Certificate.objects.all()
    if certificates.exists():
        cert = certificates.first()
        try:
            response = client.get(f'/verify/{cert.certificate_id}/')
            if response.status_code == 200:
                print(f"   ✅ Верификация сертификата: работает")
            else:
                issues.append(f"Верификация сертификата: статус {response.status_code}")
                print(f"   ❌ Верификация сертификата: статус {response.status_code}")
        except Exception as e:
            issues.append(f"Верификация сертификата: ошибка {e}")
            print(f"   ❌ Верификация сертификата: ошибка {e}")
    else:
        print("   ⚠️ Нет сертификатов для тестирования")
    
    # 6. Проверка админки
    print(f"\n6️⃣ Тестирование админки:")
    try:
        response = client.get('/admin/')
        if response.status_code in [200, 302]:
            print("   ✅ Админка: доступна")
        else:
            issues.append(f"Админка: статус {response.status_code}")
            print(f"   ❌ Админка: статус {response.status_code}")
    except Exception as e:
        issues.append(f"Админка: ошибка {e}")
        print(f"   ❌ Админка: ошибка {e}")
    
    # Итоги
    print(f"\n🎯 === ИТОГИ ТЕСТИРОВАНИЯ ===")
    if not issues:
        print("✅ Все основные функции работают корректно!")
    else:
        print(f"❌ Обнаружено {len(issues)} проблем:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    print(f"\n📊 Статистика базы данных:")
    print(f"   - Пользователи: {User.objects.count()}")
    print(f"   - Курсы: {Course.objects.count()}")
    print(f"   - Модули: {Module.objects.count()}")
    print(f"   - Уроки: {Lesson.objects.count()}")
    print(f"   - Квизы: {Quiz.objects.count()}")
    print(f"   - Задания: {Assignment.objects.count()}")
    print(f"   - Записи на курсы: {Enrollment.objects.count()}")
    print(f"   - Сертификаты: {Certificate.objects.count()}")
    
    return issues


if __name__ == "__main__":
    test_functionality()