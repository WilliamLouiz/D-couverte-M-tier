from django.urls import path
from .views import process_rapport

urlpatterns = [
    path('process-rapport/', process_rapport, name='process-rapport'),
]