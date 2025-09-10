from django.db import models

class Sobrevivente(models.Model):

    """
     irei definiar os dados do sobrevivente
    """

    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    sexo = models.CharField(max_length=1, choices=(('M', 'Masculino'), ('F', 'Feminino')))
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    infectado = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Item(models.Model):

    """
    aqui irei criar como o sistema de Item deve seguir
    """
    nome = models.CharField(max_length=50, unique=True)
    pontos = models.IntegerField()
    def __str__(self):
        return f"{self.nome} ({self.pontos} pontos)"


class Inventario(models.Model):

    """
    criar sistema de Inventario ligado ao sobrevivente
    """
    denunciante = models.ForeignKey(Sobrevivente, on_delete=models.CASCADE , related_name='denuncias_feitas')
    denunciado = models.ForeignKey(Sobrevivente, on_delete=models.CASCADE , related_name='denuncias_recebidas')

    class Meta:
        """
        garante que seja feito uma unica vez a deunincia gracas a funcao unique_together
        """
        unique_together = ('denunciante', 'denunciado')

    def __str__(self):
        return f"{self.denunciante.nome} denunciou {self.denunciado.nome}"

    """
    Usando os campos do Django (CharField, IntegerField, etc.) para poder definir as colunas no banco de dados criado

    ForeignKey cria uma relação entre duas tabelas.

    on_delete=models.CASCADE significa que se um sobrevivente for deletado, todos os seus itens de inventário e denúncias também serão.

    related_name nos ajuda a fazer buscas inversas .

    unique_together cria uma restrição para evitar dados duplicados.
    """

