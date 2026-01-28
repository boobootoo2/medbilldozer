# Tour Audio Narration Files

This directory contains audio narration files for the guided tour.

## File Structure

Each tour step should have a corresponding audio file:

```
audio/
├── tour_step_1.mp3  # Welcome to MedBillDozer
├── tour_step_2.mp3  # Demo Documents
├── tour_step_3.mp3  # Document Input
├── tour_step_4.mp3  # Add Multiple Documents
├── tour_step_5.mp3  # Start Analysis
├── tour_step_6.mp3  # Sidebar Navigation
├── tour_step_7.mp3  # Your Profile
├── tour_step_8.mp3  # Profile Management
└── tour_step_9.mp3  # API Integration
```

## Generating Audio Files

### Recommended: OpenAI Neural TTS ⭐

**Highest quality, sounds like a real human:**

```bash
# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Generate all files automatically
python scripts/generate_tour_audio.py --openai
```

**Features:**
- ⭐⭐⭐⭐⭐ Natural-sounding voices
- 🚀 Fast generation (~30 seconds for all)
- 💰 ~$0.15 total cost (one-time)
- 🔄 Auto-caching (skips existing files)
- 🎯 6 voice options (alloy, echo, fable, onyx, nova, shimmer)

**Or let it auto-generate:** If you have `OPENAI_API_KEY` set, audio generates automatically when the tour runs for the first time.

### Alternative Options

**Option 2: Print Text for Manual TTS**

```bash
python scripts/generate_tour_audio.py --print-text
```

**Option 3: Local TTS (pyttsx3)**

For offline generation (lower quality):

```bash
pip install pyttsx3
python scripts/generate_tour_audio.py --local
```

**Option 4: Record Your Own

Use Audacity or similar tools to record custom narration:
1. Read the `narration` field from each TourStep
2. Export as MP3 with 128kbps bitrate
3. Save as `tour_step_X.mp3`

## Audio Specifications

- **Format:** MP3
- **Bitrate:** 128kbps (recommended for web)
- **Sample Rate:** 44.1kHz or 22.05kHz
- **Channels:** Mono or Stereo
- **Duration:** 5-15 seconds per step

## Narration Text

The narration text for each step is defined in `_modules/ui/guided_tour.py`:

```python
TourStep(
    id=1,
    title="Welcome to MedBillDozer!",
    description="👋 Hi! I'm Billy...",
    narration="Hi! I'm Billy. With my partner Billie...",  # Use this text
    target="logo",
    position="top"
)
```

## Testing

Audio files are automatically loaded by the tour runtime:

1. Start the app: `streamlit run app.py`
2. Dismiss splash screen
3. Start the guided tour
4. Navigate through steps - audio plays automatically

## Fallback Behavior

If audio files are missing:
- ✅ Tour continues normally
- ✅ No errors displayed to users
- ✅ Visual guidance still works

The tour gracefully degrades to silent mode if audio is unavailable.
