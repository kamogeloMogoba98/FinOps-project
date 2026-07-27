resource "azurerm_resource_group" "this" {
  name     = var.resourceGroupName
  location = var.locationName

  tags = var.tags
}