# Testing Guide - Course Platform

## Overview

This guide covers testing strategies and examples for the Course Platform.

## Testing Stack

- **Django TestCase** - Unit and integration tests
- **Django REST Framework Test Client** - API testing
- **Coverage.py** - Code coverage analysis

## Setup

Install testing dependencies:
```bash
pip install coverage pytest pytest-django
```

## Running Tests

### Run all tests
```bash
python manage.py test
```

### Run specific app tests
```bash
python manage.py test courses
python manage.py test users
```

### Run with verbosity
```bash
python manage.py test --verbosity=2
```

### Run with coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Writing Tests

### Example: Model Tests

Create `courses/tests/test_models.py`:

```python
from django.test import TestCase
from django.utils import timezone
from users.models import User
from courses.models import Course, Category, Module, Lesson, Enrollment


class CourseModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='test123',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            slug='programming'
        )
    
    def test_course_creation(self):
        """Test creating a course"""
        course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test description',
            type='online',
            category=self.category,
            instructor=self.instructor,
            price=9990
        )
        self.assertEqual(course.title, 'Test Course')
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(str(course), 'Test Course (Online)')
    
    def test_course_enrollment(self):
        """Test enrolling in a course"""
        student = User.objects.create_user(
            username='student',
            password='test123',
            role='student'
        )
        course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test',
            type='online',
            category=self.category,
            instructor=self.instructor
        )
        
        enrollment = Enrollment.objects.create(
            user=student,
            course=course
        )
        
        self.assertEqual(enrollment.progress, 0)
        self.assertFalse(enrollment.completed)
```

### Example: View Tests

Create `courses/tests/test_views.py`:

```python
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from courses.models import Course, Category


class CourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='test123',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            slug='programming'
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test',
            type='online',
            category=self.category,
            instructor=self.instructor,
            is_published=True
        )
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Обучайтесь')
    
    def test_course_list_page(self):
        """Test course list page"""
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
    
    def test_course_detail_page(self):
        """Test course detail page"""
        response = self.client.get(
            reverse('course_detail', kwargs={'slug': 'test-course'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
    
    def test_enrollment_requires_login(self):
        """Test that enrollment requires authentication"""
        response = self.client.post(
            reverse('course_detail', kwargs={'slug': 'test-course'})
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
```

### Example: API Tests

Create `courses/tests/test_api.py`:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from courses.models import Course, Category


class CourseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            password='test123',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            slug='programming'
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test',
            type='online',
            category=self.category,
            instructor=self.instructor,
            is_published=True
        )
    
    def test_get_courses_list(self):
        """Test retrieving course list"""
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_course_detail(self):
        """Test retrieving course detail"""
        response = self.client.get(f'/api/courses/{self.course.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')
    
    def test_enroll_in_course(self):
        """Test enrolling in a course via API"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/courses/{self.course.slug}/enroll/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_unauthenticated_enrollment(self):
        """Test that unauthenticated users cannot enroll"""
        response = self.client.post(
            f'/api/courses/{self.course.slug}/enroll/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### Example: Authentication Tests

Create `users/tests/test_auth.py`:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/api/users/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_login(self):
        """Test user login and JWT token generation"""
        # Create user
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Login
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/users/login/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

## Test Organization

Organize tests by functionality:

```
courses/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_api.py
│   ├── test_serializers.py
│   └── test_permissions.py
users/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_auth.py
```

## Test Data Fixtures

Create fixtures for reusable test data:

```python
# courses/tests/fixtures.py
from users.models import User
from courses.models import Course, Category


class TestDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.instructor = User.objects.create_user(
            username='instructor',
            password='test123',
            role='instructor'
        )
        cls.student = User.objects.create_user(
            username='student',
            password='test123',
            role='student'
        )
        cls.category = Category.objects.create(
            name='Programming',
            slug='programming'
        )
        cls.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test',
            type='online',
            category=cls.category,
            instructor=cls.instructor,
            is_published=True
        )
```

Use in tests:
```python
class MyTest(TestDataMixin, TestCase):
    def test_something(self):
        # Use self.course, self.student, etc.
        pass
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install coverage
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          coverage run --source='.' manage.py test
          coverage report
```

## Performance Testing

Use Django's `django.test.TransactionTestCase` for database-intensive tests:

```python
from django.test import TransactionTestCase

class PerformanceTest(TransactionTestCase):
    def test_bulk_enrollment(self):
        """Test bulk enrollment performance"""
        import time
        
        # Create test data
        students = [
            User.objects.create_user(f'student{i}', password='test')
            for i in range(100)
        ]
        
        start = time.time()
        
        # Perform bulk operation
        Enrollment.objects.bulk_create([
            Enrollment(user=student, course=self.course)
            for student in students
        ])
        
        duration = time.time() - start
        
        # Assert performance
        self.assertLess(duration, 1.0)  # Should complete in < 1 second
```

## Best Practices

1. **Isolate Tests** - Each test should be independent
2. **Use setUp/tearDown** - Clean state for each test
3. **Test Edge Cases** - Invalid inputs, boundary conditions
4. **Mock External Services** - Don't rely on external APIs
5. **Keep Tests Fast** - Use in-memory databases when possible
6. **Test Coverage** - Aim for 80%+ coverage
7. **Clear Test Names** - Describe what is being tested
8. **One Assert Per Test** - Or at least one concept per test

## Common Test Patterns

### Testing Permissions
```python
def test_instructor_can_edit_own_course(self):
    self.client.force_authenticate(user=self.instructor)
    response = self.client.put(
        f'/api/courses/{self.course.slug}/',
        {'title': 'Updated Title'}
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_student_cannot_edit_course(self):
    self.client.force_authenticate(user=self.student)
    response = self.client.put(
        f'/api/courses/{self.course.slug}/',
        {'title': 'Updated Title'}
    )
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

### Testing Signals
```python
def test_certificate_generated_on_completion(self):
    # Enroll student
    enrollment = Enrollment.objects.create(
        user=self.student,
        course=self.course
    )
    
    # Complete course
    enrollment.completed = True
    enrollment.save()
    
    # Check certificate was created
    self.assertTrue(
        Certificate.objects.filter(enrollment=enrollment).exists()
    )
```

## Debugging Tests

Run specific test with extra output:
```bash
python manage.py test courses.tests.test_api.CourseAPITest.test_enroll_in_course --verbosity=2
```

Use `pdb` for debugging:
```python
def test_something(self):
    import pdb; pdb.set_trace()
    # Test code here
```

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [DRF Testing Documentation](https://www.django-rest-framework.org/api-guide/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
