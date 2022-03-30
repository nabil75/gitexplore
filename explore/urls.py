"""explore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from explore import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index', views.index, name='index'),
    path('telecharger_csv', views.telecharger_csv, name='telecharger_csv'),
    path('telecharger_pdf', views.telecharger_pdf, name='telecharger_pdf'),
    path('preparer', views.preparer, name='preparer'),
    path('explorer', views.explorer, name='explorer'),
    #Ajax
    path('get_list_product', views.get_list_product, name='get_list_product'),
    path('get_info_product', views.get_info_product, name='get_info_product'),
    path('get_list_colonnes', views.get_list_colonnes, name='get_list_colonnes'),
    path('get_list_mots_cle', views.get_list_mots_cle, name='get_list_mots_cle'),
    path('get_overview', views.get_overview, name='get_overview'),
    path('get_values_colonne', views.get_values_colonne, name='get_values_colonne'),
    path('suppr_colonne', views.suppr_colonne, name='suppr_colonne')
]
