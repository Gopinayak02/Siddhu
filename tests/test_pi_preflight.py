from __future__ import annotations

import importlib.util
import platform
import sys

from config.settings import load_settings


def check(name: str, module: str) -> None:
    result = bool(importlib.util.find_spec(module))
    print(f"{name:20s}: {'OK' if result else 'MISSING'}")


def main() -> None:
    settings = load_settings()

    print("=" * 60)
    print("SIDDHU PI PREFLIGHT")
    print("=" * 60)
    print(f"Platform             : {platform.platform()}")
    print(f"Architecture         : {platform.machine()}")
    print(f"Python               : {sys.version.split()[0]}")
    print()

    check("numpy", "numpy")
    check("sounddevice", "sounddevice")
    check("soxr", "soxr")
    check("PyYAML", "yaml")
    check("Faster-Whisper", "faster_whisper")
    check("Piper", "piper")
    check("pyopen-wakeword", "pyopen_wakeword")

    print()
    print(f"Wake model exists    : {settings.wake_model.exists()}")
    print(f"Piper model exists   : {settings.piper_model.exists()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
