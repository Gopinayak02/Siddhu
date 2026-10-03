from __future__ import annotations

import platform
from pathlib import Path


class WakeWordDetector:
    """
    Pi-first wake-word detector.

    Raspberry Pi/ARM64:
      pyopen-wakeword + TFLite

    Windows development:
      openwakeword + ONNX
    """

    def __init__(
        self,
        model_path: str | Path,
        threshold: float = 0.50,
        sample_rate: int = 16000,
    ) -> None:
        self.model_path = Path(model_path)
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.backend = None
        self.model_name = self.model_path.stem

        if platform.system() == "Linux":
            self._init_pi_backend()
        else:
            self._init_windows_backend()

    def _init_pi_backend(self) -> None:
        try:
            from pyopen_wakeword import OpenWakeWord
        except ImportError as exc:
            raise RuntimeError(
                "Pi wake-word backend missing. Install "
                "pyopen-wakeword==1.0.1."
            ) from exc

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Wake-word model not found: {self.model_path}"
            )

        self._features = None
        self._oww = OpenWakeWord.from_model(str(self.model_path))
        self.backend = "pyopen_wakeword"

    def _init_windows_backend(self) -> None:
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            raise RuntimeError(
                "Windows wake-word backend missing. Install "
                "openwakeword==0.6.0 and onnxruntime."
            ) from exc

        self._oww = Model(
            wakeword_models=[str(self.model_path)]
            if self.model_path.exists()
            else ["hey_jarvis"],
            inference_framework="onnx",
        )
        self.backend = "openwakeword"

    def _predict_pi(self, pcm_bytes: bytes) -> float:
        from pyopen_wakeword import OpenWakeWordFeatures

        if self._features is None:
            self._features = OpenWakeWordFeatures()

        best = 0.0

        for features in self._features.process_streaming(pcm_bytes):
            for prob in self._oww.process_streaming(features):
                best = max(best, float(prob))

        return best

    def score(self, pcm_int16) -> float:
        if self.backend == "pyopen_wakeword":
            return self._predict_pi(pcm_int16.tobytes())

        prediction = self._oww.predict(pcm_int16)
        if not prediction:
            return 0.0
        return max(float(v) for v in prediction.values())

    def detected(self, pcm_int16) -> tuple[bool, float]:
        score = self.score(pcm_int16)
        return score >= self.threshold, score

    def reset(self) -> None:
        if hasattr(self._oww, "reset"):
            self._oww.reset()
