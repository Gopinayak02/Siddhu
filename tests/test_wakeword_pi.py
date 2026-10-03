from __future__ import annotations

import time

import numpy as np

from config.settings import load_settings
from voice.audio.stream import LiveAudioStream
from voice.wakeword.detector import WakeWordDetector


def main() -> None:
    settings = load_settings()

    print("=" * 60)
    print("SIDDHU RASPBERRY PI WAKE-WORD TEST")
    print("=" * 60)
    print(f"Model     : {settings.wake_model}")
    print(f"Threshold : {settings.wake_threshold}")
    print("Phrase    : HEY JARVIS")
    print("Duration  : 30 seconds")
    print()

    detector = WakeWordDetector(
        settings.wake_model,
        threshold=settings.wake_threshold,
        sample_rate=16000,
    )

    stream = LiveAudioStream(
        sample_rate=settings.input_rate,
        channels=settings.channels,
        queue_size=settings.queue_size,
    )

    stream.start()

    detections = 0
    frames = 0
    max_score = 0.0
    buffer = np.empty(0, dtype=np.float32)

    start = time.monotonic()

    try:
        while time.monotonic() - start < 30:
            try:
                chunk = stream.read(timeout=1.0)
            except Exception:
                continue

            buffer = np.concatenate((buffer, chunk))

            while len(buffer) >= 1280:
                frame = buffer[:1280]
                buffer = buffer[1280:]

                frame_i16 = (
                    np.clip(frame, -1.0, 1.0) * 32767.0
                ).astype(np.int16)

                detected, score = detector.detected(frame_i16)
                frames += 1
                max_score = max(max_score, score)

                if detected:
                    detections += 1
                    print(
                        f">>> WAKE DETECTED | "
                        f"score={score:.4f}"
                    )

    finally:
        stream.stop()

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Frames processed   : {frames}")
    print(f"Max score          : {max_score:.4f}")
    print(f"Detections         : {detections}")
    print(f"Input overflows    : {stream.stats.input_overflows}")
    print(f"Queue drops        : {stream.stats.queue_drops}")
    print("=" * 60)


if __name__ == "__main__":
    main()
