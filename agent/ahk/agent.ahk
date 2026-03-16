#NoEnv
#SingleInstance Force
SetBatchLines, -1
SetWorkingDir, %A_ScriptDir%

; ============================
; CONFIG
; ============================
ws_client := "G:\agent\ahk\websocket_client.ahk"
log_file := "G:\agent\logs\ahk\agent.log"

; ============================
; LOGGING
; ============================
Log(msg) {
    global log_file
    FormatTime, t,, HH:mm:ss
    FileAppend, %t% [AGENT] %msg%`n, %log_file%
}

Log("Agent started")

; ============================
; START WEBSOCKET CLIENT
; ============================
if FileExist(ws_client) {
    Run, %ws_client%
    Log("WebSocket client launched")
} else {
    Log("WebSocket client NOT FOUND")
}

; ============================
; HOTKEYS
; ============================

; Win+Alt+A — открыть Agent Control
#!a::
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\agent_control.ps1"
Log("Agent Control opened")
return

; Win+Alt+S — запустить сервер напрямую
#!s::
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\run.ps1"
Log("Server started via hotkey")
return

; Win+Alt+R — перезапуск сервера
#!r::
Run, powershell.exe -ExecutionPolicy Bypass -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
Sleep, 500
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\run.ps1"
Log("Server restarted via hotkey")
return

; Win+Alt+L — открыть логи агента
#!l::
Run, explorer.exe "G:\agent\logs"
Log("Logs folder opened")
return

; Win+Alt+W — открыть WebSocket тест-клиент
#!w::
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\tools\websocket_test.ps1"
Log("WebSocket test client opened")
return

; ============================
; SEND COMMAND TO WS CLIENT
; ============================
SendWS(json) {
    global log_file
    try {
        FileAppend, SEND: %json%`n, %log_file%
        Run, % "G:\agent\ahk\websocket_client.ahk" " " json
    } catch e {
        FileAppend, ERROR: %e%`n, %log_file%
    }
}

; ============================
; EXAMPLE HOTKEYS FOR COMMANDS
; ============================

; Ctrl+Alt+F — прочитать win.ini через file_ops.read
^!f::
json := "{""cmd"":""file_ops.read"",""args"":{""path"":""C:\\Windows\\win.ini""}}"
SendWS(json)
Log("Sent file_ops.read")
return

; Ctrl+Alt+P — ping
^!p::
json := "{""cmd"":""ping"",""args"":{}}"
SendWS(json)
Log("Sent ping")
return

; ============================
; MINI PANEL (Win+Alt+M)
; ============================
#!m::
Gui, Destroy
Gui, +AlwaysOnTop +ToolWindow -Caption
Gui, Color, 1A1A1A
Gui, Font, cFFFFFF s10, Segoe UI

Gui, Add, Text, x10 y10 c00FFAA, AGENT PANEL
Gui, Add, Button, x10 y40 w150 h30 gBtnStart, Start Server
Gui, Add, Button, x10 y80 w150 h30 gBtnRestart, Restart Server
Gui, Add, Button, x10 y120 w150 h30 gBtnLogs, Open Logs
Gui, Add, Button, x10 y160 w150 h30 gBtnControl, Agent Control
Gui, Add, Button, x10 y200 w150 h30 gBtnExit, Close Panel

Gui, Show, x100 y100 w180 h250, AgentPanel
return

BtnStart:
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\run.ps1"
Log("Server started via panel")
return

BtnRestart:
Run, powershell.exe -ExecutionPolicy Bypass -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
Sleep, 500
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\run.ps1"
Log("Server restarted via panel")
return

BtnLogs:
Run, explorer.exe "G:\agent\logs"
Log("Logs opened via panel")
return

BtnControl:
Run, powershell.exe -ExecutionPolicy Bypass -File "G:\agent\agent_control.ps1"
Log("Agent Control opened via panel")
return

BtnExit:
Gui, Destroy
return

; ============================
; END
; ============================
return
