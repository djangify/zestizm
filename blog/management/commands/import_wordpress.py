import json
import datetime
import os
import requests
import base64
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from news.models import Post, Category
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
import re

class Command(BaseCommand):
    help = 'Import posts from WordPress JSON export'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)
        parser.add_argument('--year', type=int, required=False)
        parser.add_argument('--month', type=int, required=False)
        parser.add_argument('--limit', type=int, required=False)
        parser.add_argument('--offset', type=int, default=0, required=False)
        parser.add_argument('--debug', action='store_true', help='Show debug info')
        parser.add_argument('--download-images', action='store_true', help='Download and import images')
        parser.add_argument('--images-path', type=str, default='wp_images', help='Path to store downloaded images')
        
    def handle(self, *args, **options):
        json_file = options['json_file']
        year = options.get('year')
        month = options.get('month')
        limit = options.get('limit')
        offset = options.get('offset')
        debug = options.get('debug', False)
        download_images = options.get('download_images', False)
        images_path = options.get('images_path', 'wp_images')
        
        # Create images directory if it doesn't exist
        if download_images:
            media_root = settings.MEDIA_ROOT
            images_dir = os.path.join(media_root, 'news/images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                self.stdout.write(f"Created images directory: {images_dir}")
        
        self.stdout.write(f"Reading JSON file: {json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Navigate through the RSS structure to find posts
            posts = []
            attachments = {}  # Store attachments indexed by ID
            
            if 'rss' in data:
                rss_data = data['rss']
                if 'channel' in rss_data:
                    channel = rss_data['channel']
                    if 'item' in channel:
                        items = channel['item']
                        if not isinstance(items, list):
                            items = [items]  # Handle single post case
                        
                        # First pass - collect attachments
                        for item in items:
                            post_type = self._get_nested_value(item, 'post_type', '__cdata')
                            if post_type == 'attachment':
                                # Store attachment for later use
                                post_id = self._get_nested_value(item, 'post_id', '__text')
                                if post_id:
                                    attachments[post_id] = item
                        
                        # Second pass - filter actual posts
                        posts = [item for item in items if self._get_nested_value(item, 'post_type', '__cdata') == 'post']
            
            if debug:
                self.stdout.write(f"Found {len(posts)} posts and {len(attachments)} attachments")
            
            # Create a default category for posts without a category
            default_category, created = Category.objects.get_or_create(
                slug='uncategorized',
                defaults={'name': 'Uncategorized'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS("Created default 'Uncategorized' category"))
            
            # Process posts
            processed = 0
            imported = 0
            images_imported = 0
            
            for idx, post in enumerate(posts):
                # Skip posts that don't match year/month if specified
                post_date = self._parse_date(post)
                if not post_date:
                    continue
                    
                if year and post_date.year != year:
                    continue
                    
                if month and post_date.month != month:
                    continue
                
                processed += 1
                
                # Apply offset
                if processed <= offset:
                    continue
                
                # Apply limit
                if limit and (processed - offset) > limit:
                    break
                
                # Get featured image ID if available
                featured_image_id = None
                if 'postmeta' in post:
                    postmeta = post['postmeta']
                    if not isinstance(postmeta, list):
                        postmeta = [postmeta]
                        
                    for meta in postmeta:
                        meta_key = self._get_nested_value(meta, 'meta_key', '__cdata')
                        if meta_key == '_thumbnail_id':
                            featured_image_id = self._get_nested_value(meta, 'meta_value', '__cdata')
                            break
                
                # Import the post with default category if needed
                post_obj = self._import_post(post, post_date, default_category)
                if post_obj:
                    imported += 1
                    
                    # Handle featured image if download_images is enabled
                    if download_images and featured_image_id and featured_image_id in attachments:
                        attachment = attachments[featured_image_id]
                        image_url = self._get_attachment_url(attachment)
                        
                        if image_url:
                            try:
                                # Download and save featured image
                                image_name = self._get_image_name(image_url)
                                image_path = os.path.join('news/images', image_name)
                                
                                self.stdout.write(f"Downloading featured image: {image_url}")
                                response = requests.get(image_url, stream=True, timeout=10)
                                
                                if response.status_code == 200:
                                    image_content = ContentFile(response.content)
                                    post_obj.image.save(image_name, image_content, save=True)
                                    images_imported += 1
                                    self.stdout.write(f"Imported featured image for post: {post_obj.title}")
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"Error importing featured image: {str(e)}"))
                    
                    # Process content for inline images if needed
                    if download_images:
                        updated_content = self._process_inline_images(post_obj.content, images_path)
                        if updated_content != post_obj.content:
                            post_obj.content = updated_content
                            post_obj.save()
            
            self.stdout.write(self.style.SUCCESS(
                f"Processed {processed} posts, imported {imported} posts, {images_imported} images imported"
            ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            
    def _get_nested_value(self, data, key, nested_key=None):
        """Helper to extract possibly nested values from the JSON"""
        if key not in data:
            return None
            
        value = data[key]
        
        if nested_key and isinstance(value, dict) and nested_key in value:
            return value[nested_key]
            
        return value
    
    def _parse_date(self, post):
        """Extract and parse post date"""
        try:
            # Try different date fields
            date_value = None
            
            # Check pubDate
            if 'pubDate' in post:
                date_value = post['pubDate']
                
            # Check wp:post_date
            if not date_value and 'post_date' in post:
                post_date = post['post_date']
                if isinstance(post_date, dict) and '__cdata' in post_date:
                    date_value = post_date['__cdata']
                elif isinstance(post_date, dict) and '__prefix' in post_date:
                    # Handle nested structure
                    date_value = post_date.get('__cdata', '')
            
            if date_value:
                # Try different date formats
                formats = [
                    '%a, %d %b %Y %H:%M:%S %z',  # Sun, 14 Apr 2024 17:19:43 +0000
                    '%Y-%m-%d %H:%M:%S',         # 2024-04-14 18:19:43
                ]
                
                for fmt in formats:
                    try:
                        return datetime.datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Date parsing error: {str(e)}"))
        return None
    
    def _import_post(self, post, post_date, default_category):
        """Import a single post with a default category fallback"""
        try:
            # Extract title
            title = post.get('title', '')
            if isinstance(title, dict):
                title = title.get('__text', '')
            
            # Extract content
            content = ''
            if 'encoded' in post:
                encoded = post['encoded']
                if isinstance(encoded, list) and len(encoded) > 0:
                    content_item = encoded[0]
                    if isinstance(content_item, dict):
                        content = content_item.get('__cdata', '')
                elif isinstance(encoded, dict):
                    content = encoded.get('__cdata', '')
                elif isinstance(encoded, str):
                    content = encoded
            
            # Clean up WordPress formatting
            content = self._clean_wp_content(content)
            
            # Get the slug
            slug = None
            
            # Try post_name
            if 'post_name' in post:
                post_name = post['post_name']
                if isinstance(post_name, dict) and '__cdata' in post_name:
                    slug = post_name['__cdata']
            
            # Try link as fallback
            if not slug and 'link' in post:
                link = post['link']
                if link:
                    # Extract slug from URL
                    link = link.rstrip('/')
                    if '/' in link:
                        slug = link.split('/')[-1]
            
            # Use title as final fallback
            if not slug:
                slug = slugify(title)
            
            # Process categories
            categories = []
            if 'category' in post:
                cats = post['category']
                if not isinstance(cats, list):
                    cats = [cats]
                
                for cat in cats:
                    if isinstance(cat, dict):
                        # Check if it's a category (not a tag)
                        domain = cat.get('_domain', '')
                        if domain == 'category':
                            cat_name = cat.get('__cdata', '')
                            cat_slug = cat.get('_nicename', '')
                            
                            if not cat_slug and cat_name:
                                cat_slug = slugify(cat_name)
                                
                            if cat_name and cat_slug:
                                # Get or create category
                                category, created = Category.objects.get_or_create(
                                    slug=cat_slug,
                                    defaults={'name': cat_name}
                                )
                                categories.append(category)
            
            # Create or update post, with a category (use default if none found)
            primary_category = categories[0] if categories else default_category
            
            # Check that we have required data
            if not title or not content:
                self.stdout.write(self.style.WARNING(f"Skipping post with empty title or content: {slug}"))
                return None
                
            post_obj, created = Post.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'content': content,
                    'publish_date': timezone.make_aware(post_date) if timezone.is_naive(post_date) else post_date,
                    'status': 'published',
                    'category': primary_category,
                }
            )
            
            self.stdout.write(f"{'Created' if created else 'Updated'} post: {title}")
            return post_obj
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing post: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            return None
    
    def _get_attachment_url(self, attachment):
        """Extract URL from attachment item"""
        # Check for link first
        if 'link' in attachment:
            return attachment['link']
            
        # Try to find attachment URL in encoded content
        if 'encoded' in attachment:
            encoded = attachment['encoded']
            if isinstance(encoded, list) and len(encoded) > 0:
                content = encoded[0].get('__cdata', '')
                # Look for image URL in content
                img_match = re.search(r'<img.+?src=[\'"](.+?)[\'"]', content)
                if img_match:
                    return img_match.group(1)
            
            # Try direct URL in attachment metadata
        if 'attachment_url' in attachment:
            url = attachment['attachment_url']
            if isinstance(url, dict):
                return url.get('__cdata', '')
            return url
            
        return None
    
    def _get_image_name(self, image_url):
        """Extract image name from URL"""
        parsed_url = urlparse(image_url)
        path = parsed_url.path
        image_name = os.path.basename(path)
        
        # Generate a unique name if needed
        if not image_name or len(image_name) < 5:
            # Generate a random filename
            random_part = base64.urlsafe_b64encode(os.urandom(6)).decode('ascii')
            ext = os.path.splitext(path)[1] or '.jpg'
            image_name = f"wp_image_{random_part}{ext}"
            
        return image_name
    
    def _process_inline_images(self, content, images_path):
        """Download and update inline images in post content"""
        if not content:
            return content
            
        # Find all image tags
        img_tags = re.findall(r'<img.+?src=[\'"](.+?)[\'"].*?>', content)
        
        for img_url in img_tags:
            try:
                # Skip data URLs
                if img_url.startswith('data:'):
                    continue
                    
                # Skip relative URLs that are already in our media path
                if img_url.startswith('/media/'):
                    continue
                
                image_name = self._get_image_name(img_url)
                img_path = f'/media/news/images/{image_name}'
                
                # Download the image
                response = requests.get(img_url, stream=True, timeout=10)
                
                if response.status_code == 200:
                    # Save the image to MEDIA_ROOT
                    save_path = os.path.join(settings.MEDIA_ROOT, 'news/images', image_name)
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Replace the URL in content
                    content = content.replace(img_url, img_path)
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error processing inline image {img_url}: {str(e)}"))
        
        return content
    
    def _clean_wp_content(self, content):
        """Remove WordPress block comments and clean up HTML"""
        if not content:
            return ''
            
        # Remove WordPress block comments
        content = re.sub(r'<!-- wp:.*? -->', '', content)
        content = re.sub(r'<!-- /wp:.*? -->', '', content)
        return content
    