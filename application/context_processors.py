from .models import ParametresMounia

def parametres_mounia(request):
    return {
        'parametres': ParametresMounia.objects.first() or None
    }
    
