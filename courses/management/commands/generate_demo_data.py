from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from users.models import User
from courses.models import (Course, Enrollment, LessonProgress, 
                            Review, Notification, Certificate, Lesson)


class Command(BaseCommand):
    help = 'Генерирует дополнительные тестовые данные для демонстрации функционала'

    def handle(self, *args, **kwargs):
        self.stdout.write('Генерация дополнительных данных...')
        
        # Get or create additional users
        students = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f'student{i+1}',
                defaults={
                    'email': f'student{i+1}@example.com',
                    'first_name': f'Студент',
                    'last_name': f'{i+1}',
                    'role': 'student'
                }
            )
            if created:
                user.set_password('student123')
                user.save()
            students.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(students)} студентов'))
        
        # Enroll students in courses
        courses = Course.objects.filter(is_published=True)
        enrollments_created = 0
        
        for student in students:
            # Check if courses exist
            if courses.count() == 0:
                self.stdout.write(self.style.WARNING('No courses available for enrollment'))
                break
            
            # Enroll each student in 2-3 random courses
            num_courses = random.randint(2, min(3, courses.count()))
            selected_courses = random.sample(list(courses), num_courses)
            
            for course in selected_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    user=student,
                    course=course,
                    defaults={
                        'enrolled_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                        'progress': random.randint(0, 100)
                    }
                )
                
                if created:
                    enrollments_created += 1
                    
                    # Mark some lessons as complete
                    lessons = Lesson.objects.filter(module__course=course)
                    completed_count = int(lessons.count() * (enrollment.progress / 100))
                    
                    for lesson in list(lessons)[:completed_count]:
                        LessonProgress.objects.get_or_create(
                            enrollment=enrollment,
                            lesson=lesson,
                            defaults={
                                'completed': True,
                                'completed_at': timezone.now() - timedelta(days=random.randint(1, 20))
                            }
                        )
                    
                    # If progress is 100%, mark as completed and generate certificate
                    if enrollment.progress == 100:
                        enrollment.completed = True
                        enrollment.completed_at = timezone.now() - timedelta(days=random.randint(1, 10))
                        enrollment.save()
                        
                        Certificate.objects.get_or_create(enrollment=enrollment)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {enrollments_created} записей на курсы'))
        
        # Create reviews
        reviews_created = 0
        for enrollment in Enrollment.objects.filter(progress__gte=50):
            if random.random() > 0.5:  # 50% chance to leave a review
                review, created = Review.objects.get_or_create(
                    user=enrollment.user,
                    course=enrollment.course,
                    defaults={
                        'rating': random.randint(3, 5),
                        'comment': random.choice([
                            'Отличный курс! Все понятно и доступно.',
                            'Хороший курс, многому научился.',
                            'Интересный материал, рекомендую!',
                            'Качественное обучение, спасибо!',
                            'Курс превзошел ожидания, очень доволен.',
                        ]),
                        'created_at': timezone.now() - timedelta(days=random.randint(1, 15))
                    }
                )
                if created:
                    reviews_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {reviews_created} отзывов'))
        
        # Create notifications for enrolled students
        notifications_created = 0
        for student in students:
            # Welcome notification
            Notification.objects.get_or_create(
                user=student,
                notification_type='announcement',
                title='Добро пожаловать!',
                defaults={
                    'message': 'Добро пожаловать на платформу курсов! Начните обучение прямо сейчас.',
                    'link': '/courses/',
                    'created_at': timezone.now() - timedelta(days=25)
                }
            )
            notifications_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {notifications_created} уведомлений'))
        
        # Summary
        total_enrollments = Enrollment.objects.count()
        total_certificates = Certificate.objects.count()
        total_reviews = Review.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n=== Статистика ==='))
        self.stdout.write(f'Всего студентов: {User.objects.filter(role="student").count()}')
        self.stdout.write(f'Всего курсов: {Course.objects.count()}')
        self.stdout.write(f'Записей на курсы: {total_enrollments}')
        self.stdout.write(f'Выдано сертификатов: {total_certificates}')
        self.stdout.write(f'Отзывов: {total_reviews}')
        self.stdout.write(self.style.SUCCESS('\nГотово!'))
