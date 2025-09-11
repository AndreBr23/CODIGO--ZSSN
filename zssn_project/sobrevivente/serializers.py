from rest_framework import serializers
from .models import Sobrevivente, Item, ItemInventario

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['nome', 'pontos']

class ItemInventarioSerializer(serializers.ModelSerializer):
    # Usamos um serializer aninhado para mostrar os detalhes do item
    item = ItemSerializer(read_only=True)

    class Meta:
        model = ItemInventario
        fields = ['item', 'quantidade']

class SobreviventeSerializer(serializers.ModelSerializer):
    # Usamos a fonte correta para buscar os itens do inventário
    inventario = ItemInventarioSerializer(many=True, read_only=True, source='inventario.iteminventario_set')

    class Meta:
        model = Sobrevivente
        fields = ['id', 'nome', 'idade', 'sexo', 'latitude', 'longitude', 'infectado', 'inventario']
        read_only_fields = ['infectado'] # O status de infectado só deve ser alterado pelo sistema

class TrocaItemSerializer(serializers.Serializer):
    # Serializer para validar os dados de entrada da troca
    sobrevivente1_id = serializers.IntegerField()
    itens_sobrevivente1 = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        )
    )
    sobrevivente2_id = serializers.IntegerField()
    itens_sobrevivente2 = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        )
    )