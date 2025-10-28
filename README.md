# Платформа Курсов

Онлайн-платформа для обучения с тремя форматами: онлайн-курсы, офлайн-курсы и вебинары.

## Особенности

- 🎓 **Онлайн-курсы** - самостоятельное обучение в удобном темпе
- 🏫 **Офлайн-курсы** - занятия с расписанием и преподавателем
- 📹 **Вебинары** - трансляции в реальном времени
- 👥 **Роли пользователей** - студент, преподаватель, администратор
- 📊 **Отслеживание прогресса** - статистика по урокам и курсам
- 🔐 **JWT аутентификация** - безопасная авторизация
- 📱 **Responsive дизайн** - адаптация под все устройства

## Технологии

- **Backend**: Django 5.2, Django REST Framework
- **Database**: SQLite (можно переключить на PostgreSQL)
- **Authentication**: JWT (Simple JWT)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Media**: Pillow для обработки изображений

## Установка

1. **Клонировать репозиторий**:
```bash
cd C:\Users\roman\Desktop\Web
```

2. **Установить зависимости**:
```bash
pip install -r requirements.txt
```

3. **Применить миграции**:
```bash
python manage.py migrate
```

4. **Создать суперпользователя**:
```bash
python manage.py createsuperuser
```

5. **Запустить сервер**:
```bash
python manage.py runserver
```

Сайт будет доступен по адресу: `http://127.0.0.1:8000`

## Структура проекта

```
Web/
├── course_platform/     # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/              # Приложение пользователей
│   ├── models.py       # Модель User с ролями
│   ├── serializers.py  # Сериализаторы для API
│   ├── views.py        # API views
│   └── admin.py        # Админ панель
├── courses/            # Приложение курсов
│   ├── models.py       # Course, Module, Lesson, Enrollment и др.
│   ├── serializers.py  # Сериализаторы для API
│   ├── views.py        # API views с фильтрацией
│   └── admin.py        # Админ панель
├── templates/          # HTML шаблоны
├── static/            # Статические файлы
├── media/             # Загруженные файлы
└── manage.py
```

## API Endpoints

### Пользователи
- `POST /api/users/register/` - Регистрация
- `POST /api/users/login/` - Вход (получение JWT токена)
- `POST /api/users/token/refresh/` - Обновление токена
- `GET /api/users/profile/` - Профиль текущего пользователя
- `PUT /api/users/profile/` - Обновление профиля

### Курсы
- `GET /api/courses/` - Список курсов (с фильтрами)
- `GET /api/courses/{slug}/` - Детали курса
- `POST /api/courses/` - Создать курс (для преподавателей)
- `POST /api/courses/{slug}/enroll/` - Записаться на курс
- `GET /api/courses/{slug}/my_progress/` - Мой прогресс

### Модули и уроки
- `GET /api/modules/?course={slug}` - Модули курса
- `GET /api/lessons/` - Список уроков
- `POST /api/lessons/{id}/mark_complete/` - Отметить урок как завершённый

### Записи
- `GET /api/enrollments/` - Мои записи на курсы

### Отзывы
- `GET /api/reviews/?course={slug}` - Отзывы на курс
- `POST /api/reviews/` - Добавить отзыв

## Фильтры курсов

Примеры запросов:
- `/api/courses/?type=online` - Только онлайн-курсы
- `/api/courses/?type=webinar` - Только вебинары
- `/api/courses/?category=1` - Курсы по категории
- `/api/courses/?search=python` - Поиск по названию

## Роли пользователей

1. **Студент** (student)
   - Просмотр курсов
   - Запись на курсы
   - Отслеживание прогресса
   - Добавление отзывов

2. **Преподаватель** (instructor)
   - Все возможности студента
   - Создание и редактирование своих курсов
   - Управление модулями и уроками
   - Просмотр посещаемости

3. **Администратор** (admin)
   - Полный доступ ко всем функциям
   - Модерация контента
   - Управление пользователями
   - Просмотр статистики

## Админ панель

Доступ: `http://127.0.0.1:8000/admin/`

Возможности:
- Управление пользователями и их ролями
- Модерация курсов, модулей, уроков
- Просмотр записей и прогресса студентов
- Управление категориями
- Просмотр отзывов

## Безопасность

Реализованы защиты от:
- XSS атак (Django template auto-escaping)
- CSRF атак (CSRF middleware)
- SQL инъекций (Django ORM)
- Небезопасных запросов (CORS настройки)

## Разработка

Для разработки frontend можно настроить CORS для подключения React/Vue приложения:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
```

## Тестирование

```bash
python manage.py test
```

## Деплой

1. Изменить `DEBUG = False` в settings.py
2. Настроить `ALLOWED_HOSTS`
3. Использовать PostgreSQL вместо SQLite
4. Настроить сбор статики: `python manage.py collectstatic`
5. Использовать gunicorn или uwsgi для WSGI сервера

## Лицензия

MIT License

## Автор

Разработано согласно ТЗ платформы курсов
