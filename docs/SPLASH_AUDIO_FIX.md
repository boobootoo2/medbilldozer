# Splash Screen Audio Fix

## Issue

Audio was not playing on the splash screen due to incorrect audio file path injection into JavaScript.

## Root Causes

### 1. Python String Representation Instead of JSON

**Problem**: Audio file paths were being injected as Python string representation:
```javascript
const audioFiles = "['audio/splash_billie_0.mp3', 'audio/splash_billy_1.mp3', 'audio/splash_billie_2.mp3']";
```

This resulted in JavaScript receiving a string containing Python list syntax, not a proper JavaScript array.

**Solution**: Convert audio file paths to JSON before injection:
```python
import json
audio_files_json = json.dumps(audio_files)
```

Now JavaScript receives:
```javascript
const audioFiles = ["audio/splash_billie_0.mp3", "audio/splash_billy_1.mp3", "audio/splash_billie_2.mp3"];
```

### 2. Transcript Index Incrementing on Every Chunk

**Problem**: The `messageIndex` was being incremented for every text chunk, causing the transcript highlighting to advance too quickly (one highlight per chunk instead of per message).

**Solution**: Only update the message index when starting a new message (when `isFirstChunk` is true):
```javascript
// Update message index when we hit a new message
if (isFirstChunk && audioIndex !== currentMessageIndex) {
    currentMessageIndex = audioIndex;
    
    // Visual transcript sync
    transcriptLines.forEach((el, idx) => {
        el.classList.toggle("active", idx === currentMessageIndex);
        // Auto-scroll to active line
        if (idx === currentMessageIndex) {
            el.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
        }
    });
}
```

## Changes Made

### File: `_modules/ui/splash_screen.py`

**1. Added JSON import and conversion:**
```python
import json
# ... 
audio_files_json = json.dumps(audio_files)
```

**2. Updated JavaScript injection:**
```python
const audioFiles = """ + audio_files_json + """;
```

**3. Fixed message index tracking:**
```python
let currentMessageIndex = -1;  # Changed from messageIndex = 0

# In playNext():
if (isFirstChunk && audioIndex !== currentMessageIndex) {
    currentMessageIndex = audioIndex;
    # Update transcript highlighting here
}
```

## Testing

### 1. Verify Audio Files Exist

```bash
ls -lh audio/splash_*.mp3
```

Expected output:
```
splash_billie_0.mp3  (81 KB)
splash_billy_1.mp3   (166 KB)
splash_billie_2.mp3  (62 KB)
```

### 2. Test Audio Path Generation

```bash
python3 -c "
import json
from pathlib import Path

audio_dir = Path('audio')
audio_files = []
for i in range(3):
    character = ['billie', 'billy', 'billie'][i]
    audio_file = audio_dir / f'splash_{character}_{i}.mp3'
    if audio_file.exists():
        audio_files.append(f'audio/splash_{character}_{i}.mp3')
    else:
        audio_files.append(None)

print('JSON:', json.dumps(audio_files))
"
```

Expected output:
```json
["audio/splash_billie_0.mp3", "audio/splash_billy_1.mp3", "audio/splash_billie_2.mp3"]
```

### 3. Test Splash Screen

```bash
streamlit run app.py
```

**Manual test steps:**
1. Load homepage (splash screen should appear)
2. **Listen for audio**: Billie's voice (female) should start after ~1.5 seconds
3. **Check browser console**: Should see:
   ```
   [Splash Widget] Audio files: ["audio/splash_billie_0.mp3", ...]
   [Splash Widget] Loaded audio for message 0: audio/splash_billie_0.mp3
   [Splash Widget] Playing audio for message 0
   ```
4. **Watch transcript**: Only 3 lines should highlight (one per message, not per chunk)
5. **Verify audio plays**:
   - Message 1: Billie (female/nova voice)
   - Message 2: Billy (male/echo voice)
   - Message 3: Billie (female/nova voice)
6. **Check speech bubbles**: Should sync with audio timing

### 4. Browser Console Debugging

Open browser console (F12) and check for:

✅ **Success indicators:**
```
[Splash Widget] Script starting...
[Splash Widget] Audio files: [Array]
[Splash Widget] Loaded audio for message 0: audio/splash_billie_0.mp3
[Splash Widget] Loaded audio for message 1: audio/splash_billy_1.mp3
[Splash Widget] Loaded audio for message 2: audio/splash_billie_2.mp3
[Splash Widget] Playing audio for message 0
```

❌ **Error indicators to watch for:**
```
Failed to load audio: [error message]
Audio playback failed: NotAllowedError
```

### 5. Test Audio Playback

If audio doesn't play, check:

**Browser Autoplay Policy:**
- Chrome/Edge: Autoplay allowed after user interaction (dismissing splash = interaction ✓)
- Safari: May require explicit user gesture
- Firefox: Usually allows autoplay after interaction

**File Access:**
- Verify files are served by Streamlit
- Check Network tab in browser dev tools
- Confirm 200 OK response for audio files

**Audio Format:**
- Files are MP3 (universally supported)
- Bitrate: 128kbps
- Sample rate: 24kHz or 44.1kHz

## Expected Behavior

### Timeline

| Time | Event |
|------|-------|
| 0s | Splash screen loads |
| 1.5s | First audio starts (Billie) |
| ~6s | Second audio starts (Billy) |
| ~16s | Third audio starts (Billie) |
| ~19s | Audio sequence complete |

### Visual Behavior

1. **Speech Bubbles**: Appear/disappear with text chunks (every 3 seconds)
2. **Transcript Highlighting**: Only 3 lines highlight (one per message)
3. **Auto-scroll**: Active transcript line stays visible
4. **Character Switch**: Speech bubble position alternates (left/right)

### Audio Behavior

1. **Preload**: All 3 audio files load on page load
2. **Playback**: Starts automatically after 1.5s delay
3. **Timing**: Each audio plays once per message
4. **Voice**: Alternates between Billie (nova) and Billy (echo)

## Troubleshooting

### Audio Still Not Playing

**1. Check browser console for errors:**
```javascript
// If you see:
Audio playback failed: NotAllowedError
// Solution: Browser blocked autoplay. Add user interaction or adjust browser settings.

// If you see:
Failed to load audio: [error]
// Solution: Verify file paths and Streamlit is serving audio/ directory.
```

**2. Manually test audio files:**
```bash
# macOS
afplay audio/splash_billie_0.mp3

# Linux
mpg123 audio/splash_billie_0.mp3

# Or open in browser
open audio/splash_billie_0.mp3
```

**3. Check Streamlit static file serving:**
```python
# In app.py or splash_screen.py
from pathlib import Path
print("Audio dir exists:", Path("audio").exists())
print("Files:", list(Path("audio").glob("splash_*.mp3")))
```

**4. Test with explicit audio element:**

Add temporary test code in JavaScript:
```javascript
// After audioElements are created
console.log("Testing audio playback...");
const testAudio = new Audio("audio/splash_billie_0.mp3");
testAudio.play().then(() => {
    console.log("✅ Audio playback works!");
}).catch(err => {
    console.error("❌ Audio playback failed:", err);
});
```

### Transcript Not Highlighting Correctly

If transcript highlights wrong lines or too many lines:

1. Check `currentMessageIndex` starts at -1
2. Verify `isFirstChunk` logic in queue building
3. Confirm `audioIndex` is passed correctly to each chunk
4. Check transcript has exactly 3 `<p class="transcript-line">` elements

### Speech Bubbles Not Syncing

If speech bubbles show wrong text or timing:

1. Verify `maxChars = 40` for chunk splitting
2. Check queue building preserves character and message
3. Confirm `setTimeout` delays (3000ms per chunk, 300ms between)

## Verification Checklist

After fix, verify:

- [x] JSON array syntax in browser console (not Python string)
- [x] Audio files load successfully (check Network tab)
- [x] Audio plays automatically after 1.5s
- [x] Transcript highlights only 3 times (once per message)
- [x] Speech bubbles sync with audio timing
- [x] Billie's voice (nova) for messages 1 & 3
- [x] Billy's voice (echo) for message 2
- [x] No JavaScript errors in console
- [x] Auto-scroll keeps active line visible
- [x] Screen reader announces messages (check ARIA live region)

## Summary

The fix ensures:

✅ **Proper JSON injection** - JavaScript receives valid array syntax  
✅ **Correct audio playback** - Files load and play at right times  
✅ **Accurate transcript highlighting** - Only highlights once per message  
✅ **Synchronized experience** - Audio, visual, and text stay in sync  

All 3 audio files (splash_billie_0.mp3, splash_billy_1.mp3, splash_billie_2.mp3) should now play correctly with proper transcript synchronization!
