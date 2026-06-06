# Integração do Frontend - Sistema de Recompensas

## Resumo das Mudanças

O fluxo de resgate de recompensas foi **completamente reestruturado** no backend. O frontend agora **não precisa** fornecer o e-mail do usuário - o backend cuida de tudo isso.

## Mudança Principal: Não Use Mais `user.email`

### ❌ ANTES (Incorreto)
```javascript
// Não faça isso mais
const redeemReward = async (rewardId) => {
  const response = await fetch('/api/rewards/redeem', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': user.id
    },
    body: JSON.stringify({
      reward_id: rewardId,
      email: user.email  // ❌ REMOVIDO - NÃO FAÇA ISSO
    })
  });
};
```

### ✓ DEPOIS (Correto)
```javascript
// Faça assim agora
const redeemReward = async (rewardId) => {
  const response = await fetch('/api/rewards/redeem', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': user.id  // ID do usuário autenticado
    },
    body: JSON.stringify({
      reward_id: rewardId   // Apenas o ID da recompensa
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // Resgate bem-sucedido
    console.log('Resgate confirmado:', result.data.redemption_code);
    // E-mail foi enviado automaticamente
  } else {
    // Tratar erro
    console.error(result.message);
    console.error(result.error_code);
  }
};
```

## Novo Endpoint

### `POST /rewards/redeem`

**URL Completa:**
```
POST https://seu-backend.com/rewards/redeem
```

**Headers Obrigatórios:**
```
Content-Type: application/json
X-User-Id: {id_do_usuario_autenticado}
```

**Request Body:**
```json
{
  "reward_id": "id_da_recompensa"
}
```

**Response (Sucesso - 200):**
```json
{
  "success": true,
  "message": "Recompensa resgatada com sucesso! Verifique seu e-mail para os detalhes",
  "data": {
    "redemption_id": "65a1b2c3d4e5f6g7h8i9j0k1",
    "user_id": "usuario_123",
    "reward_id": "reward_456",
    "reward_name": "Garrafinha Reutilizável Ruralize",
    "user_email": "usuario@ufrpe.edu.br",
    "user_name": "João Silva",
    "points_deducted": 100,
    "redemption_code": "A7K9M2P4",
    "pickup_deadline": "2024-12-15T10:30:00",
    "status": "confirmed",
    "email_sent_at": "2024-12-08T10:30:00"
  }
}
```

**Response (Erro - Pontos Insuficientes - 402):**
```json
{
  "success": false,
  "message": "Pontos insuficientes. Você tem 50 pontos e precisa de 100",
  "error_code": "INSUFFICIENT_POINTS",
  "current_balance": 50,
  "points_required": 100
}
```

**Response (Erro - Outro - 400/404/500):**
```json
{
  "success": false,
  "message": "Descrição do erro",
  "error_code": "CODIGO_DO_ERRO"
}
```

## O que Acontece Automaticamente no Backend

Quando o usuário clica em "Resgatar Recompensa":

1. ✓ Backend busca o usuário no banco pelo `user_id`
2. ✓ Backend recupera **nome** e **e-mail** do usuário automaticamente
3. ✓ Backend busca a recompensa no banco
4. ✓ Backend valida se o usuário tem pontos suficientes
5. ✓ Backend gera um código único de resgate
6. ✓ **Backend envia e-mail automaticamente** para confirmar o resgate
7. ✓ Backend descontar os pontos do usuário
8. ✓ Backend registra o resgate no banco de dados
9. ✓ Backend retorna os detalhes do resgate (incluindo código)

## Tratamento de Erros no Frontend

```javascript
const redeemReward = async (rewardId) => {
  try {
    const response = await fetch('/rewards/redeem', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userId
      },
      body: JSON.stringify({ reward_id: rewardId })
    });

    const result = await response.json();

    if (!result.success) {
      // Tratar diferentes tipos de erro
      switch (result.error_code) {
        case 'USER_NOT_FOUND':
          showError('Usuário não encontrado');
          break;
        case 'REWARD_NOT_FOUND':
          showError('Recompensa não encontrada');
          break;
        case 'INSUFFICIENT_POINTS':
          showError(
            `Pontos insuficientes. Você tem ${result.current_balance} pontos ` +
            `e precisa de ${result.points_required}`
          );
          break;
        case 'NO_EMAIL_REGISTERED':
          showError('Seu usuário não possui e-mail cadastrado');
          break;
        case 'EMAIL_SEND_ERROR':
          showError('Erro ao enviar confirmação por e-mail. Tente novamente.');
          break;
        default:
          showError(result.message || 'Erro ao resgatar recompensa');
      }
      return;
    }

    // Sucesso!
    const { redemption_code, user_email } = result.data;
    showSuccess(
      `Resgate confirmado! Código: ${redemption_code}\n` +
      `Confirmação foi enviada para ${user_email}`
    );

  } catch (error) {
    console.error('Erro:', error);
    showError('Erro ao processar resgate');
  }
};
```

## Endpoints Adicionais Disponíveis

### 1. Listar Resgates do Usuário
```
GET /rewards/user/redemptions
Header: X-User-Id: {user_id}

Response:
{
  "success": true,
  "data": [
    {
      "id": "...",
      "user_name": "João Silva",
      "reward_name": "Garrafinha",
      "redemption_code": "A7K9M2P4",
      "status": "confirmed",
      "pickup_deadline": "2024-12-15T10:30:00",
      "redeemed_at": "2024-12-08T10:30:00"
    }
  ]
}
```

### 2. Buscar Resgate por Código
```
GET /rewards/code/{codigo_resgate}

Response:
{
  "success": true,
  "data": {
    "id": "...",
    "reward_name": "Garrafinha",
    "status": "confirmed",
    "pickup_deadline": "2024-12-15T10:30:00",
    "redemption_code": "A7K9M2P4"
  }
}
```

### 3. Confirmar Coleta (quando usuário retira a recompensa)
```
POST /rewards/code/{codigo_resgate}/collect

Response:
{
  "success": true,
  "message": "Recompensa marcada como coletada"
}
```

## Atualizar a Interface do Usuário

### Exemplo: Card de Recompensa

```javascript
const RewardCard = ({ reward, userId, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [userPoints, setUserPoints] = useState(0);

  const handleRedeem = async () => {
    setLoading(true);
    try {
      const response = await fetch('/rewards/redeem', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        },
        body: JSON.stringify({ reward_id: reward.id })
      });

      const result = await response.json();

      if (result.success) {
        // Mostrar sucesso com código de resgate
        showSuccessModal({
          title: 'Resgate Confirmado! ✓',
          message: `Código de Resgate: ${result.data.redemption_code}`,
          subtext: `Confirmação foi enviada para ${result.data.user_email}`
        });
        onSuccess();
      } else {
        showErrorModal({
          title: 'Erro no Resgate',
          message: result.message,
          code: result.error_code
        });
      }
    } catch (error) {
      console.error('Error:', error);
      showErrorModal({ message: 'Erro ao conectar com servidor' });
    } finally {
      setLoading(false);
    }
  };

  const canRedeem = userPoints >= reward.points_required;

  return (
    <div className="reward-card">
      <img src={reward.image_url} alt={reward.name} />
      <h3>{reward.name}</h3>
      <p>{reward.description}</p>
      <div className="points-info">
        <span className="points-required">
          {reward.points_required} pontos
        </span>
        {!canRedeem && (
          <span className="points-short">
            Faltam {reward.points_required - userPoints} pontos
          </span>
        )}
      </div>
      <button
        onClick={handleRedeem}
        disabled={!canRedeem || loading}
        className={canRedeem ? 'btn-primary' : 'btn-disabled'}
      >
        {loading ? 'Processando...' : 'Resgatar'}
      </button>
    </div>
  );
};
```

## Checklist para Atualizar o Frontend

- [ ] Remover qualquer referência a `user.email` nas requisições de resgate
- [ ] Atualizar o endpoint de `/api/redeem-reward` para `/rewards/redeem`
- [ ] Adicionar header `X-User-Id` com o ID do usuário
- [ ] Atualizar o corpo da requisição para incluir apenas `reward_id`
- [ ] Adicionar tratamento para novos códigos de erro
- [ ] Exibir o `redemption_code` para o usuário
- [ ] Mostrar mensagem de sucesso com confirmação de e-mail
- [ ] Testar fluxo completo
- [ ] Verificar logs do backend para qualquer erro de SMTP

## E-mail Enviado para o Usuário

Quando um resgate é bem-sucedido, o usuário recebe um e-mail com:

```
Assunto: Sua recompensa está disponível para resgate

Olá, João Silva.

Seu resgate foi processado com sucesso e sua recompensa já está disponível para retirada.

📦 Recompensa: Garrafinha Reutilizável Ruralize
📍 Local de Retirada: Sala 24 - DC Sala Ruralize
📅 Data para Retirada: Até 15/12/2024
🕒 Horário de Atendimento: 14h - 18h
🔑 Código de Resgate: A7K9M2P4

Apresente este código juntamente com um documento de identificação no momento da retirada.

Caso tenha dúvidas, entre em contato com a equipe Ruralize.

Atenciosamente,
Equipe Ruralize
ruralizecontato@gmail.com
```

## Dicas de Segurança

✓ Sempre valide o `X-User-Id` no backend (já implementado)
✓ Não confie em IDs vindo do frontend apenas
✓ Os pontos são desconto apenas após sucesso
✓ Códigos de resgate são únicos e imutáveis
✓ Todos os eventos são registrados em logs

## Suporte

Para questões sobre a API, consulte:
- [SMTP_CONFIGURATION.md](./SMTP_CONFIGURATION.md) - Configuração de e-mail
- [BACKEND_DOCUMENTATION.md](./BACKEND_DOCUMENTATION.md) - Documentação geral
- Logs do backend em caso de erro
