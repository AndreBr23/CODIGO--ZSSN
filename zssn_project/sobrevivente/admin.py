from django.contrib import admin
from .models import Sobrevivente, Item, Inventario, DenunciaInfeccao

class InventarioInline(admin.TabularInline):
    model = Inventario
    extra = 1

@admin.register(Sobrevivente)
class SobreviventeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'idade', 'sexo', 'latitude', 'longitude', 'infectado')
    list_filter = ('infectado', 'sexo')
    search_fields = ('nome',)
    inlines = [InventarioInline]
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pontos')
    search_fields = ('nome',)
@admin.register(DenunciaInfeccao)
class DenunciaInfeccaoAdmin(admin.ModelAdmin):
    list_dsplay = ('denunciante', 'denunciado')
    autocomplete_fields = ('denunciante', 'denunciado')
# Register your models here.
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('sobrevivente', 'item', 'quantidade')
    list_filter = ('item',)
    search_fields = ('sobrevivente', 'item', 'nome')