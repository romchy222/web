from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import User
from courses.models import Category, Course, Module, Lesson, Quiz, Question, QuestionOption, Assignment


class Command(BaseCommand):
    help = 'Создает тестовые данные для платформы'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание тестовых данных...')

        # Создание пользователей
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Администратор',
                last_name='Системы',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан администратор (admin/admin123)'))
        
        if not User.objects.filter(username='instructor').exists():
            instructor = User.objects.create_user(
                username='instructor',
                email='instructor@example.com',
                password='instructor123',
                first_name='Иван',
                last_name='Петров',
                role='instructor'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан преподаватель (instructor/instructor123)'))
        else:
            instructor = User.objects.get(username='instructor')

        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123',
                first_name='Мария',
                last_name='Сидорова',
                role='student'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан студент (student/student123)'))

        # Создание категорий
        categories_data = [
            {'name': 'Программирование', 'slug': 'programming'},
            {'name': 'Дизайн', 'slug': 'design'},
            {'name': 'Маркетинг', 'slug': 'marketing'},
            {'name': 'Бизнес', 'slug': 'business'},
        ]

        for cat_data in categories_data:
            Category.objects.get_or_create(**cat_data)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(categories_data)} категорий'))

        # Создание курсов
        programming = Category.objects.get(slug='programming')
        design = Category.objects.get(slug='design')

        courses_data = [
            {
                'title': 'Python для начинающих',
                'slug': 'python-beginners',
                'description': 'Изучите основы программирования на Python с нуля. Курс подходит для начинающих программистов.',
                'type': 'online',
                'category': programming,
                'instructor': instructor,
                'price': 5990,
                'is_published': True,
            },
            {
                'title': 'Веб-разработка на Django',
                'slug': 'django-web-development',
                'description': 'Научитесь создавать веб-приложения на Django. Полный курс от основ до продвинутых тем.',
                'type': 'online',
                'category': programming,
                'instructor': instructor,
                'price': 8990,
                'is_published': True,
            },
            {
                'title': 'UI/UX Дизайн',
                'slug': 'ui-ux-design',
                'description': 'Создавайте удобные и красивые интерфейсы. Практический курс по дизайну.',
                'type': 'offline',
                'category': design,
                'instructor': instructor,
                'price': 12990,
                'location': 'г. Москва, ул. Тверская, д. 1',
                'max_students': 15,
                'start_date': timezone.now() + timedelta(days=7),
                'is_published': True,
            },
            {
                'title': 'Вебинар: Введение в Python',
                'slug': 'webinar-python-intro',
                'description': 'Бесплатный вебинар для знакомства с Python. Узнайте, подходит ли вам программирование.',
                'type': 'webinar',
                'category': programming,
                'instructor': instructor,
                'price': 0,
                'webinar_link': 'https://zoom.us/j/example',
                'start_date': timezone.now() + timedelta(days=3, hours=18),
                'is_published': True,
            },
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults=course_data
            )
            if created:
                # Добавляем модули и уроки
                module1 = Module.objects.create(
                    course=course,
                    title='Введение',
                    description='Знакомство с курсом',
                    order=1
                )
                Lesson.objects.create(
                    module=module1,
                    title='Добро пожаловать',
                    lesson_type='text',
                    content='Добро пожаловать на курс! В этом уроке мы познакомимся с программой.',
                    order=1,
                    duration=15
                )
                Lesson.objects.create(
                    module=module1,
                    title='Видео-введение',
                    lesson_type='video',
                    content='Посмотрите это видео для лучшего понимания курса.',
                    video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
                    order=2,
                    duration=10
                )

                module2 = Module.objects.create(
                    course=course,
                    title='Основы',
                    description='Базовые концепции',
                    order=2
                )
                lesson3 = Lesson.objects.create(
                    module=module2,
                    title='Первые шаги',
                    lesson_type='text',
                    content='Начинаем изучать основы.',
                    order=1,
                    duration=30
                )
                
                # Добавляем квиз
                quiz_lesson = Lesson.objects.create(
                    module=module2,
                    title='Проверочный квиз',
                    lesson_type='quiz',
                    content='Проверьте свои знания по пройденному материалу.',
                    order=2,
                    duration=15
                )
                
                # Добавляем домашнее задание
                assignment_lesson = Lesson.objects.create(
                    module=module2,
                    title='Практическое задание',
                    lesson_type='assignment',
                    content='Выполните практическое задание для закрепления материала.',
                    order=3,
                    duration=60
                )
                
                # Создаем квиз только для курса Python
                if course.slug == 'python-beginners':
                    quiz = Quiz.objects.create(
                        lesson=quiz_lesson,
                        passing_score=75,
                        max_attempts=3,
                        time_limit=10
                    )
                    
                    # Добавляем вопросы к квизу
                    q1 = Question.objects.create(
                        quiz=quiz,
                        question_text='Что такое Python?',
                        question_type='single',
                        points=10,
                        order=1
                    )
                    
                    QuestionOption.objects.create(question=q1, option_text='Язык программирования', is_correct=True, order=1)
                    QuestionOption.objects.create(question=q1, option_text='Змея', is_correct=False, order=2)
                    QuestionOption.objects.create(question=q1, option_text='Фреймворк', is_correct=False, order=3)
                    
                    q2 = Question.objects.create(
                        quiz=quiz,
                        question_text='Какие из следующих типов данных есть в Python?',
                        question_type='multiple',
                        points=15,
                        order=2
                    )
                    
                    QuestionOption.objects.create(question=q2, option_text='int', is_correct=True, order=1)
                    QuestionOption.objects.create(question=q2, option_text='str', is_correct=True, order=2)
                    QuestionOption.objects.create(question=q2, option_text='boolean', is_correct=False, order=3)
                    QuestionOption.objects.create(question=q2, option_text='bool', is_correct=True, order=4)
                    
                    # Создаем задание
                    Assignment.objects.create(
                        lesson=assignment_lesson,
                        instructions='Напишите простую программу на Python, которая выводит "Hello, World!" на экран. Сохраните код в файл hello.py и загрузите его.',
                        max_file_size=1,
                        allowed_file_types='.py,.txt'
                    )

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(courses_data)} курсов с модулями и уроками'))
        self.stdout.write(self.style.SUCCESS('\nГотово! Тестовые данные созданы.'))
        self.stdout.write('\nДанные для входа:')
        self.stdout.write('  Администратор: admin / admin123')
        self.stdout.write('  Преподаватель: instructor / instructor123')
        self.stdout.write('  Студент: student / student123')
