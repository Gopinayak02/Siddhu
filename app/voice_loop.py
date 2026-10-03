from __future__ import annotations

import time
from datetime import datetime

import numpy as np

from ai.router.client import OmniRouterClient, RouterError
from config.settings import load_settings
from core.logging import setup_logging
from voice.audio.command_recorder import CommandRecorder
from voice.audio.stream import LiveAudioStream
from voice.stt.transcriber import SiddhuSTT
from voice.tts.synthesizer import SiddhuTTS
from voice.wakeword.detector import WakeWordDetector


def main() -> None:
    settings = load_settings()
    logger = setup_logging(settings.log_dir)

    print("=" * 64)
    print("SIDDHU RASPBERRY PI VOICE LOOP")
    print("=" * 64)
    print(f"Wake word : {settings.wakeword}")
    print(f"STT      : {settings.stt_model}")
    print(f"Input    : {settings.input_rate} Hz")
    print()

    wake = WakeWordDetector(
        settings.wake_model,
        threshold=settings.wake_threshold,
        sample_rate=16000,
    )

    stt = SiddhuSTT(
        settings.stt_model,
        settings.stt_device,
        settings.stt_compute_type,
    )

    tts = SiddhuTTS(settings.piper_model)

    router = OmniRouterClient(
        settings.omni_router_url,
        settings.omni_router_api_key,
        settings.omni_router_model,
        settings.omni_router_timeout,
    )

    stream = LiveAudioStream(
        sample_rate=settings.input_rate,
        channels=settings.channels,
        queue_size=settings.queue_size,
    )

    recorder = CommandRecorder(
        sample_rate=settings.input_rate,
        channels=settings.channels,
    )

    wake_frame = 1280
    buffer = np.empty(0, dtype=np.float32)
    last_detection = 0.0

    stream.start()

    try:
        print(">>> SIDDHU IS LISTENING")
        print(">>> Say HEY JARVIS for the development test.")
        print()

        while True:
            chunk = stream.read(timeout=1.0)
            buffer = np.concatenate((buffer, chunk))

            while len(buffer) >= wake_frame:
                frame_float = buffer[:wake_frame]
                buffer = buffer[wake_frame:]

                frame = (
                    np.clip(frame_float, -1.0, 1.0) * 32767.0
                ).astype(np.int16)

                detected, score = wake.detected(frame)

                if not detected:
                    continue

                now = time.monotonic()
                if now - last_detection < 1.5:
                    continue
                last_detection = now

                print()
                print(">>> WAKE WORD DETECTED")
                print(f">>> SCORE: {score:.4f}")
                print(">>> SIDDHU ACTIVATED")
                print()

                command_path = recorder.record(
                    stream,
                    duration=settings.command_seconds,
                    output_dir=settings.data_dir / "audio_test",
                )

                print(">>> STT PROCESSING...")
                text = stt.transcribe(
                    command_path,
                    language=None
                    if settings.language == "auto"
                    else settings.language,
                )

                print(f">>> USER: {text}")

                if not text:
                    print(">>> No speech recognized.")
                    continue

                print(">>> AI ROUTER...")
                try:
                    answer = router.chat(text)
                except RouterError as exc:
                    logger.error(str(exc))
                    answer = (
                        "The AI router is not configured or "
                        "is unavailable right now."
                    )

                print(f">>> SIDDHU: {answer}")

                output = (
                    settings.data_dir
                    / "audio_test"
                    / (
                        f"siddhu_response_"
                        f"{datetime.now():%Y%m%d_%H%M%S}.wav"
                    )
                )

                print(">>> TTS...")
                tts.synthesize_and_play(
                    answer,
                    output,
                )

                print()
                print(">>> READY FOR NEXT COMMAND")
                print()

    except KeyboardInterrupt:
        print("\nStopping SIDDHU...")

    finally:
        stream.stop()

    print(f"Input overflows : {stream.stats.input_overflows}")
    print(f"Queue drops     : {stream.stats.queue_drops}")


if __name__ == "__main__":
    main()
