output "storageAccountId" {
  value = azurerm_storage_account.this.id
}

output "storageAccountName" {
  value = azurerm_storage_account.this.name
}

output "primaryBlobEndpoint" {
  value = azurerm_storage_account.this.primary_blob_endpoint
}