from rest_framework import serializers
from .models import  Sobrevivente, Item, Inventario

class SobreviventeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['nome', 'pontos']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('nome', 'pontos')

class InventarioSerializer(serializers.ModelSerializer):

    itens = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Inventario
        fields = ('id', 'sobrevivente', 'itens')


class SobreviventeInventarioSerializer(serializers.ModelSerializer):

    inventario = InventarioSerializer(many=True, read_only=True)

    class Meta:
        model = Sobrevivente
        fields = ['id', 'nome', 'idade', 'sexo', 'latitude', 'longitude', 'infectado', 'inventario']
        read_only_fields = ['inventario', 'infectado']

    def create(self, validated_data):

        sobrevivente = Sobrevivente.objects.create(**validated_data)
        itens = Item.objects.all()

        for item in itens:
            Inventario.objects.create(sobrevivente=sobrevivente, item=item, quantidade=0)
        return sobrevivente

class TrocaItemSerializer(serializers.Serializer):
    sobrevivente1_id = serializers.IntegerField()
    itens_sobrevivente1 = serializers.ListField(child=serializers.DictField())
    sobrevivente2_id = serializers.IntegerField()
    itens_sobrevivente2 = serializers.ListField(child=serializers.DictField())
    def validate(self, data):
        return data

