from django.contrib import admin
from .models import Category, BlogPost

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'category', 'featured_image', 'alt_text', 'image_caption', 'reading_time', 'content', 'excerpt', 'status')
        }),
        ('SEO Optimization', {
            'fields': ('meta_title', 'meta_description', 'target_keywords'),
            'description': 'Fields to improve search engine rankings.'
        }),
    )
