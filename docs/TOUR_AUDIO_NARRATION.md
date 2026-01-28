# Guided Tour Audio Narration

## Overview

The MedBillDozer guided tour now supports **per-step audio narration** using Streamlit's native `st.audio()` component. This provides an accessible, engaging experience without requiring JavaScript or external dependencies.

## Features

✅ **Streamlit-Native**: Uses `st.audio()` - no JavaScript required  
✅ **Autoplay**: Audio plays automatically when each step loads  
✅ **Graceful Fallback**: Tour works perfectly even without audio files  
✅ **Zero Latency**: Pre-generated MP3s load instantly  
✅ **Offline-First**: Works without API dependencies  
✅ **Accessible**: Provides audio alternative to visual guidance  

## Architecture

### TourStep Data Structure

Each tour step includes a `narration` field:

```python
@dataclass
class TourStep:
    id: int
    title: str
    description: str
    narration: str  # Spoken version for audio playback
    target: str
    position: str
```

### Audio File Convention

Audio files follow this naming pattern:

```
audio/tour_step_{id}.mp3
```

Example:
```
audio/tour_step_1.mp3  → Step 1: Welcome to MedBillDozer!
audio/tour_step_2.mp3  → Step 2: Demo Documents
...
audio/tour_step_9.mp3  → Step 9: API Integration
```

### Runtime Behavior

When the tour renders each step:

1. **Check for audio file** at `audio/tour_step_{id}.mp3`
2. **If found**: Play audio with `st.audio(..., autoplay=True)`
3. **If not found**: Continue silently (no errors)
4. **Display visual guidance**: Info box with step description

## Generating Audio Files

### Quick Start (Automatic Generation)

**Option 1: OpenAI Neural TTS** ⭐ **Recommended**

Generate production-quality audio with one command:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'

# Generate all audio files automatically
python scripts/generate_tour_audio.py --openai
```

**Features:**
- ⭐⭐⭐⭐⭐ Quality: Sounds like a real human
- 🚀 Fast: Generates all 9 steps in ~30 seconds
- 💰 Cost: ~$0.15 total (one-time, cached forever)
- 🎯 Smart: Skips files that already exist
- 🔄 Auto-caching: Run anytime, no wasted API calls

**Or generate on-demand:** Audio is automatically generated when the tour runs if files don't exist (requires `OPENAI_API_KEY` in environment).

### Manual Generation Options

**Option 2: Print Text for Cloud TTS**

Print narration text for manual cloud TTS services:

```bash
python scripts/generate_tour_audio.py --print-text
```

### Option 3: Cloud TTS Services (Manual)

**Google Cloud Text-to-Speech:**
```bash
pip install google-cloud-texttospeech
# Configure credentials, then use cloud console or API
```

**Amazon Polly:**
```bash
aws polly synthesize-speech \
    --output-format mp3 \
    --voice-id Matthew \
    --text "$(python scripts/generate_tour_audio.py --print-text | grep 'Step 1' -A 2 | tail -1)" \
    audio/tour_step_1.mp3
```

**ElevenLabs (Highest Quality):**
- Copy narration text from script output
- Use web interface with "Billy" or "Billie" voice
- Download as MP3

### Option 4: Local TTS (Development/Testing)

```bash
pip install pyttsx3
python scripts/generate_tour_audio.py --local
```

This generates WAV files. Convert to MP3:

```bash
for f in audio/*.wav; do
    ffmpeg -i "$f" -codec:a libmp3lame -qscale:a 2 "${f%.wav}.mp3"
done
```

### Option 5: Manual Recording

1. Read narration text from `_modules/ui/guided_tour.py`
2. Record using Audacity or similar tool
3. Export as MP3 (128kbps, 44.1kHz)
4. Save as `audio/tour_step_{id}.mp3`

## How It Works

### Automatic Generation with Caching

The tour uses an intelligent caching system:

```python
def generate_audio_narration(step_id, narration_text):
    audio_file = Path(f"audio/tour_step_{step_id}.mp3")
    
    # Return cached file if exists
    if audio_file.exists():
        return audio_file
    
    # Generate using OpenAI TTS (one-time only)
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=narration_text
    )
    
    audio_file.write_bytes(response.read())
    return audio_file
```

**Benefits:**
- ✅ Zero latency after first generation
- ✅ No repeated API costs
- ✅ Works offline after initial generation
- ✅ Survives app restarts and reruns
- ✅ Can be committed to git for deployment

### Production Deployment

**Option A: Pre-generate for deployment**
```bash
# In CI/CD pipeline or before deployment
export OPENAI_API_KEY='...'
python scripts/generate_tour_audio.py --openai

# Commit to git
git add audio/*.mp3
git commit -m "Add tour audio narration"
```

**Option B: Generate on first run**
- Set `OPENAI_API_KEY` in environment variables
- Audio generates automatically on first tour launch
- Files are cached for subsequent runs
- Perfect for cloud deployments (Streamlit Cloud, Heroku, etc.)

## Narration Text

Each step has dedicated narration text optimized for audio:

| Step | Title | Narration Preview |
|------|-------|-------------------|
| 1 | Welcome | "Hi! I'm Billy. With my partner Billie, we'll help you uncover..." |
| 2 | Demo Documents | "Here are sample medical bills you can try. Expand any document..." |
| 3 | Document Input | "Paste your medical bill, pharmacy receipt, or insurance statement..." |
| 4 | Add Multiple Docs | "Click here to add multiple documents for comparison analysis." |
| 5 | Start Analysis | "Once you've pasted your document, click here to start the analysis..." |
| 6 | Sidebar Navigation | "Use the sidebar to ask Billy or Billie questions about your bills..." |
| 7 | Your Profile | "View and manage your health profile, including insurance coverage..." |
| 8 | Profile Management | "In the Profile view, you can manage your health insurance details..." |
| 9 | API Integration | "Built for healthcare and insurance workflows. MedBillDozer's API..." |

Full text available in `_modules/ui/guided_tour.py` or via:

```bash
python scripts/generate_tour_audio.py --print-text
```

## Implementation Details

### Audio Playback Code

```python
def run_guided_tour_runtime():
    # ... tour setup ...
    
    # Audio narration (if available)
    audio_dir = Path("audio")
    audio_file = audio_dir / f"tour_step_{current_step.id}.mp3"
    if audio_file.exists():
        try:
            st.audio(str(audio_file), format="audio/mp3", autoplay=True)
        except Exception:
            pass  # Silent fallback
    
    # Display visual guidance
    st.info(f"Step {current_step.id}: {current_step.title}...")
```

### Error Handling

Audio playback failures are caught silently to ensure the tour never breaks:

- ✅ Missing audio files → Tour continues without audio
- ✅ File read errors → Tour continues without audio
- ✅ Browser autoplay blocked → User sees visual guidance
- ✅ Unsupported format → Tour continues without audio

## Testing

### Test Audio Playback

1. Generate or place audio files in `audio/` directory
2. Run the app: `streamlit run app.py`
3. Start the guided tour
4. Navigate through steps
5. Verify audio plays automatically (check browser console for errors)

### Test Fallback Behavior

1. Remove all audio files from `audio/` directory
2. Start the guided tour
3. Verify tour works normally without audio
4. Confirm no errors appear in UI or console

## Browser Compatibility

| Browser | Autoplay Support | Notes |
|---------|------------------|-------|
| Chrome | ✅ Yes | Works with user interaction |
| Firefox | ✅ Yes | Works with user interaction |
| Safari | ⚠️  Limited | May require user gesture |
| Edge | ✅ Yes | Works with user interaction |

**Note**: Most browsers require user interaction before allowing autoplay. Since the tour starts after user dismisses the splash screen, this requirement is typically satisfied.

## Audio Specifications

**Recommended Settings:**
- Format: MP3
- Bitrate: 128 kbps (good quality, small size)
- Sample Rate: 44.1 kHz
- Channels: Mono (smaller file size)
- Duration: 5-15 seconds per step

**File Sizes:**
- ~100-200 KB per step
- Total: ~1-2 MB for all 9 steps

## Future Enhancements

Potential improvements:

1. **Voice Selection**: Let users choose Billy vs. Billie voice
2. **Speed Control**: Add playback speed slider (0.75x, 1x, 1.25x)
3. **Mute Option**: Toggle audio on/off
4. **Captions**: Display narration text as subtitles
5. **Multi-Language**: Support additional languages

## Troubleshooting

### Audio Not Playing

1. **Check file exists**: `ls audio/tour_step_1.mp3`
2. **Verify file path**: Audio files must be in `audio/` directory at project root
3. **Check browser console**: Look for autoplay or format errors
4. **Test file directly**: Try opening MP3 in browser

### Audio Quality Issues

1. **Use cloud TTS**: Google Cloud TTS or ElevenLabs produce better quality
2. **Increase bitrate**: Use 192 kbps instead of 128 kbps
3. **Professional recording**: Record custom narration with quality microphone
4. **Post-processing**: Apply noise reduction and normalization

## Resources

- **Streamlit Audio Docs**: [docs.streamlit.io/library/api-reference/media/st.audio](https://docs.streamlit.io/library/api-reference/media/st.audio)
- **Google Cloud TTS**: [cloud.google.com/text-to-speech](https://cloud.google.com/text-to-speech)
- **Amazon Polly**: [aws.amazon.com/polly](https://aws.amazon.com/polly)
- **ElevenLabs**: [elevenlabs.io](https://elevenlabs.io)
- **pyttsx3 (Local TTS)**: [pypi.org/project/pyttsx3](https://pypi.org/project/pyttsx3)

## Summary

Audio narration enhances the guided tour experience by:

- 🎯 **Improving accessibility** for users who prefer audio guidance
- 🚀 **Reducing cognitive load** with dual-channel information
- 💡 **Adding personality** with Billy and Billie voices
- ⚡ **Zero performance impact** with pre-generated files
- 🛡️ **Maintaining reliability** with graceful fallback

The implementation is production-ready, requiring only the addition of audio files to activate the feature.
