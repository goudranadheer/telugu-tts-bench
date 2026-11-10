"""ASR judges. Several are used on purpose: Telugu ASR is weak, so no single
recogniser can be trusted as the measure of TTS intelligibility.

NOTE: not run when the scaffold was written; check on first use.
"""
import os
from pathlib import Path


class HFWhisper:
    def __init__(self, model_id: str):
        import torch
        from transformers import pipeline

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            device=0 if torch.cuda.is_available() else -1,
            chunk_length_s=30,
        )

    def transcribe(self, path: Path) -> str:
        return self.pipe(
            str(path), generate_kwargs={"language": "telugu", "task": "transcribe"}
        )["text"]


class Scribe:
    """ElevenLabs Scribe. Conflict of interest when judging ElevenLabs TTS:
    always report it next to an independent judge, never alone."""

    def __init__(self, model_id="scribe_v2"):
        import requests

        self.requests = requests
        self.model_id = model_id
        self.key = os.environ["ELEVENLABS_API_KEY"]

    def transcribe(self, path: Path) -> str:
        with open(path, "rb") as f:
            r = self.requests.post(
                "https://api.elevenlabs.io/v1/speech-to-text",
                headers={"xi-api-key": self.key},
                data={"model_id": self.model_id, "language_code": "te"},
                files={"file": f},
                timeout=300,
            )
        r.raise_for_status()
        return r.json()["text"]


JUDGES = {
    "whisper_te": lambda: HFWhisper("vasista22/whisper-telugu-large-v2"),
    "whisper_v3": lambda: HFWhisper("openai/whisper-large-v3"),
    "scribe_v2": Scribe,
}
