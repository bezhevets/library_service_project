from rest_framework import viewsets
from borrowing.models import Borrowing
from borrowing.permissions import IsAdminOrIfAuthenticatedBorrowingPermission
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("user", "book")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAdminOrIfAuthenticatedBorrowingPermission]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            is_active = self.request.query_params.get("is_active")
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=int(user_id))
            if is_active == "true":
                queryset = queryset.filter(actual_return_data__isnull=True)
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
