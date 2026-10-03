# SIDDHU — Raspberry Pi First

SIDDHU is a voice-first assistant designed to run from a Raspberry Pi 5 as the edge controller.

## Target

- Raspberry Pi 5, 8 GB
- Raspberry Pi OS 64-bit
- Raspberry Pi OS target: Trixie (Debian 13)
- USB microphone + speaker
- Local wake word
- Local STT
- Local Piper TTS
- AI Router to a local or remote model endpoint
- No heavy work inside the PortAudio callback

## Runtime

```text
USB MIC
  ↓
Audio callback (very small)
  ↓
Queue
  ↓
Wake word
  ↓
Command capture
  ↓
Faster-Whisper STT
  ↓
AI Router
  ↓
Piper TTS
  ↓
Speaker
```

The Pi is the orchestrator. Heavy AI may be local, on a Hailo accelerator, or on a remote L40S/server. The voice stack does not depend on the model provider.

## Current development wake word

`HEY JARVIS` is used only to validate the Pi audio/wake-word path.

The final wake word is `SIDDHU`.

A real SIDDHU wake-word model must be trained/verified and placed in `models/wakeword/`. This repository does not pretend that the HEY JARVIS model is a SIDDHU model.

## Quick start on Raspberry Pi

```bash
git clone https://github.com/YOUR_GITHUB_USER/Siddhu.git
cd Siddhu
bash scripts/install_pi.sh
source .venv/bin/activate
python -m scripts.download_models
python -m piper.download_voices en_US-lessac-medium --data-dir models/piper
python -m tests.test_pi_preflight
python -m tests.test_wakeword_pi
```

For the first wake-word test, say:

```text
HEY JARVIS
```

## AI Router

The router is intentionally an adapter.

Set:

```bash
cp .env.example .env
nano .env
```

Then configure:

```text
OMNI_ROUTER_URL=
OMNI_ROUTER_API_KEY=
OMNI_ROUTER_MODEL=
```

The built-in adapter expects an OpenAI-compatible JSON endpoint. This is an integration boundary, not a claim about the private Omni Router API. When the exact Omni Router endpoint/schema is available, only `ai/router/client.py` needs to be adapted.

## Full voice loop

```bash
source .venv/bin/activate
python -m app.voice_loop
```

The first production prototype uses an 8-second command capture window. Automatic end-of-speech detection is deliberately not coupled to wake-word detection yet because the room tests showed strong false positives from simple energy VAD.

## STT model

Default:

```text
base
CPU
int8
```

Change in `.env`:

```text
SIDDHU_STT_MODEL=tiny
```

or:

```text
SIDDHU_STT_MODEL=base
```

Use `tiny` first on the Pi for a quick benchmark and then compare with `base`.

## Models are NOT stored in Git

Voice and model weights are downloaded by scripts. This keeps the repository small and reproducible.

## Raspberry Pi performance strategy

- Keep the microphone callback lightweight.
- Use bounded queues.
- Keep models resident instead of reloading them for every command.
- Use 16 kHz mono audio for wake-word inference.
- Route heavy LLM/VLM work to the configured AI backend.
- Benchmark STT on the Pi before selecting a larger model.
- Use active cooling and a proper 5 V / 5 A supply for Pi 5.

## First milestone

The first Pi milestone is:

```text
Pi boots
  ↓
Mic works
  ↓
Wake word works
  ↓
Command WAV is captured
  ↓
STT returns text
  ↓
Router returns text
  ↓
Piper speaks
```

That is the deliverable voice core.
