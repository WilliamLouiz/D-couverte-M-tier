from django.contrib import admin
from .models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('email', 'session', 'user', 'created_at', 'updated_at')
    search_fields = ('email', 'session', 'user__username')
    list_filter = ('created_at', 'updated_at')
    exclude = ('user',)  # Masquer le champ user dans le formulaire

    def get_queryset(self, request):
        # Récupérer le queryset de base
        qs = super().get_queryset(request)
        # Si l'utilisateur est un superutilisateur, il voit toutes les sessions
        if request.user.is_superuser:
            return qs
        # Sinon, filtrer pour ne montrer que les sessions de l'utilisateur authentifié
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        # Définir l'utilisateur authentifié comme l'utilisateur de la session
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)