from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("home", views.home, name="home"),

    #   path clients
    path("clients/", views.liste_clients, name="liste_clients"),
    path("clients/ajouter/", views.ajouter_client, name="ajouter_client"),

    path('clients/<int:pk>/modifier/',
         views.modifier_client, name='modifier_client'),
    path('client/<int:pk>/detail/', views.detail_client, name='detail_client'),
    path('client/<int:pk>/supprimer/',
         views.supprimer_client, name='supprimer_client'),
    #   path produits
    path('produits/', views.produit_list, name='liste_produits'),
    path('ajouter/', views.produit_create, name='ajouter_produit'),
    path('modifier/<int:pk>/', views.produit_update, name='modifier_produit'),
    path('supprimer/<int:pk>/', views.produit_delete, name='supprimer_produit'),
    path('produits/export/excel/', views.exporter_produits_excel,
         name='exporter_produits_excel'),
    path('produits/export/pdf/', views.exporter_produits_pdf,
         name='exporter_produits_pdf'),
    #   path('parametres/',  views.parametres_application, name='parametres_app'),


    path("commandes/nouvelle/", views.creer_commande, name="creer_commande"),
    path('commandes/modifier/<int:commande_id>/',
         views.modifier_commande, name='modifier_commande'),
    path("commandes/<int:pk>/supprimer/",
         views.supprimer_commande, name="supprimer_commande"),
    path("commandes/<int:commande_id>/ajouter-item/",
         views.ajouter_item, name="ajouter_item"),
    # path("commandes/<int:pk>/", views.detail_commande, name="detail_commande"),

    path("commandes/<int:pk>/envoyer/", views.envoyer_bon_livraison,
         name="envoyer_bon_livraison_email"),


    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('commande/<int:pk>/', views.detail_commande, name='detail_commande'),
    path('commande/<int:pk>/pdf/', views.export_commande_bon_pdf,
         name='export_commande_bon_pdf'),  # AJOUTEZ CETTE LIGNE
    path('commande/<int:pk>/appliquer-remise-commande/',
         views.appliquer_remise_commande, name='appliquer_remise_commande'),
    path('commande/<int:pk>/supprimer-remise-commande/',
         views.supprimer_remise_commande, name='supprimer_remise_commande'),
    path('commande/<int:pk>/dupliquer/',
         views.dupliquer_commande, name='dupliquer_commande'),
    path('commandes/export_pdf/', views.export_commandes_pdf,
         name="export_commandes_pdf"),


    # ... autres URLs ...


    path('factures/', views.liste_factures, name='liste_factures'),
    path('factures/facture-mensuelle/', views.facture_client_mois_pdf,
         name='facture_client_mois_pdf'),
    path('appliquer_remise/<int:client_id>/<str:mois_filtre>/',
         views.appliquer_remise, name='appliquer_remise'),
    path('parametres/',  views.parametres_application, name='parametres_app'),



    # path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/<int:client_id>/historique/',
         views.historique_factures_client, name='historique_factures_client'),

    path('factures/paiment/', views.liste_clientspai, name='liste_clientspai'),
    path('factures/paiment/<int:client_id>/',
         views.detail_clientpai, name='detail_clientpai'),
    path('factures/paiment/<int:client_id>/paiement/<str:mois>/',
         views.maj_paiement, name='maj_paiement'),

    path('statistiques/produits/', views.statistiques_ventes_produits,
         name='statistiques_ventes_produits'),
    path('utilisateur/ajouter/', views.ajouter_utilisateur,
         name='ajouter_utilisateur'),
    # path('utilisateur/<int:pk>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),


    path('Logout', views.logout_utilisateur, name='logout'),


    path('', views.login_utilisateur, name='login'),








    path('notifications/ajax/', views.notifications_ajax,
         name='notifications_ajax'),
    path('notifications/marquer-lue/', views.marquer_notification_lue,
         name='marquer_notification_lue'),
    path('notifications/marquer-toutes-lues/',
         views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('notifications/rafraichir/', views.rafraichir_notifications_commandes,
         name='rafraichir_notifications'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
