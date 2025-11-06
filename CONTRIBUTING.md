# Contributing to Course Platform

Спасибо за интерес к проекту! Мы приветствуем вклад от сообщества.

## Как внести вклад

### Сообщение об ошибках

Если вы нашли ошибку:

1. Проверьте, не была ли она уже сообщена в [Issues](https://github.com/yourusername/course-platform/issues)
2. Если нет, создайте новый issue с подробным описанием:
   - Шаги для воспроизведения
   - Ожидаемое поведение
   - Фактическое поведение
   - Версия Python, Django и других зависимостей
   - Скриншоты (если применимо)

### Предложение новых функций

1. Создайте issue с описанием предлагаемой функции
2. Объясните, почему эта функция будет полезна
3. Дождитесь обсуждения перед началом разработки

### Pull Requests

1. **Fork** репозитория
2. **Создайте ветку** для вашей функции:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Внесите изменения** следуя стилю кода проекта
4. **Добавьте тесты** для новой функциональности
5. **Убедитесь, что все тесты проходят**:
   ```bash
   python manage.py test
   ```
6. **Commit** изменений:
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push** в ваш fork:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Создайте Pull Request** в основной репозиторий

## Стандарты кода

### Python/Django

- Следуйте [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Используйте meaningful имена переменных
- Документируйте сложные функции docstrings
- Максимальная длина строки: 120 символов

```python
def calculate_course_progress(enrollment):
    """
    Calculate the progress percentage for a course enrollment.
    
    Args:
        enrollment: Enrollment instance
    
    Returns:
        int: Progress percentage (0-100)
    """
    total_lessons = enrollment.course.lessons.count()
    if total_lessons == 0:
        return 0
    
    completed = enrollment.lesson_progress.filter(completed=True).count()
    return int((completed / total_lessons) * 100)
```

### JavaScript

- Используйте современный ES6+ синтаксис
- Добавляйте комментарии для сложной логики
- Используйте `const` и `let` вместо `var`

```javascript
// Good
const fetchCourses = async () => {
    try {
        const response = await fetch('/api/courses/');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching courses:', error);
    }
};

// Avoid
var fetchCourses = function() {
    // old style code
};
```

### HTML/Templates

- Используйте семантические HTML5 теги
- Добавляйте ARIA атрибуты для доступности
- Следуйте структуре Django templates

```html
{% extends 'base.html' %}

{% block title %}{{ course.title }}{% endblock %}

{% block content %}
<article class="course-detail">
    <header>
        <h1>{{ course.title }}</h1>
    </header>
    
    <section class="course-content">
        {{ course.description }}
    </section>
</article>
{% endblock %}
```

### CSS

- Используйте CSS custom properties для цветов
- Следуйте BEM методологии для классов
- Мобильный-первый подход (mobile-first)

```css
/* Good */
.course-card {
    padding: var(--spacing-md);
}

.course-card__title {
    color: var(--primary-color);
}

.course-card__title--featured {
    font-weight: bold;
}

/* Avoid */
.courseCard {
    /* camelCase */
}
```

## Структура проекта

```
course_platform/
├── course_platform/      # Настройки Django
├── courses/             # Приложение курсов
│   ├── models.py       # Модели данных
│   ├── views.py        # API views
│   ├── template_views.py  # Template views
│   ├── serializers.py  # DRF сериализаторы
│   ├── analytics.py    # Аналитика
│   └── tests/          # Тесты
├── users/              # Приложение пользователей
├── templates/          # HTML шаблоны
├── static/             # Статические файлы
└── media/              # Загруженные файлы
```

## Тестирование

### Требования

- Все новые функции должны иметь тесты
- Покрытие кода тестами должно быть не менее 70%
- Все существующие тесты должны проходить

### Запуск тестов

```bash
# Все тесты
python manage.py test

# Конкретное приложение
python manage.py test courses

# С покрытием
coverage run --source='.' manage.py test
coverage report
```

### Написание тестов

Смотрите [TESTING.md](TESTING.md) для подробных примеров.

## Миграции базы данных

При изменении моделей:

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Проверить статус
python manage.py showmigrations
```

**Важно:** Всегда включайте файлы миграций в commit!

## Документация

### Обновление документации

При добавлении новых функций обновите:

- `README.md` - основная документация
- `API_DOCUMENTATION.md` - API endpoints
- `DEPLOYMENT.md` - инструкции по развертыванию
- Docstrings в коде

### Формат docstrings

Используйте Google-style docstrings:

```python
def create_certificate(enrollment):
    """
    Create a certificate for a completed course enrollment.
    
    Args:
        enrollment (Enrollment): The enrollment to create certificate for
    
    Returns:
        Certificate: The created certificate instance
    
    Raises:
        ValueError: If enrollment is not completed
    """
    if not enrollment.completed:
        raise ValueError("Course must be completed to generate certificate")
    
    return Certificate.objects.create(enrollment=enrollment)
```

## Коммиты

### Формат сообщений коммитов

Используйте четкие и описательные сообщения:

```
Тип: Краткое описание (макс. 50 символов)

Более подробное описание изменений, если необходимо.
Объясните что и почему, а не как.

Fixes #123
```

Типы коммитов:
- `feat`: Новая функция
- `fix`: Исправление ошибки
- `docs`: Изменения в документации
- `style`: Форматирование кода
- `refactor`: Рефакторинг кода
- `test`: Добавление тестов
- `chore`: Обслуживание проекта

Примеры:
```
feat: Add quiz functionality to lessons

- Add Quiz, Question, Answer models
- Create API endpoints for quiz submission
- Add quiz templates

Closes #45

---

fix: Fix enrollment progress calculation

The progress was not updating correctly when lessons
were marked as complete. Now using aggregation for
accurate calculation.

Fixes #67

---

docs: Update API documentation with quiz endpoints
```

## Безопасность

### Сообщение о уязвимостях

Если вы обнаружили уязвимость безопасности:

1. **НЕ** создавайте публичный issue
2. Отправьте email на security@example.com с деталями
3. Дайте нам время исправить проблему перед публикацией

### Рекомендации по безопасности

- Никогда не коммитьте секретные ключи или пароли
- Используйте environment variables для конфиденциальных данных
- Валидируйте все пользовательские входные данные
- Используйте Django's ORM для предотвращения SQL инъекций
- Всегда используйте CSRF защиту

## Код поведения

### Наши стандарты

- Будьте уважительны к другим участникам
- Принимайте конструктивную критику
- Фокусируйтесь на том, что лучше для проекта
- Помогайте новичкам

### Неприемлемое поведение

- Оскорбления или унижения
- Домогательства любого рода
- Публикация личной информации других людей
- Троллинг или неконструктивная критика

## Лицензия

Внося вклад в этот проект, вы соглашаетесь, что ваш код будет лицензирован под той же лицензией, что и проект (MIT License).

## Вопросы?

Если у вас есть вопросы:

- Создайте issue с меткой "question"
- Напишите в Discussions
- Свяжитесь с мейнтейнерами

## Благодарности

Спасибо всем, кто внес вклад в проект! Ваша помощь делает платформу лучше для всех.

### Мейнтейнеры

- [@yourusername](https://github.com/yourusername) - Creator & Lead Developer

### Контрибьюторы

См. список [Contributors](https://github.com/yourusername/course-platform/graphs/contributors)

---

Снова спасибо за ваш интерес к проекту! 🎓✨
