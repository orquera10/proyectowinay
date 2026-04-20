import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Post(models.Model):
    class Tone(models.TextChoices):
        PRIMARY = 'primary', 'Primary'
        SECONDARY = 'secondary', 'Secondary'
        ACCENT = 'accent', 'Accent'

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=280)
    body = models.TextField(blank=True)
    banner_image = models.ImageField(upload_to='posts/banners/', blank=True)
    body_image = models.ImageField(upload_to='posts/body/', blank=True)
    eyebrow = models.CharField(max_length=80, blank=True)
    tone = models.CharField(
        max_length=20,
        choices=Tone.choices,
        default=Tone.PRIMARY,
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'entrada'
        verbose_name_plural = 'entradas'

    def __str__(self):
        return self.title

    @property
    def description(self):
        return self.excerpt

    @property
    def banner_image_url(self):
        if self.banner_image:
            return self.banner_image.url
        return ''

    @property
    def body_image_url(self):
        if self.body_image:
            return self.body_image.url
        return ''

    @property
    def image_url(self):
        return self.banner_image_url

    @property
    def body_paragraphs(self):
        content = self.body.strip()
        if not content:
            return [self.excerpt] if self.excerpt else []
        normalized = content.replace('\r\n', '\n')
        return [paragraph.strip() for paragraph in re.split(r'\n\s*\n', normalized) if paragraph.strip()]

    @property
    def body_blocks(self):
        content = self.body.strip()
        if not content:
            return [{'type': 'paragraph', 'text': self.excerpt}] if self.excerpt else []

        normalized = content.replace('\r\n', '\n')
        blocks = []
        current_lines = []
        current_type = None

        def flush_block():
            nonlocal current_lines, current_type
            if not current_lines:
                return

            if current_type == 'list':
                items = [line[2:].strip() for line in current_lines if line.startswith('- ') and line[2:].strip()]
                if items:
                    blocks.append({'type': 'list', 'items': items})
            else:
                text = ' '.join(line.strip() for line in current_lines if line.strip())
                if text:
                    is_heading = len(current_lines) == 1 and len(text) <= 60 and '.' not in text
                    blocks.append({
                        'type': 'heading' if is_heading else 'paragraph',
                        'text': text,
                    })

            current_lines = []
            current_type = None

        for raw_line in normalized.split('\n'):
            line = raw_line.strip()
            if not line:
                flush_block()
                continue

            line_type = 'list' if line.startswith('- ') else 'text'
            if current_type and line_type != current_type:
                flush_block()

            current_type = line_type
            current_lines.append(line)

        flush_block()
        return blocks

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:180] or 'entrada'
            slug = base_slug
            counter = 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug[:170]}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:post_detail', kwargs={'slug': self.slug})
