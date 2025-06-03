import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document
from .function.pdf_generator import generate_rapport_pdf
from .function.email_sender import send_rapport_email

@csrf_exempt
def process_rapport(request):
    if request.method == 'POST':
        try:
            # Traitement du fichier JSON
            if request.FILES.get('file'):
                fichier = request.FILES['file']
                try:
                    data = json.load(fichier)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Fichier JSON invalide'}, status=400)
            elif request.body:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Corps JSON invalide'}, status=400)
            else:
                return JsonResponse({'error': 'Aucune donnée fournie'}, status=400)

            # Validation des données obligatoires
            email = data.get('email')
            pseudo = data.get('pseudo')
            
            if not email or not pseudo:
                return JsonResponse({'error': 'Email et Pseudo sont obligatoires'}, status=400)

            # Enregistrement dans Document
            document = Document.objects.create(
                email=email,
                pseudo=pseudo,
                json_data=data
            )

            # Génération du PDF
            pdf_buffer = generate_rapport_pdf(data)

            # Envoi par email
            send_rapport_email(
                recipient=email,
                pseudo=pseudo,
                pdf_data=pdf_buffer.getvalue()
            )

            return JsonResponse({
                'status': 'success',
                'document_id': document.id,
                'message': 'Rapport traité et envoyé avec succès'
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)