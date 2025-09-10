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



