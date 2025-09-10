from django.db import migrations

def popular_itens_iniciais(apps, schema_editor):
    Item = apps.get_model('sobrevivente', 'Item')
    itens = [
        {'nome': 'Agua', 'pontos': 4},
        {'nome': 'Comida', 'pontos': 3},
        {'nome': 'Remedio', 'pontos': 2},
        {'nome': 'Municao', 'pontos': 1}
    ]

    for item_data in itens:
        Item.objects.create(**item_data)

class Migration(migrations.Migration):

    dependencies = [
        ('sobrevivente', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(popular_itens_iniciais)
    ]