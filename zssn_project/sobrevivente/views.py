# ==============================================================================
# IMPORTS
# ==============================================================================
# Django
from django.db import transaction
from django.db.models import Count, Sum, F, FloatField

# Django Rest Framework
from rest_framework import viewsets, status, views
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

# Aplicação Local
from .models import Sobrevivente, Item, Inventario, ItemInventario, DenunciaInfeccao
from .serializers import SobreviventeSerializer, TrocaItemSerializer


# ==============================================================================
# VIEWS BASEADAS EM FUNÇÕES (FUNCTION-BASED VIEWS)
# ==============================================================================

@api_view(['GET', 'POST'])
def listar_criar_sobreviventes(request):
    """
    View para listar todos os sobreviventes (GET) ou criar um novo (POST).
    """
    if request.method == 'GET':
        sobreviventes = Sobrevivente.objects.all()
        serializer = SobreviventeSerializer(sobreviventes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SobreviventeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
def detalhe_sobrevivente(request, pk):
    """
    View para recuperar (GET) ou atualizar a localização de um sobrevivente (PUT/PATCH).
    """
    try:
        sobrevivente = Sobrevivente.objects.get(pk=pk)
    except Sobrevivente.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SobreviventeSerializer(sobrevivente)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # Permite apenas a atualização dos campos 'latitude' e 'longitude'
        data = {
            'latitude': request.data.get('latitude', sobrevivente.latitude),
            'longitude': request.data.get('longitude', sobrevivente.longitude)
        }
        serializer = SobreviventeSerializer(sobrevivente, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def reportar_infectado(request, sobrevivente_id):
    """
    View para reportar um sobrevivente como infectado.
    NOTA: Esta é uma das implementações de denúncia.
    """
    try:
        sobrevivente_reportado = Sobrevivente.objects.get(id=sobrevivente_id)
    except Sobrevivente.DoesNotExist:
        return Response({"erro": "O sobrevivente que você tentou reportar não existe."},
                        status=status.HTTP_404_NOT_FOUND)

    if sobrevivente_reportado.infectado:
        return Response({"mensagem": "Este sobrevivente já está marcado como infectado."},
                        status=status.HTTP_400_BAD_REQUEST)

    # CORREÇÃO: O nome do campo no modelo é 'reports', não 'reportes'.
    sobrevivente_reportado.reports += 1

    if sobrevivente_reportado.reports >= 3:
        sobrevivente_reportado.infectado = True

    sobrevivente_reportado.save()
    serializer = SobreviventeSerializer(sobrevivente_reportado)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def denunciar_infeccao(request, sobrevivente_id):
    """
    View alternativa para denunciar infecção.
    NOTA: Esta é outra implementação de denúncia, mantida conforme solicitado.
    """
    try:
        sobrevivente = Sobrevivente.objects.get(id=sobrevivente_id)
    except Sobrevivente.DoesNotExist:
        return Response({"erro": "Sobrevivente não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    reporter_id = request.data.get('reporter_id')
    if not reporter_id:
        # CORREÇÃO: A sintaxe do dicionário estava incorreta.
        return Response({'erro': "O ID do sobrevivente que reporta é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        reporter = Sobrevivente.objects.get(id=reporter_id)
    except Sobrevivente.DoesNotExist:
        return Response({"erro": "Sobrevivente que reporta não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if reporter.id == sobrevivente.id:
        return Response({"erro": "Um sobrevivente não pode denunciar a si mesmo."}, status=status.HTTP_400_BAD_REQUEST)

    # CORREÇÃO: O nome do campo no modelo é 'reports'.
    sobrevivente.reports += 1

    if sobrevivente.reports >= 3:
        sobrevivente.infectado = True

    sobrevivente.save()
    serializer = SobreviventeSerializer(sobrevivente)
    return Response(serializer.data)


# ==============================================================================
# VIEWS BASEADAS EM CLASSES (CLASS-BASED VIEWS)
# ==============================================================================

class SobreviventeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Sobreviventes e denúncias.
    """
    queryset = Sobrevivente.objects.all()
    serializer_class = SobreviventeSerializer

    def partial_update(self, request, *args, **kwargs):
        # CORREÇÃO: Corrigido erro de digitação 'sobrerivente' -> 'sobrevivente'.
        sobrevivente = self.get_object()
        if sobrevivente.infectado:
            return Response({"erro": "Não pode atualizar a localização de um sobrevivente infectado."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def denunciar_infeccao(self, request, pk=None):
        """
        Action para um sobrevivente denunciar outro.
        NOTA: Terceira implementação de denúncia, dentro de um ViewSet.
        """
        denunciado = self.get_object()
        # CORREÇÃO: Padronizado nome da variável.
        denunciante_id = request.data.get('denunciante_id')

        if not denunciante_id:
            # CORREÇÃO: A sintaxe do dicionário estava incorreta.
            return Response({'erro': "O ID do denunciante é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            denunciante = Sobrevivente.objects.get(pk=denunciante_id)
        except Sobrevivente.DoesNotExist:
            return Response({"erro": "Sobrevivente denunciante não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if denunciante.id == denunciado.id:
            return Response({"erro": "Um sobrevivente não pode denunciar a si mesmo."},
                            status=status.HTTP_400_BAD_REQUEST)

        # CORREÇÃO LÓGICA: O código abaixo estava indentado incorretamente e não seria executado.
        created, _ = DenunciaInfeccao.objects.get_or_create(denunciante=denunciante, denunciado=denunciado)

        if created:
            # CORREÇÃO LÓGICA: Verifica o total de denúncias contra o denunciado.
            total_denuncias = DenunciaInfeccao.objects.filter(denunciado=denunciado).count()
            if total_denuncias >= 3:
                denunciado.infectado = True
                denunciado.save()
                return Response(
                    {"mensagem": f"Denúncia registrada. O sobrevivente {denunciado.nome} foi marcado como infectado."})
            return Response({"mensagem": "Denúncia registrada com sucesso."})
        else:
            return Response({"mensagem": "Você já denunciou este sobrevivente."}, status=status.HTTP_400_BAD_REQUEST)


# COMENTÁRIO: Existem duas classes com o mesmo nome. Para evitar conflitos,
# renomeei-as para "...Completo" e "...Simples", mantendo ambas.
class TrocarItemViewSetCompleto(viewsets.ViewSet):
    """
    ViewSet com a lógica completa para troca de itens.
    """

    def create(self, request, *args, **kwargs):
        # CORREÇÃO: Renomeado de 'post' para 'create', que é o método correto para POST em ViewSets.
        id1 = request.data.get('sobrevivente1_id')
        id2 = request.data.get('sobrevivente2_id')
        itens1_data = request.data.get('itens_sobrevivente1')
        itens2_data = request.data.get('itens_sobrevivente2')

        try:
            sobrevivente1 = Sobrevivente.objects.get(id=id1)
            sobrevivente2 = Sobrevivente.objects.get(id=id2)

            if sobrevivente1.infectado or sobrevivente2.infectado:
                return Response({"erro": "Trocas envolvendo sobreviventes infectados não são permitidas."},
                                status=status.HTTP_400_BAD_REQUEST)

            pontos1 = self._calcular_pontos(itens1_data)
            pontos2 = self._calcular_pontos(itens2_data)

            if pontos1 != pontos2:
                return Response({"erro": "A soma dos pontos dos itens trocados deve ser igual."},
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # CORREÇÃO: Corrigido erro de digitação 'transferir_itebs'.
                self._transferir_itens(sobrevivente1, sobrevivente2, itens1_data)
                self._transferir_itens(sobrevivente2, sobrevivente1, itens2_data)

            return Response({"mensagem": "Troca realizada com sucesso!"}, status=status.HTTP_200_OK)
        except Sobrevivente.DoesNotExist:
            return Response({"erro": "Um dos sobreviventes não foi encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _calcular_pontos(self, itens_data):
        total_pontos = 0
        for item_data in itens_data:
            # CORREÇÃO: Acessando item pelo ID para mais segurança e performance.
            item = Item.objects.get(id=item_data['item_id'])
            total_pontos += item.pontos * item_data['quantidade']
        return total_pontos

    def _transferir_itens(self, doador, receptor, itens_data):
        # CORREÇÃO: Lógica ajustada para o modelo ManyToManyField com 'through'.
        inventario_doador = doador.inventario
        inventario_receptor = receptor.inventario

        for item_info in itens_data:
            item = Item.objects.get(id=item_info['item_id'])
            quantidade = item_info['quantidade']

            # Debita do doador
            item_no_inventario_doador = ItemInventario.objects.get(inventario=inventario_doador, item=item)
            if item_no_inventario_doador.quantidade < quantidade:
                raise ValueError(f"O sobrevivente {doador.nome} não possui {quantidade} unidades de {item.nome}.")

            item_no_inventario_doador.quantidade -= quantidade
            if item_no_inventario_doador.quantidade == 0:
                item_no_inventario_doador.delete()
            else:
                item_no_inventario_doador.save()

            # Credita ao receptor
            item_no_inventario_receptor, _ = ItemInventario.objects.get_or_create(inventario=inventario_receptor,
                                                                                  item=item)
            item_no_inventario_receptor.quantidade += quantidade
            item_no_inventario_receptor.save()


class TrocarItemViewSetSimples(viewsets.ViewSet):
    """
    ViewSet simples para troca de itens que apenas valida um serializer.
    """

    def create(self, request):
        serializer = TrocaItemSerializer(data=request.data)
        if serializer.is_valid():
            # NOTA: Este endpoint não realiza a troca, apenas valida os dados.
            return Response({"message": "Dados da troca são válidos!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelatoriosView(views.APIView):
    """
    View que gera os relatórios solicitados.
    """

    def get(self, request, *args, **kwargs):
        total_sobreviventes = Sobrevivente.objects.count()
        if total_sobreviventes == 0:
            return Response({"mensagem": "Não há sobreviventes cadastrados para gerar relatórios."})

        infectados_count = Sobrevivente.objects.filter(infectado=True).count()
        porc_infectados = (infectados_count / total_sobreviventes) * 100
        porc_nao_infectados = 100 - porc_infectados

        nao_infectados_count = total_sobreviventes - infectados_count
        media_itens = {}
        if nao_infectados_count > 0:
            itens = Item.objects.all()
            for item in itens:
                # CORREÇÃO: Lógica ajustada para o modelo ManyToManyField com 'through'.
                total_item = ItemInventario.objects.filter(
                    inventario__sobrevivente__infectado=False, item=item
                ).aggregate(total=Sum('quantidade'))['total'] or 0
                media_itens[f"media_de_{item.nome.lower()}"] = total_item / nao_infectados_count

        # CORREÇÃO: Lógica ajustada para o modelo ManyToManyField com 'through'.
        pontos_perdidos = ItemInventario.objects.filter(
            inventario__sobrevivente__infectado=True
        ).aggregate(
            total_pontos=Sum(F('quantidade') * F('item__pontos'), output_field=FloatField())
        )['total_pontos'] or 0

        relatorio = {
            "porcentagem_infectados": f"{porc_infectados:.2f}%",
            "porcentagem_nao_infectados": f"{porc_nao_infectados:.2f}%",
            "media_recursos_por_sobrevivente_nao_infectado": media_itens,
            "pontos_perdidos_devido_a_sobreviventes_infectados": pontos_perdidos
        }
        return Response(relatorio, status=status.HTTP_200_OK)