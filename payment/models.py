from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.Choices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.Choices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=8, choices=StatusChoices.choices)
    type = models.CharField(max_length=8, choices=TypeChoices.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.borrowing}"
