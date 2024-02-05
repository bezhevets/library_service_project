from datetime import date

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.permissions import IsAdminOrIfAuthenticatedBorrowingPermission
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer, BorrowingReturnSerializer,
)
from payment.models import Payment
from payment.stripe_helper import create_fine_session


class BorrowingViewSet(viewsets.ModelViewSet):

    """
    API endpoint for managing book borrowings.

    list:
    Retrieve a list of book borrowings. If the user is not staff,
    only their borrowings will be included.
    Additional filtering can be applied using query parameters,
    such as 'user_id' and 'is_active'.

    retrieve:
    Retrieve details of a specific book borrowing.

    create:
    Create a new book borrowing.

    return_book:
    Custom action to mark a borrowed book as returned.
    If the book is returned on time, it updates the return date.
    If the book is returned late, it generates a fine and prompts
    the user to pay it.
    """

    queryset = Borrowing.objects.all().select_related("user", "book")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAdminOrIfAuthenticatedBorrowingPermission]

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("user", "book").prefetch_related("payments")
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
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        """
        Perform custom actions when creating a new book borrowing.

        Assigns the borrowing to the current user.
        """

        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk=None):
        """
        Return a borrowed book.

        Parameters:
        - 'pk' (int): ID of the borrowing object.

        Returns:
        - HTTP 200 OK if the book was successfully returned.
        - HTTP 400 Bad Request if there is an issue returning
        the book or paying a fine.
        """

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=str,
                description="Filter for staff user by active borrowings (still not returned)(ex. ?is_active=true)",
                required=False,
            ),
            OpenApiParameter(
                "user_id",
                type=int,
                description="Filter for staff user by user_id (ex. ?user_id=2)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
