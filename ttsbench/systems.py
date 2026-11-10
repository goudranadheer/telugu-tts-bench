"""TTS system adapters. Each takes Telugu text and writes one audio file.

NOTE: these adapters call external models/APIs and were NOT run when the
scaffold was written. Expect to fix small API details on first run (day 2).
Heavy imports live inside the classes so the scoring code has no GPU deps.
"""
import os
import time
from pathlib import Path


class ElevenLabs:
    """ElevenLabs REST API. Needs ELEVENLABS_API_KEY and a voice id."""

    ext = "mp3"

    def __init__(self, model_id="eleven_v3", voice_id=None):
        import requests

        self.requests = requests
        self.model_id = model_id
        self.voice_id = voice_id or os.environ["ELEVENLABS_VOICE_ID"]
        self.key = os.environ["ELEVENLABS_API_KEY"]

    def synthesize(self, text: str, out: Path):
        r = self.requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
            headers={"xi-api-key": self.key},
            json={"text": text, "model_id": self.model_id, "language_code": "te"},
            timeout=120,
        )
        r.raise_for_status()
        out.write_bytes(r.content)


class MMS:
    """Meta MMS-TTS Telugu (VITS). Small, CPU-friendly baseline."""

    ext = "wav"

    def __init__(self):
        import torch
        from transformers import AutoTokenizer, VitsModel

        self.torch = torch
        self.model = VitsModel.from_pretrained("facebook/mms-tts-tel")
        self.tok = AutoTokenizer.from_pretrained("facebook/mms-tts-tel")

    def synthesize(self, text: str, out: Path):
        import soundfile as sf

        with self.torch.no_grad():
            wav = self.model(**self.tok(text, return_tensors="pt")).waveform[0]
        sf.write(out, wav.numpy(), self.model.config.sampling_rate)


class IndicParler:
    """AI4Bharat Indic Parler-TTS (gated on Hugging Face: accept terms first)."""

    ext = "wav"
    description = (
        "A female speaker with a clear voice delivers the speech at a moderate "
        "pace in a quiet environment with no background noise."
    )

    def __init__(self):
        import torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        name = "ai4bharat/indic-parler-tts"
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = ParlerTTSForConditionalGeneration.from_pretrained(name).to(self.device)
        self.tok = AutoTokenizer.from_pretrained(name)
        self.desc_tok = AutoTokenizer.from_pretrained(self.model.config.text_encoder._name_or_path)

    def synthesize(self, text: str, out: Path):
        import soundfile as sf

        d = self.desc_tok(self.description, return_tensors="pt").to(self.device)
        p = self.tok(text, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            wav = self.model.generate(
                input_ids=d.input_ids,
                attention_mask=d.attention_mask,
                prompt_input_ids=p.input_ids,
                prompt_attention_mask=p.attention_mask,
            )
        sf.write(out, wav.cpu().numpy().squeeze(), self.model.config.sampling_rate)


class IndicF5:
    """AI4Bharat IndicF5. Needs a short Telugu reference clip + its transcript
    (set INDICF5_REF_AUDIO and INDICF5_REF_TEXT)."""

    ext = "wav"

    def __init__(self):
        from transformers import AutoModel

        self.model = AutoModel.from_pretrained("ai4bharat/IndicF5", trust_remote_code=True)
        self.ref_audio = os.environ["INDICF5_REF_AUDIO"]
        self.ref_text = os.environ["INDICF5_REF_TEXT"]

    def synthesize(self, text: str, out: Path):
        import numpy as np
        import soundfile as sf

        wav = self.model(text, ref_audio_path=self.ref_audio, ref_text=self.ref_text)
        wav = np.asarray(wav, dtype=np.float32)
        if np.abs(wav).max() > 1.0:  # int16 range -> float
            wav = wav / 32768.0
        sf.write(out, wav, 24000)


SYSTEMS = {
    "eleven_v3": lambda: ElevenLabs("eleven_v3"),
    "eleven_flash_v2_5": lambda: ElevenLabs("eleven_flash_v2_5"),
    "mms": MMS,
    "indic_parler": IndicParler,
    "indicf5": IndicF5,
}


def timed(system, text: str, out: Path) -> float:
    """Synthesize and return wall-clock seconds."""
    t0 = time.perf_counter()
    system.synthesize(text, out)
    return time.perf_counter() - t0
