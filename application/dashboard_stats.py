from django.db.models import Count, Sum, Avg, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from decimal import Decimal
from .models import Client, Produit, Commande, CommandeItem, RemiseClient

class DashboardStats:
    
    @staticmethod
    def get_clients_stats():
        """Statistiques des clients"""
        total_clients = Client.objects.count()
        
        # Clients ajoutés ce mois
        debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        clients_ce_mois = Client.objects.filter(
            date_creation__gte=debut_mois
        ).count()
        
        # Clients par ville
        clients_par_ville = Client.objects.values('ville').annotate(
            total=Count('id')
        ).order_by('-total')
        
        return {
            'total_clients': total_clients,
            'clients_ce_mois': clients_ce_mois,
            'clients_par_ville': clients_par_ville,
        }
    
    @staticmethod
    def get_produits_stats():
        """Statistiques des produits"""
        total_produits = Produit.objects.count()
        produits_actifs = Produit.objects.filter(actif=True).count()
        produits_inactifs = Produit.objects.filter(actif=False).count()
        
        # Produits ajoutés cette semaine
        debut_semaine = timezone.now() - timedelta(days=timezone.now().weekday())
        produits_cette_semaine = Produit.objects.filter(
            date_ajout__gte=debut_semaine
        ).count()
        
        # Prix moyen des produits
        prix_moyen = Produit.objects.aggregate(
            prix_moyen=Avg('prix')
        )['prix_moyen'] or 0
        
        # Top 10 produits les plus commandés
        top_produits = Produit.objects.annotate(
            total_commandes=Count('commandeitem')
        ).order_by('-total_commandes')[:10]
        
        return {
            'total_produits': total_produits,
            'produits_actifs': produits_actifs,
            'produits_inactifs': produits_inactifs,
            'produits_cette_semaine': produits_cette_semaine,
            'prix_moyen': round(prix_moyen, 2),
            'top_produits': list(top_produits.values('id', 'nom', 'prix', 'total_commandes')),
        }
    
    @staticmethod
    def calculate_ca_total():
        """Calcule le chiffre d'affaires total manuellement"""
        commandes_confirmees = Commande.objects.filter(
            statut__in=['Confirmée', 'Livrée']
        )
        ca_total = Decimal('0.00')
        for commande in commandes_confirmees:
            ca_total += Decimal(str(commande.total))
        return ca_total
    
    @staticmethod
    def calculate_ca_mois():
        """Calcule le CA de ce mois manuellement"""
        debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        commandes_mois = Commande.objects.filter(
            statut__in=['Confirmée', 'Livrée'],
            date_commande__gte=debut_mois
        )
        ca_mois = Decimal('0.00')
        for commande in commandes_mois:
            ca_mois += Decimal(str(commande.total))
        return ca_mois
    
    @staticmethod
    def get_commandes_stats():
        """Statistiques des commandes"""
        total_commandes = Commande.objects.count()
        
        # Commandes par statut
        commandes_par_statut = Commande.objects.values('statut').annotate(
            total=Count('id')
        ).order_by('statut')
        
        # Calcul manuel du CA
        ca_total = DashboardStats.calculate_ca_total()
        ca_ce_mois = DashboardStats.calculate_ca_mois()
        
        # Commandes cette semaine
        debut_semaine = timezone.now() - timedelta(days=timezone.now().weekday())
        commandes_cette_semaine = Commande.objects.filter(
            date_commande__gte=debut_semaine
        ).count()
        
        return {
            'total_commandes': total_commandes,
            'commandes_par_statut': list(commandes_par_statut),
            'ca_total': float(ca_total),
            'ca_ce_mois': float(ca_ce_mois),
            'commandes_cette_semaine': commandes_cette_semaine,
        }
    
    @staticmethod
    def get_evolution_clients():
        """Évolution des clients sur les 6 derniers mois"""
        six_mois = timezone.now() - timedelta(days=180)
        
        evolution = Client.objects.filter(
            date_creation__gte=six_mois
        ).annotate(
            mois=TruncMonth('date_creation')
        ).values('mois').annotate(
            total=Count('id')
        ).order_by('mois')
        
        return list(evolution)
    
    @staticmethod
    def get_evolution_commandes():
        """Évolution des commandes sur les 3 derniers mois"""
        trois_mois = timezone.now() - timedelta(days=90)
        
        evolution = Commande.objects.filter(
            date_commande__gte=trois_mois
        ).annotate(
            semaine=TruncWeek('date_commande')
        ).values('semaine').annotate(
            total_commandes=Count('id')
        ).order_by('semaine')
        
        # Calcul manuel du CA pour chaque semaine
        result = []
        for item in evolution:
            semaine = item['semaine']
            commandes_semaine = Commande.objects.filter(
                date_commande__gte=semaine,
                date_commande__lt=semaine + timedelta(days=7),
                statut__in=['Confirmée', 'Livrée']
            )
            ca_semaine = Decimal('0.00')
            for commande in commandes_semaine:
                ca_semaine += Decimal(str(commande.total))
            
            result.append({
                'semaine': semaine,
                'total_commandes': item['total_commandes'],
                'total_ca': float(ca_semaine)
            })
        
        return result
    
    @staticmethod
    def get_ca_par_mois():
        """Chiffre d'affaires par mois sur l'année en cours"""
        debut_annee = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Récupérer les mois avec des commandes
        mois_avec_commandes = Commande.objects.filter(
            statut__in=['Confirmée', 'Livrée'],
            date_commande__gte=debut_annee
        ).annotate(
            mois=TruncMonth('date_commande')
        ).values('mois').distinct().order_by('mois')
        
        result = []
        for item in mois_avec_commandes:
            mois = item['mois']
            commandes_mois = Commande.objects.filter(
                statut__in=['Confirmée', 'Livrée'],
                date_commande__gte=mois,
                date_commande__lt=mois.replace(month=mois.month % 12 + 1, day=1) if mois.month != 12 
                else mois.replace(year=mois.year + 1, month=1, day=1)
            )
            
            ca_mois = Decimal('0.00')
            for commande in commandes_mois:
                ca_mois += Decimal(str(commande.total))
            
            result.append({
                'mois': mois,
                'ca_total': float(ca_mois)
            })
        
        return result
    
    @staticmethod
    def get_top_clients():
        """Top 10 clients par chiffre d'affaires"""
        clients = Client.objects.all()
        result = []
        
        for client in clients:
            commandes_client = Commande.objects.filter(
                client=client,
                statut__in=['Confirmée', 'Livrée']
            )
            total_ca = Decimal('0.00')
            for commande in commandes_client:
                total_ca += Decimal(str(commande.total))
            
            if total_ca > 0:
                result.append({
                    'nom': client.nom,
                    'ville': client.ville,
                    'total_commandes': commandes_client.count(),
                    'total_ca': float(total_ca)
                })
        
        # Trier par CA décroissant
        result.sort(key=lambda x: x['total_ca'], reverse=True)
        return result[:10]
    
    @staticmethod
    def get_stats_remises():
        """Statistiques sur les remises"""
        mois_courant = timezone.now().strftime('%Y-%m')
        remises_ce_mois = RemiseClient.objects.filter(
            mois_application=mois_courant
        ).count()
        
        total_remises = RemiseClient.objects.count()
        
        # Répartition par type de remise
        remises_par_type = RemiseClient.objects.values('type_remise').annotate(
            total=Count('id')
        )
        
        return {
            'remises_ce_mois': remises_ce_mois,
            'total_remises': total_remises,
            'remises_par_type': list(remises_par_type),
        }
    
    @staticmethod
    def get_stats_globales():
        """Récupère toutes les statistiques"""
        return {
            'clients': DashboardStats.get_clients_stats(),
            'produits': DashboardStats.get_produits_stats(),
            'commandes': DashboardStats.get_commandes_stats(),
            'remises': DashboardStats.get_stats_remises(),
            'evolution_clients': DashboardStats.get_evolution_clients(),
            'evolution_commandes': DashboardStats.get_evolution_commandes(),
            'ca_par_mois': DashboardStats.get_ca_par_mois(),
            'top_clients': DashboardStats.get_top_clients(),
        }