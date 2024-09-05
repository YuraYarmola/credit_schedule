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
        instance = self.get_object()
        payment_id = request.data.get('payment_id')
        amount_reduction = request.data.get('amount_reduction')

        payment = instance.payments.get(id=payment_id)
        payment.principal -= amount_reduction
        payment.interest = (payment.principal * instance.interest_rate / 100) * instance.periodicity_delta
        payment.save()

        self.recalculate_schedule(instance)

        return Response(PaymentScheduleSerializer(instance).data, status=status.HTTP_200_OK)

    def recalculate_schedule(self, schedule):
        payments = schedule.payments.all().order_by('date')
        outstanding_principal = sum([p.principal for p in payments])

        for payment in payments:
            payment.interest = (outstanding_principal * schedule.interest_rate / 100) * schedule.periodicity_delta
            outstanding_principal -= payment.principal
            payment.save()
