from django.db import models

class Sobrevivente(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.PositiveIntegerField()
    sexo = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino')])
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    infectado = models.BooleanField(default=False)
    reports = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome
class Item(models.Model):
    nome = models.CharField(max_length=100)
    pontos = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.nome} ({self.pontos} pontos)"
class Inventario(models.Model):
    sobrevivente = models.OneToOneField(Sobrevivente, on_delete=models.CASCADE)
    itens = models.ManyToManyField(Item, through='ItemInventario')

    def __str__(self):
        return f"Inventário de {self.sobrevivente.nome}"
class ItemInventario(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = ('item', 'inventario')

class DenunciaInfeccao(models.Model):
    denunciante = models.ForeignKey(Sobrevivente, on_delete=models.CASCADE, related_name='denuncias_feitas')
    denunciado = models.ForeignKey(Sobrevivente, on_delete=models.CASCADE, related_name='denuncias_recebidas')
    class Meta:
        unique_together = ('denunciante', 'denunciado')
    def __str__(self):
        return f"{self.denunciante.nome} denuncioi {self.denunciado.nome}"


    """
    Usando os campos do Django (CharField, IntegerField, etc.) para poder definir as colunas no banco de dados criado

    ForeignKey cria uma relação entre duas tabelas.

    on_delete=models.CASCADE significa que se um sobrevivente for deletado, todos os seus itens de inventário e denúncias também serão.

    related_name nos ajuda a fazer buscas inversas .

    unique_together cria uma restrição para evitar dados duplicados.
    """

