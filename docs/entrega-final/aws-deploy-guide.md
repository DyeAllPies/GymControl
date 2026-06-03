# Guia de deploy na AWS — passo a passo

Documento operacional. Para o **porquê** das decisões (arquitetura, modelo de ameaça, CD), veja [`added/preparing-aws-deploy.md`](added/preparing-aws-deploy.md).

> ⏱️ Tempo estimado total: **~25 min** (RDS é quem demora).
>
> 💰 Custo nos 2 primeiros meses: **~$16-22** (RDS free-tier zera o maior item).

---

## 0. Pré-requisitos (uma vez por máquina)

Instale e confirme que cada um responde:

```bash
aws --version       # AWS CLI v2
terraform --version # >= 1.6
docker --version    # daemon rodando
```

**AWS CLI:** <https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html>
**Terraform:** <https://developer.hashicorp.com/terraform/install>
**Docker Desktop:** <https://www.docker.com/products/docker-desktop>

---

## 1. Higiene da conta AWS (uma vez)

Antes de qualquer `terraform apply`, **no console AWS**:

1. **MFA na root account** (Account > Security credentials > Multi-factor authentication).
2. **Não use a root pro deploy.** Crie um IAM user *ou* use IAM Identity Center (SSO) com MFA.
3. **Billing alarm** — defina um teto antes de gastar:
   - Console > Billing > Billing preferences > marque "Receive Free Tier Usage Alerts" e "Receive Billing Alerts".
   - Console > CloudWatch > Alarms > Billing > Create alarm, métrica `EstimatedCharges`, threshold $20 (ou o que você quiser), com SNS topic mandando email pra você.

Confirme a região no `aws configure`:

```bash
aws configure
# AWS Access Key ID:     <do IAM user>
# AWS Secret Access Key: <do IAM user>
# Default region name:   sa-east-1
# Default output format: json
```

> ℹ️ Usamos `sa-east-1` (São Paulo). É a região padrão do nosso Terraform — se quiser outra, edite `infra/terraform/variables.tf`.

Validação:

```bash
aws sts get-caller-identity
# deve retornar Account, UserId, Arn
```

---

## 2. Provisionar a infra

Antes do primeiro `apply`, copie o template de variáveis e edite:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# abra terraform.tfvars, ajuste notify_email pra um email seu
# (sem isso, o billing alarm não é criado)
```

Depois:

```bash
terraform init     # baixa providers, ~30 s
terraform validate # checa sintaxe (não fala com AWS)
terraform plan     # mostra o que vai criar — confira que tudo é "Plan to add"
terraform apply    # confirma "yes"; demora ~5-10 min, RDS é o gargalo
```

> 💡 Se preferir pular o billing alarm (não recomendado), basta deixar `notify_email` vazio no tfvars. O Terraform só cria o budget quando o email está setado.

**Outputs importantes** (anote, vão ser usados):

```bash
terraform output ecr_repository_url   # ex.: 123456789.dkr.ecr.sa-east-1.amazonaws.com/gymcontrol-showcase
terraform output apprunner_url        # ex.: https://abc.us-east-1.awsapprunner.com
terraform output db_endpoint          # privado, só pra debug
```

> ⚠️ O `terraform.tfstate` que ficou no diretório **tem a senha do RDS dentro**. Não copie, não compartilhe, não commit. Já está no `.gitignore` daqui.

---

## 3. Build da imagem e push pro ECR

Da raiz do repo, o script `scripts/aws-deploy.sh` faz build + login no ECR + push + dispara o deploy do App Runner num único comando:

```bash
cd ../..   # volta pra raiz do repo
./scripts/aws-deploy.sh
```

O que ele faz nos bastidores:

1. Lê `ecr_repository_url` e `apprunner_url` do `terraform output`
2. `aws ecr get-login-password` → `docker login`
3. `docker build` → `docker tag` → `docker push`
4. `aws apprunner start-deployment`

> 💡 Se preferir rodar manualmente passo a passo (para entender o que acontece), os comandos equivalentes estão no comentário do início do script.

> 💡 No Windows, se o `docker push` parar com "denied: access denied", refaça o `aws ecr get-login-password` — o token expirou.

---

## 4. Dispara o primeiro deploy no App Runner

O App Runner foi criado pelo Terraform já apontando pro ECR, mas a imagem só existe agora. Dispara o deploy:

```bash
SERVICE_ARN=$(aws apprunner list-services --region sa-east-1 \
  --query "ServiceSummaryList[?ServiceName=='gymcontrol-showcase'].ServiceArn" \
  --output text)

aws apprunner start-deployment --region sa-east-1 --service-arn "$SERVICE_ARN"
```

Acompanhe no console: <https://console.aws.amazon.com/apprunner/>. Ou:

```bash
aws apprunner describe-service --region sa-east-1 \
  --service-arn "$SERVICE_ARN" --query 'Service.Status' --output text
# RUNNING quando estiver no ar (~3-5 min)
```

Smoke test no endpoint público:

```bash
APPRUNNER_URL=$(cd infra/terraform && terraform output -raw apprunner_url)
curl "$APPRUNNER_URL/healthz"
# {"ok":true}
```

Na **primeira subida**, o app detecta que o RDS está vazio e roda `01_schema.sql` + `02_seed.sql` automaticamente (`AUTO_MIGRATE=1`, ver [`lib/migrate.js`](../../lib/migrate.js)).

Login de teste (admin):

```bash
curl -i -X POST "$APPRUNNER_URL/api/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@gym.com","senha":"admin123"}'
# espere 200 OK + Set-Cookie com __Secure-gym_token
```

---

## 5. Integra o frontend (Vercel) com o backend (App Runner)

Hoje o frontend está em <https://gym-control-pearl.vercel.app> mas chama `/api/*` no próprio domínio do Vercel — e ali não tem backend. Precisamos redirecionar essas chamadas para o App Runner.

Edite [`vercel.json`](../../vercel.json) na raiz do repo, **adicionando uma chave `rewrites`**:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": null,
  "outputDirectory": "public",
  "cleanUrls": false,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://SUBSTITUA-PELO-OUTPUT-DO-TERRAFORM.awsapprunner.com/api/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy",        "value": "no-referrer" },
        { "key": "X-Frame-Options",        "value": "DENY" }
      ]
    }
  ]
}
```

Substitua `SUBSTITUA-PELO-OUTPUT-DO-TERRAFORM.awsapprunner.com` pela URL real (sem `https://` e sem barra final — só o host).

Commit + push: a Vercel re-deploy automaticamente. Em ~30 s, abra <https://gym-control-pearl.vercel.app> e tente logar como `admin@gym.com / admin123`.

> ⚠️ **Limitação de cookie cross-origin:** o cookie `__Secure-` + `SameSite=Strict` só funciona quando frontend e API compartilham domínio raiz. Como `gym-control-pearl.vercel.app` ≠ `xyz.awsapprunner.com`, o cookie **não** vai persistir entre sessões via rewrite. Pra showcase, isso é aceitável (login funciona dentro da sessão por causa do rewrite — o browser vê tudo como `vercel.app`). Pra "produção real", configuraríamos um domínio próprio tipo `gym.exemplo.com` (frontend) + `api.gym.exemplo.com` (backend) e cookie com `Domain=.exemplo.com`.

---

## 6. CD automático (opcional)

Agora que o deploy manual funciona, ativa o CD pra dispensar o passo 3 e 4 em mudanças futuras.

Veja a seção "Setup do CD" em [`added/preparing-aws-deploy.md`](added/preparing-aws-deploy.md#setup-do-cd-uma-vez-na-aws--uma-vez-no-github). Em resumo:

1. **No AWS:** crie um OIDC provider pro GitHub + um IAM role assumível restrito ao nosso repo.
2. **No GitHub** (Settings > Secrets and variables > Actions do nosso fork):
   - Secret `AWS_DEPLOY_ROLE_ARN` = ARN do role
   - Variable `ENABLE_CD` = `true`
3. Próximo push em `main` ativa [`.github/workflows/cd.yml`](../../.github/workflows/cd.yml): build → Trivy → push pro ECR → start-deployment → espera RUNNING → smoke /healthz.

---

## 7. Tear down (fim do semestre)

Pra zerar tudo (e a fatura):

```bash
cd infra/terraform
terraform destroy
```

Confirma com `yes`. Em ~5 min, tudo some: VPC, RDS, ECR, App Runner, Secrets Manager, CloudWatch log groups, security groups, IAM roles.

**Confira no console depois:**

- <https://console.aws.amazon.com/rds/> — não deve ter cluster.
- <https://console.aws.amazon.com/ecr/repositories> — repositório foi.
- <https://console.aws.amazon.com/apprunner/> — service não está mais lá.
- <https://console.aws.amazon.com/secretsmanager/> — sem segredos do projeto.
- <https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups> — sem `/aws/apprunner/gymcontrol-...`.

> 💡 **`recovery_window_in_days = 0`** nos secrets + **`force_delete = true`** no ECR + **`skip_final_snapshot = true`** no RDS garantem que o destroy seja realmente imediato e completo. Em projetos reais você quer o oposto.

Não esquece de **desfazer o rewrite no `vercel.json`** (commit removendo o bloco `rewrites`) — senão o frontend continua tentando bater num backend que não existe mais.

---

## Troubleshooting

**`terraform apply` falha em "VPCConfigurationException"**
→ Conta nova às vezes não tem o limite de VPC liberado. Abra um support case (gratuito) pedindo aumento, ou tente outra região.

**App Runner fica em `CREATE_FAILED`**
→ Vá no console > App Runner > o seu serviço > Logs. Normalmente é:
- Imagem não está no ECR (faça `docker push` de novo)
- Container deu crash no boot — confere os logs em `/aws/apprunner/.../application`

**`curl https://.../healthz` retorna 503**
→ App Runner ainda subindo, ou o container não conecta no RDS. Confere se o VPC connector está ligado no service e se o security group do RDS aceita a porta 3306 do SG do App Runner.

**Login funciona via `curl` mas falha no browser depois do rewrite**
→ Veja a limitação do cookie cross-origin no passo 5. Pra contornar sem comprar domínio, dá pra adicionar um modo Bearer com `AUTH_MODE=bearer` (não está implementado hoje — pediria um PR adicional).

**`docker push` retorna `no basic auth credentials`**
→ Refaça o `aws ecr get-login-password` (token expira em 12 h).

**`terraform destroy` deixa um snapshot do RDS**
→ Não deixa, com `skip_final_snapshot = true`. Mas se você editou pra `false`, depois precisa apagar manualmente: <https://console.aws.amazon.com/rds/home#snapshots:>.

---

## Resumo dos custos durante o uso

| Recurso | Mês 1-12 (free tier) | Após free tier |
|---|---|---|
| RDS t4g.micro + 20 GB gp3 | $0 | ~$13/mês |
| App Runner (0.25 vCPU, 0.5 GB, 1 instância) | ~$7-10/mês | ~$7-10/mês |
| Secrets Manager (2 segredos) | ~$0.80/mês | ~$0.80/mês |
| ECR (5 imagens ~200 MB cada) | < $0.50/mês | < $0.50/mês |
| Data transfer (uso de showcase, pouco tráfego) | ~$0-1/mês | ~$0-1/mês |
| **Total** | **~$8-12/mês** | **~$22/mês** |

Pra um showcase de 2 meses: **~$20 total**. Lembra de `terraform destroy` no fim.
