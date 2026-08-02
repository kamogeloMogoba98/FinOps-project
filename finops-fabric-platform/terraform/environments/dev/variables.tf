variable "subscriptionId" {
  description = "Azure Subscription ID"
  type        = string
}


variable "baseResourceName" {
  description = "Base name for resources"
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



variable "containerNames" {
  type = list(string)
}



variable "workspaceDescription" {
  default = "Development workspace for the FinOps Fabric Platform"
}

variable "warehouseName" {
  description = "Gold Warehouse Name"
  type        = string

  default = "goldWarehouse"
}

variable "capacity_display_name" {
  type        = string
  description = "The friendly name of your Fabric capacity"
}