from datetime import date

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.permissions import IsAdminOrIfAuthenticatedBorrowingPermission
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from payment.models import Payment
from payment.stripe_helper import create_fine_session


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("user", "book")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAdminOrIfAuthenticatedBorrowingPermission]

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related("user", "book")
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=int(user_id))
        if is_active == "true":
            queryset = queryset.filter(actual_return_data__isnull=True)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["GET"],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_data:
            return Response(
                {"detail": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if borrowing.expected_return_date >= date.today():
            borrowing.actual_return_data = date.today()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()
            return Response(
                {"detail": "This book was successfully returned."},
                status=status.HTTP_200_OK,
            )

        session = create_fine_session(borrowing, self.request)

        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.FINE,
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=session.amount_total / 100,
        )
        return Response(
            {"detail": "You must pay the fine before returning the book."},
            status=status.HTTP_400_BAD_REQUEST,
        )
