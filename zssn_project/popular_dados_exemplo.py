#!/usr/bin/env python
"""
Script para popular o banco com dados de exemplo
Execute: python manage.py shell < scripts/popular_dados_exemplo.py
"""

import os
import sys
import django

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apocalipse_api.settings')
django.setup()

from Sobrevivente.models import Sobreviventes, ItemInventario, TipoItem
from decimal import Decimal


def criar_dados_exemplo():
    """Cria dados de exemplo para testar a API"""

    print("🧟 Criando sobreviventes de exemplo...")

    # Criando sobreviventes
    sobreviventes_dados = [
        {
            'nome': 'João Silva',
            'idade': 35,
            'sexo': 'M',
            'latitude': Decimal('-23.5505'),
            'longitude': Decimal('-46.6333')
        },
        {
            'nome': 'Maria Santos',
            'idade': 28,
            'sexo': 'F',
            'latitude': Decimal('-22.9068'),
            'longitude': Decimal('-43.1729')
        },
        {
            'nome': 'Pedro Oliveira',
            'idade': 42,
            'sexo': 'M',
            'latitude': Decimal('-30.0346'),
            'longitude': Decimal('-51.2177')
        },
        {
            'nome': 'Ana Costa',
            'idade': 31,
            'sexo': 'F',
            'latitude': Decimal('-25.4284'),
            'longitude': Decimal('-49.2733')
        },
        {
            'nome': 'Carlos Ferreira',
            'idade': 45,
            'sexo': 'M',
            'latitude': Decimal('-19.9167'),
            'longitude': Decimal('-43.9345')
        }
    ]

    sobreviventes_criados = []
    for dados in sobreviventes_dados:
        sobrevivente, criado = Sobreviventes.objects.get_or_create(
            nome=dados['nome'],
            defaults=dados
        )
        if criado:
            print(f"✅ Sobrevivente criado: {sobrevivente.nome}")
        else:
            print(f"ℹ️  Sobrevivente já existe: {sobrevivente.nome}")
        sobreviventes_criados.append(sobrevivente)

    print("\n🎒 Adicionando itens aos inventários...")

    # Adicionando itens aos inventários
    itens_exemplo = [
        # João Silva
        {'sobrevivente': sobreviventes_criados[0], 'tipo_item': TipoItem.AGUA, 'quantidade': 5},
        {'sobrevivente': sobreviventes_criados[0], 'tipo_item': TipoItem.COMIDA, 'quantidade': 3},
        {'sobrevivente': sobreviventes_criados[0], 'tipo_item': TipoItem.MUNICAO, 'quantidade': 10},

        # Maria Santos
        {'sobrevivente': sobreviventes_criados[1], 'tipo_item': TipoItem.MEDICAMENTO, 'quantidade': 4},
        {'sobrevivente': sobreviventes_criados[1], 'tipo_item': TipoItem.AGUA, 'quantidade': 2},
        {'sobrevivente': sobreviventes_criados[1], 'tipo_item': TipoItem.COMIDA, 'quantidade': 6},

        # Pedro Oliveira
        {'sobrevivente': sobreviventes_criados[2], 'tipo_item': TipoItem.MUNICAO, 'quantidade': 15},
        {'sobrevivente': sobreviventes_criados[2], 'tipo_item': TipoItem.AGUA, 'quantidade': 3},

        # Ana Costa
        {'sobrevivente': sobreviventes_criados[3], 'tipo_item': TipoItem.MEDICAMENTO, 'quantidade': 2},
        {'sobrevivente': sobreviventes_criados[3], 'tipo_item': TipoItem.COMIDA, 'quantidade': 4},
        {'sobrevivente': sobreviventes_criados[3], 'tipo_item': TipoItem.AGUA, 'quantidade': 1},

        # Carlos Ferreira
        {'sobrevivente': sobreviventes_criados[4], 'tipo_item': TipoItem.AGUA, 'quantidade': 8},
        {'sobrevivente': sobreviventes_criados[4], 'tipo_item': TipoItem.MUNICAO, 'quantidade': 20},
    ]

    for item_dados in itens_exemplo:
        item, criado = ItemInventario.objects.get_or_create(
            sobrevivente=item_dados['sobrevivente'],
            tipo_item=item_dados['tipo_item'],
            defaults={'quantidade': item_dados['quantidade']}
        )
        if criado:
            print(f"✅ Item adicionado: {item.quantidade}x {item.get_tipo_item_display()} para {item.sobrevivente.nome}")
        else:
            print(
                f"ℹ️  Item já existe: {item.quantidade}x {item.get_tipo_item_display()} para {item.sobrevivente.nome}")

    print("\n📊 Resumo dos dados criados:")
    print(f"👥 Total de sobreviventes: {Sobreviventes.objects.count()}")
    print(f"🎒 Total de itens no sistema: {ItemInventario.objects.count()}")

    print("\n🎯 Dados de exemplo criados com sucesso!")
    print("Agora você pode testar a API com os endpoints disponíveis.")


if __name__ == '__main__':
    criar_dados_exemplo()
