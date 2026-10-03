# Publish this repository to GitHub

From the repository root on Windows:

```powershell
git init
git add .
git commit -m "Initial Raspberry Pi first SIDDHU voice core"
git branch -M main
```

Create an empty GitHub repository named `Siddhu` in your account, then:

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USER/Siddhu.git
git push -u origin main
```

Do not commit `.env`, model weights, or recorded audio.

On the Raspberry Pi:

```bash
git clone https://github.com/YOUR_GITHUB_USER/Siddhu.git
cd Siddhu
bash scripts/install_pi.sh
source .venv/bin/activate
python -m scripts.download_models
python -m piper.download_voices en_US-lessac-medium --data-dir models/piper
python -m tests.test_pi_preflight
python -m tests.test_wakeword_pi
python -m app.voice_loop
```
