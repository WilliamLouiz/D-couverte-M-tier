from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def get_pdf_styles():
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    styles.add(ParagraphStyle(
        name='Header1',
        parent=styles['Heading1'],
        fontSize=14, 
        textColor=colors.HexColor('#ff8e2e'),
        spaceAfter=8, 
        leading=18,
        alignment=1  # 0=gauche, 1=centre, 2=droite
    ))

    styles.add(ParagraphStyle(
        name='Header2',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#595959'),
        spaceAfter=4,
        leading=15,
        alignment=1,
        underline=True
    ))

    styles.add(ParagraphStyle(
        name='FieldLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#595959'),
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name='FieldValue',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#a3a3a3'),
        spaceAfter=2,
        leftIndent=10
    ))

    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        textColor=colors.HexColor('#595959'),
        alignment=2  # 0=gauche, 1=centre, 2=droite
    ))
    # style pour les champs de formulaire de gauche et droite
    styles.add(ParagraphStyle(
        name='LeftFieldLabel',
        parent=styles['FieldLabel'],
        fontSize=10,
        textColor=colors.HexColor('#595959'),
        spaceAfter=8,
        leftIndent=0
    ))

    styles.add(ParagraphStyle(
        name='RightFieldValue',
        parent=styles['FieldValue'],
        fontSize=10,
        textColor=colors.HexColor('#a3a3a3'),
        spaceAfter=8,
        alignment=2,  # 0=left, 1=center, 2=right
        rightIndent=0
    ))

    return styles
# Styles pour les tableaux à lignes
def get_line_table_style():
    return [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No visible border
    ]
#création du style de carte
def get_card_style():
    return [
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e1dddd')),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('SPACEAFTER', (0, 0), (-1, -1), 6),
    ]
#alignement des tableaux côte à côte
def get_side_by_side_style():
    return [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Ligne invisible
        ('SPACEAFTER', (0, 0), (0, -1), 15),  # Espace après la colonne gauche
    ]
# Style pour les tableaux avec en-tête 
def get_table_style():
    return [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F0F0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]

