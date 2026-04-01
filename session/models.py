from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model

class Session(models.Model):
    email = models.EmailField(max_length=255)
    session = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(default=timezone.now, verbose_name= 'Date de Création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name= 'Date de Modification')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name= 'Crée par')

    def __str__(self):
        return f"Session {self.session}"

    class Meta:
        ordering = ['-created_at']

# Utilisation d'un signal pour définir l'utilisateur automatiquement
@receiver(pre_save, sender=Session)
def set_session_user(sender, instance, **kwargs):
    if not instance.user_id:  # Si l'utilisateur n'est pas déjà défini
        User = get_user_model()
        instance.user = User.objects.get(id=instance._current_user_id)