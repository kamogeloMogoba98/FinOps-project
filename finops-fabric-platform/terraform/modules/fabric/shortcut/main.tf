resource "null_resource" "shortcut" {

  triggers = {
    workspace = var.workspaceId
    lakehouse = var.lakehouseId
    storage   = var.storageAccount
    container = var.containerName
  }

  provisioner "local-exec" {

    interpreter = ["PowerShell", "-Command"]

    command = <<EOT
Write-Host "PWD:"
Get-Location

Write-Host ""
Write-Host "Looking for script..."
Test-Path "../../../scripts/createOneLakeShortcut.ps1"
EOT

  }
}