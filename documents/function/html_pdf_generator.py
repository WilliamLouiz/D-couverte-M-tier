# from django.template.loader import render_to_string
# from weasyprint import HTML
# from io import BytesIO
# import os
# from django.conf import settings

# def generate_rapport_pdf(data, files=None):
#     try:
              
#         # Rendre le template HTML avec les données
#         html_string = render_to_string('rapport_template.html', {
#             'data': data,
#             'base_url': settings.BASE_DIR
#         })
        
#         # Générer le PDF
#         pdf_file = HTML(
#             string=html_string, 
#             base_url=settings.BASE_DIR
#         ).write_pdf()
        
#         buffer = BytesIO()
#         buffer.write(pdf_file)
#         buffer.seek(0)
#         return buffer
        
#     except Exception as e:
#         print(f"Erreur lors de la génération du PDF: {str(e)}")
#         raise  # Relance l'exception pour la voir dans la réponse API

from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
import base64
from django.conf import settings

def generate_rapport_pdf(data, document_instance):
    try:
        # 1. Préparer les signatures pour le template
        signatures_data = {}
        
        if document_instance:
            # Liste tous les champs de signature
            signature_fields = [
                'signature_client', 'signature_client2',
                'signature_technicien', 'signature_intervenant',
                'signature_intervenant2', 'signature_exploitant'
            ]
            
            for field in signature_fields:
                signature = getattr(document_instance, field)
                if signature:  # Si la signature existe
                    # OPTION A : URL absolue (nécessite MEDIA_URL configuré)
                    signatures_data[field] = settings.MEDIA_URL + signature.name
                    
                    # OPTION B (alternative) : Encodage base64
                    with signature.open('rb') as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                        signatures_data[field] = f"data:image/jpeg;base64,{encoded}"

        # 2. Générer le HTML
        html_string = render_to_string('rapport_template.html', {
            'data': data,
            'signatures': signatures_data,
            'MEDIA_ROOT': settings.MEDIA_ROOT
        })

        # 3. Générer le PDF
        pdf_file = HTML(
            string=html_string,
            base_url=settings.MEDIA_ROOT  # Important pour résoudre les chemins
        ).write_pdf()

        buffer = BytesIO()
        buffer.write(pdf_file)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"Erreur génération PDF : {str(e)}")
        raise