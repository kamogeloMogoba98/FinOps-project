output "resourceGroupId" {
  description = "Resource Group ID"
  value       = azurerm_resource_group.this.id
}

output "resourceGroupName" {
  description = "Resource Group Name"
  value       = azurerm_resource_group.this.name
}