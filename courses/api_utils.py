from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.utils import timezone
from courses.models import Course, Enrollment
from users.models import User


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Available endpoints
    """
    return Response({
        'message': 'Welcome to Course Platform API',
        'version': '1.0.0',
        'documentation': '/api/docs/',
        'endpoints': {
            'authentication': {
                'register': '/api/users/register/',
                'login': '/api/users/login/',
                'token_refresh': '/api/users/token/refresh/',
                'profile': '/api/users/profile/ (requires authentication)',
            },
            'courses': {
                'list': '/api/courses/',
                'detail': '/api/courses/{slug}/',
                'enroll': '/api/courses/{slug}/enroll/ (requires authentication)',
                'progress': '/api/courses/{slug}/my_progress/ (requires authentication)',
            },
            'categories': '/api/categories/',
            'modules': '/api/modules/',
            'lessons': '/api/lessons/',
            'enrollments': '/api/enrollments/ (requires authentication)',
            'reviews': '/api/reviews/',
            'quizzes': '/api/quizzes/ (requires authentication)',
            'certificates': '/api/certificates/ (requires authentication)',
            'notifications': '/api/notifications/ (requires authentication)',
        },
        'support': {
            'documentation': 'https://github.com/romchy222/web/blob/main/API_DOCUMENTATION.md',
            'issues': 'https://github.com/romchy222/web/issues',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint - Returns system status
    """
    try:
        # Check database connection
        connection.ensure_connection()
        db_status = 'connected'
    except Exception:
        # Don't expose exception details in production
        db_status = 'error'
    
    # Get basic statistics
    try:
        stats = {
            'total_courses': Course.objects.filter(is_published=True).count(),
            'total_students': User.objects.filter(role='student').count(),
            'total_enrollments': Enrollment.objects.count(),
        }
    except Exception:
        stats = None
    
    health_data = {
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'statistics': stats,
    }
    
    response_status = status.HTTP_200_OK if db_status == 'connected' else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_data, status=response_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """
    API Documentation endpoint
    """
    return Response({
        'documentation': {
            'overview': 'Course Platform REST API provides programmatic access to courses, enrollments, and user management.',
            'authentication': 'JWT (JSON Web Token) based authentication. Obtain tokens via /api/users/login/',
            'formats': ['JSON'],
            'rate_limiting': 'Not currently implemented. Consider implementing in production.',
            'versioning': 'Currently v1. Version will be added to URL path in future releases.',
        },
        'getting_started': {
            '1_register': {
                'method': 'POST',
                'url': '/api/users/register/',
                'body': {
                    'username': 'your_username',
                    'email': 'email@example.com',
                    'password': 'secure_password',
                    'password2': 'secure_password',
                    'first_name': 'First',
                    'last_name': 'Last',
                    'role': 'student'
                }
            },
            '2_login': {
                'method': 'POST',
                'url': '/api/users/login/',
                'body': {
                    'username': 'your_username',
                    'password': 'secure_password'
                }
            },
            '3_use_token': {
                'method': 'GET',
                'url': '/api/users/profile/',
                'headers': {
                    'Authorization': 'Bearer {access_token}'
                }
            }
        },
        'error_codes': {
            '200': 'Success',
            '201': 'Created',
            '400': 'Bad Request - Invalid data',
            '401': 'Unauthorized - Authentication required or invalid token',
            '403': 'Forbidden - Insufficient permissions',
            '404': 'Not Found - Resource does not exist',
            '500': 'Internal Server Error'
        },
        'full_documentation': 'https://github.com/romchy222/web/blob/main/API_DOCUMENTATION.md'
    })
