resource "null_resource" "assign_capacity" {

  depends_on = [
    fabric_workspace.this
  ]

  triggers = {

    workspace_id = fabric_workspace.this.id
    capacity_id  = var.capacityId

  }


  provisioner "local-exec" {

    command = <<EOT

az rest `
--method post `
--url "https://api.fabric.microsoft.com/v1/workspaces/${fabric_workspace.this.id}/assignToCapacity" `
--resource "https://api.fabric.microsoft.com" `
--body '{"capacityId":"${var.capacityId}"}'

Start-Sleep -Seconds 120

EOT

    interpreter = [
      "PowerShell",
      "-Command"
    ]

  }

}