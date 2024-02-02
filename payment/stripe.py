import os

import stripe
from django.urls import reverse

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]


def create_checkout_session(pk):
    success_url = reverse("payments:payment-success", kwargs={"pk": pk})
    cancel_url = reverse("payments:payment-cancel", kwargs={"pk": pk})

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "T-shirt",
                    },
                    "unit_amount": 2000,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=build_absolute_uri(success_url),
        cancel_url=build_absolute_uri(cancel_url),
    )
    return session


def build_absolute_uri(url):
    return f"http://localhost:8000{url}"

