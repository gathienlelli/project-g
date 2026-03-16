$ErrorActionPreference = "SilentlyContinue"

$MenuLog = "G:\agent\logs\menu\menu.log"
function LogMenu($msg) {
    Add-Content -Path $MenuLog -Value ("$(Get-Date -Format 'HH:mm:ss') [MENU] $msg")
}

$Global:ServerProcessName = "python"
$Global:ServerMainPath   = "G:\agent\core\server\main.py"
$Global:VenvActivatePs1  = "G:\tools\python_env\Scripts\Activate.ps1"
$Global:LogsPython       = "G:\agent\logs\python"
$Global:LogsSystem       = "G:\agent\logs\system"
$Global:ConfigsPath      = "G:\agent\configs"
$Global:UpdatesPath      = "G:\agent\updates"
$Global:WatchdogEnabled  = $false

function Show-Menu {
    Clear-Host
    Write-Host "=== AGENT CONTROL ===" -ForegroundColor Cyan
    Write-Host "1. Запустить сервер"
    Write-Host "2. Перезапустить сервер"
    Write-Host "3. Остановить сервер"
    Write-Host "4. Открыть логи Python"
    Write-Host "5. Открыть логи AHK"
    Write-Host "6. Открыть конфиги"
    Write-Host "7. Диагностика"
    Write-Host "8. Проверить обновления"
    Write-Host "9. Установить обновление"
    Write-Host "10. Запустить AHK-клиента"
    Write-Host "11. Запустить WebSocket тест-клиент"
    Write-Host "12. Мониторинг процессов"
    Write-Host "13. Watchdog включить/выключить"
    Write-Host "14. Лог-вьювер (реальное время)"
    Write-Host "15. Показать статус мониторинга"
    Write-Host "16. Авто-мониторинг (обновление каждые 2 сек)"
    Write-Host "0. Выход"
    Write-Host ""
}

function Start-Server {
    LogMenu "Запуск сервера"
    Start-Process powershell.exe "-ExecutionPolicy Bypass -Command `"
        & '$Global:VenvActivatePs1';
        python '$Global:ServerMainPath'
    `"
}

function Restart-Server {
    LogMenu "Перезапуск сервера"
    Get-Process $Global:ServerProcessName -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Server
}

function Stop-Server {
    LogMenu "Остановка сервера"
    Get-Process $Global:ServerProcessName -ErrorAction SilentlyContinue | Stop-Process -Force
}

function Diagnostics {
    LogMenu "Диагностика"
    Write-Host "=== Диагностика ===" -ForegroundColor Yellow
    Write-Host "Python:" (python --version)
    Write-Host "Pip:" (pip --version)
    Write-Host "Проверка порта 8765..."
    netstat -ano | findstr :8765
    Write-Host ""
    Write-Host "Процессы python:"
    Get-Process python -ErrorAction SilentlyContinue
    pause
}

function Check-Updates {
    LogMenu "Проверка обновлений"
    Write-Host "Проверка обновлений..."
    $latestFile = Join-Path $Global:UpdatesPath "latest.txt"
    if (Test-Path $latestFile) {
        $latest = Get-Content $latestFile
        Write-Host "Последняя доступная версия: $latest"
    } else {
        Write-Host "Файл обновлений не найден."
    }
    pause
}

function Install-Update {
    LogMenu "Установка обновления"
    Write-Host "Запуск updater.py..."
    Start-Process powershell.exe "-NoExit -Command `"
        & 'G:\tools\python_env\Scripts\Activate.ps1';
        python 'G:\agent\services\updater\updater.py'
    `"
}

function Start-AHK {
    LogMenu "Запуск AHK"
    $ahkPath = "G:\agent\ahk\agent.ahk"
    if (Test-Path $ahkPath) {
        Start-Process $ahkPath
    } else {
        Write-Host "AHK клиент не найден."
    }
}

function Start-WebSocketTest {
    LogMenu "Запуск WebSocket тест-клиента"
    Start-Process powershell.exe "-NoExit -Command `"
        Write-Host 'WebSocket Test Client'; 
        Write-Host 'Введите JSON-команду (exit для выхода):'; 
        while(\$true){ 
            \$msg = Read-Host '>'; 
            if(\$msg -eq 'exit'){ break }; 
            try { 
                \$ws = New-Object System.Net.WebSockets.ClientWebSocket; 
                \$uri = 'ws://127.0.0.1:8765'; 
                \$ws.ConnectAsync([Uri]\$uri, [Threading.CancellationToken]::None).Wait(); 
                \$bytes = [System.Text.Encoding]::UTF8.GetBytes(\$msg); 
                \$seg = New-Object System.ArraySegment[byte] -ArgumentList (, \$bytes); 
                \$ws.SendAsync(\$seg, 'Text', \$true, [Threading.CancellationToken]::None).Wait(); 
                Write-Host 'Отправлено'; 
            } catch { Write-Host 'Ошибка подключения' } 
        }
    `"
}

function AutoRescan {
    LogMenu "Мониторинг процессов"
    Write-Host "Авто-рескан процессов (Ctrl+C для выхода)"
    while ($true) {
        Clear-Host
        Write-Host "=== Мониторинг python процессов ==="
        Get-Process python -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

function Toggle-Watchdog {
    LogMenu "Watchdog переключён"
    if (-not $Global:WatchdogEnabled) {
        $Global:WatchdogEnabled = $true
        Write-Host "Watchdog включен" -ForegroundColor Green
    } else {
        $Global:WatchdogEnabled = $false
        Write-Host "Watchdog выключен" -ForegroundColor DarkYellow
    }
    Start-Sleep 1
}

function LogViewer {
    LogMenu "Лог-вьювер"
    $lastLog = Get-ChildItem $Global:LogsPython -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $lastLog) {
        Write-Host "Логов нет."
        return
    }
    Start-Process powershell.exe "-NoExit -Command `"
        Get-Content `"$($lastLog.FullName)`" -Wait -Tail 50
    `"
}

function ShowMonitorStatus {
    LogMenu "Статус мониторинга"
    Clear-Host
    Write-Host "=== Статус мониторинга ===" -ForegroundColor Cyan
    $report = Get-Content "G:\agent\logs\system\monitor.json" -Raw | ConvertFrom-Json
    Write-Host "Время: $($report.timestamp)"
    Write-Host "CPU: $($report.cpu)%"
    Write-Host "RAM: $($report.ram)%"
    Write-Host "Uptime: $($report.uptime_sec) сек"
    Write-Host "Клиентов: $($report.clients)"
    pause
}

function AutoMonitor {
    LogMenu "Авто-мониторинг"
    while ($true) {
        Clear-Host
        Write-Host "=== Мониторинг (реальное время) ===" -ForegroundColor Cyan
        $report = Get-Content "G:\agent\logs\system\monitor.json" -Raw | ConvertFrom-Json
        Write-Host "CPU: $($report.cpu)%"
        Write-Host "RAM: $($report.ram)%"
        Write-Host "Клиентов: $($report.clients)"
        Write-Host "Uptime: $($report.uptime_sec) сек"
        Start-Sleep -Seconds 2
    }
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Выберите действие"

    switch ($choice) {
        "1" { Start-Server }
        "2" { Restart-Server }
        "3" { Stop-Server }
        "4" { Start-Process "explorer.exe" $Global:LogsPython }
        "5" { Start-Process "explorer.exe" "G:\agent\logs\ahk" }
        "6" { Start-Process "explorer.exe" $Global:ConfigsPath }
        "7" { Diagnostics }
        "8" { Check-Updates }
        "9" { Install-Update }
        "10" { Start-AHK }
        "11" { Start-WebSocketTest }
        "12" { AutoRescan }
        "13" { Toggle-Watchdog }
        "14" { LogViewer }
        "15" { ShowMonitorStatus }
        "16" { AutoMonitor }
        "0" { exit }
        default { Write-Host "Неизвестная команда"; Start-Sleep 1 }
    }
}
