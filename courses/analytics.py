"""
Utility functions for course statistics and analytics
"""

from django.db.models import Avg, Count, Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from .models import Course, Enrollment, Review, LessonProgress, Lesson


def get_course_statistics(course):
    """Get comprehensive statistics for a course"""
    enrollments = course.enrollments.all()
    
    stats = {
        'total_students': enrollments.count(),
        'active_students': enrollments.filter(completed=False).count(),
        'completed_students': enrollments.filter(completed=True).count(),
        'average_progress': enrollments.aggregate(Avg('progress'))['progress__avg'] or 0,
        'completion_rate': 0,
    }
    
    if stats['total_students'] > 0:
        stats['completion_rate'] = (stats['completed_students'] / stats['total_students']) * 100
    
    # Reviews
    reviews = course.reviews.all()
    stats['total_reviews'] = reviews.count()
    stats['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Lessons
    total_lessons = Lesson.objects.filter(module__course=course).count()
    stats['total_lessons'] = total_lessons
    
    return stats


def get_instructor_statistics(instructor):
    """Get comprehensive statistics for an instructor"""
    courses = Course.objects.filter(instructor=instructor)
    enrollments = Enrollment.objects.filter(course__instructor=instructor)
    
    stats = {
        'total_courses': courses.count(),
        'published_courses': courses.filter(is_published=True).count(),
        'total_students': enrollments.values('user').distinct().count(),
        'total_enrollments': enrollments.count(),
        'completed_enrollments': enrollments.filter(completed=True).count(),
        'average_rating': Review.objects.filter(
            course__instructor=instructor
        ).aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_reviews': Review.objects.filter(course__instructor=instructor).count(),
    }
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    stats['new_enrollments_30d'] = enrollments.filter(
        enrolled_at__gte=thirty_days_ago
    ).count()
    
    return stats


def get_student_statistics(student):
    """Get comprehensive statistics for a student"""
    enrollments = Enrollment.objects.filter(user=student)
    
    stats = {
        'total_courses': enrollments.count(),
        'completed_courses': enrollments.filter(completed=True).count(),
        'in_progress_courses': enrollments.filter(completed=False).count(),
        'average_progress': enrollments.aggregate(Avg('progress'))['progress__avg'] or 0,
        'certificates_earned': enrollments.filter(
            completed=True,
            certificate__isnull=False
        ).count(),
    }
    
    # Learning time estimate (based on lesson durations)
    completed_lessons = LessonProgress.objects.filter(
        enrollment__user=student,
        completed=True
    ).select_related('lesson')
    
    total_minutes = sum(
        lesson_progress.lesson.duration or 30  # Default 30 min if not set
        for lesson_progress in completed_lessons
    )
    stats['total_learning_hours'] = total_minutes / 60
    
    return stats


def get_platform_statistics():
    """Get overall platform statistics"""
    from users.models import User
    
    stats = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_instructors': User.objects.filter(role='instructor').count(),
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(is_published=True).count(),
        'total_enrollments': Enrollment.objects.count(),
        'total_reviews': Review.objects.count(),
        'average_rating': Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0,
    }
    
    # Course type distribution
    stats['online_courses'] = Course.objects.filter(type='online', is_published=True).count()
    stats['offline_courses'] = Course.objects.filter(type='offline', is_published=True).count()
    stats['webinar_courses'] = Course.objects.filter(type='webinar', is_published=True).count()
    
    return stats


def get_popular_courses(limit=10):
    """Get most popular courses by enrollment count"""
    return Course.objects.filter(
        is_published=True
    ).annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:limit]


def get_top_rated_courses(limit=10):
    """Get highest rated courses"""
    return Course.objects.filter(
        is_published=True,
        reviews__isnull=False
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        review_count__gte=1
    ).order_by('-avg_rating', '-review_count')[:limit]


def get_recent_enrollments(limit=20):
    """Get recent course enrollments"""
    return Enrollment.objects.select_related(
        'user', 'course'
    ).order_by('-enrolled_at')[:limit]


def calculate_engagement_rate(course):
    """Calculate student engagement rate for a course"""
    enrollments = course.enrollments.count()
    if enrollments == 0:
        return 0
    
    # Consider students who have made any progress as engaged
    engaged = course.enrollments.filter(progress__gt=0).count()
    return (engaged / enrollments) * 100


def get_completion_trend(course, days=30):
    """Get course completion trend over time"""
    start_date = timezone.now() - timedelta(days=days)
    
    completions_by_day = Enrollment.objects.filter(
        course=course,
        completed=True,
        completed_at__gte=start_date
    ).extra(
        select={'day': 'date(completed_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    return list(completions_by_day)
