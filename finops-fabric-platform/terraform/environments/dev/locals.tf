locals {
  commonTags = {
    environment = var.environmentName
    project     = "FinOpsFabricPlatform"
    managedBy   = "Terraform"
    owner       = "KamogeloMogoba"
    costCenter  = "FinOps"
  }
}