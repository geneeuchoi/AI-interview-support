import os
import io
import asyncio
from fastapi import UploadFile, HTTPException
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


class AudioCompressProvider:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024

    async def compress_audio(self, audio: UploadFile) -> bytes:
        content = await audio.read()

        try:
            compressed_bytes = await asyncio.to_thread(self._blocking_compress, content)
            return compressed_bytes
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    def _blocking_compress(self, input_data: bytes) -> bytes:
        try:
            input_buffer = io.BytesIO(input_data)
            audio_segment = AudioSegment.from_file(input_buffer)
        except CouldntDecodeError:
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio processing error: {e}")

        if len(input_data) <= self.max_file_size:
            pass

        bitrates = ["128k", "96k", "64k", "48k", "32k"]

        for bitrate in bitrates:
            output_buffer = io.BytesIO()
            audio_segment.export(
                output_buffer,
                format="mp3",
                bitrate=bitrate,
                parameters=["-ar", "44100"]  # 샘플링 레이트
            )

            compressed_data = output_buffer.getvalue()

            if len(compressed_data) <= self.max_file_size:
                return compressed_data

        return compressed_data

