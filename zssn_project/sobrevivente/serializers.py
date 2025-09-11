from rest_framework import serializers
from .models import Sobrevivente, ItemInventario, ReporteInfeccao, TipoItem


class ItemInventarioSerializer(serializers.ModelSerializer):
    """Serializer para itens do inventário"""

    pontos_unitarios = serializers.SerializerMethodField()
    pontos_totais = serializers.SerializerMethodField()
    nome_item = serializers.SerializerMethodField()

    class Meta:
        model = ItemInventario
        fields = ['tipo_item', 'quantidade', 'pontos_unitarios', 'pontos_totais', 'nome_item']

    def get_pontos_unitarios(self, obj):
        """Retorna os pontos de uma unidade do item"""
        return obj.get_pontos_unitarios()

    def get_pontos_totais(self, obj):
        """Retorna os pontos totais do item"""
        return obj.calcular_pontos()

    def get_nome_item(self, obj):
        """Retorna o nome legível do item"""
        return obj.get_tipo_item_display()


class SobreviventeSerializer(serializers.ModelSerializer):
    """Serializer principal para sobreviventes"""

    inventario = ItemInventarioSerializer(many=True, read_only=True)
    total_pontos = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    total_reportes = serializers.SerializerMethodField()

    class Meta:
        model = Sobrevivente
        fields = [
            'id', 'nome', 'idade', 'sexo', 'latitude', 'longitude',
            'infectado', 'inventario', 'total_pontos', 'status',
            'total_reportes', 'data_criacao'
        ]
        read_only_fields = ['infectado', 'data_criacao']

    def get_total_pontos(self, obj):
        """Calcula o total de pontos do inventário"""
        return obj.calcular_pontos_inventario()

    def get_status(self, obj):
        """Retorna o status do sobrevivente"""
        return "INFECTADO" if obj.infectado else "SAUDÁVEL"

    def get_total_reportes(self, obj):
        """Retorna o número de reportes de infecção recebidos"""
        return obj.reportes_recebidos.count()


class SobreviventeCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de sobreviventes"""

    class Meta:
        model = Sobrevivente
        fields = ['nome', 'idade', 'sexo', 'latitude', 'longitude']

    def validate_idade(self, value):
        """Valida a idade do sobrevivente"""
        if value < 0 or value > 120:
            raise serializers.ValidationError("A idade deve estar entre 0 e 120 anos.")
        return value


class AtualizarLocalizacaoSerializer(serializers.Serializer):
    """Serializer para atualizar localização do sobrevivente"""

    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)


class ReporteInfeccaoSerializer(serializers.ModelSerializer):
    """Serializer para reportes de infecção"""

    class Meta:
        model = ReporteInfeccao
        fields = ['sobrevivente_reportado', 'data_reporte']
        read_only_fields = ['data_reporte']

    def validate(self, data):
        """Validações customizadas para o reporte"""
        request = self.context.get('request')
        sobrevivente_reportador_id = request.data.get('sobrevivente_reportador')

        if not sobrevivente_reportador_id:
            raise serializers.ValidationError("ID do sobrevivente reportador é obrigatório.")

        # Verifica se o sobrevivente não está tentando reportar a si mesmo
        if data['sobrevivente_reportado'].id == int(sobrevivente_reportador_id):
            raise serializers.ValidationError("Um sobrevivente não pode reportar a si mesmo.")

        # Verifica se já existe um reporte deste reportador para este sobrevivente
        if ReporteInfeccao.objects.filter(
                sobrevivente_reportado=data['sobrevivente_reportado'],
                sobrevivente_reportador_id=sobrevivente_reportador_id
        ).exists():
            raise serializers.ValidationError("Você já reportou este sobrevivente como infectado.")

        return data


class AdicionarItemSerializer(serializers.Serializer):
    """Serializer para adicionar itens ao inventário"""

    tipo_item = serializers.ChoiceField(choices=TipoItem.choices)
    quantidade = serializers.IntegerField(min_value=1)


class RemoverItemSerializer(serializers.Serializer):
    """Serializer para remover itens do inventário"""

    tipo_item = serializers.ChoiceField(choices=TipoItem.choices)
    quantidade = serializers.IntegerField(min_value=1)


class EscamboSerializer(serializers.Serializer):
    """Serializer para realizar escambo entre sobreviventes"""

    sobrevivente_destino_id = serializers.IntegerField()
    itens_oferecidos = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
    itens_desejados = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )

    def validate(self, data):
        """Valida se o escambo é justo (mesmo número de pontos)"""
        # Calcula pontos dos itens oferecidos
        pontos_oferecidos = 0
        for item in data['itens_oferecidos']:
            tipo_item = item.get('tipo_item')
            quantidade = item.get('quantidade', 0)
            pontos_oferecidos += quantidade * ItemInventario.PONTOS_ITENS.get(tipo_item, 0)

        # Calcula pontos dos itens desejados
        pontos_desejados = 0
        for item in data['itens_desejados']:
            tipo_item = item.get('tipo_item')
            quantidade = item.get('quantidade', 0)
            pontos_desejados += quantidade * ItemInventario.PONTOS_ITENS.get(tipo_item, 0)

        # Verifica se os pontos são iguais
        if pontos_oferecidos != pontos_desejados:
            raise serializers.ValidationError(
                f"O escambo deve ter saldo zero. "
                f"Oferecidos: {pontos_oferecidos} pontos, "
                f"Desejados: {pontos_desejados} pontos."
            )

        return data
