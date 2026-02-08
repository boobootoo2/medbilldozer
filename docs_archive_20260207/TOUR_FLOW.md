# Guided Tour Flow

## Overview
The Intro.js guided tour now triggers after **both** the splash screen AND privacy policy are accepted, ensuring users are properly onboarded before the tour begins.

## Complete User Flow

```
┌─────────────────┐
│  App Launch     │
│  (First Visit)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Password Gate  │  ← If APP_ACCESS_PASSWORD is set
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Splash Screen   │  ← If GUIDED_TOUR=TRUE and not dismissed
│ (Billy & Billie)│
│ Animation       │
└────────┬────────┘
         │
         │ Click "Get Started 🚀"
         │
         ▼
┌─────────────────┐
│ Privacy Policy  │  ← If not previously accepted
│ & Cookie Prefs  │
└────────┬────────┘
         │
         │ Click "Accept & Continue"
         │
         ▼
┌─────────────────┐
│ Intro.js Tour   │  ← Automatically starts here!
│ Starts          │
│ (8 steps)       │
└────────┬────────┘
         │
         │ Complete or Skip Tour
         │
         ▼
┌─────────────────┐
│  Main App       │
└─────────────────┘
```

## Trigger Conditions

The tour starts automatically when **ALL** of these are true:

1. ✅ `GUIDED_TOUR=TRUE` (environment or config)
2. ✅ Splash screen dismissed (`splash_dismissed = True`)
3. ✅ Privacy accepted (`privacy_acknowledged = True`)
4. ❌ Tour not completed (`tour_completed = False`)
5. ❌ Tour not already active (`tour_active = False`)

## Key Changes

### 1. Privacy Dialog (`_modules/ui/privacy_ui.py`)

**Before:**
```python
if st.button("Accept & Continue", ...):
    st.session_state.privacy_acknowledged = True
    st.rerun()
```

**After:**
```python
if st.button("Accept & Continue", ...):
    st.session_state.privacy_acknowledged = True
    # Trigger guided tour if enabled
    if st.session_state.get('splash_dismissed', False):
        from _modules.ui.guided_tour import activate_tour
        activate_tour()
    st.rerun()
```

### 2. Splash Screen (`_modules/ui/splash_screen.py`)

**Before:**
```python
if st.button("Get Started 🚀", ...):
    dismiss_splash_screen()
    from _modules.ui.guided_tour import activate_tour
    activate_tour()  # ❌ Too early!
    st.rerun()
```

**After:**
```python
if st.button("Get Started 🚀", ...):
    dismiss_splash_screen()
    st.rerun()  # ✅ Wait for privacy
```

### 3. Tour Launch Logic (`_modules/ui/guided_tour.py`)

**Before:**
```python
def maybe_launch_tour():
    if st.session_state.get('splash_dismissed', False) and \
       not st.session_state.get('tour_completed', False) and \
       not st.session_state.get('tour_active', False):
        activate_tour()
```

**After:**
```python
def maybe_launch_tour():
    # Tour should start after:
    # 1. Splash screen dismissed
    # 2. Privacy policy accepted  ← NEW!
    # 3. Tour not already completed
    # 4. Tour not already active
    if st.session_state.get('splash_dismissed', False) and \
       st.session_state.get('privacy_acknowledged', False) and \
       not st.session_state.get('tour_completed', False) and \
       not st.session_state.get('tour_active', False):
        activate_tour()
```

## Session State Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `splash_dismissed` | bool | User clicked "Get Started 🚀" |
| `privacy_acknowledged` | bool | User accepted privacy policy |
| `tour_active` | bool | Tour is currently running |
| `tour_completed` | bool | User finished or skipped tour |
| `start_tour_now` | bool | Trigger flag for immediate start |

## Manual Tour Trigger

Users can manually start the tour anytime by clicking:

**"🚀 Start Guided Tour"** button in the sidebar

This appears when:
- `tour_active = False` (tour not running)
- Regardless of splash/privacy state

## Testing the Flow

### Test 1: Fresh User (First Visit)
1. Clear browser cache or use incognito
2. Navigate to app
3. Enter password (if required)
4. See splash screen → Click "Get Started 🚀"
5. See privacy dialog → Check "I agree" → Click "Accept & Continue"
6. **Tour should start automatically!**

### Test 2: Returning User (Privacy Already Accepted)
1. Return to app (privacy already accepted in session)
2. Tour should NOT start automatically
3. Look for "🚀 Start Guided Tour" button in sidebar
4. Click button to start tour manually

### Test 3: Skip Splash but See Privacy
1. If splash was previously dismissed but privacy not accepted
2. Privacy dialog shows
3. Accept privacy
4. Tour starts

### Test 4: Disable Tour
1. Set `GUIDED_TOUR=FALSE` in environment or config
2. No tour button appears
3. No automatic tour launch

## Console Debug Output

When tour is triggered, you'll see:

```
[Intro.js] Loading library...
[Intro.js] Library loaded successfully
[Intro.js] Starting tour initialization...
[Intro.js] Library found after 1 attempts
[Intro.js] Intro.js library ready
[Intro.js] Setting up tour steps...
[Intro.js] Initializing tour...
[Intro.js] Starting tour now...
```

If there's an issue:
```
[Intro.js] Library failed to load after 20 attempts
[Intro.js] No parent window access
```

## Disabling the Tour

### Environment Variable
```bash
export GUIDED_TOUR=FALSE
streamlit run medBillDozer.py
```

### Config File (`app_config.yaml`)
```yaml
guided_tour:
  enabled: false
```

### Session State (programmatic)
```python
st.session_state.tour_completed = True
```

## Future Enhancements

- [ ] Add "Replay Tour" button in settings
- [ ] Save tour completion to browser localStorage
- [ ] Track tour step analytics
- [ ] Add tour for specific features (hints mode)
- [ ] Contextual tours based on user actions
- [ ] Tour localization for multiple languages

## Rollback

If needed, restore original behavior:

```bash
# Restore splash-triggered tour
git checkout HEAD~1 _modules/ui/splash_screen.py

# Restore privacy without tour trigger
git checkout HEAD~1 _modules/ui/privacy_ui.py

# Restore old tour launch logic
git checkout HEAD~1 _modules/ui/guided_tour.py
```
