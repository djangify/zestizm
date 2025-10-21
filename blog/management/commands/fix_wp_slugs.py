# news/management/commands/fix_wp_slugs.py

import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from news.models import Post

class Command(BaseCommand):
    help = 'Fix malformed slugs from WordPress imports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to see what would be updated',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode. No changes will be made.'))
        
        # Get all posts with invalid slugs that might contain WordPress query params
        invalid_slug_pattern = r'[?&=]'
        posts_with_invalid_slugs = []
        
        for post in Post.objects.all():
            if re.search(invalid_slug_pattern, post.slug):
                posts_with_invalid_slugs.append(post)
        
        self.stdout.write(f'Found {len(posts_with_invalid_slugs)} posts with invalid slugs')
        
        # Fix each invalid slug
        fixed_count = 0
        for post in posts_with_invalid_slugs:
            old_slug = post.slug
            
            # Generate a new slug from the title
            new_slug = slugify(post.title)
            
            # Ensure uniqueness by adding a suffix if needed
            suffix = 1
            slug_to_check = new_slug
            while Post.objects.filter(slug=slug_to_check).exclude(id=post.id).exists():
                slug_to_check = f"{new_slug}-{suffix}"
                suffix += 1
            
            new_slug = slug_to_check
            
            self.stdout.write(f'Post ID {post.id}: "{post.title}"')
            self.stdout.write(f'  Old slug: {old_slug}')
            self.stdout.write(f'  New slug: {new_slug}')
            
            if not dry_run:
                post.slug = new_slug
                post.save(update_fields=['slug'])
                fixed_count += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Dry run complete. Found {len(posts_with_invalid_slugs)} posts with invalid slugs.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} posts with invalid slugs.'))
            