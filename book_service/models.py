import os.path
import uuid

from django.db import models
from django.utils.text import slugify


def book_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
    return os.path.join("books", filename)


class Book(models.Model):
    class CoverChoices(models.Choices):
        HARD = "Hard cover"
        SOFT = "Soft cover"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    cover = models.CharField(max_length=50, choices=CoverChoices.choices)
    image = models.ImageField(
        null=True, blank=True, upload_to=book_image_file_path
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title}({self.author})"
