from django.core.mail import EmailMultiAlternatives

def send_rapport_email(recipient, pseudo, pdf_data):
    email = EmailMultiAlternatives(
        subject=f"Votre rapport technique - {pseudo}",
        body=f"Bonjour,\n\nVeuillez trouver ci-joint votre rapport technique.\n\nCordialement,",
        from_email="no-reply@votredomaine.com",
        to=[recipient]
    )
    
    email.attach(
        f"rapport_technique_{pseudo}.pdf",
        pdf_data,
        "application/pdf"
    )
    
    email.send()