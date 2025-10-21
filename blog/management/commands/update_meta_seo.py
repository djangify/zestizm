from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from news.models import Post

class Command(BaseCommand):
    help = 'Update empty meta titles and descriptions with content-based fallbacks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--titles-only',
            action='store_true',
            help='Update only meta titles',
        )
        parser.add_argument(
            '--descriptions-only',
            action='store_true',
            help='Update only meta descriptions',
        )

    def handle(self, *args, **options):
        titles_updated = 0
        descriptions_updated = 0
        
        update_titles = not options['descriptions_only']
        update_descriptions = not options['titles_only']
        
        posts = Post.objects.all().select_related('category')
        
        for post in posts:
            updated = False
            
            if update_titles and not post.meta_title:
                post.meta_title = post.title[:60]
                titles_updated += 1
                updated = True
                
            if update_descriptions and not post.meta_description:
                if post.introduction:
                    meta_desc = strip_tags(post.introduction)[:160]
                elif post.content:
                    meta_desc = strip_tags(post.content)[:160]
                else:
                    meta_desc = f"{post.title} - {post.category.name}"[:160]
                
                post.meta_description = meta_desc
                descriptions_updated += 1
                updated = True
            
            if updated:
                post.save()
        
        if update_titles:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully updated {titles_updated} posts with meta titles"
            ))
        if update_descriptions:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully updated {descriptions_updated} posts with meta descriptions"
            ))
            