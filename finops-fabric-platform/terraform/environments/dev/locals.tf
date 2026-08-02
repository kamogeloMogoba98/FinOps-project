locals {
  commonTags = {
    environment = var.environmentName
    project     = "FinOpsFabricPlatform"
    managedBy   = "Terraform"
    owner       = "KamogeloMogoba"
    costCenter  = "FinOps"
  }
  

  dynamic_resource_group_name = "rg-${var.baseResourceName}-${var.environmentName}"
  # Automatically appends "-test" or "-dev" to your base names
  resource_group_name  = "rg-${var.baseResourceName}-${var.environmentName}"
  storage_account_name = "st${var.baseResourceName}${var.environmentName}001"
  workspace_name       = "${var.baseResourceName}-${var.environmentName}-workspace"
}