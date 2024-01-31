from celery import shared_task

from borrowing.models import Borrowing


@shared_task
def count_borrowing():
    return Borrowing.objects.count()
