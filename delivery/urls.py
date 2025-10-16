from django.urls import path
from delivery.views import (
    DeliveryListView
)

urlpatterns = [
    path('list', DeliveryListView.as_view(), name='delivery-list'),
]
