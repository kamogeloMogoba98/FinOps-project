resource "fabric_warehouse" "this" {

  provider = fabric

  display_name = var.warehouseName

  description = var.description

  workspace_id = var.workspaceId

}