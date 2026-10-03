#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "SIDDHU RASPBERRY PI INSTALLER"
echo "============================================================"

if [[ "$(uname -m)" != "aarch64" ]]; then
  echo "ERROR: 64-bit ARM64 is required."
  echo "Detected: $(uname -m)"
  exit 1
fi

source /etc/os-release

echo "OS      : ${PRETTY_NAME:-unknown}"
echo "ARCH    : $(uname -m)"
echo "PYTHON  : $(python3 --version)"

echo
echo "Installing system dependencies..."

sudo apt update
sudo apt install -y   git   python3   python3-venv   python3-dev   build-essential   libsndfile1   portaudio19-dev   libopenblas-dev   alsa-utils

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements/pi.txt

mkdir -p models/wakeword models/piper data/audio_test logs

echo
echo "============================================================"
echo "INSTALL COMPLETE"
echo "============================================================"
echo "Activate with:"
echo "  source .venv/bin/activate"
echo
echo "Next:"
echo "  python -m scripts.download_models"
echo "  python -m piper.download_voices en_US-lessac-medium --data-dir models/piper"
echo "  python -m tests.test_pi_preflight"
echo "  python -m tests.test_wakeword_pi"
