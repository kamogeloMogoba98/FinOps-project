variable "subscriptionId" {
  description = "Azure Subscription ID"
  type        = string
}

variable "resourceGroupName" {
  description = "Resource Group name"
  type        = string
}

variable "locationName" {
  description = "Azure region"
  type        = string
}

variable "environmentName" {
  description = "Environment"
  type        = string
}

variable "storageAccountName" {
  type = string
}

variable "containerNames" {
  type = list(string)
}

variable "workspaceName" {
  default = "finops-dev-workspace"
}

variable "workspaceDescription" {
  default = "Development workspace for the FinOps Fabric Platform"
}

variable "warehouseName" {
  description = "Gold Warehouse Name"
  type        = string

  default = "goldWarehouse"
}

variable "capacity_name" {
  description = "The Fabric Capacity display name"
  type        = string
}
