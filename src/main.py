from openai import OpenAI
import os
from fastapi import FastAPI
from typing import Iterable
from pydantic import BaseModel
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from fastapi.responses import StreamingResponse
from pathlib import Path

app = FastAPI()

client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")


class AskRequest(BaseModel):
    messages: str
    history: Iterable[ChatCompletionMessageParam]

@app.post("/ask")
def ask(request: AskRequest):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "system", "content": Path("output/leaflet.md").read_text()},
            {"role": "system", "content": Path("output/terms-and-conditions.md").read_text()},
            {"role": "system", "content": Path("output/well_plus_data_privacy_notice_en.md").read_text()},
            *request.history,
            {"role": "user", "content": request.messages}
        ],
        stream=True
    )

    def generate():
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/event-stream")
