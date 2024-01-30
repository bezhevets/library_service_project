from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("user", "book")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingListSerializer
        return BorrowingSerializer
