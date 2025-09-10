from django.db import transaction
from django.db.models import Count, Sum, F
from django.db.models.fields import FloatField
from rest_framework import viewsets, status, views
from rest_framework.response import  Response
from rest_framework.decorators import  action
from .models import  Sobrevivente, Item, Inventario, DenunciaInfeccao
from .serializers import  SobreviventeSerializer

class SobreviventeViewSet(viewsets.ModelViewSet):
    queryset = Sobrevivente.objects.all()
    serializer_class = SobreviventeSerializer

    def partial_update(self, request, *args, **kwargs):
        sobrerivente = self.get_object()
        if sobrerivente.infectado:
            return Response({"erro": "nao pode atualizar a localizacao estando infectado"},status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def denunciar_infeccao(self, request, pk=None):
        denunciado = self.get_object()
        denuciante_id = request.data.get('denunciante_id')

        if not denuciante_id:
            return Response({'erro':"sobrevivente deve declara a ID", status:status.HTTP_400_BAD_REQUEST})
        try:
            denunciante = Sobrevivente.objects.get(pk=denuciante_id)
        except Sobrevivente.DoesNotExist:
            return Response({"erro": "sobrevivente nao encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if denuciante_id == denunciado.id:
            return Response({"erro" : "sobrevivente nao pode denunciar si mesmo"}, status=status.HTTP_400_BAD_REQUEST)

            created = DenunciaInfeccao.objects.get_or_create(denunciante=denunciante, denunciado=denunciado)
        if created:
            if denunciante.denuncias_recebidas.count() >= 3:
                denunciante.infectado = True
                denunciante.save()
                return Response({"Mensagem" : f"Denuncia registrada. sobrevivente {denunciado.nome} foi infectado e marcado"})
            return Response({"Mensagem" : "denuncia registrada com sucesso"})
        else:
            return Response({"Mensagem" : "denuncia ja registrada"})
class TrocarItemViewSet(viewsets.ModelViewSet):
    def post(self, request, *args, **kwargs):
        id1 = request.data.get('sobrevivente1_id')
        id2 = request.data.get('sobrevivente2_id')
        itens1_data = request.data.get('troca1')
        itens2_data = request.data.get('troca2')

        try:
            sobrevivente1 = Sobrevivente.objects.get(id=id1)
            sobrevivente2 = Sobrevivente.objects.get(id=id2)

            if sobrevivente1.infectado or sobrevivente2.infectado:
                return Response({"erro": "nao pode trocar itens infectados"},status=status.HTTP_400_BAD_REQUEST)

            pontos1 = self.calcular_pontos(itens1_data)
            pontos2 = self.calcular_pontos(itens2_data)

            if pontos1 != pontos2:
                return Response({"erro": "pontos de itens devem ser iguais"},status=status.HTTP_400_BAD_REQUEST)
            """
            estou usnado trasaciton para integridade de items e dados
            """
            with transaction.atomic():
                self.transferir_itens(sobrevivente1, sobrevivente2, itens1_data)
                self.transferir_itebs(sobrevivente2, sobrevivente1, itens2_data)
            return Response({"Mensagem": "troca realizada com sucesso"}, status=status.HTTP_200_OK)
        except Sobrevivente.DoesNotExist:
            return Response({"erro": "sobrevivente nao encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        """
        Estou criando a o calculo de media de pontos
        """

    def calcular_pontos(self, itens_data):
        total_pontos = 0
        for item_data in itens_data:
            item = Item.objects.get(nome=item_data['nome'])
            total_pontos += item.pontos * item_data['quantidade']
        return total_pontos
    def transferir_itens(self, sobrevivente1, sobrevivente2, doador, receptor, itens_data):
        for item_data in itens_data:
            item = Item.objects.get(nome=item_data['nome'])
            quantidade = item_data['quantidade']

            """
            sistema para verificar se existe uma quantidade correrta para o mesmo
            """
            inventario_doador = Inventario.objects.get(sobrevivente=doador, item=item)
            if inventario_doador.quantidade < quantidade:
                raise ValueError(f"sobrevivente {doador.nome} nao tem o item {item.nome} suficiente")

            inventario_doador.quantidade -= quantidade
            inventario_doador.save()
            inventario_recebedor = Inventario.objects.get_or_create(sobrevivente=receptor, item=item)[0]
            inventario_recebedor.quantidade += quantidade
            inventario_recebedor.save()

class RelatoriosView(views.APIView):
    """
       View que gera os relatórios solicitados.
       """

    def get(self, request, *args, **kwargs):
        total_sobreviventes = Sobrevivente.objects.count()
        if total_sobreviventes == 0:
            return Response({"mensagem": "Não há sobreviventes cadastrados para gerar relatórios."})

        # Relatório de Infectados e Não Infectados
        infectados_count = Sobrevivente.objects.filter(infectado=True).count()
        porc_infectados = (infectados_count / total_sobreviventes) * 100
        porc_nao_infectados = 100 - porc_infectados

        # Média de itens por sobrevivente (apenas não infectados)
        nao_infectados = Sobrevivente.objects.filter(infectado=False)
        nao_infectados_count = nao_infectados.count()

        media_itens = {}
        if nao_infectados_count > 0:
            itens = Item.objects.all()
            for item in itens:
                total_item = Inventario.objects.filter(sobrevivente__in=nao_infectados, item=item).aggregate(
                    total=Sum('quantidade'))['total'] or 0
                media_itens[f"media_de_{item.nome.lower()}"] = total_item / nao_infectados_count

        # Pontos perdidos por usuários infectados
        pontos_perdidos = Inventario.objects.filter(sobrevivente__infectado=True).aggregate(
            total_pontos=Sum(F('quantidade') * F('item__pontos'), output_field=FloatField())
        )['total_pontos'] or 0

        relatorio = {
            "porcentagem_infectados": f"{porc_infectados:.2f}%",
            "porcentagem_nao_infectados": f"{porc_nao_infectados:.2f}%",
            "media_recursos_por_sobrevivente_nao_infectado": media_itens,
            "pontos_perdidos_devido_a_sobreviventes_infectados": pontos_perdidos
        }

        return Response(relatorio, status=status.HTTP_200_OK)
