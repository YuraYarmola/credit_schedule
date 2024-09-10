from decimal import Decimal

from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PaymentSchedule, Payment
from .serializers import PaymentScheduleSerializer


class PaymentScheduleViewSet(APIView):
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer

    def post(self, request, *args, **kwargs):
        serializer = PaymentScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        schedule_id = kwargs.get('pk')
        payment_id = request.data.get('payment_id')
        new_principal = Decimal(request.data.get('principal'))

        try:
            schedule = PaymentSchedule.objects.get(id=schedule_id)
            payment = Payment.objects.get(id=payment_id, schedule=schedule)
        except (PaymentSchedule.DoesNotExist, Payment.DoesNotExist):
            return Response({"error": "Schedule or payment not found"}, status=status.HTTP_404_NOT_FOUND)

        outstanding_principal = payment.principal + payment.schedule.amount - new_principal
        payment.principal = new_principal
        payment.interest = outstanding_principal * Decimal(schedule.interest_rate) / 100
        payment.save()

        self.recalculate_subsequent_payments(schedule, payment)

        serializer = PaymentScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def recalculate_subsequent_payments(self, schedule, modified_payment):
        payments = Payment.objects.filter(schedule=schedule, date__gt=modified_payment.date).order_by('date')
        outstanding_principal = modified_payment.schedule.amount - modified_payment.principal

        for payment in payments:
            interest = outstanding_principal * Decimal(schedule.interest_rate) / 100
            principal = payment.principal + payment.interest - interest
            outstanding_principal -= principal

            payment.principal = principal
            payment.interest = interest
            payment.save()

