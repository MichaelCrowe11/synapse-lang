@echo off
echo ================================================
echo FIXING DEPLOYMENT - CREATING REQUIRED VOLUMES
echo ================================================
echo.

echo The deployment needs a volume for persistent storage.
echo Creating volume 'synapse_data' in region 'iad'...
echo.

REM Create the required volumes (2 for redundancy)
fly volumes create synapse_data -r iad -n 2 --app synapse-lang-docs --size 1

if %errorlevel% equ 0 (
    echo.
    echo ✓ Volumes created successfully!
    echo.
    echo Now redeploying the application...
    echo.

    fly deploy --dockerfile Dockerfile.production

    if %errorlevel% equ 0 (
        echo.
        echo ================================================
        echo DEPLOYMENT SUCCESSFUL!
        echo ================================================
        echo.
        echo Your v2 documentation site is now live!
        echo.
        fly status --app synapse-lang-docs
        echo.
        echo Opening site in browser...
        fly open --app synapse-lang-docs
    )
) else (
    echo.
    echo Failed to create volumes.
    echo.
    echo Alternative solution: Remove volume requirement from fly.toml
    echo.
    choice /C YN /M "Would you like to deploy without volumes"
    if errorlevel 2 goto :END
    if errorlevel 1 goto :REMOVE_VOLUMES
)

goto :END

:REMOVE_VOLUMES
echo.
echo Updating fly.toml to remove volume requirement...

REM Create a new fly.toml without the mounts section
echo # Fly.io deployment configuration for Synapse v2 Documentation > fly.toml.novolume
echo # Production-ready configuration with WebSocket support >> fly.toml.novolume
echo. >> fly.toml.novolume
echo app = 'synapse-lang-docs' >> fly.toml.novolume
echo primary_region = 'iad' >> fly.toml.novolume
echo kill_signal = 'SIGINT' >> fly.toml.novolume
echo kill_timeout = '5s' >> fly.toml.novolume
echo. >> fly.toml.novolume
echo [experimental] >> fly.toml.novolume
echo   auto_rollback = true >> fly.toml.novolume
echo. >> fly.toml.novolume
echo [build] >> fly.toml.novolume
echo   dockerfile = 'Dockerfile.production' >> fly.toml.novolume
echo. >> fly.toml.novolume
echo [env] >> fly.toml.novolume
echo   PORT = '8080' >> fly.toml.novolume
echo   FLASK_ENV = 'production' >> fly.toml.novolume
echo. >> fly.toml.novolume
echo [[services]] >> fly.toml.novolume
echo   protocol = 'tcp' >> fly.toml.novolume
echo   internal_port = 8080 >> fly.toml.novolume
echo   processes = ['app'] >> fly.toml.novolume
echo   min_machines_running = 1 >> fly.toml.novolume
echo   auto_stop_machines = false >> fly.toml.novolume
echo   auto_start_machines = true >> fly.toml.novolume
echo. >> fly.toml.novolume
echo   [[services.ports]] >> fly.toml.novolume
echo     port = 80 >> fly.toml.novolume
echo     handlers = ['http'] >> fly.toml.novolume
echo     force_https = true >> fly.toml.novolume
echo. >> fly.toml.novolume
echo   [[services.ports]] >> fly.toml.novolume
echo     port = 443 >> fly.toml.novolume
echo     handlers = ['tls', 'http'] >> fly.toml.novolume
echo. >> fly.toml.novolume
echo   [services.concurrency] >> fly.toml.novolume
echo     type = 'connections' >> fly.toml.novolume
echo     hard_limit = 250 >> fly.toml.novolume
echo     soft_limit = 200 >> fly.toml.novolume
echo. >> fly.toml.novolume
echo   [[services.tcp_checks]] >> fly.toml.novolume
echo     interval = '15s' >> fly.toml.novolume
echo     timeout = '2s' >> fly.toml.novolume
echo     grace_period = '5s' >> fly.toml.novolume
echo. >> fly.toml.novolume
echo   [[services.http_checks]] >> fly.toml.novolume
echo     interval = '30s' >> fly.toml.novolume
echo     timeout = '5s' >> fly.toml.novolume
echo     grace_period = '10s' >> fly.toml.novolume
echo     method = 'get' >> fly.toml.novolume
echo     path = '/health' >> fly.toml.novolume
echo     protocol = 'http' >> fly.toml.novolume
echo. >> fly.toml.novolume
echo [[vm]] >> fly.toml.novolume
echo   memory = '512mb' >> fly.toml.novolume
echo   cpu_kind = 'shared' >> fly.toml.novolume
echo   cpus = 1 >> fly.toml.novolume

copy fly.toml.novolume fly.toml >nul
echo.
echo Deploying without volumes...
fly deploy --dockerfile Dockerfile.production

:END
pause