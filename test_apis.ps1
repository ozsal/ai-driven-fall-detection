# API Testing Script for Fall Detection System
# Tests all endpoints and reports results

$baseUrl = "http://10.162.131.191:8000"
$results = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "Get"
    )
    
    Write-Host "`n[$Name]" -ForegroundColor Cyan
    Write-Host "Testing: $Url" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method $Method -ErrorAction Stop
        $status = "[OK] SUCCESS"
        $color = "Green"
        $data = $response | ConvertTo-Json -Depth 5 -Compress
        Write-Host $status -ForegroundColor $color
        if ($response -is [System.Array]) {
            Write-Host "  Count: $($response.Count) items" -ForegroundColor Yellow
            if ($response.Count -gt 0) {
                Write-Host "  Sample data:" -ForegroundColor Gray
                $response[0] | ConvertTo-Json -Depth 3 | Write-Host
            }
        } else {
            Write-Host "  Response:" -ForegroundColor Gray
            $response | ConvertTo-Json -Depth 3 | Write-Host
        }
        return @{
            Name = $Name
            Status = "SUCCESS"
            Data = $data
            Count = if ($response -is [System.Array]) { $response.Count } else { 1 }
        }
    } catch {
        $status = "[X] FAILED"
        $color = "Red"
        $errorMsg = $_.Exception.Message
        Write-Host $status -ForegroundColor $color
        Write-Host "  Error: $errorMsg" -ForegroundColor Red
        
        # Try to get response body if available
        if ($_.Exception.Response) {
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $responseBody = $reader.ReadToEnd()
                Write-Host "  Response: $responseBody" -ForegroundColor Red
            } catch {
                # Ignore
            }
        }
        
        return @{
            Name = $Name
            Status = "FAILED"
            Error = $errorMsg
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  API Endpoint Testing" -ForegroundColor Cyan
Write-Host "  Backend: $baseUrl" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test all endpoints
$results += Test-Endpoint "Root" "$baseUrl/"
$results += Test-Endpoint "Health Check" "$baseUrl/health"
$results += Test-Endpoint "Statistics" "$baseUrl/api/statistics"
$results += Test-Endpoint "Devices" "$baseUrl/api/devices"
$results += Test-Endpoint "Sensor Readings (limit=5)" "$baseUrl/api/sensor-readings?limit=5"
$results += Test-Endpoint "Sensor Readings (all)" "$baseUrl/api/sensor-readings?limit=100"
$results += Test-Endpoint "Fall Events" "$baseUrl/api/fall-events?limit=5"

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$successCount = ($results | Where-Object { $_.Status -eq "SUCCESS" }).Count
$failedCount = ($results | Where-Object { $_.Status -eq "FAILED" }).Count

Write-Host "Total Tests: $($results.Count)" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $failedCount" -ForegroundColor Red

Write-Host "`nFailed Endpoints:" -ForegroundColor Yellow
$results | Where-Object { $_.Status -eq "FAILED" } | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.Error)" -ForegroundColor Red
}

Write-Host "`nSuccessful Endpoints:" -ForegroundColor Yellow
$results | Where-Object { $_.Status -eq "SUCCESS" } | ForEach-Object {
    $countInfo = if ($_.Count) { " ($($_.Count) items)" } else { "" }
    Write-Host "  - $($_.Name)$countInfo" -ForegroundColor Green
}

