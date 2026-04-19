from django.contrib import admin
from .models import Category, Media, NewsPost, NewsPostMedia


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


# (Optional) Register through model separately if needed
@admin.register(NewsPostMedia)
class NewsPostMediaAdmin(admin.ModelAdmin):
    list_display = ['post', 'media', 'order']
    list_filter = ['post']