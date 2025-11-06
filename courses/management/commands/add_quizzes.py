from django.core.management.base import BaseCommand
from courses.models import Course, Lesson, Quiz, Question, Answer


class Command(BaseCommand):
    help = 'Добавляет тесты к существующим урокам'

    def handle(self, *args, **kwargs):
        self.stdout.write('Добавление тестов к урокам...')
        
        # Get all lessons without quizzes
        lessons = Lesson.objects.filter(quizzes__isnull=True)
        
        quiz_templates = [
            {
                'title': 'Проверка знаний',
                'description': 'Тест для проверки понимания материала',
                'questions': [
                    {
                        'text': 'Вы изучили материал этого урока?',
                        'type': 'single',
                        'answers': [
                            {'text': 'Да, полностью', 'correct': True},
                            {'text': 'Частично', 'correct': False},
                            {'text': 'Нет, еще не изучал', 'correct': False},
                        ]
                    },
                    {
                        'text': 'Оцените сложность материала',
                        'type': 'single',
                        'answers': [
                            {'text': 'Легко', 'correct': True},
                            {'text': 'Средне', 'correct': True},
                            {'text': 'Сложно', 'correct': True},
                        ]
                    }
                ]
            }
        ]
        
        added_count = 0
        for lesson in lessons[:6]:  # Add to first 6 lessons
            quiz = Quiz.objects.create(
                lesson=lesson,
                title=f'Тест: {lesson.title}',
                description='Проверьте свои знания по материалу урока',
                passing_score=70
            )
            
            # Add questions
            q1 = Question.objects.create(
                quiz=quiz,
                text=f'Вы поняли материал урока "{lesson.title}"?',
                question_type='single',
                points=1,
                order=1
            )
            Answer.objects.create(question=q1, text='Да, полностью понял', is_correct=True)
            Answer.objects.create(question=q1, text='Понял частично', is_correct=False)
            Answer.objects.create(question=q1, text='Не понял', is_correct=False)
            
            q2 = Question.objects.create(
                quiz=quiz,
                text='Какие концепции вы узнали из этого урока?',
                question_type='multiple',
                points=2,
                order=2
            )
            Answer.objects.create(question=q2, text='Теоретические основы', is_correct=True)
            Answer.objects.create(question=q2, text='Практические примеры', is_correct=True)
            Answer.objects.create(question=q2, text='Дополнительные материалы', is_correct=True)
            
            added_count += 1
            
        self.stdout.write(self.style.SUCCESS(f'✓ Добавлено {added_count} тестов'))
        self.stdout.write(self.style.SUCCESS('Готово!'))
