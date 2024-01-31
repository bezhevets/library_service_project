import os

import telebot
from celery import shared_task

from borrowing.models import Borrowing

bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

@shared_task
def notification_new_borrowing(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    message = (f"*New Borrowing*:"
               f"\n*Book title:* {borrowing.book.title}"
               f"\n*User:* {borrowing.user.email}"
               f"\n*Expected return date:* {borrowing.expected_return_date}")
    bot.send_message(CHAT_ID, message, parse_mode='Markdown')
