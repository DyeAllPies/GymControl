#!/usr/bin/env bash
# Build da imagem Docker, push pro ECR e disparo de novo deploy no App Runner.
#
# Pré-requisitos: terraform apply já rodado em infra/terraform/, docker rodando,
# aws cli configurado (`aws configure`).
#
# Uso: scripts/aws-deploy.sh [tag]
#   tag — opcional, default = 'latest'
set -euo pipefail

TAG="${1:-latest}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INFRA_DIR="$ROOT_DIR/infra/terraform"
SERVICE_NAME="gymcontrol-showcase"

# 1) Lê outputs do Terraform
if [ ! -d "$INFRA_DIR/.terraform" ]; then
  echo "ERRO: $INFRA_DIR não inicializado. Rode 'cd infra/terraform && terraform init && terraform apply' primeiro." >&2
  exit 1
fi
pushd "$INFRA_DIR" >/dev/null
ECR_URL="$(terraform output -raw ecr_repository_url)"
APPRUNNER_URL="$(terraform output -raw apprunner_url)"
popd >/dev/null

# Região: AWS_REGION do env tem prioridade; senão derive do registry URL
# (formato: <account>.dkr.ecr.<region>.amazonaws.com); senão fallback sa-east-1.
REGION="${AWS_REGION:-}"
if [ -z "$REGION" ]; then
  REGION="$(echo "$ECR_URL" | sed -n 's|.*\.dkr\.ecr\.\([^.]*\)\.amazonaws\.com.*|\1|p')"
fi
REGION="${REGION:-sa-east-1}"

ECR_REGISTRY="${ECR_URL%/*}"

echo ">> Região: $REGION"
echo ">> ECR:    $ECR_URL"
echo ">> App:    $APPRUNNER_URL"

# 2) Login no ECR
echo ">> login no ECR"
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# 3) Build e push
echo ">> build da imagem (tag: $TAG)"
cd "$ROOT_DIR"
docker build -t "gymcontrol:$TAG" .
docker tag "gymcontrol:$TAG" "$ECR_URL:$TAG"
echo ">> push"
docker push "$ECR_URL:$TAG"

# 4) Dispara o deploy
echo ">> disparando novo deploy no App Runner"
SERVICE_ARN="$(aws apprunner list-services --region "$REGION" \
  --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" \
  --output text)"

if [ -z "$SERVICE_ARN" ] || [ "$SERVICE_ARN" = "None" ]; then
  echo "ERRO: serviço '$SERVICE_NAME' não encontrado no App Runner. Rode 'terraform apply' antes." >&2
  exit 1
fi

aws apprunner start-deployment --region "$REGION" --service-arn "$SERVICE_ARN" >/dev/null
echo ">> deploy iniciado. Acompanhe em https://console.aws.amazon.com/apprunner/"
echo "   Status do serviço: $APPRUNNER_URL"
echo "   Healthcheck:       $APPRUNNER_URL/healthz"
