# API Documentation - Course Platform

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication
The API uses JWT (JSON Web Token) authentication for protected endpoints.

### Get JWT Token
```http
POST /api/users/login/
Content-Type: application/json

{
  "username": "student",
  "password": "student123"
}
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Use Token in Requests
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Endpoints

### Users

#### Register New User
```http
POST /api/users/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password2": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

#### Get User Profile
```http
GET /api/users/profile/
Authorization: Bearer {token}
```

#### Update Profile
```http
PUT /api/users/profile/
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Student learning web development"
}
```

### Courses

#### List All Courses
```http
GET /api/courses/
```

Query Parameters:
- `type` - Filter by course type (online, offline, webinar)
- `category` - Filter by category ID
- `search` - Search in title and description
- `ordering` - Sort by field (created_at, start_date, price)

Example:
```http
GET /api/courses/?type=online&search=python
```

#### Get Course Details
```http
GET /api/courses/{slug}/
```

#### Create Course (Instructor/Admin only)
```http
POST /api/courses/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "New Course",
  "slug": "new-course",
  "description": "Course description",
  "type": "online",
  "category": 1,
  "price": 9990,
  "is_published": true
}
```

#### Enroll in Course
```http
POST /api/courses/{slug}/enroll/
Authorization: Bearer {token}
```

#### Get My Progress
```http
GET /api/courses/{slug}/my_progress/
Authorization: Bearer {token}
```

### Categories

#### List Categories
```http
GET /api/categories/
```

#### Get Category Details
```http
GET /api/categories/{slug}/
```

### Modules

#### List Modules
```http
GET /api/modules/
```

Query Parameters:
- `course` - Filter by course slug

Example:
```http
GET /api/modules/?course=python-beginners
```

### Lessons

#### List Lessons
```http
GET /api/lessons/
```

#### Get Lesson Details
```http
GET /api/lessons/{id}/
```

#### Mark Lesson as Complete
```http
POST /api/lessons/{id}/mark_complete/
Authorization: Bearer {token}
```

### Enrollments

#### List My Enrollments
```http
GET /api/enrollments/
Authorization: Bearer {token}
```

### Reviews

#### List Reviews
```http
GET /api/reviews/
```

Query Parameters:
- `course` - Filter by course slug

#### Create Review
```http
POST /api/reviews/
Authorization: Bearer {token}
Content-Type: application/json

{
  "course": 1,
  "rating": 5,
  "comment": "Great course!"
}
```

### Quizzes

#### Get Quiz Details
```http
GET /api/quizzes/{id}/
Authorization: Bearer {token}
```

#### Submit Quiz Attempt
```http
POST /api/quizzes/{id}/submit/
Authorization: Bearer {token}
Content-Type: application/json

{
  "answers": {
    "1": [1],  // Question ID: [Answer IDs]
    "2": [3, 4]
  }
}
```

Response:
```json
{
  "attempt_id": 1,
  "score": 85.5,
  "passed": true,
  "passing_score": 70
}
```

### Certificates

#### List My Certificates
```http
GET /api/certificates/
Authorization: Bearer {token}
```

### Notifications

#### List My Notifications
```http
GET /api/notifications/
Authorization: Bearer {token}
```

#### Mark Notification as Read
```http
POST /api/notifications/{id}/mark_read/
Authorization: Bearer {token}
```

#### Mark All Notifications as Read
```http
POST /api/notifications/mark_all_read/
Authorization: Bearer {token}
```

## Response Formats

### Success Response
```json
{
  "id": 1,
  "title": "Course Title",
  "description": "Course description",
  ...
}
```

### Error Response
```json
{
  "error": "Error message description"
}
```

or

```json
{
  "field_name": ["Error message for this field"]
}
```

## Pagination

List endpoints support pagination:

```http
GET /api/courses/?page=2
```

Response:
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/courses/?page=3",
  "previous": "http://127.0.0.1:8000/api/courses/?page=1",
  "results": [...]
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, consider adding rate limiting with Django REST framework throttling.

## CORS

CORS is configured for API access. Update `CORS_ALLOWED_ORIGINS` in `settings.py` for your frontend domain.

## Examples

### Complete Flow: Register → Login → Enroll → Complete Lesson

1. **Register**
```bash
curl -X POST http://127.0.0.1:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "student"
  }'
```

2. **Login**
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

3. **Enroll in Course**
```bash
curl -X POST http://127.0.0.1:8000/api/courses/python-beginners/enroll/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

4. **Mark Lesson Complete**
```bash
curl -X POST http://127.0.0.1:8000/api/lessons/1/mark_complete/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
