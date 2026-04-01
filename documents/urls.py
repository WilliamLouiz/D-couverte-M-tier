from django.urls import path
from .views import receive_rapport

urlpatterns = [
    path('receive-rapport/', receive_rapport, name='process-rapport'),
]