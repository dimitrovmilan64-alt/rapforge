import asyncio
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="RapForge Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

ACE_STEP_URL = "http://localhost:8001"


@app.post("/api/generate")
async def generate(data: dict):
    title = data.get("title") or "Без заглавие"
    style = data.get("style", "").strip()
    lyrics = data.get("lyrics", "").strip()

    if not style or not lyrics:
        raise HTTPException(400, "Попълни стил и текстове")

    async with httpx.AsyncClient(timeout=600.0) as client:
        # Създаваме задача в ACE-Step
        payload = {
            "prompt": style,
            "lyrics": lyrics,
            "duration": 120,
            "infer_steps": 30,
        }
        try:
            r = await client.post(f"{ACE_STEP_URL}/release_task", json=payload)
            r.raise_for_status()
            task_id = r.json().get("data", {}).get("task_id")
            if not task_id:
                raise HTTPException(500, "Няма task_id от ACE-Step")
        except Exception as e:
            raise HTTPException(500, f"ACE-Step не е достъпен: {e}")

        # Чакаме резултата
        for _ in range(90):
            await asyncio.sleep(4)
            q = await client.post(
                f"{ACE_STEP_URL}/query_result",
                json={"task_ids": [task_id]},
            )
            if q.status_code != 200:
                continue
            result = q.json().get("data", {}).get(str(task_id), {})
            status = result.get("status")
            if status == "success":
                # Вземаме аудио пътя (зависи от версията на ACE-Step)
                audio_info = result.get("audio") or result.get("audio_path") or {}
                # Тук трябва да копираш/свалиш файла според реалния отговор
                filename = f"{uuid.uuid4().hex}.wav"
                # Демо: връщаме URL (замени с реално копиране)
                return {
                    "title": title,
                    "audio_url": f"/audio/{filename}",
                    "task_id": task_id,
                    "note": "Провери ACE-Step output директорията за готовия файл",
                }
            if status in ("failed", "error"):
                raise HTTPException(500, f"Генерацията се провали: {result}")

    raise HTTPException(500, "Timeout при генерация")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
