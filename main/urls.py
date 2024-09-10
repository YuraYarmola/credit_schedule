from django.urls import path
from .views import PaymentScheduleViewSet

urlpatterns = [
    path('schedule/', PaymentScheduleViewSet.as_view(), name='payment_schedule'),
    path('schedule/<int:pk>/', PaymentScheduleViewSet.as_view(), name='payment_schedule'),
]
