from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from news.models import Post

class Command(BaseCommand):
    help = 'Update empty meta descriptions with content-based fallbacks'

    def handle(self, *args, **options):
        posts_updated = 0
        posts = Post.objects.filter(meta_description='').select_related('category')
        
        for post in posts:
            # Try introduction first
            if post.introduction:
                meta_desc = strip_tags(post.introduction)[:160]
            # Fall back to content
            elif post.content:
                meta_desc = strip_tags(post.content)[:160]
            # Last resort: use title + category
            else:
                meta_desc = f"{post.title} - {post.category.name}"[:160]
            
            post.meta_description = meta_desc
            post.save()
            posts_updated += 1
            
            self.stdout.write(f"Updated meta description for: {post.title}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully updated {posts_updated} posts with meta descriptions"
        ))
        