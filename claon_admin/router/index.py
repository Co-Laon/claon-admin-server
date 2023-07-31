import asyncio
from os import environ

from fastapi import APIRouter, WebSocket, Request
from starlette.templating import Jinja2Templates

from claon_admin.config.config import Config

router = APIRouter()

templates = Jinja2Templates(directory=Config.HTML_DIR)


async def log_reader(log_file_name: str, n=0):
    log_lines = ""
    with open(f"{Config.BASE_DIR}/{log_file_name}", "r", encoding="utf-8") as file:
        log_file = file.readlines()
        size = len(log_file)
        if n == 0:
            n = max(size - 1000, 0)
        for line in log_file[n:size]:
            if "ERROR" in line:
                log_lines += f'<span class="text-red-400">{line}</span><br/>'
            elif "WARNING" in line:
                log_lines += f'<span class="text-orange-300">{line}</span><br/>'
            else:
                log_lines += f"{line}<br/>"
        return {
            "file_size": size,
            "context": log_lines
        }


@router.websocket("/ws/log")
async def websocket_endpoint_log(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await asyncio.sleep(0.1)
            data = await websocket.receive_text()
            logs = await log_reader("logs/info.log", int(data))
            await websocket.send_json(logs)
    except Exception as e:
        print(e)
    finally:
        await websocket.close()


@router.get("/log")
async def get(request: Request):
    context = {
        "log_file": "info.log",
        "env": environ.get("API_ENV"),
        "domain": request.client.host
    }
    return templates.TemplateResponse("log.html", {"request": request, "context": context})
