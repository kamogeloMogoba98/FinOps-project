param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter(Mandatory)]
    [string]$StorageAccount,

    [Parameter(Mandatory)]
    [string]$ContainerName,

    [Parameter(Mandatory)]
    [string]$ShortcutName
)

Write-Host ""
Write-Host "Checking OneLake shortcuts..."

$token = az account get-access-token `
    --resource https://api.fabric.microsoft.com `
    --query accessToken `
    -o tsv

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

$listUrl = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId/shortcuts"

try {
    $existing = Invoke-RestMethod `
        -Method GET `
        -Uri $listUrl `
        -Headers $headers

    $shortcut = $existing.value | Where-Object {
        $_.displayName -eq $ShortcutName
    }

    if ($shortcut) {
        Write-Host "Shortcut already exists."
        exit 0
    }
}
catch {
    Write-Host "No shortcuts found."
}

Write-Host "Creating shortcut..."

$body = @{
    displayName = $ShortcutName

    target = @{
        type = "AdlsGen2"

        adlsGen2 = @{
            location = "https://$StorageAccount.dfs.core.windows.net"

            subpath = "/$ContainerName"
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Method POST `
    -Uri $listUrl `
    -Headers $headers `
    -Body $body

Write-Host "Shortcut created."