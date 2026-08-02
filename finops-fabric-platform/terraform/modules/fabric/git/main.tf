terraform {
  required_providers {
    fabric = {
      source  = "microsoft/fabric"
      version = "~> 1.12.0"
    }
  }
}

variable "workspace_id" {
  type = string
}

variable "git_connection_id" {
  type = string
}

variable "repo_owner" {
  type = string
}

variable "repo_name" {
  type = string
}

variable "branch_name" {
  type    = string
  default = "main"
}

resource "fabric_workspace_git" "workspace_git_sync" {
  workspace_id            = var.workspace_id
  initialization_strategy = "PreferWorkspace"

  git_credentials = {
    source        = "ConfiguredConnection"
    connection_id = var.git_connection_id
  }

  git_provider_details = {
    git_provider_type = "GitHub"
    owner_name        = var.repo_owner
    repository_name   = var.repo_name
    branch_name       = var.branch_name
    directory_name    = "/fabricContent"
  } 

}

output "git_sync_state" {
  value = fabric_workspace_git.workspace_git_sync.git_connection_state
}