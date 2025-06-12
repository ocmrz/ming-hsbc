from openai import OpenAI
import os
from fastapi import FastAPI
from typing import Iterable, Optional
from pydantic import BaseModel
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from fastapi.responses import StreamingResponse
from pathlib import Path
from fastapi.responses import FileResponse

app = FastAPI()

client = OpenAI()


class AskRequest(BaseModel):
    messages: str
    history: Optional[Iterable[ChatCompletionMessageParam]] = None

@app.post("/ask")
async def ask(request: AskRequest):

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "system", "content": Path("output/leaflet.md").read_text()},
            {"role": "system", "content": Path("output/terms-and-conditions.md").read_text()},
            {"role": "system", "content": Path("output/well_plus_data_privacy_notice_en.md").read_text()},
            *(request.history if request.history else []),
            {"role": "user", "content": request.messages}
        ],
        stream=True,
    )

    def generate():
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/background.jpeg")
def get_background_image():
    return FileResponse("src/background.jpeg", media_type="image/jpeg")

@app.get("/team-logo.png")
def get_logo_image():
    return FileResponse("src/team-logo.png", media_type="image/png")
