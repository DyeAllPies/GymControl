# Budget mensal — só é criado se `notify_email` for setado.
# 3 alertas:
#   - 50% real: heads-up no meio do mês
#   - 80% real: já gastou bastante, hora de revisar
#   - 100% previsto: AWS projeta que vai estourar até o fim do mês
# Tudo via email, sem custo (AWS não cobra por budget).

resource "aws_budgets_budget" "monthly" {
  count = var.notify_email == "" ? 0 : 1

  name              = "${local.name}-monthly"
  budget_type       = "COST"
  limit_amount      = tostring(var.monthly_budget_usd)
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2026-01-01_00:00"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.notify_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.notify_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.notify_email]
  }
}
