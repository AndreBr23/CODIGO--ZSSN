from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Count, Avg, Sum
from .models import Sobrevivente, ItemInventario, ReporteInfeccao, TipoItem
from .serializers import (
    SobreviventeSerializer, SobreviventeCreateSerializer,
    AtualizarLocalizacaoSerializer, ReporteInfeccaoSerializer,
    AdicionarItemSerializer, RemoverItemSerializer, EscamboSerializer
)


class SobreviventeViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar sobreviventes"""

    queryset = Sobrevivente.objects.all()

    def get_serializer_class(self):
        """Retorna o serializer apropriado para cada ação"""
        if self.action == 'create':
            return SobreviventeCreateSerializer
        return SobreviventeSerializer

    def get_queryset(self):
        """Filtra sobreviventes não infectados para listagem"""
        if self.action == 'list':
            return Sobrevivente.objects.filter(infectado=False)
        return Sobrevivente.objects.all()

    @action(detail=True, methods=['patch'])
    def atualizar_localizacao(self, request, pk=None):
        """Atualiza a localização de um sobrevivente"""
        sobrevivente = self.get_object()

        if sobrevivente.infectado:
            return Response(
                {'erro': 'Sobreviventes infectados não podem atualizar sua localização.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AtualizarLocalizacaoSerializer(data=request.data)
        if serializer.is_valid():
            sobrevivente.latitude = serializer.validated_data['latitude']
            sobrevivente.longitude = serializer.validated_data['longitude']
            sobrevivente.save()

            return Response({
                'mensagem': 'Localização atualizada com sucesso!',
                'nova_latitude': sobrevivente.latitude,
                'nova_longitude': sobrevivente.longitude
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reportar_infeccao(self, request, pk=None):
        """Reporta um sobrevivente como infectado"""
        sobrevivente_reportado = self.get_object()

        # Adiciona o ID do sobrevivente reportador aos dados
        data = request.data.copy()
        data['sobrevivente_reportado'] = sobrevivente_reportado.id

        serializer = ReporteInfeccaoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            # Verifica se o sobrevivente reportador existe
            try:
                sobrevivente_reportador = Sobrevivente.objects.get(
                    id=request.data.get('sobrevivente_reportador')
                )
            except Sobrevivente.DoesNotExist:
                return Response(
                    {'erro': 'Sobrevivente reportador não encontrado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cria o reporte
            ReporteInfeccao.objects.create(
                sobrevivente_reportado=sobrevivente_reportado,
                sobrevivente_reportador=sobrevivente_reportador
            )

            # Verifica se o sobrevivente deve ser marcado como infectado (3+ reportes)
            total_reportes = sobrevivente_reportado.reportes_recebidos.count()
            if total_reportes >= 3 and not sobrevivente_reportado.infectado:
                sobrevivente_reportado.infectado = True
                sobrevivente_reportado.save()

                return Response({
                    'mensagem': f'{sobrevivente_reportado.nome} foi marcado como INFECTADO após {total_reportes} reportes.',
                    'total_reportes': total_reportes,
                    'status': 'INFECTADO'
                })

            return Response({
                'mensagem': f'Reporte registrado com sucesso. Total de reportes: {total_reportes}',
                'total_reportes': total_reportes,
                'status': 'SAUDÁVEL'
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def adicionar_item(self, request, pk=None):
        """Adiciona itens ao inventário do sobrevivente"""
        sobrevivente = self.get_object()

        if sobrevivente.infectado:
            return Response(
                {'erro': 'Sobreviventes infectados não podem manipular seu inventário.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AdicionarItemSerializer(data=request.data)
        if serializer.is_valid():
            tipo_item = serializer.validated_data['tipo_item']
            quantidade = serializer.validated_data['quantidade']

            # Busca ou cria o item no inventário
            item, created = ItemInventario.objects.get_or_create(
                sobrevivente=sobrevivente,
                tipo_item=tipo_item,
                defaults={'quantidade': 0}
            )

            item.quantidade += quantidade
            item.save()

            return Response({
                'mensagem': f'{quantidade}x {item.get_tipo_item_display()} adicionado(s) ao inventário.',
                'item': tipo_item,
                'quantidade_total': item.quantidade,
                'pontos_totais': item.calcular_pontos()
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remover_item(self, request, pk=None):
        """Remove itens do inventário do sobrevivente"""
        sobrevivente = self.get_object()

        if sobrevivente.infectado:
            return Response(
                {'erro': 'Sobreviventes infectados não podem manipular seu inventário.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RemoverItemSerializer(data=request.data)
        if serializer.is_valid():
            tipo_item = serializer.validated_data['tipo_item']
            quantidade = serializer.validated_data['quantidade']

            try:
                item = ItemInventario.objects.get(
                    sobrevivente=sobrevivente,
                    tipo_item=tipo_item
                )
            except ItemInventario.DoesNotExist:
                return Response(
                    {'erro': f'Você não possui {TipoItem(tipo_item).label} no inventário.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if item.quantidade < quantidade:
                return Response(
                    {
                        'erro': f'Quantidade insuficiente. Você possui apenas {item.quantidade}x {item.get_tipo_item_display()}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantidade -= quantidade
            if item.quantidade == 0:
                item.delete()
                return Response({
                    'mensagem': f'{quantidade}x {TipoItem(tipo_item).label} removido(s). Item removido do inventário.',
                    'item': tipo_item,
                    'quantidade_restante': 0
                })
            else:
                item.save()
                return Response({
                    'mensagem': f'{quantidade}x {TipoItem(tipo_item).label} removido(s) do inventário.',
                    'item': tipo_item,
                    'quantidade_restante': item.quantidade,
                    'pontos_restantes': item.calcular_pontos()
                })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def escambo(self, request, pk=None):
        """Realiza escambo entre dois sobreviventes"""
        sobrevivente_origem = self.get_object()

        if sobrevivente_origem.infectado:
            return Response(
                {'erro': 'Sobreviventes infectados não podem realizar escambo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EscamboSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sobrevivente_destino = Sobrevivente.objects.get(
                    id=serializer.validated_data['sobrevivente_destino_id']
                )
            except Sobrevivente.DoesNotExist:
                return Response(
                    {'erro': 'Sobrevivente de destino não encontrado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if sobrevivente_destino.infectado:
                return Response(
                    {'erro': 'Não é possível fazer escambo com sobreviventes infectados.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if sobrevivente_origem.id == sobrevivente_destino.id:
                return Response(
                    {'erro': 'Não é possível fazer escambo consigo mesmo.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Realiza o escambo em uma transação
            with transaction.atomic():
                # Remove itens do sobrevivente origem e adiciona ao destino
                for item_data in serializer.validated_data['itens_oferecidos']:
                    tipo_item = item_data['tipo_item']
                    quantidade = item_data['quantidade']

                    # Remove do origem
                    try:
                        item_origem = ItemInventario.objects.get(
                            sobrevivente=sobrevivente_origem,
                            tipo_item=tipo_item
                        )
                        if item_origem.quantidade < quantidade:
                            raise ValueError(f'Quantidade insuficiente de {TipoItem(tipo_item).label}')

                        item_origem.quantidade -= quantidade
                        if item_origem.quantidade == 0:
                            item_origem.delete()
                        else:
                            item_origem.save()
                    except ItemInventario.DoesNotExist:
                        raise ValueError(f'Você não possui {TipoItem(tipo_item).label} no inventário')

                    # Adiciona ao destino
                    item_destino, created = ItemInventario.objects.get_or_create(
                        sobrevivente=sobrevivente_destino,
                        tipo_item=tipo_item,
                        defaults={'quantidade': 0}
                    )
                    item_destino.quantidade += quantidade
                    item_destino.save()

                # Remove itens do sobrevivente destino e adiciona ao origem
                for item_data in serializer.validated_data['itens_desejados']:
                    tipo_item = item_data['tipo_item']
                    quantidade = item_data['quantidade']

                    # Remove do destino
                    try:
                        item_destino = ItemInventario.objects.get(
                            sobrevivente=sobrevivente_destino,
                            tipo_item=tipo_item
                        )
                        if item_destino.quantidade < quantidade:
                            raise ValueError(
                                f'{sobrevivente_destino.nome} não possui quantidade suficiente de {TipoItem(tipo_item).label}')

                        item_destino.quantidade -= quantidade
                        if item_destino.quantidade == 0:
                            item_destino.delete()
                        else:
                            item_destino.save()
                    except ItemInventario.DoesNotExist:
                        raise ValueError(
                            f'{sobrevivente_destino.nome} não possui {TipoItem(tipo_item).label} no inventário')

                    # Adiciona ao origem
                    item_origem, created = ItemInventario.objects.get_or_create(
                        sobrevivente=sobrevivente_origem,
                        tipo_item=tipo_item,
                        defaults={'quantidade': 0}
                    )
                    item_origem.quantidade += quantidade
                    item_origem.save()

            return Response({
                'mensagem': f'Escambo realizado com sucesso entre {sobrevivente_origem.nome} e {sobrevivente_destino.nome}!',
                'sobrevivente_origem': sobrevivente_origem.nome,
                'sobrevivente_destino': sobrevivente_destino.nome,
                'itens_oferecidos': serializer.validated_data['itens_oferecidos'],
                'itens_recebidos': serializer.validated_data['itens_desejados']
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def relatorios(self, request):
        """Gera relatórios estatísticos do sistema"""

        # Contadores básicos
        total_sobreviventes = Sobrevivente.objects.count()
        sobreviventes_infectados = Sobrevivente.objects.filter(infectado=True).count()
        sobreviventes_saudaveis = total_sobreviventes - sobreviventes_infectados

        # Calcula porcentagens
        if total_sobreviventes > 0:
            porcentagem_infectados = (sobreviventes_infectados / total_sobreviventes) * 100
            porcentagem_saudaveis = (sobreviventes_saudaveis / total_sobreviventes) * 100
        else:
            porcentagem_infectados = 0
            porcentagem_saudaveis = 0

        # Calcula médias de itens por usuário (apenas sobreviventes saudáveis)
        medias_itens = {}
        for tipo_item, nome_item in TipoItem.choices:
            if sobreviventes_saudaveis > 0:
                total_item = ItemInventario.objects.filter(
                    sobrevivente__infectado=False,
                    tipo_item=tipo_item
                ).aggregate(total=Sum('quantidade'))['total'] or 0

                media = total_item / sobreviventes_saudaveis
            else:
                media = 0

            medias_itens[f'media_{tipo_item}_por_usuario'] = round(media, 2)

        # Calcula pontos perdidos por usuários infectados
        pontos_perdidos = 0
        sobreviventes_infectados_obj = Sobrevivente.objects.filter(infectado=True)
        for sobrevivente in sobreviventes_infectados_obj:
            for item in sobrevivente.inventario.all():
                pontos_perdidos += item.calcular_pontos()

        relatorio = {
            'resumo_geral': {
                'total_sobreviventes': total_sobreviventes,
                'sobreviventes_saudaveis': sobreviventes_saudaveis,
                'sobreviventes_infectados': sobreviventes_infectados,
            },
            'porcentagens': {
                'porcentagem_infectados': round(porcentagem_infectados, 2),
                'porcentagem_nao_infectados': round(porcentagem_saudaveis, 2),
            },
            'medias_itens': medias_itens,
            'pontos_perdidos_infectados': pontos_perdidos,
            'observacoes': {
                'nota_1': 'Apenas sobreviventes saudáveis são considerados nos cálculos de média.',
                'nota_2': 'Pontos perdidos referem-se aos itens de sobreviventes infectados que ficaram inacessíveis.',
                'nota_3': 'Sobreviventes infectados não aparecem na listagem principal.'
            }
        }

        return Response(relatorio)
