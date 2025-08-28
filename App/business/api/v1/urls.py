from django.urls import path
from App.business.api.v1.views.business import businesses_collection, business_detail

urlpatterns = [
    path('businesses/', businesses_collection, name='api_businesses_list'),
    path('businesses/<int:pk>/', business_detail, name='api_businesses_detail'),
]

