from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from .models import Document, Spam
from .utils import generate_pdf_from_data, get_logo_base64

class PDFMixin:
    list_display = ('Candidat', 'Session', 'date_reception', 'pdf_button')
    
    def pdf_button(self, obj):
        url = reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_generate_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}">Générer PDF</a>', url)
    pdf_button.short_description = 'PDF'
    pdf_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-pdf/<int:obj_id>/',
                self.admin_site.admin_view(self.generate_pdf),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_generate_pdf',
            ),
        ]
        return custom_urls + urls

    def generate_pdf(self, request, obj_id):
        obj = get_object_or_404(self.model, id=obj_id)
        # Utiliser la même fonction de génération, en lui passant le logo en base64
        logo_base64 = get_logo_base64()
        pdf_bytes = generate_pdf_from_data(obj.json_data, logo_base64=logo_base64)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_{obj.Candidat}.pdf"'
        return response

@admin.register(Document)
class DocumentAdmin(PDFMixin, admin.ModelAdmin):
    list_display = PDFMixin.list_display
    readonly_fields = [field.name for field in Document._meta.fields]

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Spam)
class SpamAdmin(PDFMixin, admin.ModelAdmin):
    list_display = PDFMixin.list_display + ('raison',)
    readonly_fields = [field.name for field in Spam._meta.fields] + ['raison']

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False