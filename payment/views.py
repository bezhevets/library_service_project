from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """
        Get the queryset of payments based on user role.

        For admins, all payments are retrieved.
        For regular users, only their payments are retrieved.

        Returns:
        - queryset: Filtered queryset based on user's role.
        """
        queryset = Payment.objects.select_related("borrowing")

        if self.action == "list":
            if not self.request.user.is_staff:
                queryset = (
                    queryset.filter(borrowing_id__user_id=self.request.user)
                )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer


class PaymentSuccessView(APIView):
    def get(self, request, pk):
        print(request)
        return Response(
            {"message": "Payment was successfully processed"}, status=status.HTTP_200_OK
        )


class PaymentCancelView(APIView):
    def get(self, request, pk):
        return Response(
            {"message": "Payment can be paid later."}, status=status.HTTP_400_BAD_REQUEST
        )
