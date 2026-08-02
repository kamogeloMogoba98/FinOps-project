resource "azurerm_subscription_cost_management_export" "this" {
  name             = "finOpsDailyCostExport"
  subscription_id  = "/subscriptions/${var.subscriptionId}"

  recurrence_type  = "Daily"
  recurrence_period_start_date = formatdate("YYYY-MM-DD'T'00:00:00Z", timestamp())
  recurrence_period_end_date   = "2030-12-31T23:59:59Z"

  export_data_options {
    type       = "ActualCost"
    time_frame = "MonthToDate"
  }

  export_data_storage_location {
    container_id     = "${var.storageAccountId}/blobServices/default/containers/${var.containerName}"
    root_folder_path = "azure-cost-data"
  }
}