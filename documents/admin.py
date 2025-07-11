from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from io import BytesIO
from .models import Document
from django.utils.html import format_html

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('pseudo', 'email', 'date_reception', 'pdf_button')
    readonly_fields = [field.name for field in Document._meta.fields]
    
    def pdf_button(self, obj):
        url = f"/admin/documents/document/generate-pdf/{obj.id}/"
        return format_html(
            '<a class="button" href="{}">Générer PDF</a>',
            url
        )
    pdf_button.short_description = 'PDF'
    pdf_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-pdf/<int:doc_id>/',
                self.admin_site.admin_view(self.generate_pdf),
                name='generate_pdf',
            ),
        ]
        return custom_urls + urls

    def generate_pdf(self, request, doc_id):
        # Récupérer le document
        document = get_object_or_404(Document, id=doc_id)
        
        # Préparer les données pour le template
        context = {
            'data': document.json_data,
            'signatures': {
                'signature_client': document.signature_client.url if document.signature_client else '',
                'signature_client2': document.signature_client2.url if document.signature_client2 else '',
                'signature_technicien': document.signature_technicien.url if document.signature_technicien else '',
                'signature_intervenant': document.signature_intervenant.url if document.signature_intervenant else '',
                'signature_intervenant2': document.signature_intervenant2.url if document.signature_intervenant2 else '',
                'signature_exploitant': document.signature_exploitant.url if document.signature_exploitant else '',
            }
        }
        
        # Rendre le template HTML
        html_string = render_to_string('rapport_template.html', context)
        
        # Créer le PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()
        
        # Créer la réponse
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_{document.pseudo}.pdf"'
        return response
    
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False