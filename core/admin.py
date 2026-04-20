from django.contrib import admin

from .models import Post, PostGalleryImage, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


class PostGalleryImageInline(admin.TabularInline):
    model = PostGalleryImage
    extra = 1
    fields = ('image', 'caption', 'sort_order')
    ordering = ('sort_order', 'id')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'display_tags',
        'is_published',
        'is_featured',
        'tone',
        'published_at',
    )
    list_filter = ('is_published', 'is_featured', 'tone', 'published_at', 'tags')
    search_fields = ('title', 'excerpt', 'body', 'eyebrow', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    inlines = (PostGalleryImageInline,)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'slug',
                    'eyebrow',
                    'tags',
                    'excerpt',
                    'body',
                    'banner_image',
                    'body_image',
                ),
            },
        ),
        (
            'Publicacion',
            {
                'fields': (
                    'tone',
                    'is_featured',
                    'is_published',
                    'published_at',
                ),
            },
        ),
        (
            'Sistema',
            {
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    @admin.display(description='Etiquetas')
    def display_tags(self, obj):
        return ', '.join(obj.tags.values_list('name', flat=True)) or '-'
