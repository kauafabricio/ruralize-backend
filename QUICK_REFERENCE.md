# ⚡ Quick Reference - Sistema de Recompensas

## 🚀 Setup Rápido (5 minutos)

### 1️⃣ Configurar .env
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=ruralizecontato@gmail.com
SMTP_PASSWORD=senha_app_16_caracteres
SMTP_USE_TLS=true
```

### 2️⃣ Gerar Senha de App (Gmail)
1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione: Mail + Windows (ou seu SO)
3. Copie: `xxxx xxxx xxxx xxxx` → Cole em `SMTP_PASSWORD`

### 3️⃣ Testar Conexão
```bash
# Terminal Python
from app.services.email_service import EmailService
from app.core.config import *

service = EmailService(SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_USE_TLS)
print(service.test_connection())  # True = OK
```

### 4️⃣ Iniciar Backend
```bash
python main.py
# Backend rodando em http://localhost:8000
```

---

## 🔗 Endpoint Principal

```http
POST /rewards/redeem
Content-Type: application/json
X-User-Id: {user_id}

{
  "reward_id": "{reward_id}"
}
```

**Resposta (Sucesso):**
```json
{
  "success": true,
  "data": {
    "redemption_code": "A7K9M2P4",
    "user_email": "usuario@ufrpe.edu.br",
    "pickup_deadline": "2024-12-15T..."
  }
}
```

---

## 📋 Checklist de Variáveis

| Variável | Valor | Requerido |
|----------|-------|-----------|
| `SMTP_HOST` | `smtp.gmail.com` | ✓ |
| `SMTP_PORT` | `587` | ✓ |
| `SMTP_EMAIL` | `ruralizecontato@gmail.com` | ✓ |
| `SMTP_PASSWORD` | Senha app 16 chars | ✓ |
| `SMTP_USE_TLS` | `true` | ✓ |

---

## 🎯 O que Muda no Frontend

### ❌ Antes (REMOVIDO)
```javascript
// Não faça mais assim
body: JSON.stringify({
  reward_id: rewardId,
  email: user.email  // ❌ NÃO
})
```

### ✅ Depois (NOVO)
```javascript
// Faça assim
body: JSON.stringify({
  reward_id: rewardId  // ✓ Só isso
})
```

---

## 📧 E-mail Template

**Para:** usuario@ufrpe.edu.br
**De:** ruralizecontato@gmail.com
**Assunto:** Sua recompensa está disponível para resgate

```
Olá, João Silva.

Seu resgate foi processado com sucesso e sua recompensa já está 
disponível para retirada.

📦 Recompensa: Garrafinha Reutilizável
📍 Local de Retirada: Sala 24 - DC Sala Ruralize
📅 Data para Retirada: Até 15/12/2024
🕒 Horário de Atendimento: 14h - 18h
🔑 Código de Resgate: A7K9M2P4

Apresente este código juntamente com um documento de identificação 
no momento da retirada.

Atenciosamente,
Equipe Ruralize
ruralizecontato@gmail.com
```

---

## 🔐 Segurança - O que Mudou

✓ Backend busca email (não frontend)
✓ Pontos desconto APÓS email OK
✓ Código único de resgate
✓ Logging completo
✓ TLS/SSL encryption

---

## 🧪 Teste Rápido (cURL)

```bash
curl -X POST http://localhost:8000/rewards/redeem \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 123456" \
  -d '{"reward_id":"789012"}'
```

**Resultado Esperado:**
- HTTP 200
- Campo `success: true`
- Código de resgate gerado
- E-mail recebido

---

## 📊 Status Codes

| Código | Significado |
|--------|-------------|
| 200 | Resgate OK ✓ |
| 400 | Erro validação |
| 402 | Pontos insuficientes |
| 404 | Não encontrado |
| 500 | Erro servidor |

---

## 🔄 Fluxo Automático

```
1. Frontend envia request
2. Backend valida usuário/pontos
3. Backend envia email ← NOVO
4. Se OK: deduz pontos
5. Se erro: cancela tudo
6. Retorna resposta
```

---

## 📁 Arquivos Importantes

| Arquivo | Propósito |
|---------|----------|
| `app/services/reward_service.py` | Lógica principal |
| `app/controllers/reward_controller.py` | Endpoints |
| `app/services/email_service.py` | Envio SMTP |
| `app/core/config.py` | Config SMTP |
| `.env` | Credenciais (não commit!) |

---

## 🚨 Erros Comuns

### SMTP Authentication Error
**Solução:**
1. Use Senha de Aplicativo, não senha regular
2. Ative 2FA em myaccount.google.com
3. Confirme SMTP_PASSWORD correto

### E-mail não chega
**Solução:**
1. Verificar spam/lixo
2. Verificar logs do backend
3. Testar com `test_connection()`

### Pontos não deduzem
**Solução:**
1. E-mail foi enviado? (check logs)
2. Usuario tem pontos? (check balance)

---

## 📞 Endpoints Extras

| Método | Rota | O que faz |
|--------|------|----------|
| GET | `/rewards/list` | Listar recompensas |
| GET | `/rewards/{id}` | Detalhes recompensa |
| GET | `/rewards/user/redemptions` | Meus resgates |
| GET | `/rewards/code/{code}` | Info por código |
| POST | `/rewards/code/{code}/collect` | Marcar coletado |

---

## 💾 Backup Before Deploy

```bash
# MongoDB
mongodump --db ruralize --out ./backup_$(date +%Y%m%d)

# Code
git add .
git commit -m "Reward system v1.0"
```

---

## 📚 Documentação Completa

- **SMTP_CONFIGURATION.md** - Setup SMTP detalhado
- **FRONTEND_INTEGRATION_REWARDS.md** - Como integrar frontend
- **TESTING_GUIDE.md** - Testes completos
- **IMPLEMENTATION_SUMMARY.md** - Resumo executivo
- **README_REWARDS.md** - Referência técnica

---

## 🎯 Próximas Etapas

1. [ ] Configurar `.env`
2. [ ] Testar SMTP
3. [ ] Integrar frontend
4. [ ] Testar fluxo
5. [ ] Deploy

---

## 🔥 Pro Tips

**Testar email manual:**
```python
from app.services.email_service import EmailService
service = EmailService(...)
service.send_reward_redemption_email(
    "seu-email@test.com",
    "João",
    "Recompensa",
    "ABC123DE"
)
```

**Resetar pontos de teste:**
```javascript
db.users.updateOne({_id: user_id}, {$set: {points_balance: 1000}})
```

**Ver resgate no banco:**
```javascript
db.reward_redemptions.findOne({redemption_code: "ABC123DE"})
```

---

**Versão:** 1.0.0  
**Data:** 08/12/2024  
**Status:** ✅ Pronto para Uso
