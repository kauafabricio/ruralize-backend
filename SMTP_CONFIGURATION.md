# Configuração SMTP para Envio de E-mails de Recompensas

## Visão Geral

O backend agora implementa um sistema completo de envio de e-mails para confirmação de resgate de recompensas. O sistema utiliza SMTP (Simple Mail Transfer Protocol) para enviar os e-mails através da conta `ruralizecontato@gmail.com`.

## Variáveis de Ambiente Necessárias

Adicione as seguintes variáveis ao seu arquivo `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=ruralizecontato@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_USE_TLS=true
```

### Descrição de Cada Variável

| Variável | Valor | Tipo | Descrição |
|----------|-------|------|-----------|
| `SMTP_HOST` | `smtp.gmail.com` | String | Servidor SMTP do Gmail |
| `SMTP_PORT` | `587` | Integer | Porta padrão do Gmail com TLS |
| `SMTP_EMAIL` | `ruralizecontato@gmail.com` | String | E-mail da conta que enviará os e-mails |
| `SMTP_PASSWORD` | Senha de Aplicativo (16 chars) | String | **Senha de Aplicativo gerada no Gmail** |
| `SMTP_USE_TLS` | `true` | Boolean | Usar criptografia TLS (obrigatório para porta 587) |

## Guia de Configuração - Gmail

### Passo 1: Ativar Verificação em Duas Etapas

1. Acesse [Google Account Security](https://myaccount.google.com/security)
2. Faça login com `ruralizecontato@gmail.com`
3. Procure por "Verificação em duas etapas" e ative-a
4. Confirme seu número de telefone

### Passo 2: Gerar Senha de Aplicativo

1. Acesse [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Certifique-se de estar logado em `ruralizecontato@gmail.com`
3. Selecione:
   - **Aplicativo**: "Mail"
   - **Dispositivo**: "Windows Computer" (ou seu SO)
4. Clique em "Gerar"
5. Google exibirá uma senha com 16 caracteres espaçados: `xxxx xxxx xxxx xxxx`

### Passo 3: Copiar a Senha de Aplicativo

```
Exemplo de Senha Gerada: abcd efgh ijkl mnop
```

Use exatamente como mostrado (com espaços ou sem, ambos funcionam):
```env
SMTP_PASSWORD=abcd efgh ijkl mnop
# ou
SMTP_PASSWORD=abcdefghijklmnop
```

### Passo 4: Testar a Conexão

Você pode testar a conexão SMTP antes de usar:

```python
from app.services.email_service import EmailService
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_USE_TLS

email_service = EmailService(
    smtp_host=SMTP_HOST,
    smtp_port=SMTP_PORT,
    sender_email=SMTP_EMAIL,
    sender_password=SMTP_PASSWORD,
    use_tls=SMTP_USE_TLS
)

# Testar conexão
if email_service.test_connection():
    print("✓ Conexão SMTP funcionando corretamente")
else:
    print("✗ Erro na conexão SMTP")
```

## Implementação no Código

O sistema implementa:

1. **EmailService** (`app/services/email_service.py`):
   - Gerencia conexões SMTP
   - Envia e-mails HTML com fallback para texto plano
   - Implementa logging para depuração
   - Trata erros de autenticação e conexão

2. **RewardService** (`app/services/reward_service.py`):
   - Integra o EmailService no fluxo de resgate
   - Descontar pontos apenas após envio de e-mail bem-sucedido
   - Gera códigos únicos de resgate

3. **RewardController** (`app/controllers/reward_controller.py`):
   - Endpoint: `POST /rewards/redeem`
   - Requer autenticação (header `x_user_id`)
   - Processa resgate de forma segura

## Fluxo de Resgate Implementado

```
1. Frontend envia POST /rewards/redeem com { reward_id }
   ↓
2. Backend valida usuario existe
   ↓
3. Backend busca recompensa no banco
   ↓
4. Backend verifica saldo de pontos do usuario
   ↓
5. Backend gera codigo unico de resgate
   ↓
6. Backend ENVIA E-MAIL com confirmacao
   ↓
7. Se email enviado com SUCESSO:
   - Deduz pontos do usuario
   - Registra resgate no banco
   - Incrementa contador de resgates
   - Retorna sucesso ao frontend
   ↓
8. Se email FALHOU:
   - NÃO deduz pontos
   - NÃO registra resgate
   - Retorna erro ao frontend
```

## Modelo do E-mail Implementado

**Assunto:** Sua recompensa está disponível para resgate

**Corpo (HTML + Texto Plano):**

```
Olá, [Nome do Usuário].

Seu resgate foi processado com sucesso e sua recompensa já está disponível para retirada.

📦 Recompensa: [Nome da Recompensa]
📍 Local de Retirada: Sala 24 - DC Sala Ruralize
📅 Data para Retirada: Até [DD/MM/YYYY - 7 dias após resgate]
🕒 Horário de Atendimento: 14h - 18h
🔑 Código de Resgate: [CÓDIGO_ÚNICO]

Apresente este código juntamente com um documento de identificação no momento da retirada.

Caso tenha dúvidas, entre em contato com a equipe Ruralize.

Atenciosamente,
Equipe Ruralize
ruralizecontato@gmail.com
```

## Endpoints Disponíveis

### 1. Resgatar Recompensa
```
POST /rewards/redeem
Header: x_user_id: {user_id}
Body: { "reward_id": "{reward_id}" }

Response (Sucesso):
{
  "success": true,
  "message": "Recompensa resgatada com sucesso!",
  "data": {
    "redemption_id": "...",
    "user_id": "...",
    "reward_id": "...",
    "redemption_code": "ABC123DE",
    "pickup_deadline": "2024-12-15T10:30:00",
    "status": "confirmed"
  }
}
```

### 2. Listar Resgates do Usuário
```
GET /rewards/user/redemptions
Header: x_user_id: {user_id}

Response:
{
  "success": true,
  "data": [
    {
      "id": "...",
      "reward_name": "Garrafinha Reutilizável",
      "redemption_code": "ABC123DE",
      "status": "confirmed",
      "redeemed_at": "2024-12-08T10:30:00"
    }
  ]
}
```

### 3. Buscar Resgate por Código
```
GET /rewards/code/{codigo_resgate}

Response:
{
  "success": true,
  "data": {
    "redemption_code": "ABC123DE",
    "reward_name": "...",
    "status": "confirmed",
    "pickup_deadline": "2024-12-15T10:30:00"
  }
}
```

### 4. Marcar Resgate como Coletado
```
POST /rewards/code/{codigo_resgate}/collect

Response:
{
  "success": true,
  "message": "Recompensa marcada como coletada"
}
```

## Códigos de Erro

| Código | Status HTTP | Significado |
|--------|-------------|-------------|
| `USER_NOT_FOUND` | 404 | Usuário não encontrado |
| `REWARD_NOT_FOUND` | 404 | Recompensa não encontrada |
| `NO_EMAIL_REGISTERED` | 400 | Usuário não possui e-mail cadastrado |
| `INSUFFICIENT_POINTS` | 402 | Usuário não possui pontos suficientes |
| `EMAIL_SEND_ERROR` | 400 | Erro ao enviar e-mail |
| `INTERNAL_SERVER_ERROR` | 500 | Erro inesperado no servidor |

## Debugging

### Verificar Logs
O backend registra todos os eventos de envio de e-mail:

```
INFO: Processing reward redemption for user 123 (João Silva - joao@example.com)
INFO: Generated redemption code: ABC123DE
INFO: Email sent successfully to joao@example.com
INFO: Points transaction created: trans_xyz
INFO: Redemption recorded: redemp_xyz
```

### Erros Comuns

1. **SMTP Authentication Error**
   - Verifique se usou uma "Senha de Aplicativo" e não a senha regular
   - Confirme se a verificação em duas etapas está ativada
   - Teste a conexão: `email_service.test_connection()`

2. **Connection Refused**
   - Confirme firewall/proxy permite conexão na porta 587
   - Tente porta 465 com SSL (altere `SMTP_USE_TLS=false`)

3. **Email não enviado**
   - Verifique logs do backend
   - Confirme SMTP_EMAIL está correto
   - Valide destinatário tem e-mail cadastrado

## Suporte para Outros Servidores SMTP

Para usar outro servidor SMTP (não Gmail):

```env
SMTP_HOST=seu-servidor-smtp.com
SMTP_PORT=587  # ou 465 para SSL
SMTP_EMAIL=seu-email@seudominio.com
SMTP_PASSWORD=sua-senha
SMTP_USE_TLS=true  # false se usar SSL
```

## Segurança

✓ Senhas de aplicativo (não senha regular)
✓ TLS/SSL para criptografia
✓ Logging de tentativas e erros
✓ Validação de e-mail antes de envio
✓ Pontos desconto APÓS confirmação de envio
✓ Códigos de resgate únicos gerados com `secrets.token_hex()`

## Próximas Implementações

- [ ] Reenviar e-mail de confirmação
- [ ] Cancelamento de resgate
- [ ] Recordação por e-mail (2 dias antes do prazo)
- [ ] Dashboard admin para visualizar resgates
- [ ] Integração com WhatsApp/SMS
- [ ] Relatórios de resgates
