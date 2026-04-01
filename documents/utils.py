import io
import base64
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from weasyprint import HTML

logger = logging.getLogger(__name__)

def generate_charts(diagram_data):
    """Génère histogramme et radar en base64."""
    if not diagram_data:
        return None, None

    labels = [item['Critere'] for item in diagram_data]
    values = [item['MasteryLevel'] for item in diagram_data]

    # --- Histogramme ---
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values, color='#ff8e2e')
    ax.set_ylabel('Niveau de maîtrise')
    ax.set_title('Histogramme des compétences')
    ax.set_ylim(0, max(values) + 1 if values else 5)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    hist_buffer = io.BytesIO()
    plt.savefig(hist_buffer, format='png', dpi=100)
    plt.close(fig)
    hist_buffer.seek(0)
    hist_base64 = base64.b64encode(hist_buffer.getvalue()).decode('utf-8')

    # --- Radar ---
    N = len(labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values_radar = values + values[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values_radar, 'o-', linewidth=2, color='#ff8e2e')
    ax.fill(angles, values_radar, alpha=0.25, color='#ff8e2e')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, max(values) + 1 if values else 5)
    ax.set_title('Radar des compétences', pad=20)
    plt.tight_layout()
    radar_buffer = io.BytesIO()
    plt.savefig(radar_buffer, format='png', dpi=100)
    plt.close(fig)
    radar_buffer.seek(0)
    radar_base64 = base64.b64encode(radar_buffer.getvalue()).decode('utf-8')

    return hist_base64, radar_base64

def get_logo_base64():
    """Retourne le logo encodé en base64, ou None si introuvable."""
    try:
        with open(settings.LOGO_PATH, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        logger.warning("Fichier logo introuvable au chemin %s", settings.LOGO_PATH)
        return None

def generate_pdf_from_data(data, base_url=None, logo_base64=None):
    """Génère un PDF à partir des données."""
    # Générer les graphiques
    hist_chart = None
    radar_chart = None
    diagram_data = data.get('diagram')
    if diagram_data and isinstance(diagram_data, list) and len(diagram_data) > 0:
        hist_chart, radar_chart = generate_charts(diagram_data)

    # Logo : soit fourni en base64, soit construit via URL statique
    logo_context = {}
    if logo_base64 is not None:
        logo_context['logo_base64'] = logo_base64
    elif base_url:
        try:
            static_path = staticfiles_storage.url('logo.jpg')
            if static_path.startswith('/'):
                logo_url = base_url.rstrip('/') + static_path
            else:
                logo_url = static_path
            logo_context['logo_url'] = logo_url
        except Exception as e:
            logger.warning("Impossible de générer l'URL du logo: %s", e)

    context = {
        'data': data,
        'histogram_chart': hist_chart,
        'radar_chart': radar_chart,
        **logo_context,
    }
    html_string = render_to_string('rapport_entretien.html', context)
    html = HTML(string=html_string, base_url=base_url)
    return html.write_pdf()