import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Client, ParametresMounia,  Produit, RemiseClient
from .forms import ClientForm, CustomUserCreationForm, ParametresForm,ProduitForm, RemiseForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from django.conf.urls import handler404
from django.shortcuts import render

def custom_page_not_found_view(request, exception):
    return render(request, "404.html", status=404)

handler404 = custom_page_not_found_view


# Create your views here.
def home(request):
    # Récupérer les 8 derniers clients
   # derniers_clients = Client.objects.all().order_by('-date_inscription')[:8]
    
    # Passer les clients au template
    return render(request, 'index.html')




# 🔹 READ (liste des clients)
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, "clients/liste_clients.html", {"clients": clients})

# 🔹 CREATE
from django.shortcuts import render, redirect
from .forms import ClientForm
from .models import Client

def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_clients')  # Rediriger vers la liste des clients
    else:
        form = ClientForm()
    
    return render(request, 'clients/ajouter_client.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Client
from .forms import ClientForm

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






import openpyxl
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Produit

# Export Excel
def exporter_produits_excel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Produits"

    # En-têtes
    sheet.append(["Nom", "Description", "Prix", "Date d'ajout"])

    # Données
    for produit in Produit.objects.all():
        sheet.append([produit.nom, produit.description, str(produit.prix), produit.date_ajout.strftime("%d/%m/%Y")])

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="produits.xlsx"'
    workbook.save(response)
    return response

# Export PDF

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Produit

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors

from reportlab.lib.units import inch

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
    titre = Paragraph("<b><font size=18>Liste des Produits</font></b>", styles["Title"])
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
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)

    # Générer le PDF
    doc.build(elements)
    return response



# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Commande, CommandeItem
from .forms import CommandeForm, CommandeItemForm


from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .models import Commande
from reportlab.pdfgen import canvas
from io import BytesIO

def liste_commandes(request):
    date_filtre = request.GET.get("date")
    if date_filtre:
        commandes = Commande.objects.filter(date_commande__date=date_filtre)
    else:
        commandes = Commande.objects.all()

    return render(request, "commandes/liste_commandes.html", {
        "commandes": commandes,
        "date_filtre": date_filtre
    })
def detail_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    return render(request, "commandes/detail_commande.html", {"commande": commande})


# 📌 Créer une commande
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime

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
            messages.error(request, "Veuillez sélectionner une date de commande.")
            return redirect("creer_commande")

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            messages.error(request, "Client introuvable.")
            return redirect("creer_commande")

        # Convertir la date du formulaire
        try:
            date_commande = datetime.strptime(date_commande_str, '%Y-%m-%dT%H:%M')
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
            messages.error(request, "Veuillez sélectionner au moins un produit.")
            commande.delete()  # Supprimer la commande vide
            return redirect("creer_commande")

        for i in range(len(produits_ids)):
            produit = get_object_or_404(Produit, id=produits_ids[i])
            quantite = int(quantites[i]) if quantites[i].isdigit() else 0

            if quantite <= 0:
                messages.warning(request, f"Quantité invalide pour le produit {produit.nom}.")
                continue

            CommandeItem.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite
            )

        messages.success(request, f"Commande #{commande.id} créée avec succès !")
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
            messages.error(request, "Veuillez sélectionner une date de commande.")
            return redirect("modifier_commande", commande_id=commande_id)

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            messages.error(request, "Client introuvable.")
            return redirect("modifier_commande", commande_id=commande_id)

        # Convertir la date du formulaire
        try:
            date_commande = datetime.strptime(date_commande_str, '%Y-%m-%dT%H:%M')
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
            messages.error(request, "Veuillez sélectionner au moins un produit.")
            return redirect("modifier_commande", commande_id=commande_id)

        # Créer les nouveaux items
        for i in range(len(produits_ids)):
            produit = get_object_or_404(Produit, id=produits_ids[i])
            quantite = int(quantites[i]) if quantites[i].isdigit() else 0

            if quantite <= 0:
                messages.warning(request, f"Quantité invalide pour le produit {produit.nom}.")
                continue

            CommandeItem.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite
            )

        messages.success(request, f"Commande #{commande.id} mise à jour avec succès !")
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
from django.http import HttpResponse
from reportlab.pdfgen import canvas



# views.py
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from .models import Commande


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from decimal import Decimal
from application.models import Commande

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def export_commande_bon_pdf(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH = styles["Heading1"]

    # === EN-TÊTE (Logo - Titre - Infos Entreprise) ===
    logo_path = "static/assets/img/MOUNIA_LOGO.png"
    try:
        logo = Image(logo_path, width=1.8*inch, height=1.8*inch)
    except:
        logo = Paragraph("<b>[Logo non trouvé]</b>", styleN)

    titre = Paragraph("<b>BON DE LIVRAISION</b>", styleH)

    infos_entreprise = Paragraph(
         """<b>MOUNIA</b><br/>
        Activité : Micropousse<br/>
        Adresse : Douar Laarich, 44000 Essaouira<br/>
        Téléphone : +212 620-270-420<br/>
        Email : mounia.mand97@gmail.com""",
        styleN
    )

    header_table = Table([[logo, titre, infos_entreprise]],
                         colWidths=[120, 250, 150])
    header_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, 0), "CENTER"),  # centrer le titre
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),   # infos entreprise à droite
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # === INFOS COMMANDE ===
    elements.append(Paragraph(f"<b>Numéro :</b> {commande.id}", styleN))
    elements.append(Paragraph(f"<b>Date :</b> {commande.date_commande.strftime('%d/%m/%Y %H:%M')}", styleN))
    elements.append(Paragraph(f"<b>Statut :</b> {commande.statut}", styleN))
    elements.append(Spacer(1, 12))

    # === INFOS CLIENT ===
    elements.append(Paragraph("<b>Informations du client</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Nom : {commande.client.nom}", styleN))
    elements.append(Paragraph(f"Adresse : {commande.client.adresse}", styleN))
    elements.append(Paragraph(f"Téléphone : {commande.client.telephone}", styleN))
    elements.append(Paragraph(f"Email : {commande.client.email or 'Non renseigné'}", styleN))
    elements.append(Spacer(1, 15))

    # === TABLEAU PRODUITS ===
    data = [["Produit", "Quantité", "Prix unitaire", "Sous-total"]]

    for item in commande.items.all():
        data.append([
            item.produit.nom,
            str(item.quantite),
            f"{item.prix_unitaire:.2f}",   # pas de MAD
            f"{item.sous_total:.2f}"       # pas de MAD
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
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # === TOTAL A PART ===
    total_table = Table([
        ["", "", "Total commande :", f"{commande.total:.2f} MAD"]
    ], colWidths=[220, 80, 100, 100])
    total_table.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (3, 0), "Helvetica-Bold"),
        ("ALIGN", (3, 0), (3, 0), "RIGHT"),
        ("FONTSIZE", (2, 0), (3, 0), 11),
        ("LINEABOVE", (2, 0), (3, 0), 1, colors.black),
        ("LINEBELOW", (2, 0), (3, 0), 1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(total_table)
        # === SIGNATURES ===
    elements.append(Spacer(1, 60))  # espace avant signatures

    signatures_table = Table([
        ["Signature Client", "Cachet & Signature Entreprise"]
    ], colWidths=[250, 250])

    signatures_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 40),   # espace vertical pour signer
    ]))

    elements.append(signatures_table)

    # === GÉNÉRATION PDF ===
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="bon_commande_{commande.id}.pdf"'
    return response


    





def envoyer_bon_livraison(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    # Génération du PDF en mémoire
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Bon de livraison pour commande #{commande.id}")
    p.drawString(100, 780, f"Client : {commande.client.nom}")
    p.drawString(100, 760, f"Date : {commande.date_commande.strftime('%d/%m/%Y %H:%M')}")
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
    email.attach(f"bon_livraison_{commande.id}.pdf", buffer.getvalue(), "application/pdf")
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
from django.shortcuts import render
from django.utils import timezone
from .models import Commande

def commandes_du_jour(request):
    today = timezone.now().date()
    commandes = Commande.objects.filter(date_commande__date=today)

    context = {
        "commandes": commandes,
        "today": today,
    }
    return render(request, "commandes/commandes_du_jour.html", context)
# views.py
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from io import BytesIO
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.http import HttpResponse
from reportlab.pdfgen import canvas

from .models import Commande
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.http import HttpResponse
from .models import Commande

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


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.http import HttpResponse
from .models import Commande

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Commande, Client



from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from django.http import HttpResponse
from django.db.models import Sum


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
    commandes = Commande.objects.prefetch_related("items__produit", "client").all()

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

    header_table = Table([[logo, infos_entreprise]], colWidths=[3 * inch, 6 * inch])
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
        elements.append(Paragraph("Aucune commande trouvée.", styles["Normal"]))
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
                quantites[client_nom][produit_nom] += Decimal(item.quantite or 0)

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
        col_widths = [1.6 * inch] + [col_produit_width] * nb_produits + [1.0 * inch]

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
                style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8f9fa")))

        table.setStyle(TableStyle(style))
        elements.append(table)

    # === 🔹 Pied de page ===
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<i>Document généré automatiquement - MOUNIA MICROPOUSSE</i>", styles["Normal"]))
    elements.append(Paragraph(f"<i>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>", styles["Normal"]))

    # === 🔹 Génération finale ===
    doc.build(elements)
    buffer.seek(0)

    filename = f"tableau_croise_commandes_{date_filtre if date_filtre else 'complet'}.pdf"
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'
    return response







from django.shortcuts import render

from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Commande, Client

# views.py

# views.py

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
            # Créer un objet datetime pour l'affichage
            mois_obj = datetime(annee, mois, 1)
        except ValueError:
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
                remise_appliquee = total_mois * (remise.valeur_remise / 100)
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
        date = aujourd_hui - timedelta(days=30*i)
        mois_disponibles.append({
            'value': date.strftime('%Y-%m'),
            'label': date.strftime('%B %Y').capitalize()
        })
    
    # Inverser l'ordre pour avoir les mois les plus récents en premier
    mois_disponibles.reverse()
    
    context = {
        'commandes': commandes,
        'clients': clients,
        'mois_disponibles': mois_disponibles,
        'client_selected': client_selected,
        'mois_selected': mois_selected,
        'mois_obj': mois_obj if mois_filtre else None,
        'total_mois': total_mois,
        'remise_appliquee': remise_appliquee,
        'total_apres_remise': total_apres_remise,
    }
    return render(request, 'factures/liste_factures.html', context)

def appliquer_remise(request, client_id, mois_filtre):
    client = get_object_or_404(Client, id=client_id)
    
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
            nouvelle_remise.save()
            
            messages.success(request, "Remise appliquée avec succès!")
            return redirect(f"{reverse('liste_factures')}?client={client_id}&mois={mois_filtre}")
    else:
        form = RemiseForm(instance=remise)
    
    return render(request, 'factures/appliquer_remise.html', {
        'form': form,
        'client': client,
        'mois_filtre': mois_filtre,
        'mois_nom': datetime.strptime(mois_filtre, "%Y-%m").strftime("%B %Y")
    })

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.http import HttpResponse
from .models import Commande, Client


# views.py


def facture_client_mois_pdf(request):
    """Génère une facture mensuelle pour un client spécifique"""
    
    # Récupérer les paramètres
    client_id = request.GET.get("client")
    mois_filtre = request.GET.get("mois")  # Format: YYYY-MM
    
    if not client_id or not mois_filtre:
        return HttpResponse("Paramètres manquants: client et mois requis")
    
    try:
        client = Client.objects.get(id=client_id)
        annee, mois = map(int, mois_filtre.split('-'))
        
        # Récupérer les commandes du client pour le mois spécifié
        commandes = Commande.objects.filter(
            client=client,
            date_commande__year=annee,
            date_commande__month=mois
        ).order_by('date_commande')
        
        # Calculer les totaux
        total_mois = sum(commande.total for commande in commandes)
        total_produits = sum(commande.total_sans_livraison for commande in commandes)
        nombre_livraisons = commandes.count()
        frais_livraison_total = sum(commande.frais_livraison for commande in commandes)
        
        # Récupérer la remise
        remise_appliquee = Decimal('0.00')
        try:
            remise = RemiseClient.objects.get(
                client=client,
                mois_application=mois_filtre
            )
            if remise.type_remise == 'pourcentage':
                remise_appliquee = total_mois * (remise.valeur_remise / 100)
            else:
                remise_appliquee = remise.valeur_remise
            
            remise_appliquee = min(remise_appliquee, total_mois)
            total_apres_remise = total_mois - remise_appliquee
        except RemiseClient.DoesNotExist:
            total_apres_remise = total_mois
            remise_appliquee = Decimal('0.00')
        
    except (Client.DoesNotExist, ValueError):
        return HttpResponse("Client ou mois invalide")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
    ))
    
    styles.add(ParagraphStyle(
        name='Center',
        parent=styles['Normal'],
        alignment=TA_CENTER,
    ))
    
    # =====================
    # EN-TÊTE DE LA FACTURE
    # =====================
    
    # Logo
    try:
        logo = Image("static/assets/img/MOUNIA_LOGO.png", width=1.5*inch, height=1.5*inch)
    except:
        logo = Paragraph("<b>MOUNIA MICROPOUSSE</b>", styles['Title'])
    
    # Informations entreprise
    infos_entreprise = [
        Paragraph("<b>MOUNIA MICROPOUSSE</b>", styles['Title']),
        Paragraph("Activité : Micropousse", styles['Normal']),
        Paragraph("Douar Laarich, 44000 Essaouira", styles['Normal']),
        Paragraph("Tél: +212 620-270-420", styles['Normal']),
        Paragraph("Email: mounia.mand97@gmail.com", styles['Normal']),
    ]
    
    # Informations facture
    mois_nom = datetime(annee, mois, 1).strftime("%B %Y").capitalize()
    infos_facture = [
        Paragraph("<b>FACTURE MENSUELLE</b>", styles['Title']),
        Paragraph(f"<b>Période:</b> {mois_nom}", styles['Normal']),
        Paragraph(f"<b>Date d'émission:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']),
        Paragraph(f"<b>Référence:</b> {client.id}-{annee}{mois:02d}", styles['Normal']),
        Paragraph(f"<b>Nombre de commandes:</b> {commandes.count()}", styles['Normal']),
    ]
    
    # Tableau en-tête
    header_data = [[logo, infos_entreprise, infos_facture]]
    header_table = Table(header_data, colWidths=[2*inch, 3*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    
    # =====================
    # INFORMATIONS CLIENT
    # =====================
    elements.append(Paragraph("<b>INFORMATIONS CLIENT</b>", styles['Heading2']))
    client_info = [
        [Paragraph("<b>Nom:</b>", styles['Normal']), client.nom],
        [Paragraph("<b>Ville:</b>", styles['Normal']), client.ville],
        [Paragraph("<b>Prix livraison:</b>", styles['Normal']), f"{client.prix_livraison} MAD"],
        [Paragraph("<b>Période de facturation:</b>", styles['Normal']), mois_nom],
    ]
    
    if hasattr(client, 'adresse') and client.adresse:
        client_info.insert(1, [Paragraph("<b>Adresse:</b>", styles['Normal']), client.adresse])
    if hasattr(client, 'telephone') and client.telephone:
        client_info.append([Paragraph("<b>Téléphone:</b>", styles['Normal']), client.telephone])
    
    client_table = Table(client_info, colWidths=[1.5*inch, 5*inch])
    client_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 20))
    
    # =====================
    # RÉCAPITULATIF DE LA FACTURE
    # =====================
    elements.append(Paragraph(f"<b>RÉCAPITULATIF DE LA FACTURE - {mois_nom.upper()}</b>", styles['Heading2']))
    
    if not commandes.exists():
        elements.append(Paragraph("Aucune commande trouvée pour cette période.", styles['Normal']))
        elements.append(Spacer(1, 20))
    else:
        # Tableau récapitulatif des commandes
        recap_data = [
            ["Date", "N° Commande", "Statut", "Produits", "Livraison", "Total (MAD)"]
        ]
        
        for commande in commandes:
            recap_data.append([
                commande.date_commande.strftime("%d/%m/%Y"),
                str(commande.id),
                commande.statut,
                _format_money(commande.total_sans_livraison),
                _format_money(commande.frais_livraison),
                _format_money(commande.total)
            ])
        
        # Lignes de totaux détaillés
        recap_data.append([
            "", "", "SOUS-TOTAL PRODUITS:", 
            _format_money(total_produits), "", ""
        ])
        
        recap_data.append([
            "", "", f"FRAIS LIVRAISON ({nombre_livraisons} livraisons):", 
            "", _format_money(frais_livraison_total), ""
        ])
        
        recap_data.append([
            "", "", "SOUS-TOTAL:", 
            "", "", _format_money(total_mois)
        ])
        
        # Ligne de la remise si applicable
        if remise_appliquee > 0:
            recap_data.append([
                "", "", "REMISE APPLIQUÉE:", 
                "", "", Paragraph(f"-{_format_money(remise_appliquee)}", styles['Normal'])
            ])
        
        # Ligne du total après remise - CORRIGÉE
        recap_data.append([
            "", "", "TOTAL:", 
            Paragraph(f"<b>{_format_money(total_apres_remise)} MAD TTC</b>", styles['Heading3'])
        ])
        
        recap_table = Table(recap_data, colWidths=[1.2*inch, 1.0*inch, 1.5*inch, 1.0*inch, 1.0*inch, 1.0*inch])
        recap_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (3,1), (5,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#f8f9fa')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            # Style pour les lignes de totaux
            ('FONTNAME', (0,-5), (-1,-5), 'Helvetica-Bold'),  # Sous-total produits
            ('FONTNAME', (0,-4), (-1,-4), 'Helvetica-Bold'),  # Frais livraison
            ('FONTNAME', (0,-3), (-1,-3), 'Helvetica-Bold'),  # Sous-total
            ('BACKGROUND', (0,-3), (-1,-3), colors.HexColor('#e9ecef')),  # Fond sous-total
            # Style pour la remise
            ('TEXTCOLOR', (0,-2), (-1,-2), colors.green),  # Remise en vert
            ('FONTNAME', (0,-2), (-1,-2), 'Helvetica-Bold'),
            # Style pour le total final - CORRIGÉ
            ('SPAN', (3,-1), (5,-1)),  # Fusion des 3 dernières cellules pour le total
            ('BACKGROUND', (3,-1), (5,-1), colors.HexColor('#d4edda')),
            ('FONTSIZE', (3,-1), (5,-1), 10),
            ('FONTNAME', (3,-1), (5,-1), 'Helvetica-Bold'),
        ]))
        
        elements.append(recap_table)
        elements.append(Spacer(1, 30))
    
    # =====================
    # PIED DE PAGE
    # =====================
    elements.append(Paragraph("Conditions de paiement: 30 jours nets", styles['Normal']))
    elements.append(Paragraph("Merci pour votre confiance!", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<i>Document établi électroniquement - valable sans signature</i>", styles['Center']))
    
    # Génération du PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"facture_{client.nom}_{annee}_{mois:02d}.pdf".replace(" ", "_")
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def _format_money(value):
    """Format Decimal to string with 2 decimals (safe)."""
    if value is None:
        value = Decimal("0.00")
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except:
            value = Decimal("0.00")
    return f"{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"

from django.core.cache import cache

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
    
    return render(request, 'parametres/application.html', {
        'form': form,
        'parametres': parametres
    })
    
    
  



















































from django.contrib.auth import authenticate, login,logout

def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès !')
            return redirect('login')  # Redirigez vers une page de connexion ou autre
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'utilisateurs/ajouter_utilisateur.html', {'form': form})


from django.contrib.auth import authenticate, login,logout
from .forms import CustomLoginForm

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
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')

    return render(request, 'utilisateurs/login.html', {'form': form})

def logout_utilisateur(request):
    
    logout(request)  # Déconnexion de l'utilisateur
    messages.success(request, 'Déconnexion réussie.')
    return redirect('login')  