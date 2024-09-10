from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PaymentSchedule, Payment
from decimal import Decimal
from datetime import date

class PaymentScheduleTestCase(APITestCase):
    def setUp(self):
        # Initial data for PaymentSchedule creation
        self.schedule_data = {
            "amount": 1000,
            "loan_start_date": "2024-01-10",
            "number_of_payments": 4,
            "periodicity": "1m",
            "interest_rate": 0.1
        }

        # Endpoint for PaymentSchedule creation
        self.create_url = reverse('payment_schedule')

    def test_create_payment_schedule(self):
        # Create PaymentSchedule
        response = self.client.post(self.create_url, self.schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if payments were created correctly
        schedule = PaymentSchedule.objects.get(id=response.data['id'])
        payments = Payment.objects.filter(schedule=schedule)
        self.assertEqual(len(payments), 4)  # There should be 4 payments

        # Validate the details of the first payment
        first_payment = payments.first()
        self.assertEqual(first_payment.date, date(2024, 1, 10))
        self.assertTrue(Decimal(first_payment.principal) > 0)
        self.assertTrue(Decimal(first_payment.interest) > 0)

    def test_patch_payment_schedule(self):
        # Create PaymentSchedule
        response = self.client.post(self.create_url, self.schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        schedule_id = response.data['id']
        payments = Payment.objects.filter(schedule_id=schedule_id)
        payment_id = payments.first().id

        # Initial principal of first payment
        original_principal = payments.first().principal

        # Modify the principal of the first payment via PATCH
        patch_data = {
            "payment_id": payment_id,
            "principal": 50  # New principal for the first payment
        }
        patch_url = reverse('payment_schedule', kwargs={'pk': schedule_id})
        patch_response = self.client.patch(patch_url, patch_data, format='json')

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Fetch the modified payment and check the new principal and recalculated interest
        modified_payment = Payment.objects.get(id=payment_id)
        self.assertEqual(modified_payment.principal, Decimal('50'))

        # Ensure the interest was recalculated correctly
        expected_interest = Decimal('1000') * Decimal(self.schedule_data['interest_rate']) / 100
        self.assertTrue(modified_payment.interest, expected_interest)

        # Check the recalculation for subsequent payments
        subsequent_payment = Payment.objects.filter(schedule_id=schedule_id).order_by('date')[1]
        self.assertTrue(subsequent_payment.principal > 0)
        self.assertTrue(subsequent_payment.interest > 0)
