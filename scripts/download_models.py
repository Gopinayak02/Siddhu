from __future__ import annotations

import urllib.request
from pathlib import Path

from config.settings import load_settings


WAKE_URL = (
    "https://github.com/dscripka/openWakeWord/releases/"
    "download/v0.5.1/hey_jarvis_v0.1.tflite"
)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        print(f"Exists: {destination}")
        return

    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, destination)
    print(f"Saved: {destination}")


def main() -> None:
    settings = load_settings()

    wake_path = (
        settings.model_dir
        / "wakeword"
        / "hey_jarvis_v0.1.tflite"
    )

    download(WAKE_URL, wake_path)

    print()
    print("Piper voice:")
    print(
        "Run this command to download the voice:"
    )
    print()
    print(
        "python -m piper.download_voices "
        "en_US-lessac-medium "
        f"--data-dir {settings.model_dir / 'piper'}"
    )


if __name__ == "__main__":
    main()
