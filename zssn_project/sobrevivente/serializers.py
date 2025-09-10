from rest_framework import serializers
from .models import  Sobrevivente, Item, Inventario

class SobreviventeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['nome', 'pontos']

class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = ['item', 'quantidade']

class SobreviventeInventarioSerializer(serializers.ModelSerializer):

    inventario = InventarioSerializer(many=True, read_only=True)

    class Meta:
        model = Sobrevivente
        fields = ['id', 'nome', 'idade', 'sexo', 'latitude', 'longitude', 'infectado', 'inventario']
        read_only_fields = ['inventario', 'infectado']

    def create(self, validated_data):

        sobrevivente = sobrevivente.objects.create(**validated_data)
        itens = Item.objects.all()

        for item in itens:
            Inventario.objects.create(sobrevivente=sobrevivente, item=item, quantidade=0)
        return sobrevivente
