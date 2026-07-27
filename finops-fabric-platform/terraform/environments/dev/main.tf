module "resourceGroup" {
  source = "../../modules/resourceGroup"

  resourceGroupName = var.resourceGroupName
  locationName      = var.locationName
  environmentName   = var.environmentName

  tags = local.commonTags
}
