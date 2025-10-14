from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def transcribe_and_respond(file):
    contents = await file.read()
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    with open(temp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file,
            language="ja"
        )

    user_text = transcription.text

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
        [
            {"role": "system", "content": "あなたは日本人面接官です。あなたが満足できる答えを提示してください。"},
            {"role": "user", "content": user_text},
        ],
    )

    gpt_reply = completion.choices[0].message.content

    return {
        "stt_text": user_text,
        "gpt_reply": gpt_reply
    }
