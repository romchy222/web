# Deployment Guide - Course Platform

## Production Deployment Checklist

### 1. Environment Setup

#### Required Software
- Python 3.10+
- PostgreSQL 14+ (recommended) or MySQL 8+
- Nginx (web server)
- Gunicorn or uWSGI (WSGI server)
- Redis (optional, for caching)

#### Environment Variables
Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here-generate-new-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (for media files, optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### 2. Database Setup

#### PostgreSQL

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE course_platform;
CREATE USER course_user WITH PASSWORD 'secure_password';
ALTER ROLE course_user SET client_encoding TO 'utf8';
ALTER ROLE course_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE course_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE course_platform TO course_user;
\q
```

#### Update settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'course_platform',
        'USER': 'course_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Application Setup

```bash
# Clone repository
git clone https://github.com/yourusername/course-platform.git
cd course-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --no-input

# Create sample data (optional, for testing)
python manage.py create_sample_data
```

### 4. Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

Create systemd service `/etc/systemd/system/course-platform.service`:

```ini
[Unit]
Description=Course Platform Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/course-platform
Environment="PATH=/var/www/course-platform/venv/bin"
ExecStart=/var/www/course-platform/venv/bin/gunicorn \
          --config /var/www/course-platform/gunicorn_config.py \
          course_platform.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable course-platform
sudo systemctl start course-platform
sudo systemctl status course-platform
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/course-platform`:

```nginx
upstream course_platform {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /var/www/course-platform/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/course-platform/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://course_platform;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/course-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 7. Security Settings

Update `settings.py`:

```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 8. Monitoring & Logging

#### Application Logs
```bash
# Create log directory
sudo mkdir -p /var/log/course-platform
sudo chown www-data:www-data /var/log/course-platform

# Update settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/course-platform/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 9. Backup Strategy

#### Database Backup Script
Create `/usr/local/bin/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/course-platform"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump course_platform > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/course-platform/media/

# Delete old backups (older than 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
sudo chmod +x /usr/local/bin/backup-db.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-db.sh
```

### 10. Performance Optimization

#### Caching with Redis

Install:
```bash
pip install django-redis
```

Update `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache timeout
CACHE_TTL = 60 * 15  # 15 minutes
```

### 11. Common Issues & Solutions

#### Issue: Static files not loading
```bash
python manage.py collectstatic --no-input
sudo systemctl restart course-platform
```

#### Issue: Permission denied for media uploads
```bash
sudo chown -R www-data:www-data /var/www/course-platform/media/
sudo chmod -R 755 /var/www/course-platform/media/
```

#### Issue: Database connection error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in settings.py
- Check firewall rules

### 12. Monitoring Tools

Consider installing:
- **Sentry** - Error tracking
- **New Relic** - Application performance monitoring
- **Prometheus + Grafana** - Metrics and dashboards
- **Uptime Robot** - Uptime monitoring

### 13. Scaling Considerations

For high traffic:
1. Use multiple Gunicorn workers
2. Implement Redis caching
3. Use CDN for static/media files (AWS CloudFront)
4. Database read replicas
5. Load balancer (AWS ALB or nginx)
6. Container orchestration (Docker + Kubernetes)

### 14. Continuous Deployment

Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/course-platform
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --no-input
            sudo systemctl restart course-platform
```

## Maintenance

### Regular Tasks
- Weekly: Review logs for errors
- Monthly: Update dependencies
- Quarterly: Security audit
- Annually: Review and update SSL certificates

### Updates
```bash
cd /var/www/course-platform
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart course-platform
```

## Support

For issues or questions:
- Documentation: README.md
- API Docs: API_DOCUMENTATION.md
- GitHub Issues: https://github.com/yourusername/course-platform/issues
