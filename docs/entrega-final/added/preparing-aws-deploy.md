# Preparando o deploy na AWS

**Status:** ✅ código pronto · 🔴 esperando você rodar `terraform apply`

Frontend já no ar (Vercel). Falta subir o backend + banco na AWS. Todo o trabalho de código e IaC necessário está commitado neste branch — basta rodar o Terraform quando estiver com a conta AWS configurada.

## Arquitetura

```
  Browser ─HTTPS─► Vercel (estático, public/)
                       │
                       └ /api/*  ─rewrite─► AWS App Runner (Node + Express)
                                                  │ VPC connector
                                                  ▼
                                            RDS MySQL 8 (VPC privada)
```

- **Vercel** (frontend, já no ar): <https://gym-control-pearl.vercel.app> · [`vercel.json`](../../../vercel.json)
- **App Runner** com VPC connector, imagem do ECR, secrets do Secrets Manager
- **RDS MySQL 8** `db.t4g.micro` privado, criptografado, backup retention de 1 dia
- **Secrets Manager** guarda `JWT_SECRET` e a senha master do DB (ambos gerados pelo Terraform)
- **ECR** hospeda a imagem Docker

## Decisões aplicadas

| Decisão | Escolha | Por quê |
|---|---|---|
| IaC | Terraform | Reproduz + destrói com um comando; portável; o usuário tem familiaridade |
| Auth | Cookie httpOnly (mantido) | Diretiva "sempre o mais seguro"; XSS-resistente. Custo: precisa de domínio compartilhado entre Vercel e AWS para funcionar entre origens |
| TTL HSTS | 1 dia (mínimo) | Projeto temporário (~2 meses); preload de 1 ano não se justifica |
| Backup RDS | 1 dia | Mínimo permitido pelo RDS; descartável |
| App Runner egress | VPC only (sem NAT) | Backend só fala com RDS, não precisa de internet → corta custo do NAT Gateway |
| DB user | `dbadmin` (master) | Para o auto-migrate funcionar, precisa de DDL. O `sql/05_app_user.sql` fica documentado para uma evolução futura (separar credenciais runtime ↔ admin) |

## Checklist completo

### ✅ Código (já no repo)

- [x] `lib/auth.js` — JWT em cookie httpOnly + SameSite=Strict
- [x] `lib/validators.js` — CPF format + check digit + `requireFields`
- [x] `lib/log-sanitizer.js` — remove CPF, email, hash, token antes do `console.error`
- [x] `lib/migrate.js` — auto-aplica schema+seed se `usuarios` não existir e `AUTO_MIGRATE=1`
- [x] Helmet com CSP estrita, HSTS habilitado em prod com TTL mínimo
- [x] CORS allowlist via `CORS_ORIGINS`
- [x] Rate limit (120/min na API, 5/min no `/api/auth/login`)
- [x] Guard de `JWT_SECRET` em produção (servidor recusa subir com o default)
- [x] Endpoint público `/healthz` para o health check do App Runner
- [x] Frontend sem nenhum handler inline (event delegation via `data-action`)
- [x] 117 testes (lint + Jest + Playwright) verdes

### ✅ Build e empacotamento

- [x] [`Dockerfile`](../../../Dockerfile) multi-stage, usuário não-root, `tini`, `HEALTHCHECK` apontando para `/healthz`
- [x] [`.dockerignore`](../../../.dockerignore) — não copia `tests/`, `docs/`, `infra/`, `node_modules`, `.env*`, etc.

### ✅ Infra como código

Em [`infra/terraform/`](../../../infra/terraform/):

- [x] VPC com 2 subnets privadas (sem IGW, sem NAT)
- [x] Security groups: App Runner ↔ RDS na 3306
- [x] RDS MySQL 8 privado, criptografado, parameter group utf8mb4
- [x] Secrets Manager para `DB_PASSWORD` e `JWT_SECRET` (ambos via `random_password`)
- [x] ECR com lifecycle policy (5 imagens)
- [x] App Runner com:
  - VPC connector → enxerga o RDS
  - Imagem do ECR + secrets injetados
  - Health check em `/healthz`
  - IAM roles separadas para `access` (puxar ECR) e `instance` (ler Secrets Manager)

### 🔴 Pendente — precisa de uma conta AWS

Veja o runbook abaixo.

## Runbook de deploy

> 📘 **Guia operacional completo (recomendado):** [`../aws-deploy-guide.md`](../aws-deploy-guide.md) — passo a passo com higiene de conta AWS, billing alarm, integração com Vercel e troubleshooting.

O resumo abaixo é o caminho feliz, para quem já passou pelo guia.

Pré-requisitos: AWS CLI configurado (`aws configure`), Terraform ≥ 1.6, Docker rodando.

```bash
# 1. Provisiona toda a infra (RDS demora ~5-10 min)
cd infra/terraform
terraform init
terraform apply
# Anote os outputs: ecr_repository_url, apprunner_url, db_endpoint

# 2. Build da imagem e push pro ECR + deploy no App Runner
cd ../..
scripts/aws-deploy.sh latest
# Acompanhe em https://console.aws.amazon.com/apprunner/

# 3. Smoke test
curl https://<apprunner_url>/healthz
# Espere ver { "ok": true }

# 4. Configure o rewrite no Vercel
# Edite vercel.json adicionando:
#   "rewrites": [
#     { "source": "/api/(.*)", "destination": "https://<apprunner_url>/api/$1" }
#   ]
# Commit + push. O Vercel re-deploy automaticamente.

# 5. (Opcional, fora do escopo deste showcase) Domínio próprio
# Pra manter o cookie httpOnly funcionando entre origens, configure
# um domínio comum:
#   - DNS root → Vercel (frontend)
#   - DNS api → App Runner (backend)
# Atualize CORS_ORIGINS no Terraform e vercel.json.
```

## Plano de rollback

- **Vercel**: aba "Deployments" → "Promote" no deploy anterior (1 clique).
- **App Runner**: `aws apprunner start-deployment` apontando para uma tag antiga do ECR.
- **RDS**: `aws rds restore-db-instance-from-db-snapshot` usando o snapshot automático (retenção = 1 dia).

## Tear down (fim do semestre)

```bash
cd infra/terraform
terraform destroy
```

Tudo (RDS, secrets, ECR, App Runner, VPC) some — `recovery_window_in_days = 0`, `force_delete = true`, `skip_final_snapshot = true`. Confira no console AWS depois pra garantir.

## Modelo de ameaça (blast radius)

Antes de subir, é honesto explicitar o que esse sistema realmente expõe:

- **Sem PII real**: nenhum dado pessoal verdadeiro existe. Os "alunos", "professores", "pagamentos" do seed são fictícios.
- **Sem integrações externas**: o backend não fala com nenhum serviço externo (não tem gateway de pagamento, e-mail, SMS, etc.).
- **Credenciais de demo são públicas**: documentadas no README. Qualquer pessoa pode logar como Admin, Professor ou Aluno.

### O que um atacante consegue fazer

| Acesso | Pode fazer | Dano |
|---|---|---|
| Sem login | Olhar telas estáticas (login) | Nenhum |
| Admin (demo) | Criar/editar/deletar tudo, fazer backup/restore, ver relatórios | Cosmético — `terraform apply` recria do zero |
| Professor (demo) | Criar/editar/deletar treinos, ler alunos | Sujar dados de demonstração |
| Aluno (demo) | Ler perfil, treinos, pagamentos, frequência | Nenhum (somente leitura) |

### O que um atacante **não** consegue fazer

- **Roubar PII real** — não existe.
- **Exfiltrar segredos** — `JWT_SECRET` e senha do DB vivem em Secrets Manager, nunca tocam logs (log-sanitizer scrubba CPFs/emails/hashes).
- **Pivotear para outros serviços** — App Runner roda em VPC sem egresso para internet (sem NAT).
- **Roubar o cookie via XSS** — `HttpOnly` + `__Secure-` + `SameSite=Strict` + CSP estrita com `'unsafe-inline'` proibido em `script-src`.
- **CSRF** — `SameSite=Strict` + CORS allowlist.
- **SQL injection** — todas as queries usam binds parametrizados via `mysql2`.
- **Brute-force das credenciais** — rate-limit de 5 logins/min/IP. Como as senhas são públicas, isso protege contra robôs varrendo, não contra alguém usando o login de demo de propósito.
- **DoS estourar a conta AWS** — App Runner travado em 1 instância (`max_size=1`), `max_concurrency=25`. Tráfego acima disso vira fila, não vira instância nova.

### Camadas de defesa em profundidade

| Camada | Proteção |
|---|---|
| Frontend (Vercel) | Headers de segurança no `vercel.json` (X-Frame-Options DENY, nosniff, no-referrer) |
| Browser | CSP estrita, HSTS, cookies httpOnly + Secure + SameSite=Strict, sem inline handlers |
| App (Express) | helmet, rate-limit, validação CPF + requireFields, log-sanitizer, audit log de login |
| Rede | App Runner em frente de App Runner (TLS), RDS em VPC privada sem `publicly_accessible` |
| Identidade AWS | IAM roles separadas (build vs. instance), OIDC no CI/CD (sem AWS keys longas) |
| Segredos | Secrets Manager (não em env vars de texto) |
| Observabilidade | Audit log de login (sucesso e falha) com email mascarado; CloudWatch com retenção de 7 dias |
| Supply chain | `npm audit` (alta+) e Trivy (HIGH/CRITICAL) falham o CI/CD |
| Código | CodeQL semanal + em PRs |

## CI / CD

### CI ([`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml))

Em todo push/PR para `main`:

1. `npm ci`
2. `npm audit --omit=dev --audit-level=high` — falha se dep de prod tem CVE alta+
3. `npm run lint`
4. Sobe MySQL como service, carrega schema+seed
5. Roda os testes SQL de constraint (`sql/04_tests.sql`)
6. `npm test` — 106 testes Jest (unit + API via Supertest)
7. `npm run test:e2e` — 16 testes Playwright contra Chromium real
8. `docker build` da imagem de produção
9. Trivy scan da imagem (HIGH/CRITICAL falha)

### CodeQL ([`.github/workflows/codeql.yml`](../../../.github/workflows/codeql.yml))

Análise semântica de código (JavaScript/TypeScript) — gratuita para repos públicos no GitHub. Roda em push, PR e uma vez por semana via cron, com query suite `security-and-quality`.

### CD ([`.github/workflows/cd.yml`](../../../.github/workflows/cd.yml))

Em push para `main`, **se** `vars.ENABLE_CD == 'true'`:

1. Assume role AWS via **OIDC** (sem access keys em segredo) — `secrets.AWS_DEPLOY_ROLE_ARN`
2. `docker build` + tag com `${github.sha}` e `latest`
3. Trivy gate (HIGH/CRITICAL falha)
4. `docker push` pro ECR
5. `aws apprunner start-deployment`
6. Espera o serviço voltar a `RUNNING` (timeout 10 min)
7. `curl /healthz` no endpoint real como smoke final

### Setup do CD (uma vez na AWS + uma vez no GitHub)

```bash
# Na AWS (manual, uma vez):
# 1. Criar OIDC provider apontando pra token.actions.githubusercontent.com
#    com thumbprint padrão.
# 2. Criar IAM role com trust policy restrita ao repo:
#    "token.actions.githubusercontent.com:sub": "repo:DyeAllPies/GymControl:ref:refs/heads/main"
# 3. Anexar policy mínima com ecr:* (no ECR repo) e apprunner:StartDeployment,
#    ListServices, DescribeService.
# 4. Anotar o ARN do role.

# No GitHub (uma vez):
# Settings > Secrets and variables > Actions:
#   - secret AWS_DEPLOY_ROLE_ARN = arn:aws:iam::ACCOUNT:role/...
#   - variable ENABLE_CD = true
```

Sem essas duas chaves, o job de CD pula silenciosamente — o repo continua publicável e o CI roda normal.

## Custos

| Item | Mensal |
|---|---|
| Vercel hobby | $0 |
| RDS t4g.micro | $0 (free-tier 12m), depois ~$13 |
| App Runner (0.25 vCPU, 0.5 GB) | ~$7-10 com pouco tráfego |
| Secrets Manager (2 segredos) | ~$0.80 |
| ECR (5 imagens) | < $0.50 |
| **Total nos 2 primeiros meses** | **~$16-22** |
