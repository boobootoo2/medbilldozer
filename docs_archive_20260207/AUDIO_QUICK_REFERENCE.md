# Audio Controls - Quick Reference Card

## 🎯 What You Get

✅ **Mute button** in sidebar (🔊/🔇)  
✅ **Config control** via `app_config.yaml`  
✅ **Session persistence** - stays muted while navigating  
✅ **Automatic integration** - works with splash & tour  

## ⚡ Quick Start

```bash
# 1. Start app
streamlit run medBillDozer.py

# 2. Look for 🔊 button at top of sidebar

# 3. Click to toggle mute/unmute
```

## ⚙️ Configuration

```yaml
# app_config.yaml
features:
  audio:
    enabled: true              # Master switch
    autoplay: true             # Try to autoplay
    show_mute_button: true     # Show button
    default_volume: 1.0        # Volume (0.0-1.0)
```

## 🔧 Common Tasks

### Disable All Audio
```yaml
features:
  audio:
    enabled: false
```

### Hide Mute Button (Audio Still Works)
```yaml
features:
  audio:
    enabled: true
    show_mute_button: false
```

### Check Mute State in Code
```python
from _modules.ui.audio_controls import is_audio_muted

if not is_audio_muted():
    play_audio()
```

## 📍 Button Location

```
┌─ Sidebar ────────┐
│   [🔊]          │  ← Click here
│                  │
│ 📚 Guided Tour   │
│ Step 1 of 9      │
└──────────────────┘
```

## 🎭 Button States

| State | Icon | Meaning |
|-------|------|---------|
| **Unmuted** | 🔊 | Audio plays |
| **Muted** | 🔇 | Audio off |

## 📦 What Gets Muted

When **muted** (🔇):
- ❌ Splash screen audio (Billy & Billie)
- ❌ Guided tour step audio
- ✅ Visual guidance still works

When **unmuted** (🔊):
- ✅ Splash screen audio plays
- ✅ Guided tour audio plays
- ✅ Autoplay after user interaction

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No button | Set `audio.enabled: true` and `show_mute_button: true` |
| Audio plays when muted | Refresh page, check console |
| Button doesn't work | Clear cache, restart app |
| Resets on refresh | Expected - session-scoped only |

## 📚 Documentation

- **Quick Start**: `docs/AUDIO_CONTROLS_QUICKSTART.md`
- **Complete Guide**: `docs/AUDIO_CONTROLS.md`
- **Implementation Summary**: `docs/AUDIO_FEATURE_SUMMARY.md`
- **Regenerate Audio**: `docs/REGENERATE_AUDIO.md`

## 🔑 Key Functions

```python
# Initialize (call once at startup)
from _modules.ui.audio_controls import initialize_audio_state
initialize_audio_state()

# Check if muted
from _modules.ui.audio_controls import is_audio_muted
if not is_audio_muted():
    play_audio()

# Render button (in sidebar)
from _modules.ui.audio_controls import render_mute_button
with st.sidebar:
    render_mute_button()
```

## ✨ Files Changed

| File | Change |
|------|--------|
| `app_config.yaml` | Added audio config section |
| `_modules/utils/config.py` | Added helper functions |
| `_modules/ui/audio_controls.py` | **NEW** - mute button module |
| `_modules/ui/splash_screen.py` | Respects mute state |
| `_modules/ui/guided_tour.py` | Respects mute state |
| `medBillDozer.py` | Renders mute button |

## 🚀 Test Checklist

- [ ] Start app
- [ ] See 🔊 button in sidebar
- [ ] Click button → changes to 🔇
- [ ] Navigate to splash → no audio
- [ ] Navigate to tour → no audio
- [ ] Click 🔇 → changes to 🔊
- [ ] Navigate to splash → audio plays
- [ ] Navigate to tour → audio plays

## 💡 Pro Tips

1. **Visual fallback always works** - app usable without audio
2. **Session-scoped** - mute state doesn't persist across refreshes
3. **Skip expensive ops** - code checks mute before TTS generation
4. **Browser autoplay** - separate from mute (one-time gate)
5. **Config overrides** - set `enabled: false` to disable entirely

## 🎉 Ready!

The feature is **complete and ready to test**. Just start the app and look for the 🔊 button!

```bash
streamlit run medBillDozer.py
```

**Questions?** See full documentation in `docs/AUDIO_CONTROLS.md`
