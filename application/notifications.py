from django.utils import timezone
from datetime import datetime, timedelta
from .models import Commande, Notification

class NotificationManager:
    
    @staticmethod
    def get_commandes_du_jour():
        """Récupère les commandes du jour"""
        aujourd_hui = timezone.now().date()
        debut_jour = timezone.make_aware(datetime.combine(aujourd_hui, datetime.min.time()))
        fin_jour = timezone.make_aware(datetime.combine(aujourd_hui, datetime.max.time()))
        
        return Commande.objects.filter(
            date_commande__range=(debut_jour, fin_jour)
        )
    
    @staticmethod
    def creer_notification_commandes_jour():
        """Crée une notification pour les commandes du jour"""
        commandes_du_jour = NotificationManager.get_commandes_du_jour()
        aujourd_hui = timezone.now().date()
        
        # Vérifier si une notification existe déjà pour aujourd'hui
        notification_existante = Notification.objects.filter(
            type_notification='commande_jour',
            date_creation__date=aujourd_hui
        ).exists()
        
        if not notification_existante and commandes_du_jour.exists():
            nombre_commandes = commandes_du_jour.count()
            commandes_en_cours = commandes_du_jour.filter(statut='En cours').count()
            commandes_confirmees = commandes_du_jour.filter(statut='Confirmée').count()
            
            titre = f"📋 Commandes du jour - {aujourd_hui.strftime('%d/%m/%Y')}"
            message = f"""
            📊 Résumé des commandes du jour :
            
            • Total des commandes : {nombre_commandes}
            • En attente : {commandes_en_cours}
            • Confirmées : {commandes_confirmees}
            
            Pensez à traiter les commandes en attente !
            """
            
            Notification.objects.create(
                titre=titre,
                message=message.strip(),
                type_notification='commande_jour'
            )
    
    @staticmethod
    def get_notifications_non_lues():
        """Récupère les notifications non lues"""
        return Notification.objects.filter(lue=False).order_by('-date_creation')
    
    @staticmethod
    def marquer_comme_lue(notification_id):
        """Marque une notification comme lue"""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.lue = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def marquer_toutes_comme_lues():
        """Marque toutes les notifications comme lues"""
        Notification.objects.filter(lue=False).update(lue=True)
    
    @staticmethod
    def get_statistiques_jour():
        """Récupère les statistiques du jour pour les notifications"""
        commandes_du_jour = NotificationManager.get_commandes_du_jour()
        
        return {
            'total_commandes': commandes_du_jour.count(),
            'commandes_en_cours': commandes_du_jour.filter(statut='En cours').count(),
            'commandes_confirmees': commandes_du_jour.filter(statut='Confirmée').count(),
            'commandes_livrees': commandes_du_jour.filter(statut='Livrée').count(),
            'commandes_annulees': commandes_du_jour.filter(statut='Annulée').count(),
        }