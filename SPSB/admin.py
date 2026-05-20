from django.contrib import admin
from .models import Category, Media, NewsPost, NewsPostMedia, Volunteer, CommitteeMember, LeadershipMessage


# ✅ Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# ✅ Media Admin
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'media_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['media_type', 'uploaded_at']
    search_fields = ['caption', 'file']
    readonly_fields = ['file_hash', 'uploaded_at']

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


# 🔥 Inline for NewsPostMedia (THIS IS THE IMPORTANT PART)
class NewsPostMediaInline(admin.TabularInline):
    model = NewsPostMedia
    extra = 1
    autocomplete_fields = ['media']
    ordering = ['order']


# ✅ NewsPost Admin (Main CMS Panel)
@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'status', 'category', 'created_by', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {"slug": ("title",)}  # auto slug (optional)
    readonly_fields = ['created_at', 'updated_at']

    inlines = [NewsPostMediaInline]

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ✅ Volunteer Admin - Organized with fieldsets for public/private data
@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'volunteer_year', 'status', 'institution', 'is_public', 'created_at']
    list_filter = ['volunteer_year', 'status', 'is_public', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'institution']
    readonly_fields = ['created_at', 'updated_at', 'full_name', 'joining_date']
    
    fieldsets = (
        ('PUBLIC PROFILE', {
            'fields': (
                'first_name', 'last_name', 'profile_image',
                'bio', 'is_public'
            ),
            'description': 'These fields are visible on the public website'
        }),
        ('EDUCATION (Public)', {
            'fields': ('institution', 'degree', 'graduation_year'),
        }),
        ('SOCIAL MEDIA (Public)', {
            'fields': ('instagram_handle', 'twitter_handle', 'linkedin_url', 'facebook_url', 'website_url'),
            'description': 'Social media handles for public profile'
        }),
        ('PRIVATE INFORMATION', {
            'fields': (
                'email', 'phone_number', 'date_of_birth',
                'address', 'city', 'state', 'zip_code'
            ),
            'classes': ('collapse',),
            'description': 'Sensitive personal data - Admin only'
        }),
        ('EMERGENCY CONTACT (Private)', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',),
        }),
        ('VOLUNTEER METADATA', {
            'fields': (
                'volunteer_year', 'status', 'role',
                'joining_date', 'contribution_hours'
            ),
        }),
        ('SYSTEM', {
            'fields': ('full_name', 'added_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System generated fields'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


# ✅ Committee Member Admin - Similar to Volunteer but for leadership positions
@admin.register(CommitteeMember)
class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'committee_year', 'department', 'status', 'is_public', 'created_at']
    list_filter = ['committee_year', 'position', 'status', 'is_public', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'institution', 'department']
    readonly_fields = ['created_at', 'updated_at', 'full_name', 'joining_date']
    
    fieldsets = (
        ('🌐 PUBLIC PROFILE', {
            'fields': (
                'first_name', 'last_name', 'profile_image',
                'bio', 'is_public'
            ),
            'description': 'These fields are visible on the public website'
        }),
        ('💼 POSITION & DEPARTMENT', {
            'fields': (
                'position', 'department', 'committee_year', 'status'
            ),
        }),
        ('🎓 EDUCATION (Public)', {
            'fields': ('institution', 'qualification'),
        }),
        ('📱 SOCIAL MEDIA (Public)', {
            'fields': ('instagram_handle', 'twitter_handle', 'linkedin_url', 'facebook_url', 'website_url'),
            'description': 'Social media handles for public profile'
        }),
        ('🔒 PRIVATE INFORMATION', {
            'fields': (
                'email', 'phone_number', 'date_of_birth',
                'address', 'city', 'state', 'zip_code'
            ),
            'classes': ('collapse',),
            'description': 'Sensitive personal data - Admin only'
        }),
        ('🚨 EMERGENCY CONTACT (Private)', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',),
        }),
        ('📊 TENURE INFORMATION', {
            'fields': (
                'joining_date', 'tenure_start', 'tenure_end'
            ),
        }),
        ('👤 SYSTEM', {
            'fields': ('full_name', 'added_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System generated fields'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


# (Optional) Register through model separately if needed
@admin.register(NewsPostMedia)
class NewsPostMediaAdmin(admin.ModelAdmin):
    list_display = ['post', 'media', 'order']
    list_filter = ['post']


@admin.register(LeadershipMessage)
class LeadershipMessageAdmin(admin.ModelAdmin):
    list_display = ['position','name','designation','organization','description','image','updated_at']
    list_filter = ['name']