from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now





from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ParametresHotel, ParametresMounia

@receiver(post_migrate)
def init_parametres(sender, **kwargs):
    if sender.name == 'application' and not ParametresMounia.objects.exists():
        ParametresHotel.objects.create()
        
        

from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files import File

@receiver(pre_save, sender=ParametresMounia)
def resize_logo(sender, instance, **kwargs):
    if instance.logo:
        img = Image.open(instance.logo)
        if img.height > 120 or img.width > 360:
            output_size = (360, 120)
            img.thumbnail(output_size)
            thumb_io = BytesIO()
            img.save(thumb_io, format='PNG', quality=85)
            instance.logo.save(instance.logo.name, File(thumb_io), save=False)









