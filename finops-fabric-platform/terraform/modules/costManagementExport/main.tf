resource "azurerm_subscription_cost_management_export" "this" {

  name            = "finOpsDailyCostExport"
 subscription_id = "/subscriptions/${var.subscriptionId}"


  export_data_options {
    type       = "ActualCost"
    time_frame = "MonthToDate"
  }


  export_data_storage_location {

    container_id = "${var.storageAccountId}/blobServices/default/containers/${var.containerName}"

    root_folder_path = "azure-cost-data"

  }


  recurrence_type = "Daily"


  recurrence_period_start_date = "2026-07-27T00:00:00Z"

  recurrence_period_end_date = "2030-07-27T00:00:00Z"

}