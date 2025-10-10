from django.utils import timezone
from datetime import datetime
from .notifications import NotificationManager

class NotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier et créer les notifications des commandes du jour
        # seulement sur certaines pages pour éviter de surcharger
        if request.path in ['/', '/home', '/commandes/']:
            try:
                NotificationManager.creer_notification_commandes_jour()
            except Exception as e:
                # Logger l'erreur mais ne pas bloquer la requête
                print(f"Erreur dans NotificationMiddleware: {e}")
        
        response = self.get_response(request)
        return response