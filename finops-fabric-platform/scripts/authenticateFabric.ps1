<#
==============================================================
Microsoft Fabric Authentication
Author: Kamogelo Mogoba
Project: FinOps Fabric Platform
==============================================================
#>

function Get-FabricAccessToken {

    Write-Host ""
    Write-Host "Authenticating to Microsoft Fabric..." -ForegroundColor Cyan

    $token = az account get-access-token `
        --resource "https://api.fabric.microsoft.com" `
        --query accessToken `
        --output tsv

    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "Unable to obtain Microsoft Fabric access token."
    }

    Write-Host "Authentication successful." -ForegroundColor Green

    return $token
}