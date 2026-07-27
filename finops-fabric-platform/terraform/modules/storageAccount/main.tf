resource "azurerm_storage_account" "this" {

  name                     = var.storageAccountName

  resource_group_name      = var.resourceGroupName

  location                 = var.locationName

  account_tier             = "Standard"

  account_replication_type = "LRS"

  account_kind             = "StorageV2"

  is_hns_enabled           = true

  min_tls_version          = "TLS1_2"

  https_traffic_only_enabled = true

  public_network_access_enabled = true

  tags = var.tags
}