variable "resourceGroupName" {
  description = "Name of the Azure Resource Group"
  type        = string
}

variable "locationName" {
  description = "Azure region where resources are deployed"
  type        = string
}

variable "environmentName" {
  description = "Deployment environment"
  type        = string
}

variable "tags" {
  description = "Tags applied to the Resource Group"
  type        = map(string)
}