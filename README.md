# 🧟 API do Apocalipse Zumbi

Sistema de gerenciamento de recursos para sobreviventes do apocalipse zumbi, desenvolvido em Django REST Framework.

## 📋 Funcionalidades

- ✅ Cadastro de sobreviventes
- ✅ Atualização de localização
- ✅ Sistema de reportes de infecção
- ✅ Gerenciamento de inventário
- ✅ Sistema de escambo com pontuação
- ✅ Relatórios estatísticos

## 🚀 Como executar

### 1. Instalar dependências
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configurar PostgreSQL
\`\`\`bash
# Criar banco de dados
psql -U postgres -c "CREATE DATABASE zssn_db;"
psql -U postgres -c "CREATE USER zssn_user WITH PASSWORD '3240';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE apocalipse_zumbi_db TO apocalipse_user;"
\`\`\`

### 3. Executar migrações
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 4. Criar superusuário (opcional)
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 5. Popular dados de exemplo
\`\`\`bash
python manage.py shell < scripts/popular_dados_exemplo.py
\`\`\`

### 6. Executar servidor
\`\`\`bash
python manage.py runserver
\`\`\`

## 📡 Endpoints da API

### Sobreviventes
- `GET /api/sobreviventes/` - Listar sobreviventes saudáveis
- `POST /api/sobreviventes/` - Cadastrar novo sobrevivente
- `GET /api/sobreviventes/{id}/` - Detalhes de um sobrevivente
- `PATCH /api/sobreviventes/{id}/atualizar_localizacao/` - Atualizar localização
- `POST /api/sobreviventes/{id}/reportar_infeccao/` - Reportar infecção
- `POST /api/sobreviventes/{id}/adicionar_item/` - Adicionar item ao inventário
- `POST /api/sobreviventes/{id}/remover_item/` - Remover item do inventário
- `POST /api/sobreviventes/{id}/escambo/` - Realizar escambo

### Relatórios
- `GET /api/sobreviventes/relatorios/` - Relatórios estatísticos

## 💰 Sistema de Pontos

| Item | Pontos |
|------|--------|
| Água | 4 pontos |
| Comida | 3 pontos |
| Medicamento | 2 pontos |
| Munição | 1 ponto |

## 📊 Exemplos de Uso

### Cadastrar Sobrevivente
\`\`\`json
POST /api/sobreviventes/
{
    "nome": "João Silva",
    "idade": 35,
    "sexo": "M",
    "latitude": -23.5505,
    "longitude": -46.6333
}
\`\`\`

### Adicionar Item ao Inventário
\`\`\`json
POST /api/sobreviventes/1/adicionar_item/
{
    "tipo_item": "agua",
    "quantidade": 5
}
\`\`\`

### Realizar Escambo
\`\`\`json
POST /api/sobreviventes/1/escambo/
{
    "sobrevivente_destino_id": 2,
    "itens_oferecidos": [
        {"tipo_item": "agua", "quantidade": 1}
    ],
    "itens_desejados": [
        {"tipo_item": "municao", "quantidade": 4}
    ]
}
\`\`\`

## 🔒 Regras de Negócio

- Sobreviventes infectados não podem fazer escambo
- Sobreviventes infectados não podem manipular inventário
- Um sobrevivente é marcado como infectado após 3 reportes
- Escambos devem ter saldo zero (mesma quantidade de pontos)
- Apenas sobreviventes saudáveis aparecem na listagem

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL
- psycopg2-binary

## 📝 Observações

Sistema de Escamho as vezes funciona de forma errada.
Criar um  usuario adm e acessar o sistema com ele.
La ira mostrar as funcoes
