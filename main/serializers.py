from rest_framework import serializers
from .models import PaymentSchedule, Payment
from datetime import timedelta
from math import pow
from decimal import Decimal, getcontext

getcontext().prec = 10


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'date', 'principal', 'interest']


class PaymentScheduleSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentSchedule
        fields = ['id', 'loan_start_date', 'amount', 'number_of_payments', 'periodicity', 'interest_rate', 'payments']

    def create(self, validated_data):
        schedule = super().create(validated_data)
        payments = self.generate_payment_schedule(schedule)
        for payment in payments:
            Payment.objects.create(schedule=schedule, **payment)

        return schedule

    def generate_payment_schedule(self, schedule):
        payments = []
        periodicity_delta = self.get_periodicity_delta(schedule.periodicity)
        l = Decimal(self.get_period_length(schedule.periodicity))
        r = Decimal(schedule.interest_rate) / 100
        i = r * l

        P = Decimal(schedule.amount)
        n = Decimal(schedule.number_of_payments)
        one_plus_i = Decimal(1) + i
        denominator = Decimal(1) - one_plus_i ** (-n)
        EMI = (i * P) / denominator

        outstanding_principal = P
        payment_date = schedule.loan_start_date

        for _ in range(schedule.number_of_payments):
            interest = outstanding_principal * i
            principal = EMI - interest

            payments.append({
                'date': payment_date,
                'principal': principal,
                'interest': interest,
            })

            outstanding_principal -= principal
            payment_date += periodicity_delta

        return payments

    def get_period_length(self, periodicity):
        number = int(periodicity[:-1])
        period = periodicity[-1]
        if period == 'd':
            return Decimal(number) / Decimal(365)
        elif period == 'w':
            return Decimal(number * 7) / Decimal(365)
        elif period == 'm':
            return Decimal(number) / Decimal(12)
        else:
            raise ValueError("Invalid periodicity format")

    def get_periodicity_delta(self, periodicity):
        number = int(periodicity[:-1])
        period = periodicity[-1]
        if period == 'd':
            return timedelta(days=number)
        elif period == 'w':
            return timedelta(weeks=number)
        elif period == 'm':
            return timedelta(days=number * 30)
        else:
            raise ValueError("Invalid periodicity format")

