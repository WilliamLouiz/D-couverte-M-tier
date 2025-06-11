from django.db import models
import json

class Document(models.Model):
    email = models.EmailField(null=False, blank=False)
    pseudo = models.CharField(max_length=100)
    json_data = models.JSONField(null=True, blank=True)
    signature_client = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signature_client2 = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signature_technicien = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signature_intervenant = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signature_intervenant2 = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signature_exploitant = models.ImageField(upload_to='signatures/', null=True, blank=True)
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name='crée le')  # Date de réception du rapport
    
    def __str__(self):
        return f"{self.pseudo} - {self.email}"