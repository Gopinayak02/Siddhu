from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(
    os.getenv("SIDDHU_ROOT", Path(__file__).resolve().parents[1])
).resolve()


def _path_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser().resolve() if value else default


@dataclass(slots=True)
class Settings:
    name: str = "Siddhu"
    wakeword: str = "hey_jarvis"
    language: str = "auto"

    input_rate: int = 16000
    channels: int = 1
    queue_size: int = 50
    command_seconds: float = 8.0

    wake_threshold: float = 0.50
    wake_model: Path = ROOT / "models" / "wakeword" / "hey_jarvis_v0.1.tflite"
    wake_backend: str = "auto"

    stt_model: str = "base"
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"

    piper_model: Path = ROOT / "models" / "piper" / "en_US-lessac-medium.onnx"

    omni_router_url: str = ""
    omni_router_api_key: str = ""
    omni_router_model: str = ""
    omni_router_timeout: float = 60.0

    data_dir: Path = ROOT / "data"
    model_dir: Path = ROOT / "models"
    log_dir: Path = ROOT / "logs"


def load_settings() -> Settings:
    s = Settings(
        name=os.getenv("SIDDHU_NAME", "Siddhu"),
        wakeword=os.getenv("SIDDHU_WAKEWORD", "hey_jarvis"),
        language=os.getenv("SIDDHU_LANGUAGE", "auto"),
        input_rate=int(os.getenv("SIDDHU_INPUT_RATE", "16000")),
        channels=int(os.getenv("SIDDHU_CHANNELS", "1")),
        queue_size=int(os.getenv("SIDDHU_QUEUE_SIZE", "50")),
        command_seconds=float(os.getenv("SIDDHU_COMMAND_SECONDS", "8")),
        wake_threshold=float(os.getenv("SIDDHU_WAKE_THRESHOLD", "0.50")),
        wake_model=_path_env(
            "SIDDHU_WAKE_MODEL",
            ROOT / "models" / "wakeword" / "hey_jarvis_v0.1.tflite",
        ),
        wake_backend=os.getenv("SIDDHU_WAKE_BACKEND", "auto"),
        stt_model=os.getenv("SIDDHU_STT_MODEL", "base"),
        stt_device=os.getenv("SIDDHU_STT_DEVICE", "cpu"),
        stt_compute_type=os.getenv("SIDDHU_STT_COMPUTE_TYPE", "int8"),
        piper_model=_path_env(
            "SIDDHU_PIPER_MODEL",
            ROOT / "models" / "piper" / "en_US-lessac-medium.onnx",
        ),
        omni_router_url=os.getenv("OMNI_ROUTER_URL", "").strip(),
        omni_router_api_key=os.getenv("OMNI_ROUTER_API_KEY", "").strip(),
        omni_router_model=os.getenv("OMNI_ROUTER_MODEL", "").strip(),
        omni_router_timeout=float(
            os.getenv("OMNI_ROUTER_TIMEOUT", "60")
        ),
        data_dir=_path_env("SIDDHU_DATA_DIR", ROOT / "data"),
        model_dir=_path_env("SIDDHU_MODEL_DIR", ROOT / "models"),
        log_dir=_path_env("SIDDHU_LOG_DIR", ROOT / "logs"),
    )

    s.data_dir.mkdir(parents=True, exist_ok=True)
    s.model_dir.mkdir(parents=True, exist_ok=True)
    (s.model_dir / "wakeword").mkdir(parents=True, exist_ok=True)
    (s.model_dir / "piper").mkdir(parents=True, exist_ok=True)
    s.log_dir.mkdir(parents=True, exist_ok=True)

    return s
