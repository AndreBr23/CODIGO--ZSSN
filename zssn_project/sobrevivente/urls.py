from django.urls import path, include
from rest_framework import views
from rest_framework.routers import DefaultRouter
from .views import  SobreviventeViewSet, TrocarItemViewSet, RelatoriosView
from .import views


router = DefaultRouter()
router.register(r'trocar-itens', views.TrocarItemViewSet, basename='trocar_item')
urlpatterns = [
    # Suas views normais (não-ViewSets)
    path('', views.listar_criar_sobreviventes, name="listar_criar_sobreviventes"),
    path('<int:pk>/', views.detalhe_sobrevivente, name="detalhe_sobrevivente"),
    path('<int:sobrevivente_id>/reportar/', views.reportar_infectado, name="reportar_infectado"),
    path('', include(router.urls)),
    pat
]