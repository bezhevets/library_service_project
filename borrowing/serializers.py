from django.db import transaction
from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrowing.models import Borrowing
from payment.models import Payment

from borrowing.tasks import notification_new_borrowing
from payment.serializers import PaymentDetailSerializer
from payment.stripe_helper import create_checkout_session


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs)
        Borrowing.valid_inventory_book(
            attrs["book"].inventory,
            serializers.ValidationError,
        )
        return data

    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = Borrowing.objects.create(**validated_data)
            borrowing.book.inventory -= 1
            borrowing.book.save()

            session = create_checkout_session(
                borrowing, self.context["request"]
            )

            Payment.objects.create(
                status=Payment.StatusChoices.PENDING,
                type=Payment.TypeChoices.PAYMENT,
                borrowing=borrowing,
                session_url=session.url,
                session_id=session.id,
                money_to_pay=session.amount_total / 100,
            )

            notification_new_borrowing.delay(borrowing.id)
        return borrowing


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    user = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="full_name"
    )
    payments = serializers.SlugRelatedField(many=True, read_only=True, slug_field="status")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_data",
            "payments"
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer()
    payments = PaymentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_data",
            "payments"
        )
