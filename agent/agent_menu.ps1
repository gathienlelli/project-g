# ================================
#   ULTIMATE AGENT CONTROL MENU
#           by Лу
# ================================

# ---------- Цветовые функции ----------
function Color([string]$text, [string]$color="White") {
    $Host.UI.RawUI.ForegroundColor = $color
    Write-Host $text
    $Host.UI.RawUI.ForegroundColor = "White"
}

function ColorInline([string]$text, [string]$color="White") {
    $Host.UI.RawUI.ForegroundColor = $color
    Write-Host $text -NoNewline
    $Host.UI.RawUI.ForegroundColor = "White"
}

# ---------- ASCII-анимация ----------
function Show-Logo {
    $logo = @(
"   __    ___      __        ____            __ ",
"  / /   /   |____/ /_____ _/ __ \___  ____  / / ",
" / /   / /| / ___/ __/ __ `/ /_/ / _ \/ __ \/ /  ",
"/ /___/ ___ (__  ) /_/ /_/ / _, _/  __/ /_/ / /___",
"\____/_/  |_/____/\__/\__,_/_/ |_|\___/ .___/_____/",
"                                      /_/          "
    )

    foreach ($line in $logo) {
        Color $line "Cyan"
        Start-Sleep -Milliseconds 60
    }
}

# ---------- Логирование ----------
$logFile = "G:\agent\python\logs\agent_menu.log"
function Log($msg) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $logFile -Value "[$timestamp] $msg"
}

# ---------- Активация среды ----------
& "G:\tools\python_env\Scripts\Activate.ps1" | Out-Null
Set-Location "G:\agent\python\server"

# ---------- Проверка зависимостей ----------
function Check-Dependencies {
    Color "Проверка зависимостей..." "Yellow"
    $deps = @("aiohttp")

    foreach ($d in $deps) {
        $installed = pip show $d 2>$null
        if (-not $installed) {
            Color "Устанавливаю $d..." "Yellow"
            pip install $d | Out-Null
            Log "Установлена зависимость: $d"
        }
    }

    Color "Все зависимости в порядке." "Green"
}

# ---------- Проверка статуса сервера ----------
function Check-Server {
    $port = 8765
    $tcp = New-Object System.Net.Sockets.TcpClient

    try {
        $tcp.Connect("127.0.0.1", $port)
        if ($tcp.Connected) {
            Color "Сервер активен на порту $port" "Green"
            $tcp.Close()
            return $true
        }
    }
    catch {
        Color "Сервер НЕ запущен" "Red"
        return $false
    }
}

# ---------- Запуск сервера ----------
function Start-Server {
    Color "Запуск WebSocket-сервера..." "Yellow"
    Log "Запуск сервера"
    python main.py
}

# ---------- Автовосстановление ----------
function Auto-Recover {
    Color "Автовосстановление сервера..." "Yellow"
    Log "Автовосстановление сервера"
    Start-Server
}

# ---------- Перезапуск ----------
function Restart-Server {
    Color "Перезапуск сервера..." "Yellow"
    Log "Перезапуск сервера"
    Start-Server
}

# ---------- Меню ----------
function Show-Menu {
    Clear-Host
    Show-Logo
    Color "===============================" "Cyan"
    Color "      AGENT CONTROL MENU" "Cyan"
    Color "===============================" "Cyan"

    ColorInline "1." "Yellow"; Color " Запустить WebSocket-сервер"
    ColorInline "2." "Yellow"; Color " Открыть среду (PowerShell + venv)"
    ColorInline "3." "Yellow"; Color " Перезапустить сервер"
    ColorInline "4." "Yellow"; Color " Проверить статус сервера"
    ColorInline "5." "Yellow"; Color " Автовосстановление"
    ColorInline "6." "Yellow"; Color " Проверить зависимости"
    ColorInline "7." "Yellow"; Color " Выйти"

    Color "===============================" "Cyan"
}

# ---------- Основной цикл ----------
while ($true) {
    Show-Menu
    $choice = Read-Host "Выберите пункт"

    switch ($choice) {
        "1" { Start-Server }
        "2" { Color "Среда активирована. Вы можете работать." "Green"; break }
        "3" { Restart-Server }
        "4" { Check-Server; Pause }
        "5" { Auto-Recover }
        "6" { Check-Dependencies; Pause }
        "7" { Color "Выход..." "Yellow"; Log "Выход из меню"; exit }
        default { Color "Неверный выбор. Попробуйте снова." "Red"; Start-Sleep -Seconds 1 }
    }
}
