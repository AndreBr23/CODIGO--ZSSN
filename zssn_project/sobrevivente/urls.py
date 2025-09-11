from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SobreviventeViewSet

# Configuração do roteador do Django REST Framework
router = DefaultRouter()
router.register(r'sobreviventes', SobreviventeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
