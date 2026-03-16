#NoEnv
#SingleInstance Force
SetBatchLines, -1
SetWorkingDir, %A_ScriptDir%

; === CONFIG ===
server_url := "ws://127.0.0.1:8765"
log_file := "G:\agent\logs\ahk\client.log"
heartbeat_interval := 5000
reconnect_delay := 3000

; === LOGGING ===
Log(msg) {
    global log_file
    FormatTime, t,, HH:mm:ss
    FileAppend, %t% [AHK] %msg%`n, %log_file%
}

; === WEBSOCKET SETUP ===
OnMessage(0x5000, "WS_OnOpen")
OnMessage(0x5001, "WS_OnMessage")
OnMessage(0x5002, "WS_OnClose")
OnMessage(0x5003, "WS_OnError")

ws := ComObjCreate("Msxml2.ServerXMLHTTP")
connected := false

; === CONNECT FUNCTION ===
Connect() {
    global ws, server_url, connected
    try {
        ws := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        ws.Open("GET", server_url, true)
        ws.SetRequestHeader("Connection", "Upgrade")
        ws.SetRequestHeader("Upgrade", "websocket")
        ws.SetRequestHeader("Sec-WebSocket-Version", "13")
        ws.SetRequestHeader("Sec-WebSocket-Key", "dGhlIHNhbXBsZSBub25jZQ==")
        ws.Send()
        connected := true
        Log("Connected to server")
    } catch e {
        connected := false
        Log("Connection failed: " . e.Message)
    }
}

; === SEND FUNCTION ===
Send(msg) {
    global ws, connected
    if (!connected) {
        Log("Send failed — not connected")
        return
    }
    try {
        ws.Send(msg)
        Log("Sent: " . msg)
    } catch e {
        Log("Send error: " . e.Message)
        connected := false
    }
}

; === HEARTBEAT ===
SetTimer, Heartbeat, %heartbeat_interval%
Heartbeat:
if (connected) {
    Send("{""cmd"":""ping"",""args"":{}}")
}
return

; === RECONNECT TIMER ===
SetTimer, Reconnect, %reconnect_delay%
Reconnect:
if (!connected) {
    Log("Reconnecting...")
    Connect()
}
return

; === EVENT HANDLERS ===
WS_OnOpen(wParam, lParam, msg, hwnd) {
    global connected
    connected := true
    Log("WebSocket opened")
}

WS_OnMessage(wParam, lParam, msg, hwnd) {
    data := StrGet(lParam, "UTF-8")
    Log("Received: " . data)
}

WS_OnClose(wParam, lParam, msg, hwnd) {
    global connected
    connected := false
    Log("WebSocket closed")
}

WS_OnError(wParam, lParam, msg, hwnd) {
    global connected
    connected := false
    Log("WebSocket error")
}

; === HOTKEYS FOR TESTING ===
#IfWinActive
^!t::
Send("{""cmd"":""file_ops.read"",""args"":{""path"":""C:\\Windows\\win.ini""}}")
return

^!p::
Send("{""cmd"":""ping"",""args"":{}}")
return

; === START ===
Log("Client starting...")
Connect()
return
