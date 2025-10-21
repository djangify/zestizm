# news/management/commands/clean_wp_content.py
import re
from django.core.management.base import BaseCommand
from news.models import Post
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Clean WordPress imported content (remove unnecessary HTML, fix formatting, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to see what would be processed',
        )
        parser.add_argument(
            '--post-id',
            type=int,
            help='Clean only a specific post by ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        post_id = options.get('post_id')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode. No changes will be made.'))
        
        # Get posts to process
        if post_id:
            posts = Post.objects.filter(id=post_id)
            if not posts.exists():
                self.stdout.write(self.style.ERROR(f'Post with ID {post_id} not found.'))
                return
        else:
            posts = Post.objects.all()
        
        self.stdout.write(f'Processing {posts.count()} posts...')
        
        # Process each post
        for post in posts:
            self.stdout.write(f'Processing post: {post.id} - {post.title}')
            
            # Process content
            if post.content:
                original_content = post.content
                cleaned_content = self.clean_content(original_content)
                
                if original_content != cleaned_content:
                    if not dry_run:
                        post.content = cleaned_content
                        post.save(update_fields=['content'])
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Content cleaned'))
                else:
                    self.stdout.write('  ✓ Content already clean')
            
            # Process introduction
            if post.introduction:
                original_intro = post.introduction
                cleaned_intro = self.clean_content(original_intro)
                
                if original_intro != cleaned_intro:
                    if not dry_run:
                        post.introduction = cleaned_intro
                        post.save(update_fields=['introduction'])
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Introduction cleaned'))
                else:
                    self.stdout.write('  ✓ Introduction already clean')
        
        self.stdout.write(self.style.SUCCESS(f'Finished processing {posts.count()} posts.'))
    
    def clean_content(self, content):
        """Clean WordPress HTML content"""
        if not content:
            return content
            
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove WordPress specific classes and inline styles
        for tag in soup.find_all(True):
            if tag.has_attr('class'):
                # Remove WordPress specific classes
                classes = [c for c in tag['class'] if not c.startswith('wp-')]
                if classes:
                    tag['class'] = classes
                else:
                    del tag['class']
            
            # Remove inline styles
            if tag.has_attr('style'):
                del tag['style']
                
            # Remove empty attributes
            for attr in list(tag.attrs):
                if tag[attr] == '':
                    del tag[attr]
        
        # Remove empty paragraphs
        for p in soup.find_all('p'):
            if not p.get_text(strip=True) and not p.find('img'):
                p.decompose()
        
        # Fix WordPress captions
        for caption_div in soup.find_all('div', class_='wp-caption'):
            img = caption_div.find('img')
            caption_text = caption_div.find('p', class_='wp-caption-text')
            
            if img and caption_text:
                # Create a figure with figcaption
                figure = soup.new_tag('figure')
                figcaption = soup.new_tag('figcaption')
                figcaption.string = caption_text.get_text()
                
                # Copy the image to the figure
                figure.append(img.extract())
                figure.append(figcaption)
                
                # Replace the caption div with the figure
                caption_div.replace_with(figure)
        
        # Convert div to more semantic tags where appropriate
        for div in soup.find_all('div'):
            # Check if div might be a header
            header_text = div.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if header_text and len(div.contents) == 1:
                div.replace_with(header_text)
                
        # Convert cleaned HTML back to string
        cleaned_content = str(soup)
        
        # Fix WordPress shortcodes
        shortcode_pattern = r'\[.*?\]'
        cleaned_content = re.sub(shortcode_pattern, '', cleaned_content)
        
        return cleaned_content
    