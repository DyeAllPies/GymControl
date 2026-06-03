variable "project_name" {
  description = "Prefixo usado em nomes de recursos."
  type        = string
  default     = "gymcontrol"
}

variable "environment" {
  description = "Ambiente (dev, prod, showcase)."
  type        = string
  default     = "showcase"
}

variable "region" {
  description = "Região AWS."
  type        = string
  default     = "sa-east-1"
}

variable "db_instance_class" {
  description = "Classe da instância RDS. db.t4g.micro está no free-tier (12 meses)."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage_gb" {
  description = "Armazenamento alocado (GB)."
  type        = number
  default     = 20
}

variable "db_backup_retention_days" {
  description = "Retenção de backup automático em dias. 1 = mínimo (projeto temporário)."
  type        = number
  default     = 1
}

variable "container_image_tag" {
  description = "Tag da imagem no ECR para o App Runner. Use 'latest' ou o sha do commit."
  type        = string
  default     = "latest"
}

variable "frontend_origin" {
  description = "Origem permitida em CORS (URL do frontend no Vercel)."
  type        = string
  default     = "https://gym-control-pearl.vercel.app"
}

variable "apprunner_cpu" {
  description = "CPU para o App Runner. 256 = 0.25 vCPU (menor)."
  type        = string
  default     = "256"
}

variable "apprunner_memory" {
  description = "Memória (MB). 512 é o mínimo aceito para cpu=256."
  type        = string
  default     = "512"
}

variable "notify_email" {
  description = "Email para alertas de billing (80% e 100% do orçamento). Deixe vazio para não criar o budget."
  type        = string
  default     = ""
}

variable "monthly_budget_usd" {
  description = "Teto mensal em USD. AWS dispara aviso ao chegar em 80% e em 100% (real ou previsto)."
  type        = number
  default     = 25
}
