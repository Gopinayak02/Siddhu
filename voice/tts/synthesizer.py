from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from piper import PiperVoice


class SiddhuTTS:
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Piper model not found: {self.model_path}"
            )

        print("Loading Piper voice...")
        self.voice = PiperVoice.load(str(self.model_path))
        print("Piper voice loaded.")

    def synthesize_to_wav(
        self,
        text: str,
        output_path: str | Path,
    ) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(output_path), "wb") as wf:
            self.voice.synthesize_wav(text, wf)

        return output_path

    def synthesize_and_play(
        self,
        text: str,
        output_path: str | Path,
    ) -> Path:
        path = self.synthesize_to_wav(text, output_path)

        with wave.open(str(path), "rb") as wf:
            channels = wf.getnchannels()
            rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        audio = np.frombuffer(
            frames,
            dtype=np.int16,
        )

        if channels > 1:
            audio = audio.reshape(-1, channels)

        sd.play(audio, rate)
        sd.wait()

        return path
