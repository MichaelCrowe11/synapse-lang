# Docker Hub Publishing Script for Synapse v2.3.0
# PowerShell script with better authentication handling

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Docker Hub Publishing for Synapse Language v2.3.0" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Function to login to Docker Hub
function Login-DockerHub {
    Write-Host ""
    Write-Host "Logging in to Docker Hub..." -ForegroundColor Yellow
    Write-Host "Username: synapselang" -ForegroundColor Cyan

    # Try to login with stored credentials first
    $loginResult = docker login -u synapselang 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Login successful!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Please enter Docker Hub password for 'synapselang':" -ForegroundColor Yellow
        $password = Read-Host -AsSecureString "Password"
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
        $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

        echo $plainPassword | docker login -u synapselang --password-stdin

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Login successful!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Login failed. Please check your credentials." -ForegroundColor Red
            return $false
        }
    }
}

# Login to Docker Hub
if (-not (Login-DockerHub)) {
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Pushing images to Docker Hub..." -ForegroundColor Yellow
Write-Host ""

# Push version 2.3.0
Write-Host "Pushing synapselang/synapse-lang:2.3.0..." -ForegroundColor Cyan
docker push synapselang/synapse-lang:2.3.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to push version 2.3.0" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Version 2.3.0 pushed successfully!" -ForegroundColor Green

# Push latest tag
Write-Host "Pushing synapselang/synapse-lang:latest..." -ForegroundColor Cyan
docker push synapselang/synapse-lang:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to push latest tag" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Latest tag pushed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Docker images published to Docker Hub!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "View your images at:" -ForegroundColor Cyan
Write-Host "  https://hub.docker.com/r/synapselang/synapse-lang" -ForegroundColor White
Write-Host ""
Write-Host "Users can now pull with:" -ForegroundColor Cyan
Write-Host "  docker pull synapselang/synapse-lang:2.3.0" -ForegroundColor White
Write-Host "  docker pull synapselang/synapse-lang:latest" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"