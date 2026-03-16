import json
import asyncio
from aiohttp import web
from command_router import execute_command

WS_CLIENTS = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    WS_CLIENTS.add(ws)
    print("AHK connected")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                action = data.get("action")
                params = data.get("params", {})

                ok, result = execute_command(action, params)

                await ws.send_json({
                    "ok": ok,
                    "result": result
                })

            except Exception as e:
                await ws.send_json({"ok": False, "error": str(e)})

    WS_CLIENTS.remove(ws)
    print("AHK disconnected")
    return ws

async def start_server():
    app = web.Application()
    app.router.add_get("/ws", websocket_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8765)
    await site.start()
    print("WebSocket server started on ws://127.0.0.1:8765/ws")

async def main():
    await start_server()
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
