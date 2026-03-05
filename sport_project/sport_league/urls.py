from django.urls import path
from . import views

urlpatterns = [
    # Esasy sahypa
    path('', views.bas_sahypa, name='bas_sahypa'),
    
    # Oýunçy bilen baglanyşykly URL'ler
    path('oyuncular/', views.oyuncu_list, name='oyuncu_list'),
    path('oyuncu/<int:pk>/', views.oyuncu_detail, name='oyuncu_detail'),
    
    # Ýaryş bilen baglanyşykly URL'ler
    path('yaryslar/', views.yarys_list, name='yarys_list'),
    path('yarys/<int:pk>/', views.yarys_detail, name='yarys_detail'),
    
    # Fakultet bilen baglanyşykly URL'ler
    path('fakultetler/', views.fakultet_list, name='fakultet_list'),
    path('fakultet/<int:pk>/', views.fakultet_detail, name='fakultet_detail'),
    
    # Statistika we reýting
    path('statistika/', views.statistika, name='statistika'),
    path('reyting/', views.reyting, name='reyting'),
    
    # Goşmaça statistika we hasabatlar (isleýän bolsaňyz)
    # path('hasabat/', views.hasabat, name='hasabat'),
    # path('export/oyuncular/', views.export_oyuncular, name='export_oyuncular'),
]