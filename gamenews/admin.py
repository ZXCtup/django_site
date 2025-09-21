from django.contrib import admin

from gamenews.models import Category, Comment, Tag, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug',)
    list_display_links = ('title',)
    prepopulated_fields = {'slug' : ('title',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug',)
    prepopulated_fields = {'slug' : ('title',)}
    order_by = ('title',)
    list_display_links = ('title',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    save_on_top=True
    readonly_fields = ('views',)
    prepopulated_fields = {'slug' : ('title',)}
    filter_horizontal = ['tag']
    list_display=['title','author','views']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'date', 'verify']
    list_editable = ['verify',]
    list_display_links = ['author', 'post']
