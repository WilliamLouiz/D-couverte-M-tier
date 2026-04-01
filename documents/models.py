from django.db import models
from django.utils import timezone

class Document(models.Model):
    Candidat = models.EmailField(null=False, blank=False)
    Session = models.CharField(max_length=100)
    json_data = models.JSONField(null=True, blank=True)
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name='crée le')

    def __str__(self):
        return self.Candidat

class Spam(models.Model):
    Candidat = models.EmailField(null=False, blank=False)
    Session = models.CharField(max_length=100, blank=True)  # peut être vide
    json_data = models.JSONField(null=True, blank=True)
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name='crée le')
    raison = models.CharField(max_length=255, blank=True, help_text="Raison du classement en spam")

    def __str__(self):
        return f"{self.Candidat} - spam"