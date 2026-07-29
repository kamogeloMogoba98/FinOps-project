<#
==============================================================
Create Microsoft Fabric Workspace
Author: Kamogelo Mogoba
Project: FinOps Fabric Platform
Description:
    Creates a Microsoft Fabric Workspace if it does not exist.
==============================================================
#>

#--------------------------------------------------------------
# Import Fabric API Helper
#--------------------------------------------------------------

. "$PSScriptRoot\fabricApi.ps1"

#--------------------------------------------------------------
# Load Configuration
#--------------------------------------------------------------

$configPath = Join-Path $PSScriptRoot "..\config\fabric.json"

if (!(Test-Path $configPath)) {
    throw "Configuration file not found: $configPath"
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

$workspaceName = $config.workspaceName
$description   = $config.description

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Microsoft Fabric Workspace Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

#--------------------------------------------------------------
# Check if Workspace Already Exists
#--------------------------------------------------------------

Write-Host "Checking if workspace '$workspaceName' already exists..." -ForegroundColor Yellow

$workspace = Get-FabricWorkspace -WorkspaceName $workspaceName

if ($workspace) {

    Write-Host ""
    Write-Host "Workspace already exists." -ForegroundColor Green
    Write-Host "Workspace Name : $($workspace.displayName)"
    Write-Host "Workspace ID   : $($workspace.id)"
    Write-Host ""

    return $workspace
}

#--------------------------------------------------------------
# Create Workspace
#--------------------------------------------------------------

Write-Host ""
Write-Host "Workspace not found." -ForegroundColor Yellow
Write-Host "Creating Workspace..." -ForegroundColor Cyan

$body = @{
    displayName = $workspaceName
    description = $description
}

try {

    $newWorkspace = Invoke-FabricApi `
        -Method POST `
        -Uri "https://api.fabric.microsoft.com/v1/workspaces" `
        -Body $body

    Write-Host ""
    Write-Host "Workspace created successfully." -ForegroundColor Green
    Write-Host ""

    Write-Host "Workspace Name : $($newWorkspace.displayName)"
    Write-Host "Workspace ID   : $($newWorkspace.id)"

    return $newWorkspace

}
catch {

    Write-Host ""
    Write-Host "Workspace creation failed." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

    throw

}