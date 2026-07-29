variable "lakehouseName" {
  description = "Lakehouse name"
  type        = string
}

variable "workspaceId" {
  description = "Microsoft Fabric Workspace ID"
  type        = string
}

variable "description" {
  description = "Lakehouse description"
  type        = string

  default = "Fabric Lakehouse"
}