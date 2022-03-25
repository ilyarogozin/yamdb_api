from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year',
                    'description', 'category')
    search_fields = ('name',)
    list_filter = ('year',)
    list_editable = ('category',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'author',
                    'score', 'pub_date')
    search_fields = ('title',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'author', 'pub_date', 'review')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'bio', 'role', 'is_staff')
    search_fields = ('username',)
    list_filter = ('role',)
    empty_value_display = '-пусто-'
