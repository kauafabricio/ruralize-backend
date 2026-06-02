# Prompt de Integração Frontend - Backend Ruralize

Você precisa integrar o frontend com o backend Ruralize. Aqui está o mapeamento das APIs disponíveis e como usá-las:

## Configuração Base (utils/api.ts ou api.js)

Crie um arquivo de configuração do axios com a URL base:
- URL Base: `https://rural-backend.vercel.app/` (desenvolvimento)
- Headers: incluir token JWT se disponível
- Interceptadores para tratamento de erros

## Módulos de API Necessários

Crie um arquivo de service para cada módulo:

### 1. **authService** - Autenticação (/auth)
```
POST /auth/register
  Body: { email, password, name }
  Response: { access_token, user_id }

POST /auth/login
  Body: { email, password }
  Response: { access_token, user_id }
```

**Páginas que usam:**
- Página de Login (componente LoginForm)
- Página de Cadastro (componente RegisterForm)
- Persistir token no localStorage após login

---

### 2. **feedService** - Feed (/feed)
```
GET /feed/
  Query params: ?user_id=xxx (opcional)
  Response: lista de posts
  
GET /feed/friends/{user_id}
  Response: feed dos amigos do usuário
```

**Páginas que usam:**
- Página Home/Feed - chamar ao carregar
- Feed geral (sem user_id logado mostra público)
- Atualizar ao criar novo post

---

### 3. **postService** - Posts (/posts)
```
GET /posts/
  Response: todos os posts

GET /posts/{post_id}
  Response: detalhes de um post

POST /posts/
  Query params: ?user_id=xxx
  Body: { title, content, tags }
  Response: { post_id }

PUT /posts/{post_id}
  Body: { title, content, tags }
  Response: { success: true }

DELETE /posts/{post_id}
  Query params: ?user_id=xxx
  Response: { success: true }

POST /posts/{post_id}/like
  Query params: ?user_id=xxx
  Response: { success: true }

DELETE /posts/{post_id}/like
  Query params: ?user_id=xxx
  Response: { success: true }

POST /posts/{post_id}/comment
  Body: { user_id, content }
  Response: { success: true }

DELETE /posts/{post_id}/comment/{comment_index}
  Query params: ?user_id=xxx
  Response: { success: true }
```

**Páginas que usam:**
- Componente PostCard (exibição, like, comentário)
- Modal/Página de criar post
- Modal/Página de editar post
- Página de detalhes do post

---

### 4. **profileService** - Perfis (/profiles)
```
GET /profiles/user/{user_id}
  Response: perfil completo do usuário

PUT /profiles/user/{user_id}
  Body: { bio, profile_photo_url, tags, course, department }
  Response: { success: true }

GET /profiles/
  Response: lista de todos os perfis

GET /profiles/search/by-name?name=xxx
  Response: lista de perfis filtrados

GET /profiles/search/by-course?course=xxx
  Response: lista de perfis do curso

GET /profiles/search/by-department?department=xxx
  Response: lista de perfis do departamento

GET /profiles/search/by-role/{role}
  Response: lista de perfis por role (student/teacher)

GET /profiles/search/by-tags?tags=tag1&tags=tag2
  Response: lista de perfis com as tags
```

**Páginas que usam:**
- Página de Perfil (GET e PUT para atualizar)
- Página de Busca de Usuários
- Componente de Filtro por Papel/Curso/Departamento
- Componente de Busca por Tags
- Listagem de usuários com mesmo interesse

---

## Estrutura de Pastas Sugerida (Frontend)

```
src/
├── pages/
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Feed.jsx
│   ├── CreatePost.jsx
│   ├── EditPost.jsx
│   ├── PostDetail.jsx
│   ├── Profile.jsx
│   ├── EditProfile.jsx
│   ├── SearchUsers.jsx
│   └── UserProfile.jsx
├── components/
│   ├── PostCard.jsx
│   ├── CommentSection.jsx
│   ├── UserSearchFilter.jsx
│   ├── ProfileCard.jsx
│   └── LoginForm.jsx
├── services/
│   ├── api.js (configuração axios)
│   ├── authService.js
│   ├── feedService.js
│   ├── postService.js
│   └── profileService.js
└── context/ ou hooks/
    └── AuthContext.js (gerenciar usuário logado)
```

---

## Padrão de Implementação

Para cada service, siga este padrão:

```javascript
// postService.js
import api from './api';

export const getPosts = async () => {
  const response = await api.get('/posts/');
  return response.data;
};

export const createPost = async (postData, userId) => {
  const response = await api.post('/posts/', postData, {
    params: { user_id: userId }
  });
  return response.data;
};
```

Nas páginas, importe e use assim:

```javascript
// Feed.jsx
import { getFeed } from '../services/feedService';

const Feed = () => {
  const [posts, setPosts] = useState([]);
  
  useEffect(() => {
    getFeed().then(setPosts).catch(console.error);
  }, []);
  
  return <div>{/* renderizar posts */}</div>;
};
```

---

## Armazenamento de Dados

- **Token JWT**: localStorage (localStorage.getItem/setItem('authToken'))
- **Usuário Logado**: context/state global (ex: AuthContext)
- **Dados Temporários**: state dos componentes

---

## Importante

1. Sempre adicione o `user_id` do usuário logado nas requisições POST/DELETE que precisem
2. Recupere o token do localStorage antes de fazer requisições protegidas
3. Trate erros com try/catch ou .catch() nas requisições
4. Após criar/deletar/atualizar posts, atualize o feed localmente
5. O backend está em `https://rural-backend.vercel.app/`, ajuste a URL se necessário

---

## Endpoints Resumidos

| Método | Endpoint | Uso |
|--------|----------|-----|
| POST | /auth/register | Cadastro |
| POST | /auth/login | Login |
| GET | /feed/ | Feed geral |
| GET | /feed/friends/{id} | Feed de amigos |
| GET | /posts/ | Todos os posts |
| POST | /posts/ | Criar post |
| POST | /posts/{id}/like | Curtir post |
| POST | /posts/{id}/comment | Comentar |
| GET | /profiles/ | Todos os perfis |
| PUT | /profiles/user/{id} | Atualizar perfil |
| GET | /profiles/search/by-name?name=x | Buscar por nome |
