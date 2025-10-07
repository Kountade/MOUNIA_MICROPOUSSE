# votre_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permet d'accéder à un élément d'un dictionnaire par sa clé dans un template"""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None

@register.filter
def get_client_by_id(clients_queryset, client_id):
    """Filtre personnalisé pour récupérer un client par son ID depuis un queryset"""
    try:
        return clients_queryset.get(id=client_id)
    except:
        return None

@register.filter
def format_currency(value):
    """Formate un nombre en devise"""
    if value is None:
        return "0.00"
    return f"{float(value):.2f}"

@register.filter
def month_name(month_number):
    """Convertit un numéro de mois en nom"""
    months = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    return months.get(month_number, "")