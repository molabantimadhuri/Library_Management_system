from django.contrib import admin

from .models import Book, Issue, Member


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'copies')
    search_fields = ('title', 'author', 'category')
    list_filter = ('category',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'due_date', 'return_date', 'fine')
    search_fields = ('book__title', 'member__name', 'member__email')
    list_filter = ('return_date', 'due_date')
