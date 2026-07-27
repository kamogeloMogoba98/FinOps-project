resource "azurerm_storage_data_lake_gen2_filesystem" "this" {
  name               = var.containerName
  storage_account_id = var.storageAccountId
}