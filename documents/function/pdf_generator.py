from io import BytesIO
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import letter
from .pdf_styles import get_card_style, get_line_table_style, get_pdf_styles, get_side_by_side_style, get_table_style
from reportlab.lib.units import cm

def generate_rapport_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = get_pdf_styles()
    story = []
    
    # Titre principal
    title = Paragraph(
        f"Document B2 - Fiche de préparation de mise en service", 
        styles['Header1']
    )
    story.append(title)
    story.append(Spacer(1, 10))
    
    # Etape 1 - Date et Nom sur la même ligne
    etape1 = data.get('Etape 1', {})
    
    # Création d'un tableau à 2 colonnes pour la mise en page
    date_nom_data = [
        [
            Paragraph(f"<b>Date:</b> {etape1.get('Date', '')}", styles['Normal']),
            Paragraph(f"<b>Nom:</b> {etape1.get('Nom', '')}", styles['RightAlign'])
        ]
    ]
    
    date_nom_table = Table(date_nom_data, colWidths=['70%', '30%'])
    date_nom_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(date_nom_table)
    story.append(Spacer(1, 5))

    # Section Système
    story.append(Paragraph("Numéro ou nom du système", styles['FieldLabel']))
    story.append(Paragraph(
        etape1.get('Numero_ou_nom_systeme', '[Non spécifié]'), 
        styles['FieldValue']
    ))
    story.append(Spacer(1, 5))

    # Section Travail
    story.append(Paragraph("Désignation du travail", styles['FieldLabel']))
    story.append(Paragraph(
        etape1.get('Designation_travail', '[Non spécifié]'), 
        styles['FieldValue']
    ))
    story.append(Spacer(1, 5))

    # Tableau d'outillage
    story.append(Paragraph(
        "Outillage spécifique et outillage nécessaire à la mise en oeuvre", 
        styles['Header2']
    ))
    
    # Préparation des données du tableau
    outillage_data = [
        [
            Paragraph("<b>Désignation</b>", styles['FieldLabel']),
            Paragraph("<b>Quantité</b>", styles['FieldLabel']), 
            Paragraph("<b>Observations</b>", styles['FieldLabel'])
        ]
    ]
    
    for outil in etape1.get('outillage', []):
        outillage_data.append([
            Paragraph(outil.get('designation', '[ ]'), styles['FieldValue']),
            Paragraph(str(outil.get('quantite', '[ ]')), styles['FieldValue']),
            Paragraph(outil.get('observations', '[ ]'), styles['FieldValue'])
        ])
    
    # Si pas d'outils, ajouter une ligne vide
    if len(outillage_data) == 1:
        outillage_data.append(['[ ]', '[ ]', '[ ]'])
    
    # Création du tableau avec style
    table = Table(outillage_data, colWidths=[10*cm, 3*cm, 7*cm])
    table.setStyle(TableStyle(get_table_style()))
    
    story.append(table)
    story.append(Spacer(1, 15))

    # Action spécifique
    story.append(Paragraph("Action spécifique de prévention en matière d'hygiène et de sécurité", styles['FieldLabel']))
    story.append(Paragraph(
        etape1.get('Action_specifique', '[Non spécifié]'), 
        styles['FieldValue']
    ))
    story.append(Spacer(1, 25))

    # Ajout d'un saut de page avant l'étape 2
    story.append(PageBreak())

    # Etape 2 - Tableau de relevés
    etape2 = data.get('Etape 2', {})
    tableau_releves = etape2.get('Tableau de relevés', {})
    
    story.append(Paragraph("Tableau de relevés", styles['Header1']))
    story.append(Spacer(1, 15))

    # Fonction pour générer des tables de relevés
    def generate_releves_table(equipement_data, title):
        story.append(Paragraph(title, styles['Header2']))
        story.append(Spacer(1, 5))
        
        if not equipement_data:
            story.append(Paragraph("Aucune donnée disponible", styles['FieldValue']))
            story.append(Spacer(1, 15))
            return
        
        for equipement, mesures in equipement_data.items():
            story.append(Paragraph(equipement, styles['FieldLabel']))
            
            if not mesures:
                story.append(Paragraph("Aucune mesure disponible", styles['FieldValue']))
                story.append(Spacer(1, 10))
                continue
                
            # Préparation des données du tableau
            releves_data = []
            # headers = list(next(iter(mesures.values())).keys()) if mesures else []
            if mesures:
                first_value = next(iter(mesures.values()))
                if isinstance(first_value, dict):
                    headers = list(first_value.keys())
                else:
                    headers = []
            else:
                headers = []

            releves_data.append([Paragraph(f"<b>{header}</b>", styles['FieldLabel']) for header in ['Mesure'] + list(headers)])
            
            for mesure, valeurs in mesures.items():
                row = [Paragraph(mesure, styles['FieldValue'])]
                for header in headers:
                    row.append(Paragraph(str(valeurs.get(header, '') or '[ ]'), styles['FieldValue']))
                releves_data.append(row)
            
            # Création du tableau avec style
            col_widths = [4*cm] + [3*cm] * len(headers)
            table = Table(releves_data, colWidths=col_widths)
            table.setStyle(TableStyle(get_table_style()))
            
            story.append(table)
            story.append(Spacer(1, 10))
    
    def generate_three_columns_table(equipement_data, title, column_names):
        story.append(Paragraph(title, styles['Header2']))
        story.append(Spacer(1, 5))
        
        if not equipement_data:
            story.append(Paragraph("Aucune donnée disponible", styles['FieldValue']))
            story.append(Spacer(1, 15))
            return
        
        # Préparation des données du tableau
        table_data = []
        
        # En-tête avec les noms des colonnes
        table_data.append([Paragraph(f"<b>{name}</b>", styles['FieldLabel']) for name in column_names])
        
        # Récupérer toutes les mesures uniques (union des clés de tous les sous-équipements)
        all_measures = set()
        for sub_equip in equipement_data.values():
            if isinstance(sub_equip, dict):
                all_measures.update(sub_equip.keys())
        
        # Trier les mesures pour avoir un ordre cohérent
        sorted_measures = sorted(all_measures)
        
        # Remplir les données
        for measure in sorted_measures:
            row = []
            for sub_equip_name in column_names:
                sub_equip = equipement_data.get(sub_equip_name, {})
                value = sub_equip.get(measure, '')
                row.append(Paragraph(str(value) if value else '[ ]', styles['FieldValue']))
            
            # Ajouter le nom de la mesure en première colonne
            row.insert(0, Paragraph(measure, styles['FieldValue']))
            table_data.append(row)
        
        # Ajouter les noms de mesures dans l'en-tête
        table_data[0].insert(0, Paragraph("<b>Mesure</b>", styles['FieldLabel']))
        
        # Création du tableau avec style
        col_widths = [4*cm] + [4*cm] * len(column_names)
        table = Table(table_data, colWidths=col_widths)
        
        # Style personnalisé pour ce tableau
        table_style = TableStyle([
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
            ('SPAN', (0, 0), (0, 0)),  # Fusionner la première cellule de l'en-tête
        ])
        
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 15))
    
    # Nouvelle fonction pour le tableau à 5 colonnes (1 mesure + 4 ventilateurs)
    def generate_ventilateurs_table(equipement_data, title):
        story.append(Paragraph(title, styles['Header2']))
        story.append(Spacer(1, 5))
        
        if not equipement_data:
            story.append(Paragraph("Aucune donnée disponible", styles['FieldValue']))
            story.append(Spacer(1, 15))
            return
        
        # Préparation des données du tableau
        table_data = []
        
        # En-tête avec les noms des ventilateurs
        table_data.append(
            [Paragraph("<b>Mesure</b>", styles['FieldLabel'])] + 
            [Paragraph(f"<b>V{i}</b>", styles['FieldLabel']) for i in range(1, 5)]
        )
        
        # Récupérer toutes les mesures uniques (union des clés de tous les ventilateurs)
        all_measures = set()
        for v_num in range(1, 5):
            v_key = f"V{v_num}"
            if v_key in equipement_data and isinstance(equipement_data[v_key], dict):
                all_measures.update(equipement_data[v_key].keys())
        
        # Trier les mesures pour avoir un ordre cohérent (vous pouvez personnaliser cet ordre)
        sorted_measures = sorted(all_measures)
        
        # Remplir les données
        for measure in sorted_measures:
            row = [Paragraph(measure, styles['FieldValue'])]
            for v_num in range(1, 5):
                v_key = f"V{v_num}"
                value = equipement_data.get(v_key, {}).get(measure, '')
                row.append(Paragraph(str(value) if value else '[ ]', styles['FieldValue']))
            table_data.append(row)
        
        # Création du tableau avec style
        col_widths = [5*cm] + [3*cm] * 4  # 5cm pour la colonne Mesure, 3cm pour chaque V1-V4
        table = Table(table_data, colWidths=col_widths)
        
        # Style personnalisé pour ce tableau
        table_style = TableStyle([
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
        ])
        
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 15))

    def generate_regulateur_table(regulateur_data, title):
        story.append(Paragraph(title, styles['Header2']))
        story.append(Spacer(1, 5))

        if not regulateur_data:
            story.append(Paragraph("Aucune donnée disponible", styles['FieldValue']))
            story.append(Spacer(1, 15))
            return
        
        # Liste des paramètres dans l'ordre souhaité
        parametres = [
            "Consigne",
            "Différentiel",
            "Dégivrage durée",
            "Temp. fin de dégivrage",
            "Dégivrage début",
            "Dégivrage fin"
        ]
        
        # Préparation des données du tableau
        table_data = [
            [Paragraph("<b>Paramètre</b>", styles['FieldLabel']), 
            Paragraph("<b>Valeur</b>", styles['FieldLabel'])]
        ]
        
        for param in parametres:
            value = regulateur_data.get(param, '')
            table_data.append([
                Paragraph(param, styles['FieldValue']),
                Paragraph(str(value) if value else '[ ]', styles['FieldValue'])
            ])
        
        # Création du tableau avec style
        table = Table(table_data, colWidths=[8*cm, 4*cm])
        
        # Style personnalisé pour ce tableau
        table_style = TableStyle([
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
        ])
        
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 15))
    # Utilisation de la nouvelle fonction pour les compresseurs et condenseurs
    if 'Compresseur 1' in tableau_releves:
        generate_three_columns_table(
            tableau_releves['Compresseur 1'], 
            "Compresseur", 
            ['CP1', 'CP2']
        )

    if 'Condenseur 1' in tableau_releves:
        generate_three_columns_table(
            tableau_releves['Condenseur 1'], 
            "Condenseur", 
            ['V1', 'V2']
        )

    if 'Compresseur 2' in tableau_releves:
        generate_three_columns_table(
            tableau_releves['Compresseur 2'], 
            "Compresseur", 
            ['CP1', 'CP2']
        )
    if 'Condenseur Ventilateur' in tableau_releves:
        generate_three_columns_table(
            tableau_releves['Condenseur Ventilateur'], 
            "Condenseur Ventilateur", 
            ['V1', 'V2']
        )
    
    # Commentaire et analyse
    commentaire = tableau_releves.get('commentaire et analyse', '')
    if commentaire:
        story.append(Paragraph("Commentaire et analyse", styles['Header2']))
        story.append(Paragraph(commentaire, styles['FieldValue']))
        story.append(Spacer(1, 15))
    
    # Fluide Frigorigène
    fluide_data = tableau_releves.get('Fluide Frigorigène', {})
    if fluide_data:
        story.append(Paragraph("Fluide Frigorigène", styles['Header2']))
        fluide_table_data = [
            [Paragraph("<b>Type de fluide</b>", styles['FieldLabel']), Paragraph(fluide_data.get('Type de fluide', '[Non spécifié]'), styles['FieldValue'])],
            [Paragraph("<b>Quantité (Kg)</b>", styles['FieldLabel']), Paragraph(fluide_data.get('Quantite (Kg)', '[Non spécifié]'), styles['FieldValue'])]
        ]
        table = Table(fluide_table_data, colWidths=[6*cm, 6*cm])
        table.setStyle(TableStyle(get_table_style()))
        story.append(table)
        story.append(Spacer(1, 15))
    
    # Huile
    huile_data = tableau_releves.get('Huile', {})
    if huile_data:
        story.append(Paragraph("Huile", styles['Header2']))
        huile_table_data = [
            [Paragraph("<b>Type d'Huile</b>", styles['FieldLabel']), Paragraph(huile_data.get('Huile Type', '[Non spécifié]'), styles['FieldValue'])],
            [Paragraph("<b>Niveau</b>", styles['FieldLabel']), Paragraph(huile_data.get('Huile niveau', '[Non spécifié]'), styles['FieldValue'])]
        ]
        table = Table(huile_table_data, colWidths=[6*cm, 6*cm])
        table.setStyle(TableStyle(get_table_style()))
        story.append(table)
        story.append(Spacer(1, 15))
    
    # Utilisation de la nouvelle fonction pour les évaporateurs ventilateurs
    if 'Evaporateur Ventilateur 1' in tableau_releves:
        generate_ventilateurs_table(
            tableau_releves['Evaporateur Ventilateur 1'], 
            "Evaporateur Ventilateur(s)"
        )
    if 'Evaporateur Ventilateur 2' in tableau_releves:
        generate_ventilateurs_table(
            tableau_releves['Evaporateur Ventilateur 2'], 
            "Evaporateur Ventilateur(s)"
        )
    
    # Ajout d'un saut de page avant l\'étape 2 - Relevés techniques
    story.append(PageBreak())
    
    # Etape 2 - Relevés techniques
    releves_techniques = etape2.get('Relevés techniques', {})
    story.append(Paragraph("Étape 2 - Relevés techniques", styles['Header1']))
    story.append(Spacer(1, 15))
    # Compresseur
    if 'Compresseur' in releves_techniques:
        generate_three_columns_table(
            releves_techniques['Compresseur'], 
            "Compresseur", 
            ['C', 'NC']
        )
    
    # Condenseur Ventilateur
    if 'Condenseur Ventilateur' in releves_techniques:
        generate_three_columns_table(
            releves_techniques['Condenseur Ventilateur'], 
            "Condenseur Ventilateur", 
            ['C', 'NC']
        )

    # Réglages Pressostats
    reglages_data = releves_techniques.get('Réglages Pressostats', {})
    if reglages_data:
        story.append(Paragraph("Réglages Pressostats", styles['Header2']))
        
        reglages_table_data = [
            [Paragraph("<b>Paramètre</b>", styles['FieldLabel']), 
             Paragraph("<b>Coupure</b>", styles['FieldLabel']), 
             Paragraph("<b>Enclenchement</b>", styles['FieldLabel'])]
        ]
        
        # Ajouter les lignes pour chaque paramètre
        params = ['BP régul', 'BP sécu', 'HP sécu', 'HP régul']
        for param in params:
            reglages_table_data.append([
                Paragraph(param, styles['FieldValue']),
                Paragraph(reglages_data.get('Coupure', {}).get(param, '[ ]'), styles['FieldValue']),
                Paragraph(reglages_data.get('Enclenchement', {}).get(param, '[ ]'), styles['FieldValue'])
            ])
        
        table = Table(reglages_table_data, colWidths=[5*cm, 3.5*cm, 3.5*cm])
        table.setStyle(TableStyle(get_table_style()))
        story.append(table)
        story.append(Spacer(1, 15))
    
    # Régulateur
    # Utilisation de la fonction pour le régulateur
    if 'Régulateur' in releves_techniques:
        generate_regulateur_table(
            releves_techniques['Régulateur'], 
            "Régulateur"
        )
        
    # Fluide Frigorigène
    fluide_tech_data = releves_techniques.get('Fluide Frigorigène', {})
    if fluide_tech_data:
        story.append(Paragraph("Fluide Frigorigène", styles['Header2']))
        fluide_table_data = [
            [Paragraph("<b>Type de fluide</b>", styles['FieldLabel']), Paragraph(fluide_tech_data.get('Type de fluide', '[Non spécifié]'), styles['FieldValue'])],
            [Paragraph("<b>Quantité (kg)</b>", styles['FieldLabel']), Paragraph(fluide_tech_data.get('Quantité', '[Non spécifié]'), styles['FieldValue'])]
        ]
        table = Table(fluide_table_data, colWidths=[6*cm, 6*cm])
        table.setStyle(TableStyle(get_table_style()))
        story.append(table)
        story.append(Spacer(1, 15))
    
    # Huile
    huile_tech_data = releves_techniques.get('Huile', {})
    if huile_tech_data:
        story.append(Paragraph("Huile", styles['Header2']))
        huile_table_data = [
            [Paragraph("<b>Type</b>", styles['FieldLabel']), Paragraph(huile_tech_data.get('Huile Type', '[Non spécifié]'), styles['FieldValue'])],
            [Paragraph("<b>Niveau</b>", styles['FieldLabel']), Paragraph(huile_tech_data.get('Huile niveau', '[Non spécifié]'), styles['FieldValue'])]
        ]
        table = Table(huile_table_data, colWidths=[6*cm, 6*cm])
        table.setStyle(TableStyle(get_table_style()))
        story.append(table)
        story.append(Spacer(1, 15))
    
    # Evaporateur Ventilateur
    if 'Evaporateur Ventilateur' in releves_techniques:
        generate_ventilateurs_table(
            releves_techniques['Evaporateur Ventilateur'], 
            "Evaporateur (s)"
        )
    # Commentaire et analyse
    commentaire_tech = releves_techniques.get('commentaire et analyse', '')
    if commentaire_tech:
        story.append(Paragraph("Commentaire et analyse", styles['Header2']))
        story.append(Paragraph(commentaire_tech, styles['FieldValue']))
        story.append(Spacer(1, 15))
    
    # Ajout d'un saut de page avant l'étape 3
    story.append(PageBreak())
    
    # Etape 3
    etape3 = data.get('Etape 3', {})
    story.append(Paragraph("Document C2 - Bon d'attachement", styles['Header1']))
    story.append(Spacer(1, 15))
    
    # Fonction pour créer une ligne avec label à gauche et valeur à droite
    def add_field_line(label, value, is_checkbox=False):
        if is_checkbox:
            value_text = "- [ ] Choisissez la date et l'heure" if not value else f"{value}"
        else:
            value_text = str(value) if value else '[ ]'
        
        line_data = [
            [Paragraph(f"<b>{label}</b>", styles['LeftFieldLabel']), 
             Paragraph(value_text, styles['RightFieldValue'])]
        ]
        
        line_table = Table(line_data, colWidths=['70%', '30%'])
        line_table.setStyle(TableStyle(get_line_table_style()))
        
        story.append(line_table)

    # Ajout des champs un par un
    add_field_line("Nom du technicien", etape3.get('Nom', ''))
    story.append(Spacer(1, 5))

    add_field_line("Date et Heure départ", etape3.get('date et heure depart', ''), is_checkbox=True)
    story.append(Spacer(1, 5))

    add_field_line("Numéro ou nom du système", etape3.get('Numero_ou_nom_systeme', ''))
    story.append(Spacer(1, 5))

    add_field_line("Date et Heure d'arrivée", etape3.get('date et heure arrivé', ''), is_checkbox=True)
    story.append(Spacer(1, 5))

    add_field_line("Nombre d'heures effectuées", str(etape3.get('nombre d\'heures effectuées', '')))

    story.append(Spacer(1, 20))
    
    # Fournitures
    story.append(Paragraph("Fournitures", styles['Header2']))
    
    fournitures_data = [
        [
            Paragraph("<b>Désignation</b>", styles['FieldLabel']),
            Paragraph("<b>Quantité</b>", styles['FieldLabel']), 
            Paragraph("<b>Observations</b>", styles['FieldLabel'])
        ]
    ]
    
    for fourniture in etape3.get('Fournitures', []):
        fournitures_data.append([
            Paragraph(fourniture.get('designation', '[ ]'), styles['FieldValue']),
            Paragraph(str(fourniture.get('quantite', '[ ]')), styles['FieldValue']),
            Paragraph(fourniture.get('observations', '[ ]'), styles['FieldValue'])
        ])
    
    # Si pas de fournitures, ajouter une ligne vide
    if len(fournitures_data) == 1:
        fournitures_data.append(['[ ]', '[ ]', '[ ]'])
    
    # Création du tableau avec style
    table = Table(fournitures_data, colWidths=[8*cm, 3*cm, 7*cm])
    table.setStyle(TableStyle(get_table_style()))
    
    story.append(table)
    story.append(Spacer(1, 15))
    
    # Travail réalisé
    story.append(Paragraph("Travail réalisé", styles['Header2']))
    story.append(Paragraph(
        etape3.get('travail_realise', '[Non spécifié]'), 
        styles['FieldValue']
    ))
    story.append(Spacer(1, 15))
    
    #les cartes pour séparer le technicien et le client
    def get_card_data(title, observations, signature_date, is_technicien=True):
        card_data = []
        # Titre de la carte
        card_data.append([Paragraph(f"<b>{title}</b>", styles['Header2'])])
        
        # Section Observations
        card_data.append([Paragraph("<b>Observations</b>", styles['FieldLabel'])])
        if isinstance(observations, list):
            for obs in observations:
                card_data.append([Paragraph(f"- {obs}", styles['FieldValue'])])
        else:
            card_data.append([Paragraph(f"- {observations}", styles['FieldValue'])])
        
        # Section Signature
        card_data.append([Spacer(1, 10)])
        card_data.append([Paragraph("<b>Signature</b>", styles['FieldLabel'])])
        card_data.append([Paragraph(f"- Date de signature", styles['FieldValue'])])
        card_data.append([Paragraph(f"  {signature_date}", styles['FieldValue'])])
        
        if not is_technicien:
            # Section supplémentaire pour le client
            card_data.append([Spacer(1, 10)])
            card_data.append([Paragraph("<b>Efficer</b>", styles['FieldLabel'])])
        
        return card_data
        # Section Technicien et Client
    etape3 = data.get('Etape 3', {})
    technicien = etape3.get('technicien', {})
    client = etape3.get('client', {})

    # Préparation des données pour les deux cartes
    tech_data = get_card_data(
        "Technicien",
        technicien.get('observations', '[Aucune observation]'),
        technicien.get('date_signature', '[Non signé]'),
        is_technicien=True
    )

    client_data = get_card_data(
        "Client",
        client.get('observations', '[Aucune observation]'),
        client.get('date_signature', '[Non signé]'),
        is_technicien=False
    )

    # Création d'une table à 3 colonnes (carte + espace + carte)
    side_by_side_data = [
        [
            # Colonne gauche - Technicien
            Table(tech_data, colWidths=['*'], style=get_card_style()),
            # Colonne centrale - Espacement (vide)
            '',
            # Colonne droite - Client
            Table(client_data, colWidths=['*'], style=get_card_style())
        ]
    ]
    
    # Table principale avec largeurs proportionnelles
    cards_table = Table(side_by_side_data, 
                    colWidths=['48%', '4%', '48%'])  # 4% pour l'espace
    # Style avec espacement visible
    cards_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),  # Fond blanc pour l'espace
    ]))

    # Ajout au document
    story.append(cards_table)
    story.append(Spacer(1, 25))  # Espace après les cartes
    # Ajout d'un saut de page avant l'étape 4
    story.append(PageBreak())
    
    # Etape 4
    etape4 = data.get('Etape 4', {})
    story.append(Paragraph("Étape 4 - Contrôle de conformité", styles['Header1']))
    story.append(Spacer(1, 15))
    
    # Informations de base
    info_data = [
        [Paragraph("<b>Adresse</b>", styles['FieldLabel']), Paragraph(etape4.get('Adresse', '[Non spécifié]'), styles['FieldValue'])],
        [Paragraph("<b>Date contrôle</b>", styles['FieldLabel']), Paragraph(etape4.get('Date controle', '[Non spécifié]'), styles['FieldValue'])],
        [Paragraph("<b>Motif du contrôle</b>", styles['FieldLabel']), Paragraph(etape4.get('Motif du controle', '[Non spécifié]'), styles['FieldValue'])],
        [Paragraph("<b>Présence de fuite</b>", styles['FieldLabel']), Paragraph(etape4.get('Présence de fuite', '[Non spécifié]'), styles['FieldValue'])]
    ]
    
    info_table = Table(info_data, colWidths=[6*cm, 6*cm])
    info_table.setStyle(TableStyle(get_table_style()))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # Contrôles de conformité
    story.append(Paragraph("Contrôles de conformité", styles['Header2']))
    
    conformite_data = [
        [Paragraph("<b>Essai individuel 11 x PS</b>", styles['FieldLabel']), 
         Paragraph(str(etape4.get('essai individuel 11 x PS', '[Non spécifié]')), styles['FieldValue']),
         Paragraph("<b>Conformité</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('conformite_essai_individuel', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Position coupure pressostat</b>", styles['FieldLabel']), 
         Paragraph(str(etape4.get('Position coupure pressostat', '[Non spécifié]')), styles['FieldValue']),
         Paragraph("<b>Conformité</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Conformité Pression de coupure pressostat', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Soupape de sécurité</b>", styles['FieldLabel']), 
         Paragraph(str(etape4.get('Soupape de sécurité', '[Non spécifié]')), styles['FieldValue']),
         Paragraph("<b>Conformité</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Conformité Soupape de sécurité', '[Non spécifié]'), styles['FieldValue'])],
    ]
    
    conformite_table = Table(conformite_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
    conformite_table.setStyle(TableStyle(get_table_style()))
    story.append(conformite_table)
    story.append(Spacer(1, 15))
    
    # Vérifications diverses
    story.append(Paragraph("Vérifications diverses", styles['Header2']))
    
    verifications_data = [
        [Paragraph("<b>Installation complète conforme au schéma frigorifique</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Installation complète conforme au schéma frigorifique', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Installation complète conforme au schéma électrique</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Installation complète conforme au schéma électrique', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Vérification de tous les documents</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Vérification de tous les documents', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Vérification des supports et des fixations</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Vérification des supports et des fixations', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Vérification de la qualité des brasures et autres joints</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Vérification de la qualité des brasures et autres joints', '[Non spécifié]'), styles['FieldValue'])],
        
        [Paragraph("<b>Vérification de l'accessibilité des systèmes</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Vérification de l\'accessibilité des systèmes pour leur entretien ou réparations', '[Non spécifié]'), styles['FieldValue'])],
    ]
    
    verifications_table = Table(verifications_data, colWidths=[8*cm, 4*cm])
    verifications_table.setStyle(TableStyle(get_table_style()))
    story.append(verifications_table)
    story.append(Spacer(1, 15))
    
    # Observations
    story.append(Paragraph("Observation", styles['Header2']))
    story.append(Paragraph(
        etape4.get('Observation', '[Non spécifié]'), 
        styles['FieldValue']
    ))
    story.append(Spacer(1, 15))
    
    # Signatures
    story.append(Paragraph("Signatures", styles['Header2']))
    
    signatures_data = [
        [Paragraph("<b>Intervenant</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Intervenant', {}).get('Nom', '[Non spécifié]'), styles['FieldValue']),
         Paragraph("<b>Signature</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Intervenant', {}).get('Signature', '[Non signé]'), styles['FieldValue'])],
        
        [Paragraph("<b>Client</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Client', {}).get('Nom', '[Non spécifié]'), styles['FieldValue']),
         Paragraph("<b>Signature</b>", styles['FieldLabel']), 
         Paragraph(etape4.get('Client', {}).get('Signature', '[Non signé]'), styles['FieldValue'])],
    ]
    
    signatures_table = Table(signatures_data, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
    signatures_table.setStyle(TableStyle(get_table_style()))
    story.append(signatures_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer