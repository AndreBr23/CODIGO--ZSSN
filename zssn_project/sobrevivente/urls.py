from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para os ViewSets
router = DefaultRouter()
router.register(r'sobreviventes-vs', views.SobreviventeViewSet, basename='sobrevivente-vs')
router.register(r'troca-completa', views.TrocarItemViewSetCompleto, basename='troca-completa')
router.register(r'troca-simples', views.TrocarItemViewSetSimples, basename='troca-simples')

# URLs para as Views baseadas em função
urlpatterns = [
    # Rotas para as funções
    path('sobreviventes/', views.listar_criar_sobreviventes, name='fbv-listar-criar'),
    path('sobreviventes/<int:pk>/', views.detalhe_sobrevivente, name='fbv-detalhe'),
    path('sobreviventes/<int:sobrevivente_id>/reportar-infectado/', views.reportar_infectado, name='fbv-reportar'),
    path('sobreviventes/<int:sobrevivente_id>/denunciar-infeccao/', views.denunciar_infeccao, name='fbv-denunciar'),

    # Rota para a View de Relatórios
    path('relatorios/', views.RelatoriosView.as_view(), name='relatorios'),

    # Inclui as rotas geradas pelo router para os ViewSets
    path('sobrevivente/', include(router.urls)),
]