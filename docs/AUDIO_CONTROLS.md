# Audio Controls - Mute/Unmute Feature

## Overview

The audio controls feature provides users with the ability to mute/unmute all audio narration across the splash screen and guided tour. This includes:

- **Configuration options** in `app_config.yaml`
- **Persistent mute button** in the sidebar
- **Session state management** for mute preferences
- **Automatic integration** with splash screen and tour audio

## Configuration

### app_config.yaml

Add audio configuration under the `features` section:

```yaml
features:
  # Audio Narration - Audio settings for splash screen and guided tour
  audio:
    enabled: true  # Enable/disable all audio narration
    autoplay: true  # Attempt to autoplay (may require user interaction)
    show_mute_button: true  # Show mute/unmute button in UI
    default_volume: 1.0  # Volume level (0.0 to 1.0)
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Master switch for all audio features |
| `autoplay` | boolean | `true` | Attempt to autoplay audio (browser may block) |
| `show_mute_button` | boolean | `true` | Display mute/unmute button in UI |
| `default_volume` | float | `1.0` | Default volume level (0.0 to 1.0) |

## User Experience

### Mute Button Location

The mute button appears at the **top of the sidebar**, above the guided tour controls:

```
┌─ Sidebar ────────────────┐
│                          │
│    [🔊]                  │  ← Mute button
│                          │
│  📚 Guided Tour          │
│  Step 1 of 9             │
│  [Audio playing...]      │
│                          │
└──────────────────────────┘
```

### Button States

**Unmuted (Audio Enabled):**
- Icon: 🔊
- Tooltip: "Mute audio"
- Color: Normal
- Behavior: Audio plays normally

**Muted (Audio Disabled):**
- Icon: 🔇
- Tooltip: "Unmute audio"
- Color: Grayed out
- Behavior: All audio is suppressed

### User Flow

1. **User loads app** → Audio enabled by default (if configured)
2. **User clicks mute button** → Audio stops, icon changes to 🔇
3. **Mute state persists** → Remains muted across navigation
4. **User clicks unmute** → Audio resumes, icon changes to 🔊

## Technical Implementation

### Module Structure

```
_modules/ui/audio_controls.py
├── initialize_audio_state()        # Initialize session state
├── is_audio_muted()                # Check if audio is muted
├── toggle_mute()                   # Toggle mute state
├── render_mute_button()            # Render sidebar button
├── render_inline_mute_button()     # Render inline button
├── get_audio_enabled_for_javascript()  # Get state for JS
└── inject_audio_state_into_html()  # Inject state into HTML
```

### Session State

The mute state is stored in `st.session_state.audio_muted`:

```python
# Initialize
if 'audio_muted' not in st.session_state:
    st.session_state.audio_muted = False

# Check state
muted = st.session_state.audio_muted

# Toggle
st.session_state.audio_muted = not st.session_state.audio_muted
```

### Integration with Splash Screen

The splash screen checks mute state before playing audio:

```python
# In splash_screen.py
from _modules.ui.audio_controls import is_audio_muted

def render_splash_screen():
    # Check if audio is muted
    audio_muted = is_audio_muted()
    
    # Inject into JavaScript
    const audioMuted = """ + ("true" if audio_muted else "false") + """;
    let audioEnabled = !audioMuted;
```

JavaScript respects the mute state:

```javascript
// Only play if not muted
if (isFirstChunk && !audioMuted) {
    currentAudio.play();
}
```

### Integration with Guided Tour

The guided tour checks mute state before generating/playing audio:

```python
# In guided_tour.py
from _modules.ui.audio_controls import is_audio_muted

def run_guided_tour_runtime():
    # Only generate/play audio if not muted
    if not is_audio_muted():
        audio_file = generate_audio_narration(step.id, step.narration)
        if audio_file and audio_file.exists():
            st.audio(str(audio_file), format="audio/mp3", autoplay=True)
```

### Config Helper Functions

```python
# In _modules/utils/config.py

def is_audio_enabled() -> bool:
    """Check if audio narration is enabled."""
    return get_config().is_feature_enabled("audio")

def is_audio_autoplay_enabled() -> bool:
    """Check if audio autoplay is enabled."""
    config = get_config()
    return config.get("features.audio.autoplay", True)

def should_show_mute_button() -> bool:
    """Check if mute button should be shown in UI."""
    config = get_config()
    return config.get("features.audio.show_mute_button", True)

def get_default_volume() -> float:
    """Get default audio volume (0.0 to 1.0)."""
    config = get_config()
    return config.get("features.audio.default_volume", 1.0)
```

## Usage Examples

### Basic Usage (In app.py)

```python
from _modules.ui.audio_controls import (
    initialize_audio_state,
    render_mute_button,
)

def main():
    # Initialize audio state
    initialize_audio_state()
    
    with st.sidebar:
        # Render mute button at top
        render_mute_button()
        
        # Rest of sidebar content...
```

### Check Mute State

```python
from _modules.ui.audio_controls import is_audio_muted

if is_audio_muted():
    print("Audio is currently muted")
else:
    print("Audio is enabled")
```

### Inline Mute Button

For use within other components:

```python
from _modules.ui.audio_controls import render_inline_mute_button

with st.expander("Audio Settings"):
    render_inline_mute_button()
```

### JavaScript Integration

Pass mute state to JavaScript:

```python
from _modules.ui.audio_controls import get_audio_enabled_for_javascript

html = f"""
<script>
    const audioEnabled = {get_audio_enabled_for_javascript()};
    if (audioEnabled) {{
        // Play audio
    }}
</script>
"""
```

## Behavior Details

### Mute State Persistence

The mute state persists **within the session** (browser tab):

- ✅ Persists across page navigation
- ✅ Persists across tour steps
- ✅ Persists during splash screen
- ❌ Does NOT persist after browser refresh
- ❌ Does NOT persist across browser tabs

### Config vs. Session State

| Scenario | Config `enabled: false` | Session `audio_muted: true` |
|----------|-------------------------|---------------------------|
| **Mute button visible?** | No | Yes |
| **Audio plays?** | No | No |
| **User can unmute?** | No (disabled) | Yes (click button) |
| **Persistence** | Permanent | Session only |

**Priority:** Config `enabled: false` takes precedence over session state.

### Browser Autoplay Policy

The mute feature works **independently** of browser autoplay blocking:

1. **Browser blocks autoplay** → "Enable Audio" button appears
2. **User clicks enable** → Audio unblocks
3. **User clicks mute** → Audio stops
4. **Browser remembers** user interaction → Future audio works

Both features coexist:
- **Enable Audio button** = Override browser blocking
- **Mute button** = User preference control

## Styling

### Button CSS

The mute button uses custom styling:

```css
.audio-mute-button {
    position: fixed;
    top: 70px;
    right: 20px;
    z-index: 9999;
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #e0e0e0;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    /* ... */
}

.audio-mute-button:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.audio-mute-button.muted {
    background: rgba(200, 200, 200, 0.95);
    border-color: #999;
}
```

### Dark Mode Support

```css
@media (prefers-color-scheme: dark) {
    .audio-mute-button {
        background: rgba(40, 40, 40, 0.95);
        border-color: #555;
    }
}
```

## Testing

### Manual Testing

1. **Test mute button appears:**
   ```bash
   streamlit run app.py
   # Check sidebar for 🔊 button
   ```

2. **Test mute toggle:**
   - Click mute button → Icon changes to 🔇
   - Navigate to tour → Audio should NOT play
   - Click unmute → Icon changes to 🔊
   - Navigate to tour → Audio SHOULD play

3. **Test splash screen:**
   - Refresh app with tour enabled
   - Mute audio before splash
   - Splash should show NO audio
   - Unmute during splash → Audio should resume

4. **Test config disabled:**
   ```yaml
   features:
     audio:
       enabled: false
   ```
   - Mute button should NOT appear
   - No audio should play anywhere

5. **Test button hidden:**
   ```yaml
   features:
     audio:
       show_mute_button: false
   ```
   - Mute button should NOT appear
   - Audio should still play (can't mute)

### Automated Testing

```python
def test_audio_controls():
    """Test audio mute functionality."""
    from _modules.ui.audio_controls import (
        initialize_audio_state,
        is_audio_muted,
        toggle_mute,
    )
    
    # Initialize
    initialize_audio_state()
    
    # Should start unmuted
    assert not is_audio_muted()
    
    # Toggle to muted
    toggle_mute()
    assert is_audio_muted()
    
    # Toggle back to unmuted
    toggle_mute()
    assert not is_audio_muted()
```

## Troubleshooting

### Mute Button Not Showing

**Check config:**
```yaml
features:
  audio:
    enabled: true  # Must be true
    show_mute_button: true  # Must be true
```

**Check imports:**
```python
from _modules.ui.audio_controls import render_mute_button
```

**Check placement:**
```python
with st.sidebar:
    render_mute_button()  # Must be inside sidebar
```

### Audio Still Playing When Muted

**Check integration:**
```python
# Must check mute state before playing
if not is_audio_muted():
    play_audio()
```

**Check JavaScript:**
```javascript
const audioMuted = true;  // Should match Python state
if (!audioMuted) {
    audio.play();
}
```

### Mute State Not Persisting

**Expected:** Mute state persists within session, NOT across browser refreshes.

**Solution:** This is by design. To persist across sessions:
1. Use browser localStorage
2. Save preference to user profile
3. Use cookies with session management

## Future Enhancements

Potential improvements:

1. **Volume Slider**: Adjust volume level (not just mute/unmute)
2. **Persistent Preference**: Save mute state across sessions
3. **Per-Feature Mute**: Separate mute for splash vs. tour
4. **Keyboard Shortcut**: Press `M` to toggle mute
5. **Audio Visualization**: Show audio waveform while playing
6. **Speed Control**: Adjust playback speed (0.75x, 1x, 1.25x)

## Summary

| Feature | Status |
|---------|--------|
| ✅ Config-based enable/disable | Implemented |
| ✅ Sidebar mute button | Implemented |
| ✅ Session state persistence | Implemented |
| ✅ Splash screen integration | Implemented |
| ✅ Guided tour integration | Implemented |
| ✅ Dark mode support | Implemented |
| ⏳ Volume slider | Future |
| ⏳ Cross-session persistence | Future |
| ⏳ Keyboard shortcuts | Future |

The audio controls feature provides users with **complete control** over audio narration while maintaining a **simple, intuitive interface**! 🔊🔇
