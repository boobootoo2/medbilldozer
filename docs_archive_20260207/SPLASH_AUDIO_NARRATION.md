# Splash Screen Audio Narration

## Overview

The MedBillDozer splash screen features **dual-voice audio narration** with Billy (male voice) and Billie (female voice) introducing the application. This creates an engaging, accessible, and professional first impression for users.

## Features

### 🎭 Character-Specific Voices

- **Billy (Male)**: OpenAI `echo` voice - authoritative, clear, professional
- **Billie (Female)**: OpenAI `nova` voice - warm, friendly, welcoming

### 🎵 Audio Specifications

| Property | Value |
|----------|-------|
| **Format** | MP3 |
| **Model** | OpenAI TTS-1 (Neural) |
| **Quality** | Production (128kbps) |
| **Total Size** | ~310 KB (3 files) |
| **Billy Voice** | `echo` (male) |
| **Billie Voice** | `nova` (female) |

### 📝 Narration Script

1. **Billie** (nova): "Hi! We're Billy and Billie—your guides to finding billing mistakes."
2. **Billy** (echo): "We scan medical bills, pharmacy receipts, dental claims, and insurance statements to uncover overcharges, duplicates, and missed reimbursements."
3. **Billie** (nova): "Ready to see how easy it is to double-check your bills?"

## Implementation

### Audio Generation

Audio files are pre-generated using OpenAI Neural TTS and cached in the `audio/` directory:

```python
from _modules.ui.splash_screen import prepare_splash_audio

# Generate all splash screen audio files
prepare_splash_audio()
```

**Generated files:**
- `audio/splash_billie_0.mp3` - Billie's welcome (81 KB)
- `audio/splash_billy_1.mp3` - Billy's explanation (166 KB)
- `audio/splash_billie_2.mp3` - Billie's call to action (62 KB)

### Auto-Generation Script

```bash
python3 scripts/generate_splash_audio.py
```

**Features:**
- ✅ Smart caching (skips existing files)
- ✅ Progress feedback
- ✅ Size reporting
- ✅ Voice assignment display
- ✅ Next steps guidance

### Integration in Splash Screen

The `render_splash_screen()` function automatically:

1. **Pre-generates audio** (if not cached)
2. **Loads audio files** into the HTML component
3. **Synchronizes playback** with visual speech bubbles
4. **Handles errors gracefully** (splash works without audio)

```python
def render_splash_screen():
    # Pre-generate audio files (uses cache if exist)
    prepare_splash_audio()
    
    # Check which audio files are available
    audio_files = []
    for i in range(3):
        character = ["billie", "billy", "billie"][i]
        audio_file = Path("audio") / f"splash_{character}_{i}.mp3"
        if audio_file.exists():
            audio_files.append(f"audio/splash_{character}_{i}.mp3")
        else:
            audio_files.append(None)
    
    # Render with audio integration...
```

### JavaScript Audio Playback

The JavaScript in the splash screen HTML:

1. **Preloads audio elements** for all 3 messages
2. **Plays audio on first chunk** of each message
3. **Synchronizes with speech bubbles** and transcript
4. **Handles errors gracefully** with fallback

```javascript
// Audio elements for each message
const audioElements = [];
rawMessages.forEach((msg, idx) => {
    const audioPath = audioFiles[idx];
    if (audioPath && audioPath !== 'None' && audioPath !== null) {
        const audio = new Audio(audioPath);
        audio.preload = 'auto';
        audioElements.push(audio);
    } else {
        audioElements.push(null);
    }
});

// Play audio on first chunk
if (isFirstChunk && audioElements[audioIndex]) {
    currentAudio = audioElements[audioIndex];
    currentAudio.play().catch(err => {
        console.warn('[Splash Widget] Audio playback failed:', err);
    });
}
```

## Voice Selection Rationale

### Billy - `echo` Voice (Male)

**Characteristics:**
- Authoritative and professional
- Clear articulation
- Technical credibility
- Trustworthy tone

**Best for:**
- Explaining complex features
- Technical descriptions
- Professional credentials

**Sample line:** *"We scan medical bills, pharmacy receipts, dental claims..."*

### Billie - `nova` Voice (Female)

**Characteristics:**
- Warm and friendly
- Welcoming tone
- Approachable personality
- Engaging delivery

**Best for:**
- Greetings and introductions
- Calls to action
- Building rapport

**Sample lines:**
- *"Hi! We're Billy and Billie..."*
- *"Ready to see how easy it is?"*

## Accessibility

### Screen Reader Support

- ✅ **Live region** for dynamic content announcements
- ✅ **Transcript visible** on screen (synced with audio)
- ✅ **Active line highlighting** shows current speech
- ✅ **ARIA labels** on widget container

### Audio Fallback

If audio fails to load or play:
- ✅ Visual speech bubbles still display
- ✅ Transcript remains visible and synced
- ✅ No JavaScript errors or broken experience
- ✅ User can still dismiss and continue

## User Experience

### First-Time Users

1. **Splash screen loads** with gradient background
2. **Billy & Billie animation** starts automatically
3. **Audio narration plays** (Billie → Billy → Billie)
4. **Speech bubbles sync** with audio and transcript
5. **Transcript highlights** current message
6. **User dismisses** when ready → Guided tour starts

### Timing & Flow

| Event | Timing | Description |
|-------|--------|-------------|
| **Animation Start** | 0s | Characters appear with envelope |
| **First Audio** | 1.5s | Billie welcomes users |
| **Second Audio** | ~5s | Billy explains features |
| **Third Audio** | ~12s | Billie's call to action |
| **Total Duration** | ~15s | Complete narration sequence |
| **User Control** | Anytime | Can dismiss immediately |

## Cost & Performance

### OpenAI TTS Costs

| Item | Cost |
|------|------|
| **Billie #1** | ~$0.08 (81 KB) |
| **Billy #2** | ~$0.17 (166 KB) |
| **Billie #3** | ~$0.06 (62 KB) |
| **Total** | **~$0.31** (one-time) |

### Performance

- **Preload Strategy**: Audio loaded before playback
- **File Size**: ~310 KB total (acceptable for splash)
- **Caching**: Files cached forever (no regeneration)
- **Network**: 3 small files, minimal bandwidth

## Testing

### Test Audio Generation

```bash
# Generate audio files
python3 scripts/generate_splash_audio.py

# Verify files exist
ls -lh audio/splash_*.mp3

# Expected output:
# splash_billie_0.mp3  (~81 KB)
# splash_billie_2.mp3  (~62 KB)
# splash_billy_1.mp3   (~166 KB)
```

### Test Splash Screen

```bash
# Start app
streamlit run medBillDozer.py

# Manual test steps:
# 1. Load homepage (splash should appear)
# 2. Listen for Billie's welcome (female voice)
# 3. Listen for Billy's explanation (male voice)
# 4. Listen for Billie's call to action (female voice)
# 5. Verify speech bubbles sync with audio
# 6. Check transcript highlighting
# 7. Click "Get Started" to dismiss
```

### Test Audio Playback

```bash
# Play individual files (macOS)
afplay audio/splash_billie_0.mp3
afplay audio/splash_billy_1.mp3
afplay audio/splash_billie_2.mp3

# Or open in browser
open audio/splash_billie_0.mp3
```

### Test Fallback (No Audio)

```bash
# Temporarily remove audio files
mv audio/splash_billie_0.mp3 audio/splash_billie_0.mp3.bak
mv audio/splash_billy_1.mp3 audio/splash_billy_1.mp3.bak
mv audio/splash_billie_2.mp3 audio/splash_billie_2.mp3.bak

# Run app - should work without audio
streamlit run medBillDozer.py

# Restore files
mv audio/splash_billie_0.mp3.bak audio/splash_billie_0.mp3
mv audio/splash_billy_1.mp3.bak audio/splash_billy_1.mp3
mv audio/splash_billie_2.mp3.bak audio/splash_billie_2.mp3
```

## Deployment

### Strategy: Pre-Generated Audio (Recommended)

Commit the pre-generated audio files to git for production deployment:

```bash
# Stage audio files
git add audio/splash_*.mp3

# Commit with descriptive message
git commit -m "Add splash screen dual-voice audio narration

- Billy (male, echo voice): Technical explanation
- Billie (female, nova voice): Welcome & call to action
- 3 audio files, ~310 KB total
- OpenAI Neural TTS (production quality)
- Synchronized with speech bubbles and transcript"

# Push to repository
git push origin develop
```

### Production Deployment

**Files included in deployment:**
```
audio/
├── splash_billie_0.mp3  ✓ (81 KB)
├── splash_billy_1.mp3   ✓ (166 KB)
└── splash_billie_2.mp3  ✓ (62 KB)
```

**Deployment targets:**
- ✅ Streamlit Cloud (automatic)
- ✅ Heroku (in slug)
- ✅ Docker (in image)
- ✅ Manual deployment (in repo)

### Environment Requirements

**Production:**
- ❌ No `OPENAI_API_KEY` required (pre-generated)
- ✅ Audio files in `audio/` directory
- ✅ MP3 format support in browser

**Development:**
- ✅ `OPENAI_API_KEY` in `.env` (for generation)
- ✅ `openai` Python package installed

## Troubleshooting

### Audio Not Playing

**Check browser console:**
```javascript
// Should see:
[Splash Widget] Loaded audio for message 0: audio/splash_billie_0.mp3
[Splash Widget] Playing audio for message 0
```

**Common issues:**
1. **Autoplay blocked**: Audio plays after user interaction (dismiss button)
2. **Files missing**: Run `python3 scripts/generate_splash_audio.py`
3. **Path incorrect**: Check `audio_files` array in console

### Audio Out of Sync

**Check timing:**
- Each message chunk displays for 3 seconds
- Audio plays on first chunk of each message
- Visual transcript should highlight active line

**Fix:**
- Adjust `setTimeout(playNext, 300)` for faster/slower pacing
- Modify `3000` ms display time per chunk

### Generation Fails

**Check requirements:**
```bash
# Verify OpenAI API key
echo $OPENAI_API_KEY

# Verify openai package
pip list | grep openai

# Check logs
python3 scripts/generate_splash_audio.py
```

**Common errors:**
- `ImportError: No module named 'openai'` → Run `pip install openai`
- `AuthenticationError` → Set `OPENAI_API_KEY` in `.env`
- `Permission denied` → Check `audio/` directory permissions

## Future Enhancements

### Potential Improvements

1. **Voice Customization**: Allow users to select preferred voices
2. **Language Support**: Multi-language narration
3. **Skip/Replay Controls**: UI controls for audio playback
4. **Volume Control**: Adjustable audio volume
5. **Subtitle Toggle**: Optional on-screen captions
6. **Alternative Voices**: Different voice packs for accessibility

### Alternative Voices

**Other OpenAI TTS Voices:**
- `alloy` - Balanced, neutral (good alternative for Billy)
- `fable` - British accent, expressive (alternative for Billie)
- `onyx` - Deep, authoritative (strong male alternative)
- `shimmer` - Soft, gentle (alternative for Billie)

## Best Practices

### Do's ✅

- ✅ Pre-generate audio for production (no API calls)
- ✅ Test with audio enabled and disabled
- ✅ Keep audio files under 200 KB each
- ✅ Use descriptive voice for technical content (Billy/echo)
- ✅ Use friendly voice for greetings (Billie/nova)
- ✅ Sync audio with visual elements
- ✅ Provide transcript for accessibility

### Don'ts ❌

- ❌ Don't regenerate audio on every page load
- ❌ Don't block UI while audio loads
- ❌ Don't force audio playback (respect browser policies)
- ❌ Don't rely solely on audio (keep visual fallback)
- ❌ Don't make audio too long (15s max recommended)
- ❌ Don't forget to test without audio

## Summary

✅ **Dual-voice narration** (Billy/echo + Billie/nova)  
✅ **Production-quality** OpenAI Neural TTS  
✅ **Pre-generated files** (~310 KB total)  
✅ **Smart caching** (no API calls in production)  
✅ **Synchronized playback** with speech bubbles  
✅ **Accessibility features** (transcript, live region)  
✅ **Graceful fallback** (works without audio)  
✅ **One-time cost** (~$0.31)  

The splash screen audio creates a **professional, engaging, and accessible** first impression for MedBillDozer users! 🎭🎵
