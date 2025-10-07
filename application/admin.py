from django.contrib import admin

# Register your models here.



from django.contrib import admin
from .models import ParametresMounia

@admin.register(ParametresMounia)
class ParametresHotelAdmin(admin.ModelAdmin):
    list_display = ('nom_hotel', 'email_contact', 'telephone_contact')
    # Empêche la création de multiples instances (une seule configuration)
    def has_add_permission(self, request):
        return not ParametresMounia.objects.exists()