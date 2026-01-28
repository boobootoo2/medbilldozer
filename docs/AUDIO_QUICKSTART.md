# Audio Narration Quick Start

## 🎯 30-Second Setup

Generate production-quality audio narration for the guided tour:

```bash
# 1. Install OpenAI library (if not already installed)
pip install openai

# 2. Set your API key
export OPENAI_API_KEY='sk-...'

# 3. Generate all audio files
python scripts/generate_tour_audio.py --openai

# Done! Audio will play automatically in the tour
```

## 💡 Or Let It Auto-Generate

If you have `OPENAI_API_KEY` in your environment, audio files will be generated automatically the first time each tour step is shown. No manual generation needed!

## 🎙️ Voice Options

Edit `scripts/generate_tour_audio.py` to change the voice:

```python
voice="alloy"   # Current: warm, neutral
# voice="echo"   # Male, clear and expressive
# voice="fable"  # British accent, warm
# voice="onyx"   # Deep, authoritative male
# voice="nova"   # Female, energetic
# voice="shimmer" # Female, soft and calm
```

## 📊 Costs & Specs

- **Cost**: ~$0.15 for all 9 tour steps (one-time)
- **Size**: ~100-200 KB per audio file
- **Quality**: Neural TTS (sounds human)
- **Generation**: ~30 seconds for all files
- **Caching**: Skips existing files (no wasted API calls)

## 🚀 Deployment Options

### Option A: Pre-generate (Recommended)

Generate before deployment:

```bash
python scripts/generate_tour_audio.py --openai
git add audio/*.mp3
git commit -m "Add tour audio"
git push
```

### Option B: Auto-generate on First Run

Set environment variable in deployment:

```bash
# Streamlit Cloud
OPENAI_API_KEY=sk-...

# Heroku
heroku config:set OPENAI_API_KEY=sk-...

# Docker
docker run -e OPENAI_API_KEY=sk-... ...
```

## 🔧 Troubleshooting

**No audio playing?**
```bash
# Check if files exist
ls -lh audio/

# Test generation
python scripts/generate_tour_audio.py --openai

# Check API key
echo $OPENAI_API_KEY
```

**API errors?**
- Verify API key is valid
- Check OpenAI account has credits
- Ensure `openai` library is installed: `pip install openai`

**Want to regenerate?**
```bash
# Delete existing files
rm audio/tour_step_*.mp3

# Generate fresh
python scripts/generate_tour_audio.py --openai
```

## 📚 More Info

- Full documentation: `docs/TOUR_AUDIO_NARRATION.md`
- Audio directory: `audio/README.md`
- Generation script: `scripts/generate_tour_audio.py`
