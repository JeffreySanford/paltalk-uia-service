from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from .probe import probe_window, send_message

app = FastAPI(title="Paltalk UIA Service")

class MessagePayload(BaseModel):
    message: str

@app.get("/room/{title}/status")
async def room_status(title: str):
    res = probe_window(title, activate=False)
    if not res.get("found"):
        raise HTTPException(status_code=404, detail="room_not_found")
    return res

@app.post("/room/{title}/message")
async def room_message(title: str, payload: MessagePayload):
    res = send_message(title, payload.message, activate=True)
    if not res.get("ok"):
        raise HTTPException(status_code=500, detail=res.get("error"))
    return {"status": "sent", "method": res.get("method")}
