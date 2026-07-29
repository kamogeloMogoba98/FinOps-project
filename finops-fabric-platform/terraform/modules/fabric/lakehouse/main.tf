resource "fabric_lakehouse" "this" {

  display_name = var.lakehouseName

  description = var.description

  workspace_id = var.workspaceId

  configuration = {
    enable_schemas = true
  }

}