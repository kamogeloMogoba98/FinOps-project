data "azurerm_client_config" "current" {}

module "resourceGroup" {
  source = "../../modules/resourceGroup"

  resourceGroupName = var.resourceGroupName
  locationName      = var.locationName
  environmentName   = var.environmentName

  tags = local.commonTags
}

module "storageAccount" {

  source = "../../modules/storageAccount"

  storageAccountName = var.storageAccountName

  resourceGroupName = module.resourceGroup.resourceGroupName

  locationName = var.locationName

  tags = local.commonTags
}

module "storageContainer" {
  source = "../../modules/storageContainer"

  for_each = toset(var.containerNames)

  containerName   = each.value
  storageAccountId = module.storageAccount.storageAccountId
}

module "costManagementExport" {

  source = "../../modules/costManagementExport"


  subscriptionId = data.azurerm_client_config.current.subscription_id


  storageAccountId = module.storageAccount.storageAccountId


  storageAccountName = module.storageAccount.storageAccountName


  containerName = "costexports"
}

