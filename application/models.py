from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


from django.db import models
from django.utils import timezone
from decimal import Decimal

class Client(models.Model):
    nom = models.CharField(max_length=150, verbose_name="Nom du restaurant")
    responsable = models.CharField(max_length=100, verbose_name="Nom du responsable", blank=True, null=True)
    telephone = models.CharField(
        max_length=20, 
        verbose_name="Téléphone", 
        unique=True, 
        blank=True, 
        null=True
    )
    ice = models.CharField(
        max_length=15, 
        verbose_name="ICE", 
        unique=False,
        blank=True,
        null=True
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    adresse = models.TextField(verbose_name="Adresse", blank=True, null=True)
    ville = models.CharField(max_length=100, verbose_name="Ville")
    prix_livraison = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix de livraison (en MAD)"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Client (Restaurant)"
        verbose_name_plural = "Clients (Restaurants)"
        ordering = ["nom"]

    def get_commandes_par_mois(self, annee, mois):
        """Récupère toutes les commandes pour un mois donné"""
        return self.commandes.filter(
            date_commande__year=annee,
            date_commande__month=mois
        )

    def get_total_mois(self, annee, mois):
        """Calcule le total ACTUEL des commandes pour un mois donné"""
        commandes_mois = self.get_commandes_par_mois(annee, mois)
        total = Decimal('0.00')
        for commande in commandes_mois:
            # Utiliser total_avec_remise pour avoir le montant final
            total += commande.total_avec_remise
        return total

    def get_statut_paiement_mois(self, annee, mois):
        """Récupère ou met à jour le statut de paiement pour un mois"""
        mois_str = f"{annee}-{str(mois).zfill(2)}"
        
        # Calculer le total ACTUEL du mois
        total_mois_actuel = self.get_total_mois(annee, mois)
        
        try:
            paiement = Paiement.objects.get(client=self, mois=mois_str)
            
            # Mettre à jour le montant_du si nécessaire
            if paiement.montant_du != total_mois_actuel:
                paiement.montant_du = total_mois_actuel
                
                # Recalculer le statut basé sur le nouveau montant
                if paiement.montant_paye >= total_mois_actuel:
                    paiement.statut = 'paye'
                elif paiement.montant_paye > 0:
                    paiement.statut = 'partiel'
                else:
                    paiement.statut = 'non_paye'
                    
                paiement.save()
            
            return paiement
            
        except Paiement.DoesNotExist:
            # Créer un nouveau paiement seulement s'il y a des commandes
            if total_mois_actuel > 0:
                return Paiement.objects.create(
                    client=self,
                    mois=mois_str,
                    montant_du=total_mois_actuel,
                    montant_paye=0,
                    statut='non_paye'
                )
            return None

    def get_historique_paiements(self):
        """Retourne l'historique complet des paiements"""
        return self.paiements.all().order_by('-mois')

    def forcer_mise_a_jour_paiements(self):
        """Force la mise à jour de tous les paiements pour ce client"""
        from datetime import datetime
        maintenant = timezone.now()
        
        # Mettre à jour les 12 derniers mois
        for i in range(12):
            mois_date = maintenant - timezone.timedelta(days=30*i)
            annee = mois_date.year
            mois = mois_date.month
            self.get_statut_paiement_mois(annee, mois)

    def __str__(self):
        return f"{self.nom} - {self.ville} ({self.prix_livraison} MAD)"


class Produit(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="produits/", blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True, verbose_name="Produit actif")

    class Meta:
        ordering = ["-date_ajout"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.nom

from decimal import Decimal
from django.db import models
from django.utils import timezone


class Commande(models.Model):
    STATUT_CHOICES = [
        ('En cours', 'En cours'),
        ('Confirmée', 'Confirmée'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="commandes")
    date_commande = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="En cours")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes internes")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-date_commande"]

    def __str__(self):
        return f"Commande #{self.id} - {self.client.nom}"

    # === PROPRIÉTÉS CALCULÉES POUR LES TOTAUX ===
    
    @property
    def total_sans_livraison(self):
        """Total des produits sans le prix de livraison"""
        try:
            return sum(Decimal(str(item.sous_total)) for item in self.items.all())
        except:
            return Decimal('0.00')

    @property
    def total(self):
        """Total final incluant le prix de livraison du client"""
        try:
            total_produits = self.total_sans_livraison
            prix_livraison = Decimal(str(self.client.prix_livraison))
            return total_produits + prix_livraison
        except:
            return Decimal('0.00')

    @property
    def frais_livraison(self):
        """Retourne les frais de livraison du client"""
        try:
            return Decimal(str(self.client.prix_livraison))
        except:
            return Decimal('0.00')
    @property
    def montant_paye(self):
        return sum(paiement.montant for paiement in self.paiements.all())

    @property
    def statut_paiement(self):
        total = self.total_avec_remise
        paye = self.montant_paye
        if paye == 0:
            return 'non_paye'
        elif paye < total:
            return 'partiellement_paye'
        elif paye >= total:
            return 'paye'

    # === PROPRIÉTÉS POUR LES REMISES (CORRIGÉES) ===
    
    @property
    def remise_appliquee(self):
        """Retourne la remise applicable pour ce client ce mois-ci"""
        mois_commande = self.date_commande.strftime('%Y-%m')
        try:
            return RemiseClient.objects.get(
                client=self.client,
                mois_application=mois_commande
            )
        except RemiseClient.DoesNotExist:
            return None

    @property
    def montant_remise(self):
        """Calcule le montant de la remise en MAD (UNIQUEMENT sur les produits)"""
        remise = self.remise_appliquee
        if not remise:
            return Decimal('0.00')
        
        try:
            if remise.type_remise == 'pourcentage':
                # Remise uniquement sur le total des produits
                return self.total_sans_livraison * (Decimal(str(remise.valeur_remise)) / Decimal('100'))
            else:
                # Remise fixe, limitée au total des produits
                return min(Decimal(str(remise.valeur_remise)), self.total_sans_livraison)
        except:
            return Decimal('0.00')

    @property
    def total_avec_remise(self):
        """Calcule le total après remise (produits remisés + frais livraison)"""
        try:
            total_produits_remise = self.total_sans_livraison - self.montant_remise
            # On s'assure que le total des produits après remise n'est pas négatif
            total_produits_remise = max(total_produits_remise, Decimal('0.00'))
            # On ajoute les frais de livraison (sans remise)
            return total_produits_remise + self.frais_livraison
        except:
            return self.total

    @property
    def total_produits_apres_remise(self):
        """Retourne le total des produits après application de la remise"""
        try:
            total_apres_remise = self.total_sans_livraison - self.montant_remise
            return max(total_apres_remise, Decimal('0.00'))
        except:
            return self.total_sans_livraison

    @property
    def pourcentage_remise(self):
        """Retourne le pourcentage de remise appliqué"""
        remise = self.remise_appliquee
        if remise and remise.type_remise == 'pourcentage':
            try:
                return Decimal(str(remise.valeur_remise))
            except:
                return Decimal('0.00')
        return Decimal('0.00')


class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="items")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Item de commande"
        verbose_name_plural = "Items de commande"
        ordering = ["date_ajout"]

    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour définir le prix unitaire automatiquement"""
        if not self.prix_unitaire:
            self.prix_unitaire = self.produit.prix
        super().save(*args, **kwargs)

    @property
    def sous_total(self):
        """Calcule le sous-total pour cet item"""
        try:
            return Decimal(str(self.quantite)) * Decimal(str(self.prix_unitaire))
        except:
            return Decimal('0.00')

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite} - {self.sous_total:.2f} MAD"

class RemiseClient(models.Model):
    TYPE_REMISE_CHOICES = [
        ('pourcentage', 'Pourcentage (%)'),
        ('fixe', 'Montant fixe (MAD)'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="remises")
    type_remise = models.CharField(max_length=20, choices=TYPE_REMISE_CHOICES, verbose_name="Type de remise")
    valeur_remise = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Valeur de la remise"
    )
    mois_application = models.CharField(
        max_length=7,
        verbose_name="Mois d'application",
        help_text="Format: YYYY-MM"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Description de la remise"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Remise client"
        verbose_name_plural = "Remises clients"
        unique_together = ['client', 'mois_application']
        ordering = ['-mois_application', 'client']
    
    def __str__(self):
        type_affichage = "%" if self.type_remise == 'pourcentage' else "MAD"
        return f"Remise {self.client.nom} - {self.mois_application} ({self.valeur_remise} {type_affichage})"

    @property
    def valeur_affichage(self):
        """Retourne la valeur formatée pour l'affichage"""
        if self.type_remise == 'pourcentage':
            return f"{self.valeur_remise}%"
        else:
            return f"{self.valeur_remise} MAD"

    def calculer_remise(self, montant_total_produits):
        """Calcule le montant de la remise pour un montant donné de produits"""
        if self.type_remise == 'pourcentage':
            return float(montant_total_produits) * (float(self.valeur_remise) / 100)
        else:
            return min(float(self.valeur_remise), float(montant_total_produits))


class Notification(models.Model):
    TYPE_CHOIX = [
        ('commande_jour', 'Commandes du jour'),
        ('statut', 'Changement de statut'),
        ('rapport', 'Rapport quotidien'),
        ('alerte', 'Alerte importante'),
    ]
    
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOIX, default='commande_jour')
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, null=True, blank=True)
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.date_creation.strftime('%d/%m/%Y %H:%M')}"
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
        
        




class Paiement(models.Model):
    STATUT_PAIEMENT_CHOICES = [
        ('paye', 'Payé'),
        ('partiel', 'Partiellement payé'),
        ('non_paye', 'Non payé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="paiements")
    mois = models.CharField(max_length=7, verbose_name="Mois (YYYY-MM)")
    montant_du = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant dû")
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant payé")
    statut = models.CharField(max_length=20, choices=STATUT_PAIEMENT_CHOICES, default='non_paye')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        unique_together = ['client', 'mois']
        ordering = ['-mois']

    def __str__(self):
        return f"Paiement {self.client.nom} - {self.mois}"

    @property
    def reste_a_payer(self):
        return self.montant_du - self.montant_paye

    def save(self, *args, **kwargs):
        # Mise à jour automatique du statut
        if self.montant_paye >= self.montant_du:
            self.statut = 'paye'
        elif self.montant_paye > 0:
            self.statut = 'partiel'
        else:
            self.statut = 'non_paye'
        super().save(*args, **kwargs)


