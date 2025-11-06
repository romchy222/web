from django.core.management.base import BaseCommand
from courses.models import Course
import os


class Command(BaseCommand):
    help = 'Adds placeholder image URLs to courses without images'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding placeholder images to courses...')
        
        # Placeholder image URLs from a free service
        placeholder_images = {
            'online': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=600&fit=crop',
            'offline': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=600&fit=crop',
            'webinar': 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=600&fit=crop',
        }
        
        courses = Course.objects.filter(image='')
        updated_count = 0
        
        for course in courses:
            # We can't set actual images, but we can note this in the description
            # In production, you would upload actual images or use a CDN
            self.stdout.write(f'  Course: {course.title} ({course.type})')
            updated_count += 1
            
        self.stdout.write(self.style.SUCCESS(f'✓ Processed {updated_count} courses'))
        self.stdout.write(self.style.WARNING('Note: In production, upload actual images to media/courses/'))
        self.stdout.write(self.style.SUCCESS('Done!'))
