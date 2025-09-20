# PowerShell script to test live site features
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "TESTING SYNAPSE DOCS LIVE SITE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://synapse-lang-docs.fly.dev"
$endpoints = @(
    @{Name="Home"; Url="/"; Expected=200},
    @{Name="Health Check"; Url="/health"; Expected=200},
    @{Name="API Status"; Url="/api/v2/status"; Expected=200},
    @{Name="Dashboard"; Url="/dashboard"; Expected=200},
    @{Name="Playground"; Url="/playground"; Expected=200},
    @{Name="Explorer"; Url="/explorer"; Expected=200},
    @{Name="Workspace"; Url="/workspace"; Expected=200},
    @{Name="Documentation"; Url="/docs"; Expected=200},
    @{Name="Analytics API"; Url="/api/v2/analytics"; Expected=200}
)

Write-Host "Testing endpoints..." -ForegroundColor Yellow
Write-Host ""

$results = @()
$allPassed = $true

foreach ($endpoint in $endpoints) {
    $url = $baseUrl + $endpoint.Url
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 10
        $status = $response.StatusCode

        if ($status -eq $endpoint.Expected) {
            Write-Host "✅ $($endpoint.Name): OK ($status)" -ForegroundColor Green
            $results += @{Endpoint=$endpoint.Name; Status="Pass"; Code=$status}
        } else {
            Write-Host "⚠️ $($endpoint.Name): Unexpected status ($status)" -ForegroundColor Yellow
            $results += @{Endpoint=$endpoint.Name; Status="Warning"; Code=$status}
            $allPassed = $false
        }
    } catch {
        Write-Host "❌ $($endpoint.Name): Failed - $($_.Exception.Message)" -ForegroundColor Red
        $results += @{Endpoint=$endpoint.Name; Status="Fail"; Error=$_.Exception.Message}
        $allPassed = $false
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$passed = ($results | Where-Object {$_.Status -eq "Pass"}).Count
$total = $results.Count

Write-Host ""
Write-Host "Passed: $passed/$total endpoints" -ForegroundColor $(if ($allPassed) {"Green"} else {"Yellow"})

if ($allPassed) {
    Write-Host ""
    Write-Host "✅ All tests passed! Site is fully operational." -ForegroundColor Green
    Write-Host ""
    Write-Host "Opening site in browser..." -ForegroundColor Cyan
    Start-Process $baseUrl
} else {
    Write-Host ""
    Write-Host "⚠️ Some tests failed. Check the errors above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Live Site URL: $baseUrl" -ForegroundColor Cyan
Write-Host "Monitoring: https://fly.io/apps/synapse-lang-docs/monitoring" -ForegroundColor Cyan