from django.contrib import admin
from .models import Sobrevivente, ItemInventario, ReporteInfeccao


@admin.register(Sobrevivente)
class SobreviventeAdmin(admin.ModelAdmin):
    """Configuração do admin para Sobreviventes"""

    list_display = ['nome', 'idade', 'sexo', 'infectado', 'data_criacao']
    list_filter = ['infectado', 'sexo', 'data_criacao']
    search_fields = ['nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']

    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'idade', 'sexo')
        }),
        ('Localização', {
            'fields': ('latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('infectado',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemInventario)
class ItemInventarioAdmin(admin.ModelAdmin):
    """Configuração do admin para Itens do Inventário"""

    list_display = ['sobrevivente', 'tipo_item', 'quantidade', 'calcular_pontos']
    list_filter = ['tipo_item', 'sobrevivente__infectado']
    search_fields = ['sobrevivente__nome']


@admin.register(ReporteInfeccao)
class ReporteInfeccaoAdmin(admin.ModelAdmin):
    """Configuração do admin para Reportes de Infecção"""

    list_display = ['sobrevivente_reportado', 'sobrevivente_reportador', 'data_reporte']
    list_filter = ['data_reporte']
    search_fields = ['sobrevivente_reportado__nome', 'sobrevivente_reportador__nome']
    readonly_fields = ['data_reporte']
