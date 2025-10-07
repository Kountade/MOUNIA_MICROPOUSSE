from django.db import models
from django.utils import timezone
# Create your models here.
from django.db import models
from decimal import Decimal
    
import time
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import uuid
from django.db import models
from django.db.models import Avg, Sum, F
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _ 

from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=150, verbose_name="Nom du restaurant")
    responsable = models.CharField(max_length=100, verbose_name="Nom du responsable")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", unique=True)
    ice = models.CharField(
        max_length=15, 
        verbose_name="ICE", 
        unique=True,
        blank=True,
        null=True
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    adresse = models.TextField(verbose_name="Adresse")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    prix_livraison = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix de livraison (en €)"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d’ajout")

    class Meta:
        verbose_name = "Client (Restaurant)"
        verbose_name_plural = "Clients (Restaurants)"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} - {self.ville} ({self.prix_livraison} €)"


class Produit(models.Model):
    nom = models.CharField(max_length=100, unique=True)  # Nom du produit
    description = models.TextField(blank=True, null=True)  # Description du produit
    prix = models.DecimalField(max_digits=10, decimal_places=2)  # Prix du produit
    image = models.ImageField(upload_to="produits/", blank=True, null=True)  # Image du produit
    date_ajout = models.DateTimeField(auto_now_add=True)  # Date d'ajout automatique

    class Meta:
        ordering = ["-date_ajout"]  # Produits les plus récents en premier
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.nom


class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="commandes")
  
    date_commande = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=20, default="En cours")

    def __str__(self):
        return f"Commande #{self.id} - {self.client.nom}"

    @property
    def total_sans_livraison(self):
        """Total des produits sans le prix de livraison"""
        return sum(item.sous_total for item in self.items.all())

    @property
    def total(self):
        """Total final incluant le prix de livraison du client"""
        total_produits = self.total_sans_livraison
        prix_livraison = self.client.prix_livraison
        return total_produits + prix_livraison

    @property
    def frais_livraison(self):
        """Retourne les frais de livraison du client"""
        return self.client.prix_livraison


class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="items")
    produit = models.ForeignKey("Produit", on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = self.produit.prix
        super().save(*args, **kwargs)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"

# models.py

class RemiseClient(models.Model):
    TYPE_REMISE_CHOICES = [
        ('pourcentage', 'Pourcentage'),
        ('fixe', 'Montant fixe'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    type_remise = models.CharField(max_length=20, choices=TYPE_REMISE_CHOICES)
    valeur_remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mois_application = models.CharField(max_length=7)  # Format: YYYY-MM
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['client', 'mois_application']
    
    def __str__(self):
        return f"Remise {self.client.nom} - {self.mois_application}"
    

class ParametresMounia(models.Model):
    nom_hotel = models.CharField(max_length=100, default="Mon app")
    adresse = models.TextField(default="Adresse par défaut")
    email_contact = models.EmailField(default="contact@mounia.com")
    telephone_contact = models.CharField(max_length=20, default="+123456789")
    politique_annulation = models.TextField(
        default="Annulation gratuite jusqu'à 48h avant l'arrivée.",
        help_text="Texte explicatif pour les annulations"
    )
    logo = models.ImageField(upload_to='hotel_logos/', blank=True, null=True)  # Optionnel

    def __str__(self):
        return f"Paramètres de {self.nom_hotel}"

    class Meta:
        verbose_name_plural = "Paramètres de mounia"  # Nom correct dans l'admin Django
        
        



