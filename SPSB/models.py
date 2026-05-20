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
    file_hash = models.CharField(max_length=64, editable=False)
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


# Volunteer Model - Separates public and private data
class Volunteer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('past', 'Past Volunteer'),
    ]

    username = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique identifier provided via Excel",
        default="",
    )
    # ========== PUBLIC DATA (Visible on website/public profile) ==========
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Profile Picture
    profile_image = models.ImageField(upload_to='volunteers/', blank=True, null=True)
    
    # Bio/Description - What they do, their contribution
    bio = models.TextField(blank=True, default="", help_text="Public bio/contribution description")
    
    # Education Information (Public)
    institution = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="School/College/University Name"
    )
    degree = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="e.g., B.Tech CSE, B.A. English"
    )
    graduation_year = models.IntegerField(
        blank=True,
        null=True,
        help_text="Expected/Actual graduation year"
    )
    
    # Social Media Handles (Public)
    instagram_handle = models.CharField(max_length=100, blank=True, default="")
    twitter_handle = models.CharField(max_length=100, blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    facebook_url = models.URLField(blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    
    # ========== PRIVATE/SENSITIVE DATA (Admin Only) ==========
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Address Information (Private)
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    zip_code = models.CharField(max_length=20, blank=True, default="")
    
    # Emergency Contact (Private)
    emergency_contact_name = models.CharField(max_length=150, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default="")
    
    # ========== META DATA ==========
    volunteer_year = models.IntegerField(
        db_index=True,
        help_text="Year of volunteering (e.g., 2024)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    role = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="e.g., Event Coordinator, Social Media Manager"
    )
    
    joining_date = models.DateField(auto_now_add=True)
    contribution_hours = models.IntegerField(default=0)
    
    # Toggle to show/hide volunteer publicly
    is_public = models.BooleanField(
        default=True,
        help_text="Check to display this volunteer's public profile"
    )
    
    # Who added this volunteer
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_volunteers'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-volunteer_year', 'first_name']
        indexes = [
            models.Index(fields=['volunteer_year', 'status']),
            models.Index(fields=['is_public', 'volunteer_year']),
        ]
        verbose_name = 'Volunteer'
        verbose_name_plural = 'Volunteers'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.volunteer_year})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# Committee Member Model - Similar structure to volunteers but for leadership roles
class CommitteeMember(models.Model):

    username = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique identifier provided via Excel",
        default="",
    )

    POSITION_LEVEL = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('general_secretary', 'General Secretary'),
        ('joint_secretary', 'Joint Secretary'),
        ('treasurer', 'Treasurer'),
        ('coordinator', 'Coordinator'),
        ('program_officer', 'Program Officer'),
        ('senior_program_officer', 'Senior Program Officer'),
        ('program_associate', 'Program Associate'),
        ('member', 'Member'),
        ('academic_councilor', 'Academic Councilor'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('past', 'Past Member'),
    ]

    # ========== PUBLIC DATA (Visible on website/public profile) ==========
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Profile Picture
    profile_image = models.ImageField(upload_to='committee/', blank=True, null=True)
    
    # Bio/Description - What they do, their role details
    bio = models.TextField(blank=True, default="", help_text="Public bio/role description")
    department = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Department/Area they manage (e.g., Marketing, Operations)"
    )
    
    # Education Information (Public)
    institution = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="School/College/University Name"
    )
    qualification = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="e.g., B.Tech CSE, MBA"
    )
    
    # Social Media Handles (Public)
    instagram_handle = models.CharField(max_length=100, blank=True, default="")
    twitter_handle = models.CharField(max_length=100, blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    facebook_url = models.URLField(blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    
    # ========== PRIVATE/SENSITIVE DATA (Admin Only) ==========
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Address Information (Private)
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    zip_code = models.CharField(max_length=20, blank=True, default="")
    
    # Emergency Contact (Private)
    emergency_contact_name = models.CharField(max_length=150, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default="")
    
    # ========== META DATA ==========
    committee_year = models.IntegerField(
        db_index=True,
        help_text="Year of committee tenure (e.g., 2024)"
    )
    position = models.CharField(
        max_length=30,
        choices=POSITION_LEVEL,
        default='member',
        help_text="Committee position/role"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    joining_date = models.DateField(auto_now_add=True)
    tenure_start = models.DateField(blank=True, null=True, help_text="Actual tenure start date")
    tenure_end = models.DateField(blank=True, null=True, help_text="Tenure end date for past members")
    
    # Toggle to show/hide member publicly
    is_public = models.BooleanField(
        default=True,
        help_text="Check to display this member's public profile"
    )
    
    # Who added this committee member
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_committee_members'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-committee_year', 'position', 'first_name']
        indexes = [
            models.Index(fields=['committee_year', 'status']),
            models.Index(fields=['is_public', 'committee_year']),
            models.Index(fields=['position', 'committee_year']),
        ]
        verbose_name = 'Committee Member'
        verbose_name_plural = 'Committee Members'
        unique_together = [('email', 'committee_year')]  # One email per year
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_position_display()} ({self.committee_year})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class LeadershipMessage(models.Model):

    POSITION_CHOICES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('general_secretary', 'General Secretary'),
    ]

    position = models.CharField(max_length=50, choices=POSITION_CHOICES, unique=True)

    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True, default="")
    organization = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")

    image = models.ImageField(upload_to="leaders/", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_position_display()