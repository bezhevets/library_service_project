import os
from datetime import date, timedelta

import telebot
from celery import shared_task

from borrowing.models import Borrowing

bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


@shared_task
def notification_new_borrowing(borrowing_id):
    """
    Send a notification about a new borrowing to a Telegram chat.
    """

    borrowing = Borrowing.objects.get(id=borrowing_id)
    message = (
        f"*New Borrowing*:"
        f"\n*Book title:* {borrowing.book.title}"
        f"\n*User:* {borrowing.user.email}"
        f"\n*Expected return date:* {borrowing.expected_return_date}"
    )
    bot.send_message(CHAT_ID, message, parse_mode="Markdown")


@shared_task
def check_borrowings_overdue():
    """
    Check for overdue borrowings and send a notification to a Telegram chat.

    By default, once a day
    """

    borrowings = Borrowing.objects.filter(actual_return_data__isnull=True)
    message = None
    for object_borrowing in borrowings:
        if object_borrowing.expected_return_date <= date.today():
            if not message:
                message = "*🚨---List of overdue---🚨*"

            message += (
                f"\n*ID:* {object_borrowing.id}"
                f"\n*Expected data:* {object_borrowing.expected_return_date}"
                f"\n*Book:* {object_borrowing.book.title}"
                f"\n*User:* {object_borrowing.user.email}\n"
            )

    if message:
        bot.send_message(CHAT_ID, message, parse_mode="Markdown")
    else:
        bot.send_message(
            CHAT_ID, "No borrowings overdue today!👍", parse_mode="Markdown"
        )
