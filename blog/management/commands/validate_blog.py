# news/management/commands/validate_blog.py

import re
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from news.models import Post, Category

class Command(BaseCommand):
    help = 'Validate all blog URLs to ensure they resolve without errors'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Validating blog URLs...'))
        
        # Step 1: Validate categories
        self.stdout.write('Checking categories...')
        categories = Category.objects.all()
        invalid_categories = []
        
        for category in categories:
            try:
                url = reverse('news:category', kwargs={'slug': category.slug})
                self.stdout.write(f'  ✓ Category: {category.name} -> {url}')
            except NoReverseMatch:
                invalid_categories.append(category)
                self.stdout.write(self.style.ERROR(f'  ✗ Category: {category.name} (slug: {category.slug}) cannot generate URL'))
        
        # Step 2: Validate posts
        self.stdout.write('\nChecking posts...')
        posts = Post.objects.all()
        invalid_posts = []
        invalid_slug_pattern = r'[?&=]'
        
        for post in posts:
            if re.search(invalid_slug_pattern, post.slug):
                invalid_posts.append(post)
                self.stdout.write(self.style.ERROR(f'  ✗ Post: "{post.title}" has invalid slug: {post.slug}'))
                continue
                
            try:
                url = reverse('news:detail', kwargs={'slug': post.slug})
                self.stdout.write(f'  ✓ Post: {post.title[:30]}... -> {url}')
            except NoReverseMatch:
                invalid_posts.append(post)
                self.stdout.write(self.style.ERROR(f'  ✗ Post: "{post.title}" (slug: {post.slug}) cannot generate URL'))
        
        # Summary
        self.stdout.write('\nValidation Summary:')
        self.stdout.write(f'  Total categories: {categories.count()}')
        self.stdout.write(f'  Invalid categories: {len(invalid_categories)}')
        self.stdout.write(f'  Total posts: {posts.count()}')
        self.stdout.write(f'  Invalid posts: {len(invalid_posts)}')
        
        if invalid_categories or invalid_posts:
            self.stdout.write(self.style.WARNING('\nTo fix invalid slugs, run:'))
            self.stdout.write('  python manage.py fix_wp_slugs')
        else:
            self.stdout.write(self.style.SUCCESS('\nAll blog URLs are valid!'))
            