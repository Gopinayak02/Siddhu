from __future__ import annotations

import queue
import threading
from dataclasses import dataclass

import numpy as np
import sounddevice as sd


@dataclass(slots=True)
class AudioStats:
    callbacks: int = 0
    input_overflows: int = 0
    queue_drops: int = 0
    frames_received: int = 0


class LiveAudioStream:
    """Real-time capture with a non-blocking PortAudio callback."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "float32",
        queue_size: int = 50,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self._queue: queue.Queue[np.ndarray] = queue.Queue(
            maxsize=queue_size
        )
        self._stream: sd.InputStream | None = None
        self._running = False
        self._lock = threading.Lock()
        self.stats = AudioStats()

    @property
    def running(self) -> bool:
        return self._running

    def _callback(self, indata, frames, time_info, status) -> None:
        self.stats.callbacks += 1
        self.stats.frames_received += frames

        if status.input_overflow:
            self.stats.input_overflows += 1

        audio = indata[:, 0].copy()

        try:
            self._queue.put_nowait(audio)
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass

            try:
                self._queue.put_nowait(audio)
            except queue.Full:
                pass

            self.stats.queue_drops += 1

    def start(self) -> None:
        with self._lock:
            if self._running:
                return

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=None,
                blocksize=0,
                callback=self._callback,
            )
            self._stream.start()
            self._running = True

    def read(self, timeout: float = 1.0) -> np.ndarray:
        return self._queue.get(timeout=timeout)

    def queue_size(self) -> int:
        return self._queue.qsize()

    def stop(self) -> None:
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            self._running = False

    def clear(self) -> None:
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def close(self) -> None:
        self.stop()
        self.clear()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
