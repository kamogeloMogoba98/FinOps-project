<#
==============================================================
Bootstrap Deployment
Author: Kamogelo Mogoba
Project: FinOps Fabric Platform

Description:
    Entry point for the FinOps Fabric Platform deployment.
    This script authenticates to Azure/Fabric and starts
    the deployment process.
==============================================================
#>

#--------------------------------------------------------------
# Stop execution if an error occurs
#--------------------------------------------------------------

$ErrorActionPreference = "Stop"

Clear-Host

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "        FinOps Fabric Platform Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

#--------------------------------------------------------------
# Locate Scripts Folder
#--------------------------------------------------------------

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

#--------------------------------------------------------------
# Import Required Scripts
#--------------------------------------------------------------

Write-Host "Loading deployment modules..." -ForegroundColor Yellow

. "$scriptRoot\authenticateFabric.ps1"
. "$scriptRoot\fabricApi.ps1"
. "$scriptRoot\deployFabric.ps1"

Write-Host "Modules loaded successfully." -ForegroundColor Green
Write-Host ""

#--------------------------------------------------------------
# Authenticate
#--------------------------------------------------------------

Write-Host "Authenticating..." -ForegroundColor Cyan

Test-AzureLogin
Get-FabricAccessToken | Out-Null

Write-Host "Authentication successful." -ForegroundColor Green
Write-Host ""

#--------------------------------------------------------------
# Deploy Fabric Resources
#--------------------------------------------------------------

Write-Host "Starting Microsoft Fabric deployment..." -ForegroundColor Cyan
Write-Host ""

Deploy-Fabric

#--------------------------------------------------------------
# Finished
#--------------------------------------------------------------

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "     Deployment completed successfully." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""