# How to Regenerate Specific Audio Files

## Quick Answer

To regenerate a **specific tour MP3**, simply delete it and run the generation script:

```bash
# Delete the specific file you want to regenerate
rm audio/tour_step_5.mp3

# Regenerate using OpenAI Neural TTS
python scripts/generate_tour_audio.py --openai
```

The script automatically **skips existing files**, so it will only generate the missing one!

---

## Regenerate Single Tour Step

### Step 1: Delete the File

```bash
# Example: Regenerate step 5
rm audio/tour_step_5.mp3
```

### Step 2: Run Generation Script

```bash
export OPENAI_API_KEY='sk-...'  # If not already set
python scripts/generate_tour_audio.py --openai
```

**Output:**
```
🎙️  Generating audio narration with OpenAI Neural TTS...

⏭️  Step 1: Already exists, skipping
⏭️  Step 2: Already exists, skipping
⏭️  Step 3: Already exists, skipping
⏭️  Step 4: Already exists, skipping
🎤 Step 5: Upload Documents
   Text: Let's start by uploading a medical bill or insurance statement...
   ✅ Saved: tour_step_5.mp3 (88 KB)
⏭️  Step 6: Already exists, skipping
⏭️  Step 7: Already exists, skipping
⏭️  Step 8: Already exists, skipping
⏭️  Step 9: Already exists, skipping

✅ Audio generation complete!
```

---

## Regenerate Multiple Specific Steps

```bash
# Delete multiple files
rm audio/tour_step_{3,5,7}.mp3

# Regenerate only those
python scripts/generate_tour_audio.py --openai
```

---

## Regenerate ALL Audio Files

### Option 1: Delete and Regenerate

```bash
# Delete all tour audio
rm audio/tour_step_*.mp3

# Regenerate everything
python scripts/generate_tour_audio.py --openai
```

### Option 2: Force Regeneration (Coming Soon)

*Currently, the script respects existing files. To regenerate, you must delete first.*

---

## Regenerate Splash Screen Audio

The splash screen has 3 audio files (Billy & Billie voices):

```bash
# Delete splash audio
rm audio/splash_*.mp3

# Regenerate by running the app
streamlit run app.py
# Audio generates automatically on splash screen load
```

Or regenerate manually:

```python
# In Python console or script
from _modules.ui.splash_screen import prepare_splash_audio
prepare_splash_audio()
```

---

## Change Voice or Settings

To regenerate with **different voice** or settings:

### Step 1: Delete the File

```bash
rm audio/tour_step_5.mp3
```

### Step 2: Edit Generation Script

Edit `scripts/generate_tour_audio.py`:

```python
response = client.audio.speech.create(
    model="tts-1",  # or "tts-1-hd" for higher quality
    voice="nova",   # Change voice here! ⬅️
    input=step.narration,
    speed=1.0       # Adjust speed (0.25 to 4.0)
)
```

**Available voices:**
- `alloy` - Warm, neutral (current default)
- `echo` - Male, clear and expressive
- `fable` - British accent, warm
- `onyx` - Deep, authoritative male
- `nova` - Female, energetic ⭐
- `shimmer` - Female, soft and calm

### Step 3: Regenerate

```bash
python scripts/generate_tour_audio.py --openai
```

---

## Alternative: Edit Code Directly

If you want to regenerate from within the guided tour module:

```python
# In Python console
from pathlib import Path
from _modules.ui.guided_tour import generate_audio_narration, TOUR_STEPS

# Regenerate step 5
step = TOUR_STEPS[4]  # Index 4 = Step 5
audio_file = Path("audio") / f"tour_step_{step.id}.mp3"
audio_file.unlink(missing_ok=True)  # Delete
generate_audio_narration(step.id, step.narration)  # Regenerate
```

---

## Verify Regeneration

### Check File Exists

```bash
ls -lh audio/tour_step_5.mp3
```

### Test in App

1. Start app: `streamlit run app.py`
2. Start guided tour
3. Navigate to the step you regenerated
4. Audio should play with new version

### Play in Terminal

```bash
# macOS
afplay audio/tour_step_5.mp3

# Linux
mpg123 audio/tour_step_5.mp3

# Windows (WSL)
powershell.exe -c "(New-Object Media.SoundPlayer 'audio/tour_step_5.mp3').PlaySync();"
```

---

## Troubleshooting

### Script Says "Already Exists, Skipping"

You forgot to delete the file first:

```bash
# Delete it
rm audio/tour_step_5.mp3

# Try again
python scripts/generate_tour_audio.py --openai
```

### "OpenAI API Key Not Set"

```bash
export OPENAI_API_KEY='sk-your-key-here'
```

Or add to your shell config:

```bash
# ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY='sk-your-key-here'
```

### "OpenAI Library Not Installed"

```bash
pip install openai
```

### File Regenerates But Sounds the Same

OpenAI TTS is **deterministic** - same input = same output.

To get different audio:
1. Change the **voice** (see "Change Voice or Settings" above)
2. Change the **narration text** in `_modules/ui/guided_tour.py`
3. Change the **speed** parameter

---

## Cost & Time

**Per file:**
- Cost: ~$0.015 per file
- Time: ~2-3 seconds per file

**All 9 tour steps:**
- Cost: ~$0.15 total
- Time: ~20-30 seconds

**Splash screen (3 files):**
- Cost: ~$0.045 total
- Time: ~10 seconds

---

## Summary

| Task | Command |
|------|---------|
| **Regenerate step 5** | `rm audio/tour_step_5.mp3 && python scripts/generate_tour_audio.py --openai` |
| **Regenerate all tour** | `rm audio/tour_step_*.mp3 && python scripts/generate_tour_audio.py --openai` |
| **Regenerate splash** | `rm audio/splash_*.mp3 && streamlit run app.py` |
| **Change voice** | Edit `scripts/generate_tour_audio.py`, delete file, regenerate |

**Remember**: The generation script is **smart** - it only generates missing files, so you must **delete first** to regenerate!
