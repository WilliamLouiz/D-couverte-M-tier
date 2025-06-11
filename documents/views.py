import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document
from .function.email_sender import send_rapport_email
from .function.html_pdf_generator import generate_rapport_pdf

@csrf_exempt
def process_rapport(request):
    if request.method == 'POST':
        try:
            # Initialisation
            data = {}
            json_file = request.FILES.get('file')
            form_data = request.POST.get('json_data')

            # 1. Récupération des données JSON
            if json_file:  # Si fichier JSON envoyé via FILES
                try:
                    data = json.load(json_file)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Fichier JSON invalide'}, status=400)
            elif form_data:  # Si JSON envoyé comme champ form-data
                try:
                    data = json.loads(form_data)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Champ JSON invalide'}, status=400)
            elif request.body:  # Si JSON brut dans le corps
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Corps JSON invalide'}, status=400)
            else:
                return JsonResponse({'error': 'Aucune donnée JSON fournie'}, status=400)

            # 2. Validation des champs obligatoires
            email = data.get('email')
            pseudo = data.get('pseudo')
            if not email or not pseudo:
                return JsonResponse({'error': 'Email et Pseudo sont obligatoires'}, status=400)

            # 3. Préparation des données pour la création du Document
            document_data = {
                'email': email,
                'pseudo': pseudo,
                'json_data': data
            }

            # 4. Traitement des signatures (méthode corrigée)
            signature_fields = {
                'signature_client': 'signature_client',
                'signature_client2': 'signature_client2',
                'signature_technicien': 'signature_technicien',
                'signature_intervenant': 'signature_intervenant',
                'signature_intervenant2': 'signature_intervenant2',
                'signature_exploitant': 'signature_exploitant'
            }

            for field_name, model_field in signature_fields.items():
                uploaded_file = request.FILES.get(field_name)
                if uploaded_file:
                    document_data[model_field] = uploaded_file

            # 5. Création et sauvegarde du document
            document = Document.objects.create(**document_data)

            # 6. Génération du PDF (passez l'instance document complète)
            pdf_buffer = generate_rapport_pdf(data, document)

            # 7. Envoi par email
            send_rapport_email(
                recipient=email,
                pseudo=pseudo,
                pdf_data=pdf_buffer.getvalue()
            )

            return JsonResponse({
                'status': 'success',
                'document_id': document.id,
                'message': 'Rapport et signatures enregistrés avec succès'
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)