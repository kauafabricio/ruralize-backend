# Refatoração de Ações Sustentáveis - Backend Implementation

## Arquivos Criados

### 1. **app/schemas/sustainable_action_schema.py**
   - `SustainableActionCreate`: Schema para criar ações (name, icon)
   - `SustainableActionUpdate`: Schema para atualizar ações
   - `SustainableActionResponse`: Schema de resposta com id, name, icon, is_default, created_by, created_at

### 2. **app/repositories/sustainable_action_repository.py**
   - CRUD completo para SustainableAction
   - Lookup por `id` (string slug, não ObjectId)
   - Método `action_exists()` para validação
   - Migração e inicialização de dados

### 3. **app/services/sustainable_action_service.py**
   - `SustainableActionService` com lógica de negócio
   - `init_default_actions()`: Popula 10 ações padrão (idempotente)
   - `resolve_action_id()`: Resolve compatibilidade com dados legacy
   - `LEGACY_ACTION_MAPPING`: Mapeia strings antigas para action IDs
   - Validação e criação de ações customizadas

### 4. **app/controllers/sustainable_action_controller.py**
   - Endpoints:
     - `GET /sustainable-actions/` - Lista todas as ações
     - `GET /sustainable-actions/{action_id}` - Obtém uma ação
     - `POST /sustainable-actions/` - Cria ação customizada (requer `user_id`)
     - `PUT /sustainable-actions/{action_id}` - Atualiza ação
     - `DELETE /sustainable-actions/{action_id}` - Deleta ação
     - `POST /sustainable-actions/init` - Inicializa ações padrão
     - `POST /sustainable-actions/migrate` - Migra posts antigos

## Arquivos Modificados

### 1. **main.py**
   - Adicionado import: `from app.controllers.sustainable_action_controller import router as sustainable_action_router`
   - Registrado router: `app.include_router(sustainable_action_router, prefix="/sustainable-actions", tags=["Sustainable Actions"])`

### 2. **app/schemas/post_schema.py**
   - `PostCreate`: 
     - NOVO: `sustainable_action_id: Optional[str] = None`
     - MANTÉM: `sustainable_action: Optional[str] = None` (compatibilidade)
   - `PostUpdate`: Mesmas mudanças
   - `PostResponse`: Retorna ambos `sustainable_action_id` e `sustainable_action`
   - `PostEnrichedResponse`: Mesmas mudanças

### 3. **app/repositories/post_repository.py**
   - `_serialize()`: Adicionado `sustainable_action_id` na resposta
   - NOVO: `migrate_posts_to_action_ids()` - Migra posts com mapeamento de legacy strings

### 4. **app/services/post_service.py**
   - Constructor: Adicionado parâmetro `action_service: SustainableActionService`
   - `create_post()`: Valida e resolve `sustainable_action_id`, com fallback para `sustainable_action`
   - `update_post()`: Valida `sustainable_action_id` se fornecido

### 5. **app/controllers/post_controller.py**
   - Importado `SustainableActionService` e `SustainableActionRepository`
   - Instanciado `action_service` e injetado no `PostService`

## 10 Ações Padrão (Inicializadas)

| ID | Nome | Ícone |
|----|------|-------|
| `tree-planting` | Plantio de Árvores | 🌱 |
| `recycling` | Reciclagem | ♻️ |
| `water-conservation` | Conservação de Água | 💧 |
| `energy-efficiency` | Eficiência Energética | ⚡ |
| `composting` | Compostagem | 🌿 |
| `biodiversity` | Biodiversidade | 🦋 |
| `sustainable-agriculture` | Agricultura Sustentável | 🌾 |
| `clean-energy` | Energia Limpa | ☀️ |
| `pollution-reduction` | Redução de Poluição | 🌍 |
| `education` | Educação Ambiental | 📚 |

## Fluxo de Configuração Inicial

1. **Inicializar Ações Padrão:**
   ```bash
   curl -X POST http://localhost:8000/sustainable-actions/init
   ```

2. **Migrar Posts Antigos (opcional):**
   ```bash
   curl -X POST http://localhost:8000/sustainable-actions/migrate
   ```

3. **Criar Post com Ação:**
   ```bash
   curl -X POST http://localhost:8000/posts/ \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Plantei uma árvore!",
       "sustainable_action_id": "tree-planting"
     }' \
     -G --data-urlencode "user_id=user123"
   ```

4. **Compatibilidade (fallback):**
   ```bash
   curl -X POST http://localhost:8000/posts/ \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Texto antigo",
       "sustainable_action": "general"
     }' \
     -G --data-urlencode "user_id=user123"
   ```

## Validações Implementadas

1. ✅ `sustainable_action_id` em POST/PUT deve existir em `sustainable_actions`
2. ✅ Ações criadas por usuários têm `created_by = user_id`
3. ✅ Ações padrão têm `created_by = null`
4. ✅ Criação de post: aceita `sustainable_action_id` OU `sustainable_action` (prioriza ID)
5. ✅ Resposta sempre retorna: `sustainable_action_id` + `sustainable_action` (para compatibilidade)

## Data Migration

**Mapeamento de Legacy Strings:**
- `"general"` → `"tree-planting"`
- `"events"` → `"tree-planting"`
- `"warnings"` → `"pollution-reduction"`
- `"projects"` → `"sustainable-agriculture"`
- Strings desconhecidas → `"tree-planting"` (padrão)

## Compatibilidade (Backward Compatible)

- ✅ Posts antigos com `sustainable_action` (string) continuam funcionando
- ✅ Endpoint de criação aceita ambos: `sustainable_action_id` e `sustainable_action`
- ✅ `sustainable_action_id` tem prioridade, mas `sustainable_action` é fallback
- ✅ Respostas retornam ambos os campos

## Próximas Etapas (Frontend)

1. Frontend envia `sustainable_action_id` como string (slug)
2. Backend valida se ação existe
3. Backend retorna resposta com `id`, `name`, `icon`
4. Frontend exibe badge com ícone baseado em `sustainable_action_id`
5. Frontend pode filtrar posts por ação usando os IDs

## Testing

Execute o script de teste:
```bash
cd ruralize-backend
python -m pytest test_sustainable_actions.py -v
```

Ou manualmente:
```bash
python -c "from test_sustainable_actions import *"
```
