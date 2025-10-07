from django import forms
from .models import Client
from django.shortcuts import render, redirect
from django.contrib import messages



from django import forms
from django.core.exceptions import ValidationError
from .models import Client
import re

class ClientForm(forms.ModelForm):
    # Rendre les champs obligatoires
    nom = forms.CharField(
        max_length=150,
        required=True,
        label="Nom du restaurant",
        error_messages={'required': 'Le nom du restaurant est obligatoire'}
    )
    
    ice = forms.CharField(
        max_length=15,
        required=True,
        label="ICE",
        error_messages={
            'required': 'Le numéro ICE est obligatoire',
            'unique': 'Ce numéro ICE existe déjà'
        }
    )
    
    ville = forms.CharField(
        max_length=100,
        required=True,
        label="Ville",
        error_messages={'required': 'La ville est obligatoire'}
    )
    
    prix_livraison = forms.DecimalField(
        required=True,
        label="Prix de livraison (en €)",
        max_digits=10,
        decimal_places=2,
        min_value=0,
        error_messages={
            'required': 'Le prix de livraison est obligatoire',
            'invalid': 'Veuillez entrer un prix valide',
            'min_value': 'Le prix ne peut pas être négatif'
        }
    )

    class Meta:
        model = Client
        fields = ['nom', 'ice', 'ville', 'prix_livraison', 'responsable', 'telephone', 'email', 'adresse']

    def clean_ice(self):
        ice = self.cleaned_data.get('ice')
        
        # Validation du format ICE (15 chiffres pour le Maroc)
        if ice:
            # Supprimer les espaces et caractères spéciaux
            ice_clean = re.sub(r'[^\d]', '', ice)
            
            # Vérifier la longueur
            if len(ice_clean) != 15:
                raise ValidationError("Le numéro ICE doit contenir exactement 15 chiffres")
            
            # Vérifier l'unicité
            if Client.objects.filter(ice=ice_clean).exists():
                if self.instance and self.instance.pk:
                    # Pour la modification, vérifier si l'ICE appartient à un autre client
                    if Client.objects.filter(ice=ice_clean).exclude(pk=self.instance.pk).exists():
                        raise ValidationError("Ce numéro ICE est déjà utilisé par un autre client")
                else:
                    # Pour la création
                    raise ValidationError("Ce numéro ICE est déjà utilisé")
            
            return ice_clean
        
        return ice

    def clean_prix_livraison(self):
        prix = self.cleaned_data.get('prix_livraison')
        if prix is not None and prix < 0:
            raise ValidationError("Le prix de livraison ne peut pas être négatif")
        return prix

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        # Marquer les champs obligatoires avec un astérisque
        for field in self.fields:
            if self.fields[field].required:
                self.fields[field].label += ' *'


from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ["nom", "description", "prix", "image"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom du produit"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Description"}),
            "prix": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Prix en MAD"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # Validation du champ nom
    def clean_nom(self):
        nom = self.cleaned_data.get("nom")
        if len(nom) < 3:
            raise forms.ValidationError("Le nom du produit doit contenir au moins 3 caractères.")
        return nom.capitalize()  # Met la première lettre en majuscule

    # Validation du champ prix
    def clean_prix(self):
        prix = self.cleaned_data.get("prix")
        if prix is None or prix <= 0:
            raise forms.ValidationError("Le prix doit être supérieur à 0.")
        return prix


# forms.py
from django import forms
from .models import Commande, CommandeItem, Client, Produit


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ["client"]  # seulement le client
        widgets = {
            "client": forms.Select(attrs={"class": "form-control"})
        }


class CommandeItemForm(forms.ModelForm):
    class Meta:
        model = CommandeItem
        fields = ["produit", "quantite", "prix_unitaire"]

        widgets = {
            "produit": forms.Select(attrs={"class": "form-control produit-select"}),
            "quantite": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "prix_unitaire": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }

from django.forms import inlineformset_factory

CommandeItemFormSet = inlineformset_factory(
    Commande,
    CommandeItem,
    form=CommandeItemForm,
    extra=1,
    can_delete=True
)


# forms.py

from django import forms
from .models import RemiseClient

class RemiseForm(forms.ModelForm):
    class Meta:
        model = RemiseClient
        fields = ['type_remise', 'valeur_remise']
        widgets = {
            'type_remise': forms.Select(attrs={'class': 'form-control'}),
            'valeur_remise': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def clean_valeur_remise(self):
        type_remise = self.cleaned_data.get('type_remise')
        valeur_remise = self.cleaned_data.get('valeur_remise')
        
        if type_remise == 'pourcentage' and (valeur_remise < 0 or valeur_remise > 100):
            raise forms.ValidationError("Le pourcentage doit être entre 0 et 100")
        
        if type_remise == 'fixe' and valeur_remise < 0:
            raise forms.ValidationError("Le montant ne peut pas être négatif")
        
        return valeur_remise





from django import forms
from .models import ParametresMounia
from django.core.validators import FileExtensionValidator

class ParametresForm(forms.ModelForm):
    class Meta:
        model = ParametresMounia
        fields = ['nom_hotel', 'logo', 'adresse', 'telephone_contact', 'email_contact']
        widgets = {
            'nom_hotel': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom_hotel': "Nom de l'établissement",
            'logo': "Logo (format PNG/JPG, max 500KB)",
        }
    
    logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])]
    )
    
    











































from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Entrez une adresse email valide.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
    )

    class Meta:
        model = User
        fields = ['username', 'password']





from django import forms
from django.contrib.auth.models import User


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']