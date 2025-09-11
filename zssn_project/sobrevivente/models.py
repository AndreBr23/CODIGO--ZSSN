from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TipoItem(models.TextChoices):
    """Tipos de itens disponíveis no sistema"""
    AGUA = 'agua', 'Água'
    COMIDA = 'comida', 'Comida'
    MEDICAMENTO = 'medicamento', 'Medicamento'
    MUNICAO = 'municao', 'Munição'


class SexoChoices(models.TextChoices):
    """Opções de sexo para os sobreviventes"""
    MASCULINO = 'M', 'Masculino'
    FEMININO = 'F', 'Feminino'
    OUTRO = 'O', 'Outro'


class Sobreviventes(models.Model):
    """Modelo que representa um sobrevivente no sistema"""

    nome = models.CharField(max_length=100, verbose_name="Nome do Sobrevivente")
    idade = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        verbose_name="Idade"
    )
    sexo = models.CharField(
        max_length=1,
        choices=SexoChoices.choices,
        verbose_name="Sexo"
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Latitude da Localização"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Longitude da Localização"
    )
    infectado = models.BooleanField(default=False, verbose_name="Está Infectado?")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Sobrevivente"
        verbose_name_plural = "Sobreviventes"
        ordering = ['-data_criacao']

    def __str__(self):
        status = "INFECTADO" if self.infectado else "SAUDÁVEL"
        return f"{self.nome} ({status})"

    def pode_fazer_escambo(self):
        """Verifica se o sobrevivente pode participar de escambos"""
        return not self.infectado

    def calcular_pontos_inventario(self):
        """Calcula o total de pontos do inventário do sobrevivente"""
        if self.infectado:
            return 0

        total_pontos = 0
        for item in self.inventario.all():
            total_pontos += item.calcular_pontos()
        return total_pontos


class ReporteInfeccao(models.Model):
    """Modelo para registrar reportes de infecção entre sobreviventes"""

    sobrevivente_reportado = models.ForeignKey(
        Sobreviventes,
        on_delete=models.CASCADE,
        related_name='reportes_recebidos',
        verbose_name="Sobrevivente Reportado"
    )
    sobrevivente_reportador = models.ForeignKey(
        Sobreviventes,
        on_delete=models.CASCADE,
        related_name='reportes_feitos',
        verbose_name="Sobrevivente que Reportou"
    )
    data_reporte = models.DateTimeField(auto_now_add=True, verbose_name="Data do Reporte")

    class Meta:
        verbose_name = "Reporte de Infecção"
        verbose_name_plural = "Reportes de Infecção"
        unique_together = ['sobrevivente_reportado', 'sobrevivente_reportador']

    def __str__(self):
        return f"{self.sobrevivente_reportador.nome} reportou {self.sobrevivente_reportado.nome}"


class ItemInventario(models.Model):
    """Modelo que representa itens no inventário de um sobrevivente"""

    # Tabela de pontos dos itens
    PONTOS_ITENS = {
        TipoItem.AGUA: 4,
        TipoItem.COMIDA: 3,
        TipoItem.MEDICAMENTO: 2,
        TipoItem.MUNICAO: 1,
    }

    sobrevivente = models.ForeignKey(
        Sobreviventes,
        on_delete=models.CASCADE,
        related_name='inventario',
        verbose_name="Sobrevivente"
    )
    tipo_item = models.CharField(
        max_length=20,
        choices=TipoItem.choices,
        verbose_name="Tipo do Item"
    )
    quantidade = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Quantidade"
    )

    class Meta:
        verbose_name = "Item do Inventário"
        verbose_name_plural = "Itens do Inventário"
        unique_together = ['sobrevivente', 'tipo_item']

    def __str__(self):
        return f"{self.sobrevivente.nome} - {self.quantidade}x {self.get_tipo_item_display()}"

    def calcular_pontos(self):
        """Calcula os pontos totais deste item"""
        return self.quantidade * self.PONTOS_ITENS[self.tipo_item]

    def get_pontos_unitarios(self):
        """Retorna os pontos de uma unidade deste item"""
        return self.PONTOS_ITENS[self.tipo_item]
