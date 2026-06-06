# Guia de Testes - Sistema de Recompensas

## 🧪 Pré-requisitos

1. Backend rodando: `python main.py`
2. MongoDB conectado
3. Variáveis de ambiente configuradas (ver `.env.example`)
4. Conta ruralizecontato@gmail.com com:
   - ✓ Verificação em duas etapas ativada
   - ✓ Senha de Aplicativo gerada e configurada

## 📋 Teste 1: Configuração SMTP

### Objetivo
Validar se a conexão SMTP está funcionando

### Código (Python REPL)
```python
from app.services.email_service import EmailService
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_USE_TLS

# Criar serviço
email = EmailService(SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_USE_TLS)

# Testar
if email.test_connection():
    print("✓ Conexão SMTP OK")
else:
    print("✗ Erro na conexão SMTP")
    print("Verificar: SMTP_PASSWORD, firewall, variáveis de ambiente")
```

### Resultado Esperado
```
✓ Conexão SMTP OK
```

---

## 📋 Teste 2: Envio de E-mail Manual

### Objetivo
Validar se o e-mail é enviado com sucesso

### Código (Python REPL)
```python
from app.services.email_service import EmailService
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_USE_TLS
from datetime import datetime, timedelta

email_service = EmailService(
    smtp_host=SMTP_HOST,
    smtp_port=SMTP_PORT,
    sender_email=SMTP_EMAIL,
    sender_password=SMTP_PASSWORD,
    use_tls=SMTP_USE_TLS
)

# Enviar e-mail de teste
success = email_service.send_reward_redemption_email(
    recipient_email="seu-email-teste@example.com",
    user_name="João Silva",
    reward_name="Garrafinha Reutilizável",
    redemption_code="TEST1234",
    pickup_location="Sala 24 - DC",
    office_hours="14h - 18h",
    days_valid=7
)

if success:
    print("✓ E-mail enviado com sucesso")
else:
    print("✗ Erro ao enviar e-mail")
```

### Resultado Esperado
- ✓ E-mail enviado
- ✓ E-mail chega na caixa de entrada
- ✓ Contém código TEST1234
- ✓ Contém prazo de 7 dias

---

## 📋 Teste 3: Teste do Endpoint de Resgate

### Objetivo
Testar o fluxo completo de resgate via API

### Pré-requisitos
```
- Ter um usuário criado no banco: user_id = "123456"
- Ter uma recompensa criada: reward_id = "789012"
- Usuário ter e-mail cadastrado
- Usuário ter 100+ pontos
```

### cURL (Terminal)
```bash
curl -X POST http://localhost:8000/rewards/redeem \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 123456" \
  -d '{"reward_id": "789012"}'
```

### Python (Requests)
```python
import requests

url = "http://localhost:8000/rewards/redeem"
headers = {
    "Content-Type": "application/json",
    "X-User-Id": "123456"
}
payload = {
    "reward_id": "789012"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print("Status Code:", response.status_code)
print("Response:", result)

if result.get("success"):
    print("✓ Resgate bem-sucedido")
    print("  - Código:", result["data"]["redemption_code"])
    print("  - E-mail:", result["data"]["user_email"])
else:
    print("✗ Erro:", result.get("message"))
    print("  - Código do erro:", result.get("error_code"))
```

### JavaScript (Fetch)
```javascript
const response = await fetch('http://localhost:8000/rewards/redeem', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-User-Id': '123456'
  },
  body: JSON.stringify({
    reward_id: '789012'
  })
});

const result = await response.json();
console.log(result);
```

### Resultado Esperado (Sucesso - HTTP 200)
```json
{
  "success": true,
  "message": "Recompensa resgatada com sucesso! Verifique seu e-mail para os detalhes",
  "data": {
    "redemption_id": "65a1b2c3d4e5f6g7h8i9j0k1",
    "user_id": "123456",
    "reward_id": "789012",
    "reward_name": "Garrafinha Reutilizável",
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

### Validações
- [x] Status code 200
- [x] `success: true`
- [x] Código de resgate gerado (ex: A7K9M2P4)
- [x] E-mail do usuário retornado
- [x] Pontos deduzidos registrado
- [x] Status `confirmed`
- [x] E-mail recebido na caixa de entrada

---

## 📋 Teste 4: Erro - Pontos Insuficientes

### Objetivo
Validar tratamento quando usuário não tem pontos

### Setup
```
- Usuário com apenas 10 pontos
- Recompensa requer 100 pontos
```

### Comando
```bash
curl -X POST http://localhost:8000/rewards/redeem \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user_com_10_pontos" \
  -d '{"reward_id": "recompensa_100_pontos"}'
```

### Resultado Esperado (HTTP 402)
```json
{
  "success": false,
  "message": "Pontos insuficientes. Você tem 10 pontos e precisa de 100",
  "error_code": "INSUFFICIENT_POINTS",
  "current_balance": 10,
  "points_required": 100
}
```

### Validações
- [x] Status code 402 (Payment Required)
- [x] `success: false`
- [x] Mensagem clara do erro
- [x] Saldo atual mostrado
- [x] Pontos requeridos mostrados
- [x] **IMPORTANTE**: Pontos NÃO foram deduzidos

---

## 📋 Teste 5: Erro - Usuário Não Encontrado

### Objetivo
Validar tratamento de usuário inexistente

### Comando
```bash
curl -X POST http://localhost:8000/rewards/redeem \
  -H "Content-Type: application/json" \
  -H "X-User-Id: usuario_inexistente" \
  -d '{"reward_id": "qualquer_recompensa"}'
```

### Resultado Esperado (HTTP 404)
```json
{
  "success": false,
  "message": "Usuário não encontrado",
  "error_code": "USER_NOT_FOUND"
}
```

---

## 📋 Teste 6: Erro - Sem E-mail Cadastrado

### Objetivo
Validar tratamento quando usuário não tem e-mail

### Setup
```
- Usuário no banco com campo email vazio/null
```

### Resultado Esperado (HTTP 400)
```json
{
  "success": false,
  "message": "Usuário não possui e-mail cadastrado",
  "error_code": "NO_EMAIL_REGISTERED"
}
```

---

## 📋 Teste 7: Verificar Pontos Deduzidos

### Objetivo
Confirmar que pontos foram deduzidos após resgate bem-sucedido

### Processo
```
1. Anotar saldo antes: GET /points (antes = 500)
2. Executar resgate de recompensa (100 pontos)
3. Verificar saldo depois: GET /points (depois = 400)
```

### Validação
- [x] Saldo anterior = 500
- [x] Resgate de 100 pontos bem-sucedido
- [x] Saldo posterior = 400
- [x] Transação registrada no histórico

---

## 📋 Teste 8: Verificar Resgate no Banco

### Objetivo
Confirmar que resgate foi registrado no MongoDB

### Query (MongoDB)
```javascript
// Verificar redemptions collection
db.reward_redemptions.find({
  user_id: "123456",
  reward_id: "789012"
}).pretty()
```

### Resultado Esperado
```javascript
{
  "_id": ObjectId("..."),
  "user_id": "123456",
  "user_email": "usuario@ufrpe.edu.br",
  "user_name": "João Silva",
  "reward_id": "789012",
  "reward_name": "Garrafinha Reutilizável",
  "points_deducted": 100,
  "redemption_code": "A7K9M2P4",
  "pickup_deadline": ISODate("2024-12-15T..."),
  "status": "confirmed",
  "email_sent_at": ISODate("2024-12-08T..."),
  "collected_at": null,
  "redeemed_at": ISODate("2024-12-08T...")
}
```

---

## 📋 Teste 9: Buscar Resgate por Código

### Objetivo
Validar endpoint para buscar resgate usando código

### Comando
```bash
curl -X GET "http://localhost:8000/rewards/code/A7K9M2P4"
```

### Resultado Esperado (HTTP 200)
```json
{
  "success": true,
  "data": {
    "id": "65a1b2c3d4e5f6g7h8i9j0k1",
    "user_id": "123456",
    "user_email": "usuario@ufrpe.edu.br",
    "user_name": "João Silva",
    "reward_id": "789012",
    "reward_name": "Garrafinha Reutilizável",
    "points_deducted": 100,
    "redemption_code": "A7K9M2P4",
    "pickup_deadline": "2024-12-15T10:30:00",
    "status": "confirmed"
  }
}
```

---

## 📋 Teste 10: Marcar como Coletado

### Objetivo
Validar quando usuário retira a recompensa

### Comando
```bash
curl -X POST "http://localhost:8000/rewards/code/A7K9M2P4/collect"
```

### Resultado Esperado (HTTP 200)
```json
{
  "success": true,
  "message": "Recompensa marcada como coletada"
}
```

### Verificação no Banco
```javascript
db.reward_redemptions.findOne({
  redemption_code: "A7K9M2P4"
})
// Deve ter:
// - status: "collected"
// - collected_at: ISODate("2024-12-08T...")
```

---

## 🔍 Verificação de Logs

### Verificar logs do backend
```bash
# Buscar em stdout do servidor
# Você deveria ver:
# INFO: Processing reward redemption for user 123456 (João Silva - usuario@ufrpe.edu.br)
# INFO: Generated redemption code: A7K9M2P4
# INFO: Email sent successfully to usuario@ufrpe.edu.br
# INFO: Points transaction created: trans_xyz
# INFO: Redemption recorded: redemp_xyz
```

---

## 📊 Checklist de Testes Completos

- [ ] Teste 1: Conexão SMTP OK
- [ ] Teste 2: E-mail manual enviado
- [ ] Teste 3: Endpoint retorna sucesso
- [ ] Teste 4: E-mail recebido no inbox
- [ ] Teste 5: Pontos deduzidos após resgate
- [ ] Teste 6: Pontos NÃO deduzido se email falhar
- [ ] Teste 7: Erro com pontos insuficientes (HTTP 402)
- [ ] Teste 8: Erro com usuário não encontrado (HTTP 404)
- [ ] Teste 9: Resgate registrado no MongoDB
- [ ] Teste 10: Buscar por código funciona
- [ ] Teste 11: Marcar como coletado funciona
- [ ] Teste 12: Logs aparecem corretamente
- [ ] Teste 13: E-mail tem formato correto
- [ ] Teste 14: Código de resgate é único
- [ ] Teste 15: Prazo de retirada é 7 dias

---

## 🐛 Troubleshooting

### Problema: SMTP Authentication Error

**Checklist:**
```
❌ Usando senha regular da conta? → Use Senha de Aplicativo
❌ Falta verificação em 2 etapas? → Ative em myaccount.google.com
❌ Variável SMTP_PASSWORD vazia? → Configure no .env
❌ Erro de digitação? → Copie exatamente da tela
```

### Problema: E-mail não chega

**Checklist:**
```
❌ Verificar spam/lixo eletrônico
❌ Confirmar se SMTP_EMAIL está correto
❌ Verificar logs para erros
❌ Testar com test_connection()
```

### Problema: Pontos não são deduzidos

**Checklist:**
```
❌ Confirmar se e-mail foi enviado (log)
❌ Verificar se transação foi criada
❌ Consultar points_transactions no MongoDB
```

### Problema: Status code diferente do esperado

**Checklist:**
```
400 → Erro de validação (verifique mensagem)
402 → Pontos insuficientes
404 → Usuário/recompensa não encontrado
500 → Erro interno (verifique logs)
```

---

## 📝 Template de Relatório de Teste

```markdown
# Teste de Recompensas - [DATA]

## Ambiente
- Backend: ✓/✗
- MongoDB: ✓/✗
- SMTP: ✓/✗

## Testes Executados
- [ ] Teste 1: ✓/✗
- [ ] Teste 2: ✓/✗
- [ ] Teste 3: ✓/✗
...

## Problemas Encontrados
- Problema A: [descrição]
  Solução: [como resolver]

## Conclusão
✓ Tudo OK / ✗ Ajustes necessários

## Assinado por: _______________  Data: ___/___/_____
```

---

## 💡 Dicas Úteis

**Limpar dados de teste:**
```javascript
// MongoDB
db.reward_redemptions.deleteMany({ user_id: "teste" })
db.points_transactions.deleteMany({ user_id: "teste" })
```

**Resetar status de resgate:**
```javascript
db.reward_redemptions.updateMany(
  { redemption_code: "A7K9M2P4" },
  { $set: { status: "confirmed", collected_at: null } }
)
```

**Criar usuário de teste:**
```javascript
db.users.insertOne({
  name: "João Teste",
  email: "teste@example.com",
  password: "hashed_password",
  points_balance: 500,
  role: "student"
})
```

---

**Última atualização: 08/12/2024**
