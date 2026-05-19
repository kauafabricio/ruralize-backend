# 📱 Guia de Integração Frontend - Ruralize API

## 1. Configuração Inicial

### 1.1 URL Base da API
```
Development: http://localhost:8000
Production: https://ruralize-api.com (ajustar conforme necessário)
```

### 1.2 Headers Padrão
Todo request deve incluir estes headers:
```javascript
headers: {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}
```

### 1.3 Tratamento de Erros Padrão
A API retorna erros em formato consistente:
```json
{
  "detail": "Descrição do erro"
}
```

**Códigos HTTP principais:**
- `200` OK - Sucesso
- `400` Bad Request - Validação falhou
- `403` Forbidden - Sem permissão (ex: tentar deletar post de outro usuário)
- `404` Not Found - Recurso não existe
- `500` Server Error - Erro interno

---

## 2. Autenticação

### 2.1 Registro (Sign Up)

**Endpoint:**
```
POST /auth/register
```

**Request Body:**
```json
{
  "name": "João Silva",
  "email": "joao@ufrpe.edu.br",
  "password": "senha_segura_123",
  "role": "student",
  "registration": "2023001",
  "course": "Engenharia Ambiental",
  "campus_location": "Recife",
  "description": "Apaixonado por sustentabilidade",
  "profile_photo_url": null,
  "cover_photo_url": null,
  "tags": ["sustentabilidade", "energia-limpa"]
}
```

**Validações:**
- `role`: obrigatório, valores válidos: `"student"` ou `"teacher"`
- **Se `role = "student"`:**
  - `registration` e `course` são obrigatórios
- **Se `role = "teacher"`:**
  - `department` é opcional
- `email`: deve ser um email válido
- `password`: mínimo 8 caracteres recomendado
- `name`: obrigatório, mínimo 2 caracteres

**Response:**
```json
{
  "message": "Usuário criado com sucesso"
}
```

**Próximas ações após registro:**
1. Redirecionar para login
2. Criar perfil com dados complementares via `PUT /profiles/user/{user_id}`

---

### 2.2 Login (Sign In)

**Endpoint:**
```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "joao@ufrpe.edu.br",
  "password": "senha_segura_123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Como usar o token:**
1. Armazenar em `localStorage` ou `sessionStorage`
   ```javascript
   localStorage.setItem('access_token', response.access_token);
   ```
2. Incluir em futuras requisições como `user_id` parameter:
   ```javascript
   // Extrair user_id do token JWT
   const decoded = jwt_decode(token);
   const user_id = decoded.user_id;
   ```
3. Guardar `user_id` também no localStorage para facilitar requests

**Segurança:**
- Nunca exponha o token em logs
- Use HTTPS em produção
- Token expira em 24h (configurável)
- Ao logout, limpar token e user_id do storage

---

## 3. Perfil do Usuário

### 3.1 Obter Perfil Completo (com info acadêmica)

**Endpoint:**
```
GET /profiles/user/{user_id}
```

**Quando usar:** Quando o usuário logado quer ver seu próprio perfil com informações sensíveis (email, matrícula)

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "user_id": "507f1f77bcf86cd799439012",
  "name": "João Silva",
  "role": "student",
  "course": "Engenharia Ambiental",
  "department": null,
  "description": "Apaixonado por sustentabilidade",
  "profile_photo_url": "https://example.com/joao.jpg",
  "cover_photo_url": "https://example.com/capa.jpg",
  "tags": ["sustentabilidade", "energia-limpa"],
  "academic_info": {
    "email": "joao@ufrpe.edu.br",
    "registration": "2023001",
    "campus_location": "Recife"
  },
  "created_at": "2025-05-18T10:00:00",
  "updated_at": "2025-05-18T14:30:00"
}
```

---

### 3.2 Obter Perfil Público (sem info acadêmica)

**Endpoint:**
```
GET /profiles/{profile_id}
```

**Quando usar:** Quando visualiza o perfil de outro usuário (não mostra email/matrícula)

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "João Silva",
  "role": "student",
  "course": "Engenharia Ambiental",
  "department": null,
  "profile_photo_url": "https://example.com/joao.jpg",
  "description": "Apaixonado por sustentabilidade",
  "tags": ["sustentabilidade", "energia-limpa"]
}
```

---

### 3.3 Atualizar Perfil

**Endpoint:**
```
PUT /profiles/user/{user_id}
```

**Request Body (todos os campos são opcionais):**
```json
{
  "description": "Novo texto de descrição",
  "profile_photo_url": "https://example.com/nova-foto.jpg",
  "cover_photo_url": "https://example.com/nova-capa.jpg",
  "tags": ["sustentabilidade", "educação-ambiental", "energia-solar"]
}
```

**Response:**
```json
{
  "message": "Perfil atualizado com sucesso"
}
```

---

### 3.4 Buscar Perfis

#### 3.4.1 Listar todos os perfis
```
GET /profiles/
```

**Response:**
```json
[
  {
    "id": "...",
    "name": "João Silva",
    "role": "student",
    "course": "Engenharia Ambiental",
    "profile_photo_url": "...",
    "description": "...",
    "tags": ["sustentabilidade"]
  }
]
```

#### 3.4.2 Buscar por nome
```
GET /profiles/search/by-name?name=João
```

#### 3.4.3 Buscar por curso
```
GET /profiles/search/by-course?course=Engenharia Ambiental
```

#### 3.4.4 Buscar por departamento (professores)
```
GET /profiles/search/by-department?department=Engenharia
```

#### 3.4.5 Buscar por role
```
GET /profiles/search/by-role/student
GET /profiles/search/by-role/teacher
```

#### 3.4.6 Buscar por tags
```
GET /profiles/search/by-tags?tags=sustentabilidade&tags=energia-limpa
```

---

## 4. Posts (Postagens)

### 4.1 Criar Post

**Endpoint:**
```
POST /posts/?user_id={user_id}
```

**Request Body:**
```json
{
  "content": "Hoje plantei 10 árvores em meu campus!",
  "location": "UFRPE - Campus Recife",
  "sustainable_action": "Reflorestamento",
  "event_id": null,
  "image_url": "https://example.com/foto-arvores.jpg"
}
```

**Validações:**
- `content`: obrigatório, mínimo 1 caractere
- `sustainable_action`: obrigatório (ex: "Reflorestamento", "Economia de Energia", "Reciclagem")
- Outros campos são opcionais

**Response:**
```json
{
  "message": "Post criado com sucesso",
  "id": "507f1f77bcf86cd799439013"
}
```

---

### 4.2 Obter Post

**Endpoint:**
```
GET /posts/{post_id}
```

**Response (com dados enriquecidos):**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "user_id": "507f1f77bcf86cd799439012",
  "content": "Hoje plantei 10 árvores em meu campus!",
  "location": "UFRPE - Campus Recife",
  "sustainable_action": "Reflorestamento",
  "event_id": null,
  "image_url": "https://example.com/foto-arvores.jpg",
  "likes": 3,
  "liked_by": [
    {
      "user_id": "507f1f77bcf86cd799439014",
      "user_name": "Maria Costa",
      "user_photo": "https://example.com/maria.jpg"
    },
    {
      "user_id": "507f1f77bcf86cd799439015",
      "user_name": "Pedro Silva",
      "user_photo": "https://example.com/pedro.jpg"
    }
  ],
  "comments": [
    {
      "user_id": "507f1f77bcf86cd799439014",
      "user_name": "Maria Costa",
      "user_photo": "https://example.com/maria.jpg",
      "content": "Que iniciativa incrível! 🌱",
      "created_at": "2025-05-18T14:30:00"
    }
  ],
  "created_at": "2025-05-18T10:00:00"
}
```

**Informações retornadas:**
- `liked_by`: Array com nome + foto de quem curtiu
- `comments`: Array com nome + foto do comentarista
- Frontend pode exibir tudo sem requests adicionais

---

### 4.3 Listar Posts (Feed Geral)

**Endpoint:**
```
GET /posts/
```

**Response:** Array de posts com formato idêntico ao 4.2

**Uso:** Página inicial/feed geral com todos os posts ordenados por likes + data

---

### 4.4 Feed Personalizado

#### 4.4.1 Feed Geral (com priorização de amigos)
```
GET /feed/?user_id={user_id}
```

**Lógica de ordenação:**
1. Posts de amigos (following AND followers) - prioridade máxima
2. Posts de quem segue (following apenas)
3. Posts de outros
4. Dentro de cada categoria: ordenado por likes + data mais recente

#### 4.4.2 Feed de Amigos
```
GET /feed/friends/{user_id}
```

Retorna apenas posts de usuários que são amigos (relacionamento bidirecional)

---

### 4.5 Curtir Post

**Endpoint:**
```
POST /posts/{post_id}/like?user_id={user_id}
```

**Behavior:**
- Primeira curtida: Incrementa contador, adiciona user_id ao `liked_by`
- Curtida duplicada: Retorna `{"message": "Like já registrado"}` (sem duplicar)

**Response:**
```json
{
  "message": "Like registrado com sucesso"
}
```

---

### 4.6 Remover Curtida (Unlike)

**Endpoint:**
```
DELETE /posts/{post_id}/like?user_id={user_id}
```

**Behavior:**
- Remove user_id de `liked_by`
- Decrementa contador de likes

**Response:**
```json
{
  "message": "Like removido com sucesso"
}
```

---

### 4.7 Comentar em Post

**Endpoint:**
```
POST /posts/{post_id}/comment
```

**Request Body:**
```json
{
  "user_id": "507f1f77bcf86cd799439012",
  "content": "Que iniciativa incrível! 🌱"
}
```

**Validações:**
- `user_id`: obrigatório
- `content`: obrigatório, mínimo 1 caractere

**Response:**
```json
{
  "message": "Comentário adicionado com sucesso"
}
```

**Importante:** O comentário aparece imediatamente no array `comments` do post com nome + foto do usuário (enriquecido no backend)

---

### 4.8 Remover Comentário

**Endpoint:**
```
DELETE /posts/{post_id}/comment/{comment_index}?user_id={user_id}
```

**Parâmetros:**
- `comment_index`: Posição do comentário no array (0, 1, 2...)
- `user_id`: ID de quem está removendo (validação: só o autor pode remover)

**Validações:**
- Apenas o autor do comentário pode remover
- O comment_index deve existir no array

**Response:**
```json
{
  "message": "Comentário deletado com sucesso"
}
```

**Tratamento de erro (403 Forbidden):**
```json
{
  "detail": "Você não tem permissão para deletar este comentário"
}
```

---

### 4.9 Editar Post

**Endpoint:**
```
PUT /posts/{post_id}
```

**Request Body (todos opcionais):**
```json
{
  "content": "Texto atualizado",
  "location": "Novo local",
  "sustainable_action": "Nova ação",
  "event_id": null,
  "image_url": "nova-url.jpg"
}
```

**Behavior:** Atualiza apenas os campos fornecidos

**Response:**
```json
{
  "message": "Post atualizado com sucesso"
}
```

---

### 4.10 Deletar Post

**Endpoint:**
```
DELETE /posts/{post_id}?user_id={user_id}
```

**Validações:**
- Apenas o dono do post pode deletar
- Valida se user_id === post.user_id

**Response:**
```json
{
  "message": "Post deletado com sucesso"
}
```

**Tratamento de erro (403 Forbidden):**
```json
{
  "detail": "Você não tem permissão para deletar este post"
}
```

---

## 5. Padrões de Integração Frontend

### 5.1 Fluxo de Autenticação

```
┌─────────────────────────────────────────────────────────┐
│ 1. Usuário preenche formulário e clica "Cadastrar"     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Validar localmente (email format, password strength)│
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 3. POST /auth/register com dados completos             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Sucesso? (200)       │
        └──────────────────────┘
         │                  │
         ▼ Sim              ▼ Não
    ┌─────────────────┐  ┌────────────────────┐
    │ Redirecionar    │  │ Exibir erro        │
    │ para login      │  │ (email duplicado?) │
    └─────────────────┘  └────────────────────┘
```

### 5.2 Fluxo de Login

```
POST /auth/login
    ▼
Recebe token JWT
    ▼
localStorage.setItem('access_token', token)
    ▼
Decodificar token: jwt_decode(token)
    ▼
Extrair user_id e armazenar
    ▼
localStorage.setItem('user_id', user_id)
    ▼
GET /profiles/user/{user_id}
    ▼
Armazenar dados do perfil em estado global (Context/Redux)
    ▼
Redirecionar para home/feed
```

### 5.3 Armazenamento de Dados no Frontend

**localStorage:**
```javascript
localStorage.setItem('access_token', token);     // Para futuros requests
localStorage.setItem('user_id', user_id);        // Para operações do usuário
```

**Estado Global (Redux/Context):**
```javascript
{
  user: {
    id: "...",
    name: "João Silva",
    email: "joao@ufrpe.edu.br",
    role: "student",
    profile_photo_url: "...",
    ...
  },
  posts: [],
  feed: [],
  notifications: []
}
```

### 5.4 Interceptors HTTP (Exemplo Axios)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Interceptor para adicionar user_id em query params quando necessário
api.interceptors.request.use(config => {
  const user_id = localStorage.getItem('user_id');
  if (user_id && config.url.includes('?')) {
    config.url += `&user_id=${user_id}`;
  } else if (user_id && config.method === 'delete') {
    config.url += `?user_id=${user_id}`;
  }
  return config;
});

// Interceptor para tratamento de erros global
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expirado - redirecionar para login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 6. Exemplos de Uso (React)

### 6.1 Hook para Posts

```javascript
// usePost.js
import { useState, useEffect } from 'react';
import api from './api';

export function usePost(postId) {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get(`/posts/${postId}`)
      .then(res => setPost(res.data))
      .catch(err => setError(err.response?.data?.detail))
      .finally(() => setLoading(false));
  }, [postId]);

  const likePost = async () => {
    try {
      await api.post(`/posts/${postId}/like`);
      // Recarregar post para atualizar likes
      const res = await api.get(`/posts/${postId}`);
      setPost(res.data);
    } catch (err) {
      setError(err.response?.data?.detail);
    }
  };

  const addComment = async (content) => {
    try {
      const user_id = localStorage.getItem('user_id');
      await api.post(`/posts/${postId}/comment`, {
        user_id,
        content
      });
      // Recarregar post
      const res = await api.get(`/posts/${postId}`);
      setPost(res.data);
    } catch (err) {
      setError(err.response?.data?.detail);
    }
  };

  return { post, loading, error, likePost, addComment };
}
```

### 6.2 Componente de Post

```javascript
function PostCard({ postId }) {
  const { post, likePost, addComment } = usePost(postId);
  const userId = localStorage.getItem('user_id');

  if (!post) return <div>Carregando...</div>;

  const hasLiked = post.liked_by.some(like => like.user_id === userId);

  return (
    <article className="post">
      <header>
        <img src={post.user_photo} alt={post.user_name} />
        <div>
          <h3>{post.user_name}</h3>
          <time>{new Date(post.created_at).toLocaleString()}</time>
        </div>
      </header>

      <p>{post.content}</p>
      {post.image_url && <img src={post.image_url} alt="Post" />}

      {/* Likes */}
      <section className="likes">
        <button 
          onClick={likePost}
          className={hasLiked ? 'liked' : ''}
        >
          ❤️ {post.likes}
        </button>
        
        {/* Lista de quem curtiu */}
        <div className="liked-by">
          {post.liked_by.map(user => (
            <div key={user.user_id}>
              <img src={user.user_photo} alt={user.user_name} />
              <span>{user.user_name}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Comentários */}
      <section className="comments">
        {post.comments.map((comment, index) => (
          <div key={index} className="comment">
            <img src={comment.user_photo} alt={comment.user_name} />
            <div>
              <strong>{comment.user_name}</strong>
              <p>{comment.content}</p>
            </div>
          </div>
        ))}
      </section>

      {/* Input para novo comentário */}
      <form onSubmit={(e) => {
        e.preventDefault();
        const content = e.target.comment.value;
        addComment(content);
        e.target.reset();
      }}>
        <input 
          type="text" 
          name="comment" 
          placeholder="Escreva um comentário..."
          required
        />
        <button type="submit">Enviar</button>
      </form>
    </article>
  );
}

export default PostCard;
```

---

## 7. Checklist de Integração

### Antes de Produção:

- [ ] Autenticação JWT implementada
- [ ] Tokens armazenados seguramente (não em localStorage se sensível)
- [ ] Tratamento de erros global
- [ ] Refresh token quando expirar
- [ ] Validação local de emails e senhas
- [ ] Upload de imagens para URL pública (AWS S3, Cloudinary, etc.)
- [ ] Feed carregando dados com paginação (não todos de uma vez)
- [ ] Tratamento de loading e error states
- [ ] Feedback visual para ações (curtir, comentar, deletar)
- [ ] Confirmação antes de deletar posts
- [ ] CORS habilitado apenas para domínio do frontend
- [ ] HTTPS em produção
- [ ] Rate limiting na API
- [ ] Logs de erro no frontend

---

## 8. Troubleshooting Comum

### Erro 403 ao deletar post
**Causa:** `user_id` no query param não matches com `post.user_id`
**Solução:** Verificar se está passando o user_id correto do usuário logado

### Comentários aparecem sem nome/foto
**Causa:** Backend não encontrou perfil do usuário
**Solução:** Garantir que perfil foi criado (feito automaticamente no registro, mas verificar)

### Likes duplicando
**Causa:** Clicando múltiplas vezes rapidamente
**Solução:** Desabilitar botão durante request ou usar `disabled` state

### Token expirando sem aviso
**Causa:** Sem implementar refresh token
**Solução:** Implementar refresh token flow ou reautenticar quando receber 401

### Feed muito lento
**Causa:** Carregando todos os posts de uma vez
**Solução:** Implementar paginação: `GET /posts/?limit=10&offset=0`

---

## 9. Roadmap - Funcionalidades Futuras Recomendadas

- [ ] Sistema de seguir/deixar de seguir
- [ ] Notificações de novos comentários/curtidas
- [ ] Busca de posts por palavras-chave
- [ ] Upload direto de imagens (não URL externa)
- [ ] Editar comentários
- [ ] Sistema de rankings/badges por contribuições
- [ ] Filtros por tipo de ação sustentável
- [ ] Gráficos de impacto (árvores plantadas, CO2 economizado, etc.)
- [ ] Compartilhar posts
- [ ] Denunciar posts inadequados

---

**Última atualização:** 2025-05-18
**Versão API:** 1.0.0
