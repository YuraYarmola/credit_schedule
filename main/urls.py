from django.urls import path
from .views import PaymentScheduleViewSet

urlpatterns = [
    path('', PaymentScheduleViewSet.as_view()),
]
