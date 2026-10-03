from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel


class SiddhuSTT:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        print(
            f"Loading Faster-Whisper: "
            f"{model_size} | {device} | {compute_type}"
        )
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        print("Faster-Whisper loaded.")

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> str:
        segments, info = self.model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=False,
        )

        return " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()
