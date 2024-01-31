from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from book_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_data = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.full_name} borrowing {self.book.title}"

    @staticmethod
    def valid_inventory_date_book(inventory, expected_return_date, error_to_raise):
        if not inventory:
            raise error_to_raise({"book": "This book is out of stock."})
        if expected_return_date < date.today():
            raise error_to_raise(
                {
                    "expected_return_date":
                        "Expected return date must be more today date."
                }
            )

    def clean(self):
        Borrowing.valid_inventory_date_book(
            self.book.inventory,
            self.expected_return_date,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )
