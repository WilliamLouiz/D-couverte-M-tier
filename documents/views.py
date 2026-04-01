import json
import logging
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
from .models import Document, Spam
from session.models import Session
from django.contrib.staticfiles.storage import staticfiles_storage
from .utils import generate_pdf_from_data

logger = logging.getLogger(__name__)

@csrf_exempt  
@require_POST
def receive_rapport(request):
    try:
        # Récupérer le fichier JSON envoyé dans FormData
        json_file = request.FILES.get('file')
        if not json_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        # Lire le contenu du fichier
        try:
            file_content = json_file.read().decode('utf-8')
            data = json.loads(file_content)
        except UnicodeDecodeError:
            return JsonResponse({'error': 'File encoding error, UTF-8 expected'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        rapport = data.get('rapport_entretien')
        if not rapport:
            return JsonResponse({'error': 'Missing rapport_entretien'}, status=400)

        session_name = rapport.get('SessionId')
        candidat_email = rapport.get('Candidat')

        if not candidat_email:
            return JsonResponse({'error': 'Missing Candidat'}, status=400)

        # Nettoyer les placeholders éventuels
        if session_name.startswith('{') and session_name.endswith('}'):
            session_name = None
        if candidat_email.startswith('{') and candidat_email.endswith('}'):
            candidat_email = None

        # Vérifier si la session existe dans la table Session
        session = None
        if session_name:
            try:
                session = Session.objects.get(session=session_name)
            except Session.DoesNotExist:
                pass

        if session:
            # Stocker dans Document
            doc = Document.objects.create(
                Candidat=candidat_email,
                Session=session_name,
                json_data=rapport
            )

            # --- Envoi de l'e-mail à l'adresse de la session ---
            try:
                pdf_bytes = generate_pdf_from_data(rapport, request.build_absolute_uri('/'))
                subject = f"Rapport de découverte pour {session_name}"
                body = "Veuillez trouver ci-joint le rapport de découverte."
                email = EmailMessage(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [session.email],  # Destinataire : l'email associé à la session
                )
                filename = f"rapport_{candidat_email}_{session_name}.pdf"
                email.attach(filename, pdf_bytes, 'application/pdf')
                email.send()
                logger.info(f"E-mail envoyé pour le document {doc.id} à {session.email}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'e-mail pour le document {doc.id}: {e}")

            return JsonResponse({'status': 'ok', 'type': 'document', 'id': doc.id})
        else:
            # Stocker dans Spam
            spam = Spam.objects.create(
                Candidat=candidat_email,
                Session=session_name or '',
                json_data=rapport,
                raison='Session invalide ou manquante'
            )

            # --- Envoi de l'e-mail à l'adresse par défaut ---
            try:
                pdf_bytes = generate_pdf_from_data(rapport, request.build_absolute_uri('/'))
                subject = f"Rapport Découverte (spam) - session {session_name or 'inconnue'}"
                body = "Un rapport a été classé en spam car la session n'existe pas. Veuillez trouver le PDF ci-joint."
                email = EmailMessage(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    ['joulnar@i-oasis.com'],
                )
                filename = f"spam_{candidat_email}_{session_name or 'no_session'}.pdf"
                email.attach(filename, pdf_bytes, 'application/pdf')
                email.send()
                logger.info(f"E-mail de spam envoyé pour l'entrée {spam.id} à webmaster@i-oasis.fr")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'e-mail de spam pour {spam.id}: {e}")

            return JsonResponse({'status': 'ok', 'type': 'spam', 'id': spam.id})

    except Exception as e:
        logger.exception("Erreur dans receive_rapport")
        return JsonResponse({'error': str(e)}, status=500)