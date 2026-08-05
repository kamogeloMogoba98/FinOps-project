data "azurerm_client_config" "current" {}

module "resourceGroup" {
  source = "../../modules/resourceGroup"

  resourceGroupName = local.dynamic_resource_group_name
  locationName      = var.locationName
  environmentName   = var.environmentName

  tags = local.commonTags
}

module "storageAccount" {
  source = "../../modules/storageAccount"

  storageAccountName = local.storage_account_name
  resourceGroupName  = module.resourceGroup.resourceGroupName
  locationName       = var.locationName

  tags = local.commonTags
}

module "storageContainer" {
  source = "../../modules/storageContainer"

  for_each = toset(var.containerNames)

  containerName    = each.value
  storageAccountId = module.storageAccount.storageAccountId
}

module "costManagementExport" {
  source = "../../modules/costManagementExport"

  subscriptionId     = data.azurerm_client_config.current.subscription_id
  storageAccountId   = module.storageAccount.storageAccountId
  storageAccountName = module.storageAccount.storageAccountName
  containerName      = "costexports"
}

data "fabric_capacity" "current" {
  display_name = var.capacity_display_name
}

module "fabricWorkspace" {
  source               = "../../modules/fabric/workspace"
  workspaceName        = "finops-${var.environmentName}-workspace"
  workspaceDescription = "FinOps Fabric ${title(var.environmentName)} Workspace"
  capacityId           = data.fabric_capacity.current.id
}

module "goldWarehouse" {
  source = "../../modules/fabric/warehouse"

  warehouseName = "Gold"
  description   = "Gold Warehouse"
  workspaceId   = module.fabricWorkspace.workspaceId

  depends_on = [
    module.fabricWorkspace
  ]
}

module "bronzeLakehouse" {
  source = "../../modules/fabric/lakehouse"

  lakehouseName = "Bronze"
  description   = "Bronze Layer"
  workspaceId   = module.fabricWorkspace.workspaceId

  depends_on = [
    module.fabricWorkspace
  ]
}

module "silverLakehouse" {
  source = "../../modules/fabric/lakehouse"

  lakehouseName = "Silver"
  description   = "Silver Layer"
  workspaceId   = module.fabricWorkspace.workspaceId

  depends_on = [
    module.fabricWorkspace
  ]
}

module "bronzeShortcut" {
  source = "../../modules/fabric/shortcut"

  workspaceId    = module.fabricWorkspace.workspaceId
  lakehouseId    = module.bronzeLakehouse.lakehouseId
  storageAccount = module.storageAccount.storageAccountName
  containerName  = "costexports"
  shortcutName   = "CostExports"
  scriptPath     = "${path.root}/../../../scripts/createOneLakeShortcut.ps1"

  depends_on = [
    module.bronzeLakehouse
  ]
}

module "fabric_git_sync" {
  source            = "../../modules/fabric/git"
  workspace_id      = module.fabricWorkspace.workspaceId
  git_connection_id = "169eaf5b-817a-4a93-b203-d1223835b23a"
  repo_owner        = "kamogeloMogoba98"
  repo_name         = "finops-fabric-platform"
  
  # Dynamically syncs with the matching Git branch name (e.g., dev or test)
  branch_name       = var.environmentName 
}