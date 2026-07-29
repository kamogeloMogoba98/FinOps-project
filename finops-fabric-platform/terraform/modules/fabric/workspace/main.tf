resource "fabric_workspace" "this" {

  display_name = var.workspaceName

  description = var.workspaceDescription

  capacity_id = var.capacityId

}