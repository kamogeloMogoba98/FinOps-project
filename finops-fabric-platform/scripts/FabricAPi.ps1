#--------------------------------------------------------------
# Invoke Fabric REST API
#--------------------------------------------------------------

function Invoke-FabricApi {

    param(

        [Parameter(Mandatory)]
        [string]$Method,

        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter()]
        $Body

    )

    $token = Get-FabricAccessToken

    $headers = @{
        Authorization = "Bearer $token"
        "Content-Type" = "application/json"
    }

    Write-Host ""
    Write-Host "$Method $Uri" -ForegroundColor Yellow

    if ($Body) {

        return Invoke-RestMethod `
            -Method $Method `
            -Uri $Uri `
            -Headers $headers `
            -Body ($Body | ConvertTo-Json -Depth 10)

    }
    else {

        return Invoke-RestMethod `
            -Method $Method `
            -Uri $Uri `
            -Headers $headers

    }

}