from django.db import models


class PaymentSchedule(models.Model):
    loan_start_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_payments = models.IntegerField()
    periodicity = models.CharField(max_length=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)


class Payment(models.Model):
    schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
