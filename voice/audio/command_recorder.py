from __future__ import annotations

import wave
from datetime import datetime
from pathlib import Path

import numpy as np


class CommandRecorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels

    def record(
        self,
        audio_stream,
        duration: float = 8.0,
        output_dir: str | Path = "data/audio_test",
    ) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        path = output_dir / (
            f"command_{datetime.now():%Y%m%d_%H%M%S}.wav"
        )

        target = int(self.sample_rate * duration)
        chunks: list[np.ndarray] = []
        total = 0

        print(">>> LISTENING FOR COMMAND")
        print(f">>> Maximum recording time: {duration:.1f} seconds")

        while total < target:
            try:
                chunk = audio_stream.read(timeout=1.0)
            except Exception:
                continue

            chunk = np.asarray(chunk, dtype=np.float32)
            remaining = target - total
            chunk = chunk[:remaining]
            chunks.append(chunk)
            total += len(chunk)

        audio = np.concatenate(chunks)
        audio_int16 = (
            np.clip(audio, -1.0, 1.0) * 32767.0
        ).astype(np.int16)

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        print(f">>> COMMAND AUDIO SAVED: {path}")
        return path
