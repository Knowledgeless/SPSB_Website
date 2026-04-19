import hashlib
from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Media(models.Model):
    MEDIA_TYPES = [
        ('gallery', 'Gallery'),
        ('hero', 'Hero Section'),
        ('news', 'News'),
    ]

    file = models.ImageField(upload_to='media/')
    file_hash = models.CharField(max_length=64, unique=True, editable=False)
    caption = models.TextField(blank=True, default="")
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPES,
        default='gallery',
        db_index=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    alt_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.file and not self.file_hash:
            self.file.seek(0)
            file_bytes = self.file.read()
            self.file_hash = hashlib.sha256(file_bytes).hexdigest()
            self.file.seek(0)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name


# INFO: This is a through model to allow for additional fields on the relationship between NewsPost and Media 
class NewsPostMedia(models.Model):
    post = models.ForeignKey(
        'NewsPost', 
        on_delete=models.CASCADE,
        related_name='post_media'
    )
    media = models.ForeignKey('Media', on_delete=models.CASCADE, null=True, blank=True)

    order = models.PositiveIntegerField(default=0)

    caption_override = models.TextField(blank=True, default="")
    section_text = models.TextField(blank=True, default="")  # 🔥 ADD THIS

    is_banner = models.BooleanField(default=False)  # 🔥 HERO IMAGE CONTROL

    class Meta:
        ordering = ['order']



# !WARNING: Post model with proper user relation and media handling
class NewsPost(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)

    content = models.TextField(default="")  # safe default

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )

    # allow multiple media
    media = models.ManyToManyField(
        Media,
        blank=True,
        through='NewsPostMedia',
        related_name='posts'
    )
    

    # proper user relation
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_posts'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(uuid.uuid4())[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    