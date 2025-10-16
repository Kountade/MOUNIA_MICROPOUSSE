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
        try:
            total_clients = Client.objects.count()
            print(f"🔍 Total clients dans la base: {total_clients}")
            
            # Clients ajoutés ce mois
            debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            clients_ce_mois = Client.objects.filter(
                date_creation__gte=debut_mois
            ).count()
            print(f"🔍 Clients ce mois: {clients_ce_mois}")
            
            # Clients par ville
            clients_par_ville = Client.objects.values('ville').annotate(
                total=Count('id')
            ).order_by('-total')
            clients_list = list(clients_par_ville)
            print(f"🔍 Clients par ville: {clients_list}")
            
            return {
                'total_clients': total_clients,
                'clients_ce_mois': clients_ce_mois,
                'clients_par_ville': clients_list,
            }
        except Exception as e:
            print(f"❌ Erreur dans get_clients_stats: {e}")
            return {
                'total_clients': 0,
                'clients_ce_mois': 0,
                'clients_par_ville': [],
            }
    
    @staticmethod
    def get_produits_stats():
        """Statistiques des produits"""
        try:
            total_produits = Produit.objects.count()
            produits_actifs = Produit.objects.filter(actif=True).count()
            produits_inactifs = Produit.objects.filter(actif=False).count()
            
            print(f"🔍 Total produits: {total_produits}, Actifs: {produits_actifs}, Inactifs: {produits_inactifs}")
            
            # Produits ajoutés cette semaine
            debut_semaine = timezone.now() - timedelta(days=timezone.now().weekday())
            debut_semaine = debut_semaine.replace(hour=0, minute=0, second=0, microsecond=0)
            produits_cette_semaine = Produit.objects.filter(
                date_ajout__gte=debut_semaine
            ).count()
            
            # Prix moyen des produits
            prix_moyen_result = Produit.objects.aggregate(prix_moyen=Avg('prix'))
            prix_moyen = prix_moyen_result['prix_moyen'] or Decimal('0.00')
            
            # Top 10 produits les plus commandés
            top_produits = Produit.objects.annotate(
                total_commandes=Count('commandeitem')
            ).order_by('-total_commandes')[:10]
            
            top_produits_list = list(top_produits.values('id', 'nom', 'prix', 'total_commandes'))
            print(f"🔍 Top produits trouvés: {len(top_produits_list)}")
            
            return {
                'total_produits': total_produits,
                'produits_actifs': produits_actifs,
                'produits_inactifs': produits_inactifs,
                'produits_cette_semaine': produits_cette_semaine,
                'prix_moyen': float(prix_moyen),
                'top_produits': top_produits_list,
            }
        except Exception as e:
            print(f"❌ Erreur dans get_produits_stats: {e}")
            return {
                'total_produits': 0,
                'produits_actifs': 0,
                'produits_inactifs': 0,
                'produits_cette_semaine': 0,
                'prix_moyen': 0.0,
                'top_produits': [],
            }
    
    @staticmethod
    def calculate_ca_total():
        """Calcule le chiffre d'affaires total"""
        try:
            commandes = Commande.objects.all()
            ca_total = Decimal('0.00')
            commandes_count = 0
            
            for commande in commandes:
                commandes_count += 1
                montant_commande = Decimal(str(commande.total))
                ca_total += montant_commande
            
            print(f"🔍 CA total calculé sur {commandes_count} commandes: {ca_total} MAD")
            return ca_total
        except Exception as e:
            print(f"❌ Erreur dans calculate_ca_total: {e}")
            return Decimal('0.00')
    
    @staticmethod
    def calculate_ca_mois():
        """Calcule le CA de ce mois"""
        try:
            debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            commandes_mois = Commande.objects.filter(
                date_commande__gte=debut_mois
            )
            ca_mois = Decimal('0.00')
            commandes_count = 0
            
            for commande in commandes_mois:
                commandes_count += 1
                montant_commande = Decimal(str(commande.total))
                ca_mois += montant_commande
            
            print(f"🔍 CA ce mois ({commandes_count} commandes): {ca_mois} MAD")
            return ca_mois
        except Exception as e:
            print(f"❌ Erreur dans calculate_ca_mois: {e}")
            return Decimal('0.00')
    
    @staticmethod
    def get_commandes_stats():
        """Statistiques des commandes"""
        try:
            total_commandes = Commande.objects.count()
            print(f"🔍 Total commandes dans la base: {total_commandes}")
            
            # Commandes par statut
            commandes_par_statut = Commande.objects.values('statut').annotate(
                total=Count('id')
            ).order_by('statut')
            statuts_list = list(commandes_par_statut)
            print(f"🔍 Commandes par statut: {statuts_list}")
            
            # Calcul du CA
            ca_total = DashboardStats.calculate_ca_total()
            ca_ce_mois = DashboardStats.calculate_ca_mois()
            
            # Commandes cette semaine
            debut_semaine = timezone.now() - timedelta(days=timezone.now().weekday())
            debut_semaine = debut_semaine.replace(hour=0, minute=0, second=0, microsecond=0)
            commandes_cette_semaine = Commande.objects.filter(
                date_commande__gte=debut_semaine
            ).count()
            
            return {
                'total_commandes': total_commandes,
                'commandes_par_statut': statuts_list,
                'ca_total': float(ca_total),
                'ca_ce_mois': float(ca_ce_mois),
                'commandes_cette_semaine': commandes_cette_semaine,
            }
        except Exception as e:
            print(f"❌ Erreur dans get_commandes_stats: {e}")
            return {
                'total_commandes': 0,
                'commandes_par_statut': [],
                'ca_total': 0.0,
                'ca_ce_mois': 0.0,
                'commandes_cette_semaine': 0,
            }
    
    @staticmethod
    def get_evolution_clients():
        """Évolution des clients sur les 6 derniers mois"""
        try:
            six_mois = timezone.now() - timedelta(days=180)
            
            evolution = Client.objects.filter(
                date_creation__gte=six_mois
            ).annotate(
                mois=TruncMonth('date_creation')
            ).values('mois').annotate(
                total=Count('id')
            ).order_by('mois')
            
            evolution_list = list(evolution)
            print(f"🔍 Évolution clients: {len(evolution_list)} mois de données")
            return evolution_list
        except Exception as e:
            print(f"❌ Erreur dans get_evolution_clients: {e}")
            return []
    
    @staticmethod
    def get_evolution_commandes():
        """Évolution des commandes sur les 3 derniers mois"""
        try:
            trois_mois = timezone.now() - timedelta(days=90)
            
            evolution = Commande.objects.filter(
                date_commande__gte=trois_mois
            ).annotate(
                semaine=TruncWeek('date_commande')
            ).values('semaine').annotate(
                total_commandes=Count('id')
            ).order_by('semaine')
            
            result = []
            for item in evolution:
                semaine = item['semaine']
                commandes_semaine = Commande.objects.filter(
                    date_commande__gte=semaine,
                    date_commande__lt=semaine + timedelta(days=7)
                )
                ca_semaine = Decimal('0.00')
                for commande in commandes_semaine:
                    ca_semaine += Decimal(str(commande.total))
                
                result.append({
                    'semaine': semaine,
                    'total_commandes': item['total_commandes'],
                    'total_ca': float(ca_semaine)
                })
            
            print(f"🔍 Évolution commandes: {len(result)} semaines de données")
            return result
        except Exception as e:
            print(f"❌ Erreur dans get_evolution_commandes: {e}")
            return []
    
    @staticmethod
    def get_ca_par_mois():
        """Chiffre d'affaires par mois sur l'année en cours"""
        try:
            debut_annee = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Récupérer les mois avec des commandes
            mois_avec_commandes = Commande.objects.filter(
                date_commande__gte=debut_annee
            ).annotate(
                mois=TruncMonth('date_commande')
            ).values('mois').distinct().order_by('mois')
            
            result = []
            for item in mois_avec_commandes:
                mois = item['mois']
                if mois.month == 12:
                    fin_mois = mois.replace(year=mois.year + 1, month=1, day=1)
                else:
                    fin_mois = mois.replace(month=mois.month + 1, day=1)
                
                commandes_mois = Commande.objects.filter(
                    date_commande__gte=mois,
                    date_commande__lt=fin_mois
                )
                
                ca_mois = Decimal('0.00')
                for commande in commandes_mois:
                    ca_mois += Decimal(str(commande.total))
                
                result.append({
                    'mois': mois,
                    'ca_total': float(ca_mois)
                })
            
            print(f"🔍 CA par mois: {len(result)} mois de données")
            return result
        except Exception as e:
            print(f"❌ Erreur dans get_ca_par_mois: {e}")
            return []
    
    @staticmethod
    def get_top_clients():
        """Top 10 clients par chiffre d'affaires"""
        try:
            clients = Client.objects.all()
            result = []
            
            print(f"🔍 Calcul du top clients sur {clients.count()} clients")
            
            for client in clients:
                commandes_client = Commande.objects.filter(client=client)
                total_ca = Decimal('0.00')
                total_commandes = commandes_client.count()
                
                for commande in commandes_client:
                    total_ca += Decimal(str(commande.total))
                
                if total_commandes > 0:
                    result.append({
                        'id': client.id,
                        'nom': client.nom,
                        'ville': client.ville,
                        'total_commandes': total_commandes,
                        'total_ca': float(total_ca)
                    })
            
            # Trier par CA décroissant
            result.sort(key=lambda x: x['total_ca'], reverse=True)
            top_10 = result[:10]
            
            print(f"🔍 Top clients trouvés: {len(top_10)}")
            return top_10
        except Exception as e:
            print(f"❌ Erreur dans get_top_clients: {e}")
            return []
    
    @staticmethod
    def get_commandes_par_ville():
        """Répartition des commandes par ville - CORRIGÉE"""
        try:
            print("🔍 Calcul des commandes par ville...")
            
            # Méthode optimisée avec aggregation
            from django.db.models import Count, Sum
            
            # Vérifier d'abord s'il y a des commandes
            total_commandes = Commande.objects.count()
            print(f"   Total commandes dans la base: {total_commandes}")
            
            if total_commandes == 0:
                print("   ⚠️ Aucune commande trouvée")
                return []
            
            # Récupérer les villes des clients qui ont des commandes
            commandes_par_ville = Commande.objects.select_related('client').values(
                'client__ville'
            ).annotate(
                total_commandes=Count('id'),
                total_ca=Sum('total')
            ).filter(
                client__ville__isnull=False  # Exclure les valeurs nulles
            ).order_by('-total_commandes')
            
            result = []
            for item in commandes_par_ville:
                ville = item['client__ville']
                total_cmd = item['total_commandes'] or 0
                total_ca = float(item['total_ca'] or 0)
                
                result.append({
                    'ville': ville,
                    'total_commandes': total_cmd,
                    'total_ca': total_ca
                })
                print(f"   📍 {ville}: {total_cmd} commandes, {total_ca} MAD")
            
            print(f"✅ Commandes par ville: {len(result)} villes trouvées")
            return result
            
        except Exception as e:
            print(f"❌ Erreur dans get_commandes_par_ville: {e}")
            return []
    
    @staticmethod
    def get_stats_rapides():
        """Retourne les statistiques principales pour un affichage rapide"""
        try:
            clients_stats = DashboardStats.get_clients_stats()
            produits_stats = DashboardStats.get_produits_stats()
            commandes_stats = DashboardStats.get_commandes_stats()
            
            stats_rapides = {
                'total_clients': clients_stats.get('total_clients', 0),
                'clients_ce_mois': clients_stats.get('clients_ce_mois', 0),
                'total_produits': produits_stats.get('total_produits', 0),
                'produits_actifs': produits_stats.get('produits_actifs', 0),
                'prix_moyen_produits': produits_stats.get('prix_moyen', 0.0),
                'total_commandes': commandes_stats.get('total_commandes', 0),
                'ca_total': commandes_stats.get('ca_total', 0.0),
                'ca_ce_mois': commandes_stats.get('ca_ce_mois', 0.0),
                'commandes_cette_semaine': commandes_stats.get('commandes_cette_semaine', 0),
            }
            
            print("🔍 === STATS RAPIDES RÉELLES ===")
            for key, value in stats_rapides.items():
                print(f"   {key}: {value}")
            
            return stats_rapides
        except Exception as e:
            print(f"❌ Erreur dans get_stats_rapides: {e}")
            return {
                'total_clients': 0,
                'clients_ce_mois': 0,
                'total_produits': 0,
                'produits_actifs': 0,
                'prix_moyen_produits': 0.0,
                'total_commandes': 0,
                'ca_total': 0.0,
                'ca_ce_mois': 0.0,
                'commandes_cette_semaine': 0,
            }
    
    @staticmethod
    def get_stats_globales():
        """Récupère toutes les statistiques pour le dashboard"""
        try:
            stats = {
                'stats_rapides': DashboardStats.get_stats_rapides(),
                'clients_par_ville': DashboardStats.get_clients_stats().get('clients_par_ville', []),
                'top_produits': DashboardStats.get_produits_stats().get('top_produits', []),
                'top_clients': DashboardStats.get_top_clients(),
                'evolution_clients': DashboardStats.get_evolution_clients(),
                'evolution_commandes': DashboardStats.get_evolution_commandes(),
                'ca_par_mois': DashboardStats.get_ca_par_mois(),
                'commandes_par_ville': DashboardStats.get_commandes_par_ville(),
                'commandes_par_statut': DashboardStats.get_commandes_stats().get('commandes_par_statut', []),
                'timestamp': timezone.now().isoformat()
            }
            
            print("🎯 === STATISTIQUES GLOBALES RÉELLES GÉNÉRÉES ===")
            for key, value in stats.items():
                if key != 'timestamp':
                    if isinstance(value, list):
                        print(f"   {key}: {len(value)} éléments")
                    elif isinstance(value, dict):
                        print(f"   {key}: {len(value)} clés")
                    else:
                        print(f"   {key}: {value}")
            
            return stats
            
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE dans get_stats_globales: {e}")
            return {
                'stats_rapides': {},
                'clients_par_ville': [],
                'top_produits': [],
                'top_clients': [],
                'evolution_clients': [],
                'evolution_commandes': [],
                'ca_par_mois': [],
                'commandes_par_ville': [],
                'commandes_par_statut': [],
                'erreur': str(e),
                'timestamp': timezone.now().isoformat()
            }