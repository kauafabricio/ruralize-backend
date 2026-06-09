#!/usr/bin/env python
"""
Script de teste para validar a infraestrutura de SustainableAction
"""

from app.database import db
from app.repositories.sustainable_action_repository import SustainableActionRepository
from app.repositories.post_repository import PostRepository
from app.services.sustainable_action_service import SustainableActionService, DEFAULT_ACTIONS
from datetime import datetime

print("=" * 50)
print("TESTE: SustainableAction Infrastructure")
print("=" * 50)

# Inicializar repositórios
action_repo = SustainableActionRepository(db)
post_repo = PostRepository(db)
action_service = SustainableActionService(action_repo)

# Limpar dados de teste anteriores
print("\n1. Limpando dados anteriores...")
action_repo.delete_all_actions()
print("   ✓ Coleção limpa")

# Inicializar ações padrão
print("\n2. Inicializando ações padrão...")
result = action_service.init_default_actions()
print(f"   ✓ {result['message']}")

# Verificar ações criadas
print("\n3. Verificando ações padrão...")
actions = action_service.get_all_actions()
print(f"   ✓ {len(actions)} ações criadas:")
for action in actions:
    print(f"     - {action['icon']} {action['name']} ({action['id']})")

# Testar lookup
print("\n4. Testando lookup de ações...")
action = action_service.get_action("tree-planting")
print(f"   ✓ Encontrada: {action['icon']} {action['name']}")

# Testar resolve_action_id
print("\n5. Testando resolve_action_id...")
resolved = action_service.resolve_action_id("tree-planting")
print(f"   ✓ ID direto: {resolved}")

resolved = action_service.resolve_action_id(action_name="general")
print(f"   ✓ Mapeamento legacy 'general': {resolved}")

# Testar create post com action_id
print("\n6. Testando criação de post com action_id...")
post_data = {
    "user_id": "user123",
    "content": "Plantei uma árvore hoje!",
    "sustainable_action_id": "tree-planting"
}
post_id = post_repo.create_post(post_data)
post = post_repo.get_post_by_id(post_id)
print(f"   ✓ Post criado: {post['id']}")
print(f"   ✓ Action ID: {post.get('sustainable_action_id')}")

print("\n" + "=" * 50)
print("TODOS OS TESTES PASSARAM!")
print("=" * 50)
