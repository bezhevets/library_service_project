from django.db import transaction
from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrowing.models import Borrowing
from payment.models import Payment

from borrowing.tasks import notification_new_borrowing
from payment.stripe_helper import create_checkout_session


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_data",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_data")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer()
    user = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_data",
        )


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)
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

            notification_new_borrowing.delay(borrowing.id)

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

        return borrowing
