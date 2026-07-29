<#
==============================================================
Assign Microsoft Fabric Workspace to Capacity
Author: Kamogelo Mogoba
Project: FinOps Fabric Platform
==============================================================
#>


param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceId,

    [Parameter(Mandatory=$true)]
    [string]$CapacityId
)


Write-Host ""
Write-Host "Assigning Fabric workspace to capacity..." -ForegroundColor Cyan


# Get Fabric token

$token = az account get-access-token `
    --resource "https://api.fabric.microsoft.com" `
    --query accessToken `
    --output tsv


if ([string]::IsNullOrWhiteSpace($token)) {

    throw "Unable to get Fabric access token"

}


$headers = @{

    "Authorization" = "Bearer $token"

    "Content-Type" = "application/json"

}


$body = @{

    capacityId = $CapacityId

} | ConvertTo-Json



$url = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/assignToCapacity"



$response = Invoke-RestMethod `
    -Method Post `
    -Uri $url `
    -Headers $headers `
    -Body $body



Write-Host ""
Write-Host "Workspace assigned successfully!" -ForegroundColor Green