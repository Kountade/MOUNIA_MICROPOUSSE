from django.conf.urls import handler404
from .forms import RemiseForm
from .models import Client, Commande, RemiseClient
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from django.shortcuts import render, get_object_or_404, redirect, reverse
from datetime import datetime, timedelta, date
from django.contrib.auth import authenticate, login, logout
from .notifications import NotificationManager
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import CustomLoginForm
from .models import Client, Paiement
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.core.cache import cache
from django.db.models import Sum
from reportlab.lib.pagesizes import A4, landscape
from collections import defaultdict
from .models import Commande, Client
from datetime import datetime, timedelta
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from decimal import Decimal, ROUND_HALF_UP
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from application.models import Commande
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from django.core.mail import EmailMessage
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from io import BytesIO
from .models import Commande
from django.utils import timezone
from .forms import CommandeForm, CommandeItemForm
from .models import Commande, CommandeItem
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .models import Produit
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
import openpyxl
from .models import Client
from .forms import ClientForm
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from .dashboard_stats import DashboardStats
import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Client, Paiement, ParametresMounia,  Produit, RemiseClient
from .forms import ClientForm, CustomUserCreationForm, ParametresForm, ProduitForm, RemiseForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# views.py - IMPORTS CORRIGÉS
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, date  # ✅ IMPORT CORRECT
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q, Sum
import logging

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer

# Models imports
from .models import Client, Commande, RemiseClient
from .forms import RemiseForm

logger = logging.getLogger(__name__)


def custom_page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


handler404 = custom_page_not_found_view


def home(request):
    """Vue principale du tableau de bord"""
    try:
        # Récupération des statistiques
        stats = DashboardStats.get_stats_globales()

        print("=== DEBUG GRAPHIQUES ===")
        print(
            f"Commandes par ville: {len(stats.get('commandes_par_ville', []))}")

        # Préparation des données pour le graphique "Commandes par Ville"
        commandes_par_ville_data = stats.get('commandes_par_ville', [])

        # Données pour le graphique circulaire des commandes par ville
        commandes_ville_chart = {
            # Limiter à 8 villes max
            'labels': [item['ville'] for item in commandes_par_ville_data[:8]],
            'data': [item['total_commandes'] for item in commandes_par_ville_data[:8]],
            'ca_data': [item['total_ca'] for item in commandes_par_ville_data[:8]]
        }

        print(
            f"📊 Données graphique commandes par ville: {commandes_ville_chart}")

        # Préparation des autres données pour les graphiques
        evolution_data = {
            'mois': [item['mois'].strftime("%b %Y") for item in stats.get('evolution_clients', [])],
            'clients': [item['total'] for item in stats.get('evolution_clients', [])],
        }

        commandes_evolution = {
            'semaines': [item['semaine'].strftime("%d/%m") for item in stats.get('evolution_commandes', [])],
            'commandes': [item['total_commandes'] for item in stats.get('evolution_commandes', [])],
            'ca': [item['total_ca'] for item in stats.get('evolution_commandes', [])],
        }

        ca_mensuel = {
            'mois': [item['mois'].strftime("%b") for item in stats.get('ca_par_mois', [])],
            'montants': [item['ca_total'] for item in stats.get('ca_par_mois', [])],
        }

        # Données pour le graphique des statuts de commandes
        commandes_stats = stats.get('commandes_par_statut', [])
        statuts_commandes = {
            'labels': [item['statut'] for item in commandes_stats],
            'data': [item['total'] for item in commandes_stats],
        }

        context = {
            'stats_rapides': stats.get('stats_rapides', {}),
            'stats_completes': stats,
            'clients_par_ville': stats.get('clients_par_ville', []),
            'evolution_clients': stats.get('evolution_clients', []),
            'evolution_data': mark_safe(json.dumps(evolution_data)),
            'commandes_evolution': mark_safe(json.dumps(commandes_evolution)),
            'ca_mensuel': mark_safe(json.dumps(ca_mensuel)),
            'statuts_commandes': mark_safe(json.dumps(statuts_commandes)),
            # NOUVEAU
            'commandes_ville_chart': mark_safe(json.dumps(commandes_ville_chart)),
            'top_clients': stats.get('top_clients', []),
            'top_produits': stats.get('top_produits', []),
            'commandes_par_ville_data': commandes_par_ville_data,  # Pour le tableau
        }

        print("✅ Tous les graphiques préparés")
        return render(request, 'index.html', context)

    except Exception as e:
        print(f"❌ ERREUR dans home: {e}")
        import traceback
        traceback.print_exc()

        # Contexte d'erreur
        return render(request, 'index.html', {
            'stats_rapides': {},
            'stats_completes': {},
            'clients_par_ville': [],
            'evolution_clients': [],
            'evolution_data': mark_safe(json.dumps({'mois': [], 'clients': []})),
            'commandes_evolution': mark_safe(json.dumps({'semaines': [], 'commandes': [], 'ca': []})),
            'ca_mensuel': mark_safe(json.dumps({'mois': [], 'montants': []})),
            'statuts_commandes': mark_safe(json.dumps({'labels': [], 'data': []})),
            'commandes_ville_chart': mark_safe(json.dumps({'labels': [], 'data': [], 'ca_data': []})),
            'top_clients': [],
            'top_produits': [],
            'commandes_par_ville_data': [],
        })

# 🔹 READ (liste des clients)


def liste_clients(request):
    clients = Client.objects.all()
    return render(request, "clients/liste_clients.html", {"clients": clients})


# 🔹 CREATE


def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            # Rediriger vers la liste des clients
            return redirect('liste_clients')
    else:
        form = ClientForm()

    return render(request, 'clients/ajouter_client.html', {'form': form})


def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('detail_client', pk=client.pk)
    else:
        form = ClientForm(instance=client)

    return render(request, 'clients/modifier_client.html', {'form': form, 'client': client})


def detail_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/detail_client.html', {
        'client': client
    })
# 🔹 DELETE


def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect("liste_clients")
    return render(request, "clients/supprimer_client.html", {"client": client})


# Liste
def produit_list(request):
    produits = Produit.objects.all()
    return render(request, "produits/produit_list.html", {"produits": produits})

# Création


def produit_create(request):
    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès ✅")
            return redirect("liste_produits")
    else:
        form = ProduitForm()
    return render(request, "produits/ajouter_produit.html", {"form": form})

# Modification


def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès ✅")
            return redirect("liste_produits")
    else:
        form = ProduitForm(instance=produit)
    return render(request, "produits/modifier_produit.html", {"form": form})

# Suppression


def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == "POST":
        produit.delete()
        messages.success(request, "Produit supprimé avec succès ❌")
        return redirect("liste_produits")
    return render(request, "produits/produit_confirm_delete.html", {"produit": produit})


# Export Excel

def exporter_produits_excel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Produits"

    # En-têtes
    sheet.append(["Nom", "Description", "Prix", "Date d'ajout"])

    # Données
    for produit in Produit.objects.all():
        sheet.append([produit.nom, produit.description, str(
            produit.prix), produit.date_ajout.strftime("%d/%m/%Y")])

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="produits.xlsx"'
    workbook.save(response)
    return response

# Export PDF


def exporter_produits_pdf(request):
    # Préparer la réponse HTTP
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="produits.pdf"'

    # Création du document avec marges
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    elements = []
    styles = getSampleStyleSheet()

    # =====================
    # 1. En-tête (Logo à gauche + Infos à droite)
    # =====================
    logo_path = "static/assets/img/MOUNIA_LOGO.png"
    try:
        logo = Image(logo_path, width=1.8*inch, height=1.8*inch)
    except:
        logo = Paragraph("<b>[Logo non trouvé]</b>", styles["Normal"])

    infos_entreprise = Paragraph(
        """<b>MOUNIA</b><br/>
        Activité : Micropousse<br/>
        Adresse : Douar Laarich, 44000 Essaouira<br/>
        Téléphone : +212 620-270-420<br/>
        Email : mounia.mand97@gmail.com""",
        styles["Normal"]
    )

    # Table sur 2 colonnes équilibrées
    header_table = Table([[logo, infos_entreprise]], colWidths=[380, 200])

    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),   # logo bien à gauche
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),  # infos bien à droite
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # =====================
    # 2. Titre
    # =====================
    titre = Paragraph(
        "<b><font size=18>Liste des Produits</font></b>", styles["Title"])
    elements.append(titre)
    elements.append(Spacer(1, 20))

    # =====================
    # 3. Tableau Produits
    # =====================
    data = [["Nom", "Prix (MAD)", "Date d'ajout"]]

    for produit in Produit.objects.all():
        data.append([
            produit.nom,
            f"{produit.prix:.2f}",
            produit.date_ajout.strftime("%d/%m/%Y"),
        ])

    table = Table(data, colWidths=[80, 220])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7b837d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)

    # Générer le PDF
    doc.build(elements)
    return response


# views.py


def liste_commandes(request):
    # Récupérer le filtre de date s'il existe
    date_filtre = request.GET.get('date')

    if date_filtre:
        try:
            # Convertir la date du format YYYY-MM-DD en objet date
            date_obj = datetime.strptime(date_filtre, '%Y-%m-%d').date()
            commandes = Commande.objects.filter(date_commande__date=date_obj)
        except ValueError:
            commandes = Commande.objects.all()
    else:
        commandes = Commande.objects.all()

    # Calculer le total général
    total_general = Decimal('0.00')
    for commande in commandes:
        try:
            total_general += Decimal(str(commande.total))
        except:
            continue

    context = {
        'commandes': commandes,
        'total_general': total_general,
    }

    return render(request, "commandes/liste_commandes.html", context)


def detail_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    # Calculer la quantité totale
    quantite_totale = sum(item.quantite for item in commande.items.all())

    # Calculer les totaux avec remise
    context = {
        "commande": commande,
        "montant_remise": commande.montant_remise,
        "total_avec_remise": commande.total_avec_remise,
        "remise_appliquee": commande.remise_appliquee,
        "quantite_totale": quantite_totale,  # Ajout de la quantité totale
    }

    return render(request, "commandes/detail_commande.html", context)


# 📌 Créer une commande


def creer_commande(request):
    clients = Client.objects.all()
    produits = Produit.objects.all()

    if request.method == "POST":
        client_id = request.POST.get("client")
        date_commande_str = request.POST.get("date_commande")

        if not client_id:
            messages.error(request, "Veuillez sélectionner un client.")
            return redirect("creer_commande")

        if not date_commande_str:
            messages.error(
                request, "Veuillez sélectionner une date de commande.")
            return redirect("creer_commande")

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            messages.error(request, "Client introuvable.")
            return redirect("creer_commande")

        # Convertir la date du formulaire
        try:
            date_commande = datetime.strptime(
                date_commande_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, "Format de date invalide.")
            return redirect("creer_commande")

        # Créer la commande avec la date spécifiée
        commande = Commande.objects.create(
            client=client,
            date_commande=date_commande
        )

        # Récupérer les produits et quantités
        produits_ids = request.POST.getlist("produit[]")
        quantites = request.POST.getlist("quantite[]")

        if not produits_ids:
            messages.error(
                request, "Veuillez sélectionner au moins un produit.")
            commande.delete()  # Supprimer la commande vide
            return redirect("creer_commande")

        for i in range(len(produits_ids)):
            produit = get_object_or_404(Produit, id=produits_ids[i])
            quantite = int(quantites[i]) if quantites[i].isdigit() else 0

            if quantite <= 0:
                messages.warning(
                    request, f"Quantité invalide pour le produit {produit.nom}.")
                continue

            CommandeItem.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite
            )

        messages.success(
            request, f"Commande #{commande.id} créée avec succès !")
        return redirect("liste_commandes")

    # Normalisation des tags error → danger pour Bootstrap
    for message in messages.get_messages(request):
        if message.tags == "error":
            message.tags = "danger"

    # Passer la date actuelle au template
    now = timezone.now()

    return render(request, "commandes/ajouter_commandes.html", {
        "clients": clients,
        "produits": produits,
        "title": "Nouvelle commande",
        "now": now
    })

# 📌 Modifier une commande (et ses items)


def modifier_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    clients = Client.objects.all()
    produits = Produit.objects.all()

    if request.method == "POST":
        client_id = request.POST.get("client")
        date_commande_str = request.POST.get("date_commande")
        statut = request.POST.get("statut")

        if not client_id:
            messages.error(request, "Veuillez sélectionner un client.")
            return redirect("modifier_commande", commande_id=commande_id)

        if not date_commande_str:
            messages.error(
                request, "Veuillez sélectionner une date de commande.")
            return redirect("modifier_commande", commande_id=commande_id)

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            messages.error(request, "Client introuvable.")
            return redirect("modifier_commande", commande_id=commande_id)

        # Convertir la date du formulaire
        try:
            date_commande = datetime.strptime(
                date_commande_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, "Format de date invalide.")
            return redirect("modifier_commande", commande_id=commande_id)

        # Mettre à jour la commande
        commande.client = client
        commande.date_commande = date_commande
        commande.statut = statut
        commande.save()

        # Supprimer les anciens items
        commande.items.all().delete()

        # Récupérer les nouveaux produits et quantités
        produits_ids = request.POST.getlist("produit[]")
        quantites = request.POST.getlist("quantite[]")

        if not produits_ids:
            messages.error(
                request, "Veuillez sélectionner au moins un produit.")
            return redirect("modifier_commande", commande_id=commande_id)

        # Créer les nouveaux items
        for i in range(len(produits_ids)):
            produit = get_object_or_404(Produit, id=produits_ids[i])
            quantite = int(quantites[i]) if quantites[i].isdigit() else 0

            if quantite <= 0:
                messages.warning(
                    request, f"Quantité invalide pour le produit {produit.nom}.")
                continue

            CommandeItem.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite
            )

        messages.success(
            request, f"Commande #{commande.id} mise à jour avec succès !")
        return redirect("liste_commandes")

    # Normalisation des tags error → danger pour Bootstrap
    for message in messages.get_messages(request):
        if message.tags == "error":
            message.tags = "danger"

    return render(request, "commandes/modifier_commande.html", {
        "commande": commande,
        "clients": clients,
        "produits": produits,
        "title": f"Modifier la commande #{commande.id}"
    })
# 📌 Supprimer une commande


def supprimer_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == "POST":
        commande.delete()
        return redirect("liste_commandes")
    return render(request, "commandes/commande_confirm_delete.html", {"commande": commande})


# views.py


# views.py


@require_http_methods(["POST"])
def appliquer_remise_commande(request, pk):
    """
    Applique une remise à une commande spécifique via AJAX
    """
    try:
        commande = get_object_or_404(Commande, pk=pk)

        # Charger les données JSON
        data = json.loads(request.body.decode('utf-8'))
        type_remise = data.get('type_remise')
        valeur_remise_str = data.get('valeur_remise')

        # Validation des données
        if not type_remise or not valeur_remise_str:
            return JsonResponse({
                'success': False,
                'message': 'Type de remise et valeur sont requis.'
            })

        try:
            valeur_remise = float(valeur_remise_str)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'La valeur de la remise doit être un nombre valide.'
            })

        if valeur_remise <= 0:
            return JsonResponse({
                'success': False,
                'message': 'La valeur de la remise doit être positive.'
            })

        if type_remise == 'pourcentage' and valeur_remise > 100:
            return JsonResponse({
                'success': False,
                'message': 'Le pourcentage de remise ne peut pas dépasser 100%.'
            })

        # Appliquer la remise pour le mois de la commande
        mois_commande = commande.date_commande.strftime('%Y-%m')

        remise, created = RemiseClient.objects.update_or_create(
            client=commande.client,
            mois_application=mois_commande,
            defaults={
                'type_remise': type_remise,
                'valeur_remise': valeur_remise
            }
        )

        # Recharger la commande pour avoir les nouvelles valeurs calculées
        commande = Commande.objects.get(pk=pk)

        return JsonResponse({
            'success': True,
            'message': 'Remise appliquée avec succès!',
            'total_avec_remise': f'{commande.total_avec_remise:.2f}',
            'montant_remise': f'{commande.montant_remise:.2f}',
            'total_original': f'{float(commande.total):.2f}',
            'total_produits': f'{float(commande.total_sans_livraison):.2f}',
            'frais_livraison': f'{float(commande.frais_livraison):.2f}',
            'pourcentage_remise': commande.pourcentage_remise
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def supprimer_remise_commande(request, pk):
    """
    Supprime la remise d'une commande via AJAX
    """
    try:
        commande = get_object_or_404(Commande, pk=pk)

        # Trouver et supprimer la remise pour le mois de la commande
        mois_commande = commande.date_commande.strftime('%Y-%m')

        try:
            remise = RemiseClient.objects.get(
                client=commande.client,
                mois_application=mois_commande
            )
            remise.delete()

            return JsonResponse({
                'success': True,
                'message': 'Remise supprimée avec succès!',
                'total_sans_remise': f'{commande.total:.2f}'
            })

        except RemiseClient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Aucune remise trouvée pour ce mois.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


def dupliquer_commande(request, pk):
    commande_originale = get_object_or_404(Commande, pk=pk)

    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            client_id = request.POST.get('client')
            date_commande_str = request.POST.get('date_commande')

            # Validation
            if not client_id:
                messages.error(request, "Veuillez sélectionner un client")
                return redirect('dupliquer_commande', pk=pk)

            if not date_commande_str:
                messages.error(request, "Veuillez sélectionner une date")
                return redirect('dupliquer_commande', pk=pk)

            # Convertir la date (autoriser les dates futures)
            from datetime import datetime
            try:
                date_commande = datetime.strptime(
                    date_commande_str, '%Y-%m-%d')
                # SUPPRIMER la validation qui empêche les dates futures
                # if date_commande.date() > timezone.now().date():
                #     messages.warning(request, "La date ne peut pas être dans le futur")
                #     return redirect('dupliquer_commande', pk=pk)
            except ValueError:
                messages.error(request, "Format de date invalide")
                return redirect('dupliquer_commande', pk=pk)

            # Récupérer le client sélectionné
            try:
                client = Client.objects.get(id=client_id)
            except Client.DoesNotExist:
                messages.error(request, "Client sélectionné introuvable")
                return redirect('dupliquer_commande', pk=pk)

            # Créer une nouvelle commande avec les nouvelles données
            nouvelle_commande = Commande.objects.create(
                client=client,
                date_commande=date_commande,
                statut="En cours",
                notes=f"Dupliquée de la commande #{commande_originale.id} du {commande_originale.date_commande.strftime('%d/%m/%Y')}"
            )

            # Dupliquer les items
            items_dupliques = []
            for item in commande_originale.items.all():
                nouvel_item = CommandeItem.objects.create(
                    commande=nouvelle_commande,
                    produit=item.produit,
                    quantite=item.quantite,
                    prix_unitaire=item.prix_unitaire
                )
                items_dupliques.append(nouvel_item)

            messages.success(
                request,
                f'Commande #{commande_originale.id} dupliquée avec succès! '
                f'Nouvelle commande #{nouvelle_commande.id} créée pour {client.nom}'
            )
            return redirect('detail_commande', pk=nouvelle_commande.id)

        except Exception as e:
            messages.error(request, f'Erreur lors de la duplication: {str(e)}')
            return redirect('detail_commande', pk=pk)

    # Afficher le formulaire de duplication
    clients = Client.objects.all()
    now = timezone.now().date()

    return render(request, 'commandes/dupliquer_commande.html', {
        'commande': commande_originale,
        'clients': clients,
        'now': now
    })


def export_commande_bon_pdf(request, pk):
    try:
        commande = get_object_or_404(Commande, pk=pk)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        elements = []

        styles = getSampleStyleSheet()
        styleN = styles["Normal"]
        styleH = styles["Heading1"]

        # === Style personnalisé pour le nom du client ===
        styleClientNom = ParagraphStyle(
            "ClientNom",
            parent=styleN,
            fontSize=14,        # Taille plus grande
            leading=16,         # Espacement vertical
            spaceAfter=6,
            textColor=colors.HexColor("#000000"),
            fontName="Helvetica-Bold"  # En gras
        )

        # === EN-TÊTE (Logo - Titre - Infos Entreprise) ===
        logo_path = "static/assets/img/MOUNIA_LOGO.png"
        try:
            logo = Image(logo_path, width=1.8*inch, height=1.8*inch)
        except:
            logo = Paragraph("<b>[Logo non trouvé]</b>", styleN)

        titre = Paragraph("<b>BON DE LIVRAISON</b>", styleH)

        infos_entreprise = Paragraph(
            """<b>MOUNIA MAJID</b><br/>
            Activité : Micropousse<br/>
            Adresse : Douar Laarich, 44000 Essaouira<br/>
            Téléphone : +212 702-704-420<br/>
            Email : mounia.majid97@gmail.com""",
            styleN
        )

        header_table = Table([[logo, titre, infos_entreprise]],
                             colWidths=[120, 250, 150])
        header_table.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # === INFOS COMMANDE ===
        elements.append(Paragraph(f"<b>Numéro :</b> {commande.id}", styleN))
        elements.append(Paragraph(
            f"<b>Date :</b> {commande.date_commande.strftime('%d/%m/%Y')}", styleN))
        elements.append(Spacer(1, 12))

        # === INFOS CLIENT ===
        elements.append(
            Paragraph("<b>Informations du client</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"Nom : {commande.client.nom}", styleClientNom))
        if commande.client.ice:
            elements.append(Paragraph(f"ICE : {commande.client.ice}", styleN))
        elements.append(Paragraph(f"Ville : {commande.client.ville}", styleN))
        elements.append(
            Paragraph(f"Adresse : {commande.client.adresse}", styleN))
        elements.append(
            Paragraph(f"Téléphone : {commande.client.telephone}", styleN))
        elements.append(
            Paragraph(f"Email : {commande.client.email or 'Non renseigné'}", styleN))
        elements.append(Spacer(1, 15))

        # === TABLEAU PRODUITS ===
        data = [["Produit", "Quantité", "Prix unitaire", "Sous-total"]]

        quantite_totale = 0
        for item in commande.items.all():
            data.append([
                item.produit.nom,
                str(item.quantite),
                f"{float(item.prix_unitaire):.2f} MAD",
                f"{float(item.sous_total):.2f} MAD"
            ])
            quantite_totale += item.quantite

        # Ligne de total quantité
        data.append([
            "TOTAL",
            str(quantite_totale),
            "",
            f"{float(commande.total_sans_livraison):.2f} MAD"
        ])

        table = Table(data, colWidths=[220, 80, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#838586")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0f0f0")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # === TOTAUX AVEC REMISE ===
        data_totaux = [
            ["", "", "Sous-total produits:",
                f"{float(commande.total_sans_livraison):.2f} MAD"],
        ]

        if commande.remise_appliquee:
            remise_type = "Remise"
            if commande.remise_appliquee.type_remise == 'pourcentage':
                remise_type += f" ({commande.remise_appliquee.valeur_remise}%)"
            else:
                remise_type += f" ({commande.remise_appliquee.valeur_remise} MAD)"

            data_totaux.append(
                ["", "", remise_type + ":", f"-{float(commande.montant_remise):.2f} MAD"])
            total_produits_apres_remise = commande.total_sans_livraison - commande.montant_remise
            data_totaux.append(["", "", "Sous-total après remise:",
                               f"{float(total_produits_apres_remise):.2f} MAD"])

        data_totaux.append(["", "", "Frais de livraison:",
                           f"{float(commande.frais_livraison):.2f} MAD"])
        data_totaux.append(
            ["", "", "Total:", f"{float(commande.total_avec_remise):.2f} TTC"])

        total_table = Table(data_totaux, colWidths=[220, 80, 100, 100])
        total_table.setStyle(TableStyle([
            ("FONTNAME", (2, 0), (3, -1), "Helvetica-Bold"),
            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
            ("FONTSIZE", (2, 0), (3, -1), 11),
            ("LINEABOVE", (2, -1), (3, -1), 1, colors.black),
            ("LINEBELOW", (2, -1), (3, -1), 1, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(total_table)

        # === SIGNATURES ===
        elements.append(Spacer(1, 60))
        signatures_table = Table([
            ["Signature Client", "Cachet & Signature Entreprise"]
        ], colWidths=[250, 250])
        signatures_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 40),
        ]))
        elements.append(signatures_table)

        # === GÉNÉRATION PDF ===
        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type="application/pdf")

        # === Nom du fichier : client + date ===
        nom_client = commande.client.nom.replace(" ", "_").replace("/", "_")
        date_str = commande.date_commande.strftime("%d-%m-%Y")
        response['Content-Disposition'] = f'attachment; filename="BL_{nom_client}_{date_str}.pdf"'

        return response

    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF: {str(e)}", status=500)


def envoyer_bon_livraison(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    # Génération du PDF en mémoire
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Bon de livraison pour commande #{commande.id}")
    p.drawString(100, 780, f"Client : {commande.client.nom}")
    p.drawString(
        100, 760, f"Date : {commande.date_commande.strftime('%d/%m/%Y %H:%M')}")
    p.showPage()
    p.save()
    buffer.seek(0)

    # Email
    email = EmailMessage(
        subject=f"Bon de livraison - Commande #{commande.id}",
        body="Veuillez trouver ci-joint le bon de livraison.",
        from_email="tonemail@exemple.com",
        to=[commande.client.email],  # Assure-toi que Client a un champ `email`
    )
    email.attach(f"bon_livraison_{commande.id}.pdf",
                 buffer.getvalue(), "application/pdf")
    email.send()

    return HttpResponse("Bon de livraison envoyé avec succès !")


# 📌 Ajouter un produit dans une commande
def ajouter_item(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)
    if request.method == "POST":
        form = CommandeItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.commande = commande
            item.save()
            return redirect("modifier_commande", pk=commande.pk)
    else:
        form = CommandeItemForm()
    return render(request, "commandes/item_form.html", {"form": form, "commande": commande})


# views.py


def commandes_du_jour(request):
    today = timezone.now().date()
    commandes = Commande.objects.filter(date_commande__date=today)

    context = {
        "commandes": commandes,
        "today": today,
    }
    return render(request, "commandes/commandes_du_jour.html", context)

# views.py


def _format_money(value: Decimal) -> str:
    """Format Decimal to string with 2 decimals (safe)."""
    if value is None:
        value = Decimal("0.00")
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except:
            value = Decimal("0.00")
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _format_decimal(value):
    """Format Decimal to string with 2 decimals."""
    if value is None:
        return "0.00"
    try:
        return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except Exception:
        return "0.00"


def export_commandes_pdf(request):
    from .models import Commande, Produit, Client  # ✅ import interne

    # --- 🔹 Filtrage optionnel par date ---
    date_filtre = request.GET.get("date")
    commandes = Commande.objects.prefetch_related(
        "items__produit", "client").all()

    date_obj = None
    if date_filtre:
        try:
            date_obj = datetime.strptime(date_filtre, "%Y-%m-%d").date()
            commandes = commandes.filter(date_commande__date=date_obj)
        except ValueError:
            pass

    # --- 🔹 Préparation du buffer PDF ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30,
    )

    elements = []
    styles = getSampleStyleSheet()

    # === 🔹 En-tête avec logo et infos entreprise ===
    try:
        logo_path = "static/assets/img/MOUNIA_LOGO.png"
        logo = Image(logo_path, width=1.4 * inch, height=1.4 * inch)
    except Exception:
        logo = Paragraph("<b>[Logo non trouvé]</b>", styles["Normal"])

    infos_entreprise = Paragraph(
        """<b>MOUNIA MICROPOUSSE</b><br/>
        Activité : Micropousse<br/>
        Adresse : Douar Laarich, Essaouira<br/>
        Téléphone : +212 620-270-420<br/>
        Email : mounia.mand97@gmail.com""",
        styles["Normal"]
    )

    header_table = Table([[logo, infos_entreprise]],
                         colWidths=[3 * inch, 6 * inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # === 🔹 Titre principal ===
    titre = (
        f"TABLEAU CROISÉ CLIENTS / PRODUITS - {date_obj.strftime('%d/%m/%Y')}"
        if date_obj else "TABLEAU CROISÉ CLIENTS / PRODUITS (Toutes commandes)"
    )
    elements.append(Paragraph(titre, styles["Title"]))
    elements.append(Spacer(1, 10))

    # === 🔹 Construction du tableau croisé ===
    if not commandes.exists():
        elements.append(
            Paragraph("Aucune commande trouvée.", styles["Normal"]))
    else:
        produits = list(Produit.objects.all().order_by("nom"))

        # Récupérer uniquement les clients ayant au moins une commande
        clients = (
            Client.objects.filter(commandes__isnull=False)
            .distinct()
            .order_by("nom")
        )

        # Dictionnaire: client -> produit -> quantité
        quantites = defaultdict(lambda: defaultdict(Decimal))

        for commande in commandes:
            for item in commande.items.all():
                client_nom = commande.client.nom
                produit_nom = item.produit.nom
                quantites[client_nom][produit_nom] += Decimal(
                    item.quantite or 0)

        # === En-tête : Produits + Total client ===
        data = [["Client"] + [p.nom for p in produits] + ["Total Client"]]

        total_general = Decimal("0.00")
        totaux_produits = defaultdict(Decimal)

        # === Lignes clients (uniquement ceux ayant commandé) ===
        for client in clients:
            total_client = sum(quantites[client.nom].values())
            if total_client == 0:
                continue  # ✅ Ignorer le client sans commandes réelles

            ligne = [client.nom]
            for produit in produits:
                qte = quantites[client.nom][produit.nom]
                ligne.append(str(qte) if qte > 0 else "")
                totaux_produits[produit.nom] += qte
            ligne.append(str(total_client))
            total_general += total_client
            data.append(ligne)

        # === Ligne des totaux produits ===
        ligne_total = ["TOTAL PRODUITS"]
        for produit in produits:
            ligne_total.append(str(totaux_produits[produit.nom]))
        ligne_total.append(str(total_general))
        data.append(ligne_total)

        # === 🔹 Calcul dynamique des largeurs ===
        base_width = 9.5 * inch
        nb_produits = len(produits)
        col_produit_width = max(0.5 * inch, base_width / (nb_produits + 2))
        col_widths = [1.6 * inch] + [col_produit_width] * \
            nb_produits + [1.0 * inch]

        # === 🔹 Création du tableau ===
        table = Table(data, repeatRows=1, colWidths=col_widths)

        # === 🔹 Style du tableau ===
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, 0), 7),

            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 1), (-1, -1), 6),

            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d4edda")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, -1), (-1, -1), "CENTER"),
        ]

        # === Alternance de couleurs pour lisibilité ===
        for i in range(1, len(data) - 1):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i),
                             colors.HexColor("#f8f9fa")))

        table.setStyle(TableStyle(style))
        elements.append(table)

    # === 🔹 Pied de page ===
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "<i>Document généré automatiquement - MOUNIA MICROPOUSSE</i>", styles["Normal"]))
    elements.append(Paragraph(
        f"<i>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>", styles["Normal"]))

    # === 🔹 Génération finale ===
    doc.build(elements)
    buffer.seek(0)

    filename = f"tableau_croise_commandes_{date_filtre if date_filtre else 'complet'}.pdf"
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'
    return response


# views.py


def _format_money(value):
    """Format Decimal to string with 2 decimals (safe)."""
    if value is None:
        value = Decimal("0.00")
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except (TypeError, ValueError):
            value = Decimal("0.00")
    return f"{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"


def liste_factures(request):
    # Récupérer les paramètres de filtrage
    client_id = request.GET.get('client')
    mois_filtre = request.GET.get('mois')  # Format: YYYY-MM

    commandes = Commande.objects.all().order_by('-date_commande')
    clients = Client.objects.all().order_by('nom')

    # Variables pour suivre les filtres appliqués
    client_selected = None
    mois_selected = None
    total_mois = Decimal('0.00')
    remise_appliquee = Decimal('0.00')
    total_apres_remise = Decimal('0.00')
    mois_obj = None  # ✅ Initialiser à None pour éviter l'erreur

    # Filtre par client
    if client_id:
        try:
            client_selected = Client.objects.get(id=client_id)
            commandes = commandes.filter(client=client_selected)
        except Client.DoesNotExist:
            pass

    # Filtre par mois
    if mois_filtre:
        try:
            # Convertir YYYY-MM en année et mois
            annee, mois = map(int, mois_filtre.split('-'))
            commandes = commandes.filter(
                date_commande__year=annee,
                date_commande__month=mois
            )
            mois_selected = mois_filtre
            # ✅ CORRECTION : Utiliser datetime.datetime pour créer l'objet
            mois_obj = datetime(annee, mois, 1)
        except (ValueError, TypeError):
            pass

    # Calculer le total du mois pour les commandes filtrées
    if client_selected and mois_selected:
        total_mois = sum(commande.total for commande in commandes)

        # Récupérer la remise applicable pour ce client ce mois-ci
        try:
            remise = RemiseClient.objects.get(
                client=client_selected,
                mois_application=mois_filtre
            )
            if remise.type_remise == 'pourcentage':
                remise_appliquee = total_mois * \
                    (remise.valeur_remise / Decimal('100'))
            else:
                remise_appliquee = remise.valeur_remise

            # La remise ne peut pas dépasser le total
            remise_appliquee = min(remise_appliquee, total_mois)
            total_apres_remise = total_mois - remise_appliquee

        except RemiseClient.DoesNotExist:
            # Aucune remise trouvée, les totaux restent identiques
            total_apres_remise = total_mois
            remise_appliquee = Decimal('0.00')

    # Préparer les mois disponibles pour le filtre (12 derniers mois)
    aujourd_hui = timezone.now()
    mois_disponibles = []
    for i in range(12):
        # ✅ CORRECTION : Utiliser timedelta correctement
        date_mois = aujourd_hui - timedelta(days=30*i)
        mois_disponibles.append({
            'value': date_mois.strftime('%Y-%m'),
            'label': date_mois.strftime('%B %Y').capitalize()
        })

    # Inverser l'ordre pour avoir les mois les plus récents en premier
    mois_disponibles.reverse()

    context = {
        'commandes': commandes,
        'clients': clients,
        'mois_disponibles': mois_disponibles,
        'client_selected': client_selected,
        'mois_selected': mois_selected,
        'mois_obj': mois_obj,  # ✅ Peut être None mais c'est OK
        'total_mois': total_mois,
        'remise_appliquee': remise_appliquee,
        'total_apres_remise': total_apres_remise,
    }
    return render(request, 'factures/liste_factures.html', context)


def appliquer_remise(request, client_id, mois_filtre):
    client = get_object_or_404(Client, id=client_id)

    # Calculer le total des produits pour information
    annee, mois = map(int, mois_filtre.split('-'))
    commandes = Commande.objects.filter(
        client=client,
        date_commande__year=annee,
        date_commande__month=mois
    )
    total_produits = sum(
        commande.total_sans_livraison for commande in commandes)

    # Récupérer la remise existante ou initialiser une nouvelle
    try:
        remise = RemiseClient.objects.get(
            client=client,
            mois_application=mois_filtre
        )
    except RemiseClient.DoesNotExist:
        remise = None

    if request.method == 'POST':
        form = RemiseForm(request.POST, instance=remise)
        if form.is_valid():
            nouvelle_remise = form.save(commit=False)
            nouvelle_remise.client = client
            nouvelle_remise.mois_application = mois_filtre

            # Validation : la remise fixe ne peut pas dépasser le total des produits
            if (nouvelle_remise.type_remise == 'fixe' and
                    nouvelle_remise.valeur_remise > total_produits):
                messages.error(
                    request,
                    f"La remise fixe ne peut pas dépasser le total des produits ({total_produits:.2f} MAD)"
                )
                return render(request, 'factures/appliquer_remise.html', {
                    'form': form,
                    'client': client,
                    'mois_filtre': mois_filtre,
                    # ✅ CORRECTION : Utiliser datetime.datetime.strptime
                    'mois_nom': datetime.strptime(mois_filtre, "%Y-%m").strftime("%B %Y"),
                    'total_produits': total_produits
                })

            nouvelle_remise.save()

            messages.success(request, "Remise appliquée avec succès!")
            return redirect(f"{reverse('liste_factures')}?client={client_id}&mois={mois_filtre}")
    else:
        form = RemiseForm(instance=remise)

    return render(request, 'factures/appliquer_remise.html', {
        'form': form,
        'client': client,
        'mois_filtre': mois_filtre,
        # ✅ CORRECTION : Utiliser datetime.datetime.strptime
        'mois_nom': datetime.strptime(mois_filtre, "%Y-%m").strftime("%B %Y"),
        'total_produits': total_produits
    })


def facture_client_mois_pdf(request):
    """Génère une facture mensuelle pour un client spécifique"""

    client_id = request.GET.get("client")
    mois_filtre = request.GET.get("mois")

    if not client_id or not mois_filtre:
        return HttpResponse("Paramètres manquants: client et mois requis")

    try:
        client = Client.objects.get(id=client_id)
        annee, mois = map(int, mois_filtre.split('-'))

        commandes = Commande.objects.filter(
            client=client,
            date_commande__year=annee,
            date_commande__month=mois
        ).order_by('date_commande')

        # Calcul des totaux avec gestion des valeurs None
        total_produits_sans_remise = sum(
            commande.total_sans_livraison or Decimal('0.00')
            for commande in commandes
        )
        nombre_livraisons = commandes.count()
        frais_livraison_total = sum(
            commande.frais_livraison or Decimal('0.00')
            for commande in commandes
        )
        total_sans_remise = total_produits_sans_remise + frais_livraison_total

        remise_appliquee = Decimal('0.00')
        total_produits_apres_remise = total_produits_sans_remise
        total_apres_remise = total_sans_remise

        try:
            remise = RemiseClient.objects.get(
                client=client, mois_application=mois_filtre)
            if remise.type_remise == 'pourcentage':
                remise_appliquee = total_produits_sans_remise * \
                    (remise.valeur_remise / Decimal('100'))
            else:
                remise_appliquee = min(
                    remise.valeur_remise, total_produits_sans_remise)

            total_produits_apres_remise = total_produits_sans_remise - remise_appliquee
            total_apres_remise = total_produits_apres_remise + frais_livraison_total

        except RemiseClient.DoesNotExist:
            pass

    except (Client.DoesNotExist, ValueError):
        return HttpResponse("Client ou mois invalide")

    # Création du PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()

    # Styles personnalisés
    styles.add(ParagraphStyle(name='RightAlign',
               parent=styles['Normal'], alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Center',
               parent=styles['Normal'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(
        name='Small', parent=styles['Normal'], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name='SmallBold',
               parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold'))

    # ✅ Style Total réduit
    styles.add(ParagraphStyle(name='TotalStyle',
               parent=styles['Normal'], fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER))

    # Logo
    try:
        logo = Image("static/assets/img/MOUNIA_LOGO.png",
                     width=1.2*inch, height=1.2*inch)
    except:
        logo = Paragraph("<b>MOUNIA MAJID</b>", styles['Title'])

    infos_entreprise = [
        Paragraph("<b>MOUNIA MAJID</b>", styles['Heading2']),
        Paragraph("Adresse : Douar Laarich, Essaouira", styles['Small']),
        Paragraph(
            "Tél: +212 702-704-420 • Email: mounia.majid97@gmail.com", styles['Small']),
    ]

    # ✅ LIGNE CORRIGÉE : Utilisation correcte de datetime
    mois_nom = datetime(annee, mois, 1).strftime("%B %Y").capitalize()

    infos_client = [
        Paragraph("<b>INFORMATIONS CLIENT</b>", styles['SmallBold']),
        Paragraph(f"<b>Nom:</b> {client.nom}", styles['Small']),
        Paragraph(f"<b>ICE:</b> {client.ice}", styles['Small']),
        Paragraph(f"<b>Ville:</b> {client.ville}", styles['Small']),
    ]

    infos_facture = [
        Paragraph("<b>FACTURE MENSUELLE</b>", styles['Heading2']),
        Paragraph(f"<b>Période:</b> {mois_nom}", styles['Small']),
        # ✅ CORRECT : datetime.now() fonctionne maintenant
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Small']),
        Paragraph(
            f"<b>Réf:</b> {client.id}-{annee}{mois:02d}", styles['Small']),
        Paragraph(f"<b>Commandes:</b> {commandes.count()}", styles['Small']),
    ]

    # En-tête
    header_data = [[logo, infos_entreprise, infos_client, infos_facture]]
    header_table = Table(header_data, colWidths=[
                         1.5*inch, 2.5*inch, 2*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(
        f"<b>DÉTAIL DES COMMANDES - {mois_nom.upper()}</b>", styles['Heading2']))

    if not commandes.exists():
        elements.append(
            Paragraph("Aucune commande trouvée pour cette période.", styles['Normal']))
    else:
        recap_data = [["Date", "N° Commande",
                       "Produits", "Livraison", "Total (MAD)"]]

        for commande in commandes:
            recap_data.append([
                commande.date_commande.strftime("%d/%m/%Y"),
                str(commande.id),
                _format_money(commande.total_sans_livraison),
                _format_money(commande.frais_livraison),
                _format_money(commande.total)
            ])

        recap_data.append(["", "", "TOTAL PRODUITS:", "",
                          _format_money(total_produits_sans_remise)])

        if remise_appliquee > 0:
            recap_data.append(["", "", "REMISE SUR PRODUITS:",
                              "", f"-{_format_money(remise_appliquee)}"])
            recap_data.append(["", "", "TOTAL APRÈS REMISE:",
                              "", _format_money(total_produits_apres_remise)])

        recap_data.append(["", "", f"FRAIS LIVRAISON ({nombre_livraisons} livraisons):", "", _format_money(
            frais_livraison_total)])

        # ✅ LIGNE TOTAL À PAYER RÉDUITE
        recap_data.append([
            Paragraph(
                f"<b>TOTAL À PAYER : {_format_money(total_apres_remise)} MAD/TTC</b>", styles['TotalStyle']),
            "", "", "", ""
        ])

        recap_table = Table(recap_data, colWidths=[
                            1.2*inch, 1.0*inch, 2.0*inch, 1.0*inch, 1.0*inch])

        # Style du tableau avec taille réduite pour le total
        recap_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -2), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -2), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (4, -2), 'RIGHT'),

            # En-tête
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

            # Bloc des totaux
            ('FONTNAME', (2, -4), (-1, -2), 'Times-Bold'),

            # Ligne avant total final
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),

            # Fusion et centrage
            ('SPAN', (0, -1), (-1, -1)),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),

            # ✅ TAILLE RÉDUITE pour le total
            ('FONTSIZE', (0, -1), (-1, -1), 14),  # Réduit de 20 à 14
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),  # Réduit de 14 à 8
            ('TOPPADDING', (0, -1), (-1, -1), 8),   # Réduit de 14 à 8
            ('BOX', (0, -1), (-1, -1), 2, colors.black),
        ]))

        elements.append(recap_table)
        elements.append(Spacer(1, 30))

    # Pied de page
    elements.append(
        Paragraph("Merci pour votre confiance !", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "<i>Mounia Majid, ICE: 002947761000020, IF 50621840, TP 11000/2022/3069 "
        "Banque Crédit du Maroc, IBAN: MA64 021 240 0000315027053382 95</i>",
        styles['Center'])
    )

    # Génération du PDF
    doc.build(elements)
    buffer.seek(0)

    filename = f"Facture_{client.nom}_{annee}_{mois:02d}.pdf".replace(" ", "_")
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def parametres_mounia(request):
    parametres = cache.get('parametres_mouinia')
    if not parametres:
        parametres = ParametresMounia.objects.first()
        cache.set('parametres_mouinia', parametres, 3600)  # Cache 1h
    return {'parametres': parametres}


@login_required
def parametres_application(request):
    # Récupère ou crée les paramètres (une seule instance)
    parametres, created = ParametresMounia.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = ParametresForm(request.POST, request.FILES, instance=parametres)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres mis à jour avec succès!')
            return redirect('parametres_app')
    else:
        form = ParametresForm(instance=parametres)

    return render(request, 'parametre/applications.html', {
        'form': form,
        'parametres': parametres
    })


def historique_factures_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    commandes = Commande.objects.filter(client=client).select_related(
        'client').prefetch_related('paiements').order_by('date_commande')

    # Précharger les remises pour ce client pour tous les mois concernés?
    # On va plutôt laisser la propriété remise_appliquee faire son travail, mais on peut précharger toutes les remises du client et les mettre en cache dans le client?
    # Pour l'instant, on fait sans.

    groupes = {}
    for commande in commandes:
        mois = commande.date_commande.strftime('%Y-%m')
        if mois not in groupes:
            groupes[mois] = {
                'commandes': [],
                'total_mois': Decimal('0.00'),
                'total_paye_mois': Decimal('0.00'),
            }
        groupes[mois]['commandes'].append(commande)
        groupes[mois]['total_mois'] += commande.total_avec_remise
        groupes[mois]['total_paye_mois'] += commande.montant_paye

    data_mois = []
    for mois, data in groupes.items():
        total_mois = data['total_mois']
        total_paye = data['total_paye_mois']
        reste = total_mois - total_paye
        if total_paye == 0:
            statut = 'non_paye'
        elif reste > 0:
            statut = 'partiellement_paye'
        else:
            statut = 'paye'

        data_mois.append({
            'mois': mois,
            'total_mois': total_mois,
            'total_paye': total_paye,
            'reste': reste,
            'statut': statut
        })

    # Trier par mois décroissant
    data_mois.sort(key=lambda x: x['mois'], reverse=True)

    return render(request, 'historique_factures_client.html', {'client': client, 'data_mois': data_mois})


def liste_clientspai(request):
    # Récupérer tous les clients
    clients = Client.objects.all().order_by('nom')

    # Obtenir les 6 derniers mois
    mois_courant = timezone.now()
    mois_liste = []
    for i in range(6):
        mois = mois_courant - timedelta(days=30*i)
        mois_liste.append({
            'annee': mois.year,
            'mois': mois.month,
            'nom': mois.strftime('%B %Y'),
            'mois_str': mois.strftime('%Y-%m')
        })

    # FORCER la mise à jour de tous les paiements avant l'affichage
    for client in clients:
        for mois_info in mois_liste:
            # Cette appel va recalculer et mettre à jour le montant_du
            client.get_statut_paiement_mois(
                mois_info['annee'], mois_info['mois'])

    # Préparer les données pour chaque client
    clients_data = []
    for client in clients:
        client_info = {
            'id': client.id,
            'nom': client.nom,
            'ville': client.ville,
            'telephone': client.telephone,
            'responsable': client.responsable,
            'email': client.email,
            'paiements_mois': []
        }

        # Ajouter les statuts de paiement pour chaque mois
        for mois_info in mois_liste:
            paiement = client.get_statut_paiement_mois(
                mois_info['annee'], mois_info['mois'])
            client_info['paiements_mois'].append({
                'mois': mois_info['mois_str'],
                'nom_mois': mois_info['nom'],
                'paiement': paiement
            })

        clients_data.append(client_info)

    return render(request, 'factures/liste_clients.html', {
        'clients': clients_data,
        'mois_liste': mois_liste,
        'title': 'Liste des Clients',
        'now': timezone.now()
    })


def detail_clientpai(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    # Obtenir les 12 derniers mois
    mois_courant = timezone.now()
    historique = []

    for i in range(12):
        mois_date = mois_courant - timedelta(days=30*i)
        annee = mois_date.year
        mois = mois_date.month
        mois_str = f"{annee}-{str(mois).zfill(2)}"

        # Commandes du mois
        commandes = client.get_commandes_par_mois(annee, mois)
        total_mois = client.get_total_mois(annee, mois)
        paiement = client.get_statut_paiement_mois(annee, mois)

        historique.append({
            'mois': mois_str,
            'nom_mois': mois_date.strftime('%B %Y'),
            'commandes': commandes,
            'total_mois': total_mois,
            'paiement': paiement,
            'nombre_commandes': commandes.count()
        })

    return render(request, 'factures/detail_client.html', {
        'client': client,
        'historique': historique,
        'title': f'Historique - {client.nom}'
    })


def maj_paiement(request, client_id, mois):
    client = get_object_or_404(Client, id=client_id)
    paiement = get_object_or_404(Paiement, client=client, mois=mois)

    if request.method == 'POST':
        montant_paye = Decimal(request.POST.get('montant_paye', 0))
        paiement.montant_paye = montant_paye
        paiement.save()

        # Rediriger vers la page détail du client
        return redirect('detail_clientpai', client_id=client_id)

    return render(request, 'factures/maj_paiement.html', {
        'client': client,
        'paiement': paiement,
        'title': f'Mise à jour paiement - {mois}'
    })


def mettre_a_jour_paiement(request, client_id, mois):
    """Vue pour mettre à jour le statut de paiement"""
    client = get_object_or_404(Client, id=client_id)
    paiement = get_object_or_404(Paiement, client=client, mois=mois)

    if request.method == 'POST':
        montant_paye = Decimal(request.POST.get('montant_paye', 0))
        paiement.montant_paye = montant_paye
        paiement.save()

        # Rediriger vers la page détail du client
        return redirect('detail_client', pk=client_id)

    return render(request, 'factres/maj_paiement.html', {
        'client': client,
        'paiement': paiement
    })


def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès !')
            # Redirigez vers une page de connexion ou autre
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'utilisateurs/ajouter_utilisateur.html', {'form': form})


def login_utilisateur(request):
    form = CustomLoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Connexion réussie.')
                return redirect('home')  # Redirige après connexion
            else:
                messages.error(
                    request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(
                request, 'Veuillez corriger les erreurs ci-dessous.')

    return render(request, 'utilisateurs/login.html', {'form': form})


def logout_utilisateur(request):

    logout(request)  # Déconnexion de l'utilisateur
    messages.success(request, 'Déconnexion réussie.')
    return redirect('login')


def notifications_ajax(request):
    """Endpoint AJAX pour récupérer les notifications"""
    notifications_non_lues = NotificationManager.get_notifications_non_lues()
    statistiques = NotificationManager.get_statistiques_jour()

    data = {
        'notifications': [
            {
                'id': notif.id,
                'titre': notif.titre,
                'message': notif.message,
                'type': notif.type_notification,
                'date_creation': notif.date_creation.strftime('%H:%M'),
                'lue': notif.lue
            }
            for notif in notifications_non_lues
        ],
        'statistiques': statistiques,
        'total_non_lues': notifications_non_lues.count()
    }

    return JsonResponse(data)


@require_POST
@csrf_exempt
def marquer_notification_lue(request):
    """Marque une notification comme lue"""
    data = json.loads(request.body)
    notification_id = data.get('notification_id')

    if notification_id:
        success = NotificationManager.marquer_comme_lue(notification_id)
        return JsonResponse({'success': success})

    return JsonResponse({'success': False})


@require_POST
@csrf_exempt
def marquer_toutes_lues(request):
    """Marque toutes les notifications comme lues"""
    NotificationManager.marquer_toutes_comme_lues()
    return JsonResponse({'success': True})


def rafraichir_notifications_commandes(request):
    """Force la création d'une notification pour les commandes du jour"""
    NotificationManager.creer_notification_commandes_jour()
    return JsonResponse({'success': True})
