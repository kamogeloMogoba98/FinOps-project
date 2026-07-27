variable "storageAccountName" {
  description = "Azure Storage Account name"
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

variable "tags" {
  description = "Tags applied to the Storage Account"
  type        = map(string)
}