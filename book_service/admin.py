from django.contrib import admin

from book_service.models import Book


# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "inventory",
        "daily_fee",
    ]
    search_fields = ["title"]
