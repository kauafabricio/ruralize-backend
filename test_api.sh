#!/bin/bash
# Script de teste da API de Ações Sustentáveis
# Execute este script para testar todos os endpoints

API_URL="http://localhost:8000"

echo "======================================"
echo "Teste API: Sustainable Actions"
echo "======================================"

# 1. Inicializar ações padrão
echo -e "\n1. Inicializando ações padrão..."
curl -s -X POST "$API_URL/sustainable-actions/init" | jq .

# 2. Listar todas as ações
echo -e "\n2. Listando todas as ações..."
curl -s -X GET "$API_URL/sustainable-actions/" | jq .

# 3. Obter uma ação específica
echo -e "\n3. Obtendo ação 'tree-planting'..."
curl -s -X GET "$API_URL/sustainable-actions/tree-planting" | jq .

# 4. Criar ação customizada
echo -e "\n4. Criando ação customizada..."
curl -s -X POST "$API_URL/sustainable-actions/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Limpeza de Praia",
    "icon": "🌊"
  }' \
  -G --data-urlencode "user_id=user123" | jq .

# 5. Criar post com sustainable_action_id
echo -e "\n5. Criando post com sustainable_action_id..."
curl -s -X POST "$API_URL/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Plantei uma árvore hoje!",
    "location": "Recife, PE",
    "sustainable_action_id": "tree-planting"
  }' \
  -G --data-urlencode "user_id=user123" | jq .

# 6. Criar post com sustainable_action (compatibilidade)
echo -e "\n6. Criando post com sustainable_action (legacy)..."
curl -s -X POST "$API_URL/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Separei o lixo reciclável",
    "sustainable_action": "general"
  }' \
  -G --data-urlencode "user_id=user456" | jq .

# 7. Listar posts
echo -e "\n7. Listando todos os posts..."
curl -s -X GET "$API_URL/posts/" | jq '.[] | {id, content, sustainable_action_id, sustainable_action, user_id}'

# 8. Migrar posts antigos (se houver)
echo -e "\n8. Migrando posts antigos..."
curl -s -X POST "$API_URL/sustainable-actions/migrate" | jq .

echo -e "\n======================================"
echo "Testes concluídos!"
echo "======================================"
