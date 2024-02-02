import os

import stripe
from django.urls import reverse


stripe.api_key = os.environ["STRIPE_SECRET_KEY"]


def calculate_amount_borrowing(borrowing):
    sum_days = borrowing.expected_return_date - borrowing.borrow_date
    amount = int((sum_days.days + 1) * borrowing.book.daily_fee)
    return amount


def create_checkout_session(borrowing, request):
    success_url = reverse(
        "payments:payment-success", kwargs={"pk": borrowing.id}
    )
    cancel_url = reverse(
        "payments:payment-cancel", kwargs={"pk": borrowing.id}
    )

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": calculate_amount_borrowing(borrowing) * 100,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(success_url),
        cancel_url=request.build_absolute_uri(cancel_url),
    )
    return session
