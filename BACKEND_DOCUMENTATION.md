# Documentação do Backend Ruralize

## Visão Geral

**Nome:** Ruralize API  
**Versão:** 1.0.0  
**Framework:** FastAPI (Python)  
**Descrição:** API para gerenciamento de ações sustentáveis na UFRPE

**URL Base (Produção):** `https://rural-backend.vercel.app`  
**URL Base (Desenvolvimento):** `http://localhost:8000`

---

## CORS Configurado

O backend aceita requisições de:
- `http://localhost:3000` (desenvolvimento local)
- `http://127.0.0.1:3000` (desenvolvimento local)
- `https://ruralize-ufrpe.vercel.app` (produção)

**Headers CORS habilitados:**
- Credenciais: ✅ Habilitadas
- Métodos: ✅ Todos (`*`)
- Headers: ✅ Todos (`*`)

---

## Módulos de API

### 1️⃣ **AUTH** - Autenticação

**Prefix:** `/auth`

#### POST `/auth/register`
Criar nova conta de usuário

**Body:**
```json
{
  "name": "string",
  "email": "user@ufrpe.edu.br",
  "password": "string",
  "role": "student" | "teacher",
  "registration": "202312345" | null,
  "course": "Engenharia Agrônoma" | null,
  "department": "Engenharia" | null,
  "campus_location": "string" | null,
  "description": "string" | null,
  "profile_photo_url": "string" | null,
  "cover_photo_url": "string" | null,
  "tags": ["tag1", "tag2"] | []
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "user_id": "user_uuid"
}
```

**Validações:**
- Email obrigatório (validação de email)
- Password obrigatório (mínimo de força?)
- Role obrigatório ("student" ou "teacher")
- Se role="student": course é recomendado
- Se role="teacher": department é recomendado

---

#### POST `/auth/login`
Autenticar usuário

**Body:**
```json
{
  "email": "user@ufrpe.edu.br",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "user_id": "user_uuid"
}
```

**Armazenamento Frontend:**
- Guardar `access_token` em `localStorage.authToken`
- Guardar `user_id` em `localStorage` ou state global

---

### 2️⃣ **FEED** - Feed de Posts

**Prefix:** `/feed`

#### GET `/feed/`
Retorna feed geral ou personalizado

**Query Parameters:**
- `user_id` (opcional): Se fornecido, filtra feed do usuário

**Response:**
```json
[
  {
    "id": "post_uuid",
    "user_id": "user_uuid",
    "content": "string",
    "location": "string" | null,
    "sustainable_action": "string",
    "event_id": "event_uuid" | null,
    "image_url": "string" | null,
    "likes": 5,
    "liked_by": ["user_id_1", "user_id_2"],
    "comments": [
      {
        "user_id": "user_uuid",
        "content": "comentário",
        "created_at": "2024-01-01T12:00:00"
      }
    ],
    "created_at": "2024-01-01T12:00:00"
  }
]
```

**Uso:** Carregar feed na Home/página inicial

---

#### GET `/feed/friends/{user_id}`
Retorna feed apenas dos amigos do usuário

**Response:** Array de posts (mesmo formato acima)

**Uso:** Página de feed de amigos (filtrado)

---

### 3️⃣ **POSTS** - Gerenciamento de Posts

**Prefix:** `/posts`

#### GET `/posts/`
Retorna todos os posts

**Response:** Array de PostResponse (mesmo formato de /feed/)

---

#### GET `/posts/{post_id}`
Retorna detalhes de um post específico

**Response:**
```json
{
  "id": "post_uuid",
  "user_id": "user_uuid",
  "content": "string",
  "location": "string" | null,
  "sustainable_action": "string",
  "event_id": "event_uuid" | null,
  "image_url": "string" | null,
  "likes": 5,
  "liked_by": ["user_id_1"],
  "comments": [...],
  "created_at": "2024-01-01T12:00:00"
}
```

---

#### POST `/posts/`
Criar novo post

**Query Parameters:**
- `user_id` (obrigatório): ID do usuário autenticado

**Body:**
```json
{
  "content": "string (obrigatório)",
  "location": "string" | null,
  "sustainable_action": "string (obrigatório)",
  "event_id": "event_uuid" | null,
  "image_url": "string" | null
}
```

**Response:**
```json
{
  "message": "Post created successfully",
  "post_id": "post_uuid"
}
```

**Padrão de Chamada (Frontend):**
```javascript
await postService.createPost(
  {
    content: "Texto do post",
    sustainable_action: "Reciclagem",
    location: "Campus UFRPE",
    image_url: "url_da_imagem"
  },
  userId
);
```

---

#### PUT `/posts/{post_id}`
Atualizar um post

**Body:**
```json
{
  "content": "string" | null,
  "location": "string" | null,
  "sustainable_action": "string" | null,
  "event_id": "event_uuid" | null,
  "image_url": "string" | null
}
```

**Response:**
```json
{
  "message": "Post updated successfully"
}
```

---

#### DELETE `/posts/{post_id}`
Deletar um post

**Query Parameters:**
- `user_id` (obrigatório): Apenas o dono pode deletar

**Response:**
```json
{
  "message": "Post deleted successfully"
}
```

---

#### POST `/posts/{post_id}/like`
Curtir um post

**Query Parameters:**
- `user_id` (obrigatório): ID do usuário que está curtindo

**Response:**
```json
{
  "message": "Post liked",
  "likes": 6
}
```

**Padrão (Frontend):**
```javascript
await postService.likePost(postId, userId);
```

---

#### DELETE `/posts/{post_id}/like`
Remover like de um post

**Query Parameters:**
- `user_id` (obrigatório)

**Response:**
```json
{
  "message": "Like removed",
  "likes": 5
}
```

---

#### POST `/posts/{post_id}/comment`
Adicionar comentário a um post

**Body:**
```json
{
  "user_id": "user_uuid (obrigatório)",
  "content": "string (obrigatório)"
}
```

**Response:**
```json
{
  "message": "Comment added successfully"
}
```

---

#### DELETE `/posts/{post_id}/comment/{comment_index}`
Remover um comentário específico

**Query Parameters:**
- `user_id` (obrigatório): Apenas o autor do comentário pode remover

**Path Parameters:**
- `comment_index`: Índice do comentário no array (0, 1, 2...)

**Response:**
```json
{
  "message": "Comment removed successfully"
}
```

---

### 4️⃣ **PROFILES** - Perfis de Usuários

**Prefix:** `/profiles`

#### GET `/profiles/`
Retorna lista de todos os perfis (informações públicas)

**Response:**
```json
[
  {
    "id": "user_uuid",
    "name": "João Silva",
    "role": "student",
    "course": "Engenharia Agrônoma",
    "department": "Engenharia" | null,
    "profile_photo_url": "url" | null,
    "description": "string" | null,
    "tags": ["tag1", "tag2"]
  }
]
```

---

#### GET `/profiles/user/{user_id}`
Retorna perfil completo de um usuário

**Response:**
```json
{
  "id": "user_uuid",
  "name": "João Silva",
  "email": "joao@ufrpe.edu.br",
  "role": "student",
  "registration": "202312345" | null,
  "course": "Engenharia Agrônoma" | null,
  "department": null,
  "campus_location": "string" | null,
  "description": "Sou estudante de agronomia interessado em sustentabilidade",
  "profile_photo_url": "url" | null,
  "cover_photo_url": "url" | null,
  "tags": ["sustentabilidade", "reciclagem"],
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

#### PUT `/profiles/user/{user_id}`
Atualizar perfil do usuário

**Body:**
```json
{
  "description": "string" | null,
  "profile_photo_url": "string" | null,
  "cover_photo_url": "string" | null,
  "tags": ["tag1", "tag2"] | [],
  "course": "string" | null,
  "department": "string" | null
}
```

**Response:**
```json
{
  "message": "Profile updated successfully"
}
```

---

#### GET `/profiles/search/by-name`
Buscar perfis por nome

**Query Parameters:**
- `name` (obrigatório): Mínimo 2 caracteres

**Example:** `/profiles/search/by-name?name=João`

**Response:** Array de UserProfileResponse (mesmo formato acima)

---

#### GET `/profiles/search/by-course`
Buscar perfis por curso

**Query Parameters:**
- `course` (obrigatório)

**Example:** `/profiles/search/by-course?course=Engenharia Agrônoma`

**Response:** Array de UserProfileResponse

---

#### GET `/profiles/search/by-department`
Buscar perfis por departamento

**Query Parameters:**
- `department` (obrigatório)

**Example:** `/profiles/search/by-department?department=Engenharia`

**Response:** Array de UserProfileResponse

---

#### GET `/profiles/search/by-role/{role}`
Buscar perfis por papel (student/teacher)

**Path Parameters:**
- `role`: "student" ou "teacher"

**Response:** Array de UserProfileResponse

---

#### GET `/profiles/search/by-tags`
Buscar perfis por tags

**Query Parameters:**
- `tags` (obrigatório, múltiplo): Array de tags

**Example:** `/profiles/search/by-tags?tags=sustentabilidade&tags=reciclagem`

**Response:** Array de UserProfileResponse

---

### 5️⃣ **ACTIONS** - Ações Sustentáveis

**Prefix:** `/actions`

#### GET `/actions/`
Retorna todas as ações sustentáveis disponíveis

**Response:**
```json
[
  {
    "id": "action_uuid",
    "name": "Reciclagem",
    "description": "Iniciativa de reciclagem de resíduos na universidade"
  }
]
```

**Uso:** Preencher lista de ações ao criar post ou evento

---

#### GET `/actions/{action_id}`
Retorna detalhes de uma ação específica

**Response:**
```json
{
  "id": "action_uuid",
  "name": "Reciclagem",
  "description": "Iniciativa de reciclagem de resíduos na universidade"
}
```

---

#### POST `/actions/`
Criar nova ação sustentável (admin)

**Body:**
```json
{
  "name": "string (obrigatório)",
  "description": "string (obrigatório)"
}
```

**Response:**
```json
{
  "message": "Action created successfully",
  "action_id": "action_uuid"
}
```

---

#### PUT `/actions/{action_id}`
Atualizar uma ação (admin)

**Body:**
```json
{
  "name": "string" | null,
  "description": "string" | null
}
```

---

#### DELETE `/actions/{action_id}`
Deletar uma ação (admin)

---

### 6️⃣ **EVENTS** - Eventos Sustentáveis

**Prefix:** `/events` (mesma rota que subscriptions)

#### GET `/events/`
Listar eventos com filtros opcionais

**Query Parameters (todos opcionais):**
- `action_id`: Filtrar por ação
- `status`: Filtrar por status (draft, published, ended)
- `start_date`: Data inicial (ISO format)
- `end_date`: Data final (ISO format)

**Response:**
```json
[
  {
    "id": "event_uuid",
    "title": "Dia da Limpeza do Campus",
    "description": "Evento de limpeza do campus",
    "promoter_name": "Prof. João",
    "action_name": "Limpeza",
    "start_date": "2024-05-15T10:00:00",
    "end_date": "2024-05-15T14:00:00",
    "location_name": "Campus Central",
    "max_participants": 50,
    "points": 10,
    "status": "published",
    "photo_url": "url" | null,
    "participant_count": 25
  }
]
```

---

#### GET `/events/{event_id}`
Retorna detalhes completos de um evento

**Response:**
```json
{
  "id": "event_uuid",
  "title": "Dia da Limpeza do Campus",
  "description": "Evento de limpeza do campus",
  "promoter_id": "user_uuid",
  "promoter_name": "Prof. João",
  "promoter_photo": "url" | null,
  "action_id": "action_uuid",
  "action_name": "Limpeza",
  "start_date": "2024-05-15T10:00:00",
  "end_date": "2024-05-15T14:00:00",
  "location_name": "Campus Central",
  "address": "Rua da Universidade, 123",
  "latitude": -8.0277,
  "longitude": -34.9447,
  "max_participants": 50,
  "points": 10,
  "status": "published",
  "photo_url": "url" | null,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-15T10:30:00",
  "participant_count": 25
}
```

---

#### POST `/events/`
Criar novo evento (apenas professores)

**Headers:**
- `x-user-id` (obrigatório): ID do usuário autenticado

**Body:**
```json
{
  "title": "string (obrigatório)",
  "description": "string (obrigatório)",
  "action_id": "action_uuid (obrigatório)",
  "start_date": "2024-05-15T10:00:00 (obrigatório)",
  "end_date": "2024-05-15T14:00:00 (obrigatório)",
  "location_name": "string (obrigatório)",
  "address": "string (obrigatório)",
  "latitude": -8.0277 | null,
  "longitude": -34.9447 | null,
  "max_participants": 50 (obrigatório),
  "points": 10 (obrigatório),
  "photo_url": "string" | null,
  "status": "draft" | "published"
}
```

**Response:**
```json
{
  "message": "Event created successfully",
  "event_id": "event_uuid"
}
```

**Padrão (Frontend):**
```javascript
await eventService.createEvent(eventData, {
  headers: {
    'x-user-id': userId
  }
});
```

---

#### PUT `/events/{event_id}`
Atualizar evento (apenas promoter)

**Headers:**
- `x-user-id` (obrigatório)

**Body:** (todos os campos opcionais)
```json
{
  "title": "string" | null,
  "description": "string" | null,
  "action_id": "string" | null,
  "start_date": "datetime" | null,
  "end_date": "datetime" | null,
  "location_name": "string" | null,
  "address": "string" | null,
  "latitude": float | null,
  "longitude": float | null,
  "max_participants": int | null,
  "points": int | null,
  "photo_url": "string" | null,
  "status": "draft" | "published" | null
}
```

---

#### DELETE `/events/{event_id}`
Deletar evento (apenas promoter)

**Headers:**
- `x-user-id` (obrigatório)

---

### 7️⃣ **SUBSCRIPTIONS** - Inscrição em Eventos

**Prefix:** `/events` (mesmo prefix que events)

#### POST `/events/{event_id}/subscribe`
Inscrever usuário em um evento

**Headers:**
- `x-user-id` (obrigatório): ID do usuário que quer se inscrever

**Response:**
```json
{
  "message": "Successfully subscribed to event",
  "event_id": "event_uuid"
}
```

**Padrão (Frontend):**
```javascript
await subscriptionService.subscribe(eventId, {
  headers: {
    'x-user-id': userId
  }
});
```

---

#### DELETE `/events/{event_id}/unsubscribe`
Desinscrever usuário de um evento

**Headers:**
- `x-user-id` (obrigatório)

**Response:**
```json
{
  "message": "Successfully unsubscribed from event"
}
```

---

#### GET `/events/{event_id}/participants`
Listar participantes de um evento

**Response:**
```json
{
  "participants": [
    {
      "id": "user_uuid",
      "name": "João Silva",
      "profile_photo_url": "url" | null
    }
  ]
}
```

---

## 🔐 Autenticação e Headers

### Padrão de Autenticação

O backend usa dois padrões:

#### 1. Query Parameter (Endpoints mais antigos)
```javascript
// Enviar user_id como query param
axios.post(`/posts/?user_id=${userId}`, data);
axios.delete(`/posts/${postId}?user_id=${userId}`);
```

#### 2. Header HTTP (Endpoints mais novos)
```javascript
// Enviar user_id no header x-user-id
axios.post('/events/', data, {
  headers: {
    'x-user-id': userId
  }
});
```

#### 3. JWT Token (se implementado)
```javascript
// Guardar token após login
localStorage.setItem('authToken', response.access_token);

// Enviar token em requisições
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

---

## 📊 Modelos de Dados

### User
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "password": "hashed",
  "role": "student" | "teacher",
  "registration": "string",
  "course": "string",
  "department": "string",
  "campus_location": "string",
  "description": "string",
  "profile_photo_url": "string",
  "cover_photo_url": "string",
  "tags": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Post
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "content": "string",
  "location": "string",
  "sustainable_action": "string",
  "event_id": "uuid",
  "image_url": "string",
  "likes": "int",
  "liked_by": ["uuid"],
  "comments": ["Comment[]"],
  "created_at": "datetime"
}
```

### Event
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "promoter_id": "uuid",
  "action_id": "uuid",
  "start_date": "datetime",
  "end_date": "datetime",
  "location_name": "string",
  "address": "string",
  "latitude": "float",
  "longitude": "float",
  "max_participants": "int",
  "points": "int",
  "status": "draft" | "published" | "ended",
  "photo_url": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "participant_count": "int"
}
```

### Action
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string"
}
```

---

## ⚠️ Validações Importantes

| Campo | Validação |
|-------|-----------|
| `email` | Deve ser email válido (@ufrpe.edu.br preferível) |
| `name` | String obrigatória |
| `password` | String obrigatória |
| `role` | "student" ou "teacher" |
| `tags` | Array de strings |
| `start_date` | Deve ser antes de `end_date` |
| `max_participants` | Número positivo |
| `points` | Número positivo |
| `content` (post) | Obrigatório, não pode ser vazio |
| `sustainable_action` | Obrigatório, deve existir em Actions |

---

## 🚀 Fluxo Recomendado de Integração

### 1. **Autenticação**
```
1. POST /auth/register (novo usuário)
   ↓ Guardar token + user_id
2. POST /auth/login (usuários existentes)
   ↓ Guardar token + user_id em localStorage
3. Configurar axios com headers padrão
```

### 2. **Home/Feed**
```
1. GET /feed/ (ou /feed/?user_id=xxx para personalizado)
2. Exibir posts com componentes PostCard
3. Usuário pode curtir, comentar, etc
```

### 3. **Criar Post**
```
1. Modal com formulário
2. POST /posts/?user_id=xxx
3. Atualizar feed (remover cache ou buscar novamente)
```

### 4. **Ver Perfil**
```
1. GET /profiles/user/{user_id}
2. Exibir informações
3. PUT /profiles/user/{user_id} para atualizar
```

### 5. **Eventos**
```
1. GET /events/ (listar eventos)
2. GET /events/{event_id} (detalhes)
3. POST /events/{event_id}/subscribe (participar)
4. GET /events/{event_id}/participants (ver participantes)
```

### 6. **Buscar Usuários**
```
1. GET /profiles/search/by-name?name=xxx
2. GET /profiles/search/by-tags?tags=xxx
3. GET /profiles/search/by-course?course=xxx
4. GET /profiles/search/by-department?department=xxx
5. GET /profiles/search/by-role/{role}
```

---

## 🔍 Checklist para Validar Integração

- [ ] Login e Cadastro funcionam e guardam token
- [ ] Feed carrega posts ao abrir home
- [ ] Pode criar novo post (POST /posts/)
- [ ] Pode curtir post (POST /posts/{id}/like)
- [ ] Pode comentar (POST /posts/{id}/comment)
- [ ] Pode editar perfil (PUT /profiles/user/{id})
- [ ] Busca de usuários funciona (todos os 5 tipos)
- [ ] Cria evento (POST /events/)
- [ ] Lista eventos com filtros
- [ ] Inscreve em evento (POST /events/{id}/subscribe)
- [ ] Vê participantes do evento
- [ ] user_id é passado corretamente em todas requisições
- [ ] Headers x-user-id são usados em endpoints que requerem
- [ ] Tratamento de erros implementado
- [ ] Refresh token/auto-logout após expiração

---

## 📝 Notas Importantes

1. **Dois padrões de autenticação:** Alguns endpoints usam query param `user_id`, outros usam header `x-user-id`. Certifique-se de usar o padrão correto.

2. **Comentários por índice:** Para deletar comentário, use o índice do array (0, 1, 2...), não um ID.

3. **Status de eventos:** Pode ser "draft", "published" ou "ended"

4. **Coordenadas geográficas:** Latitude e longitude são opcionais, úteis para mapa

5. **Points:** Sistema de pontos para eventos sustentáveis (gamificação)

6. **Participants:** Cada evento rastreia inscrições de usuários

7. **Tags:** Podem ser usadas para filtrar perfis e posts

8. **Ações sustentáveis:** Conceito importante - posts e eventos são vinculados a ações específicas
