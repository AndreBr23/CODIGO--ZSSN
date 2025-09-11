from django.contrib import admin
from .models import Sobrevivente, Item, Inventario, ItemInventario


class ItemInventarioInline(admin.TabularInline):
    model = ItemInventario
    extra = 1
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pontos')
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('sobrevivente',)
    inlines = [ItemInventarioInline]
@admin.register(Sobrevivente)
class SobreviventeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'idade', 'sexo', 'infectado', 'reports')
    list_filter = ('infectado', 'sexo')
@admin.register(ItemInventario)
class ItemInventarioAdmin(admin.ModelAdmin):
    list_display = ('inventario', 'item', 'quantidade')