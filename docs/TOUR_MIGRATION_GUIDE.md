# Tour Migration Guide: Intro.js → Session-Driven

## Executive Summary

The MedBillDozer guided tour has been migrated from **Intro.js (JavaScript-based)** to a **pure Streamlit session-driven approach**. This eliminates all external JavaScript dependencies while providing a more reliable and maintainable solution.

## What Changed

### Before: Intro.js Implementation

- **588 lines** of complex JavaScript injection code
- External CDN dependency (intro.js library)
- DOM manipulation via iframe access
- Complex timing and element detection logic
- Browser compatibility issues
- Difficult to debug and test

### After: Session-Driven Implementation

- **~350 lines** of clean Python code
- Zero external dependencies
- Pure Streamlit components (info boxes, buttons)
- Simple session state management
- Works reliably across all browsers
- Easy to debug with standard Python tools

## Architecture Comparison

### Old Architecture (Intro.js)

```
App Start
   ↓
Install Intro.js Library (CDN)
   ↓
Inject Custom CSS
   ↓
Wait for DOM elements
   ↓
Add data-intro attributes via JS
   ↓
Start Intro.js tour
   ↓
Handle step changes via JS callbacks
```

**Problems:**
- Race conditions with element rendering
- Iframe access limitations
- CDN dependency/failures
- Complex debugging
- No control over tour UI

### New Architecture (Session-Driven)

```
App Start
   ↓
Initialize Session State
   ↓
Render Main UI
   ↓
Check Tour Conditions
   ↓
Display Tour Info Box (if active)
   ↓
Handle Navigation via Button Clicks
```

**Benefits:**
- No timing issues
- Full control over UI
- Standard Streamlit workflow
- Easy debugging
- Reliable behavior

## API Compatibility

### Unchanged Functions

These functions still work exactly the same:

```python
initialize_tour_state()    # Still required
activate_tour()            # Still activates tour
maybe_launch_tour()        # Still auto-launches
```

### Changed Functions

#### `run_guided_tour_runtime()`

**Before:**
```python
# Complex multi-step process
install_introjs_library()
render_tour_steps()
if start_now:
    start_introjs_tour()
    st.session_state.start_tour_now = False
```

**After:**
```python
# Single function does everything
run_guided_tour_runtime()
```

### Deprecated Functions (Now No-Ops)

These functions are kept for backward compatibility but do nothing:

- `install_introjs_library()`
- `render_tour_steps()`
- `start_introjs_tour()`
- `install_paste_detector()`
- `install_copy_button_detector()`
- `check_pharmacy_copy_click()`
- `install_tour_highlight_styles()`
- `highlight_tour_elements()`
- `open_and_scroll_pipeline_workflow_step6()`
- `check_tour_progression()`
- `open_sidebar_for_tour()`

### New Functions

Added for enhanced functionality:

```python
tour_step_marker(target: str)          # Highlight UI elements
show_tour_step_hint(target: str)       # Show inline hints
is_tour_on_step(step_id: int)          # Query current step
is_tour_on_target(target: str)         # Query current target
get_tour_progress()                     # Get progress tuple
pause_tour() / resume_tour()           # Pause control
is_tour_paused()                        # Query pause state
```

## Migration Steps

### Step 1: Update Imports

No changes needed! All imports remain the same:

```python
from _modules.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
    run_guided_tour_runtime,
    activate_tour,
)
```

### Step 2: Verify Flow

Ensure your app follows this pattern:

```python
def main():
    # 1. Initialize tour state (early)
    initialize_tour_state()
    
    # 2. Handle splash/privacy
    if should_show_splash():
        show_splash_screen()
        return
    
    if not privacy_acknowledged():
        show_privacy_dialog()
        return
    
    # 3. Check if tour should launch
    maybe_launch_tour()
    
    # 4. Render main UI
    render_main_app()
    
    # 5. Render tour (at the end)
    run_guided_tour_runtime()
```

### Step 3: Remove Old Code (Optional)

If you have any manual calls to deprecated functions, you can remove them:

```python
# OLD - can be removed
install_introjs_library()
render_tour_steps()
start_introjs_tour()

# NEW - just this one call
run_guided_tour_runtime()
```

### Step 4: Add Tour Markers (Optional Enhancement)

To highlight specific UI elements during the tour:

```python
from _modules.ui.guided_tour import tour_step_marker

# Highlight logo during step 1
tour_step_marker("logo")
st.image("logo.png")

# Highlight text input during step 3
tour_step_marker("text_input")
bill_text = st.text_area("Paste your medical bill")

# Highlight analyze button during step 5
tour_step_marker("analyze_button")
if st.button("Analyze"):
    analyze_bill(bill_text)
```

### Step 5: Test

1. Start app with `GUIDED_TOUR=TRUE`
2. Complete splash and privacy screens
3. Verify tour auto-starts
4. Test all navigation buttons:
   - ← Back
   - Next →
   - Skip Tour
   - Done! 🎉
5. Verify tour completes and doesn't restart

## Visual Comparison

### Old Tour (Intro.js)

```
┌────────────────────────────────────────┐
│ [Floating overlay with dark background]│
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ Step 1 of 9                      │  │
│  │ Welcome to MedBillDozer!         │  │
│  │ Hi! I'm Billy...                 │  │
│  │                                   │  │
│  │ [Skip] [← Back] [Next →]         │  │
│  └─────────────────────────────────┘  │
│                                         │
└────────────────────────────────────────┘
```

**Issues:**
- Could overlap UI elements
- Hard to position correctly
- Sometimes invisible or misaligned

### New Tour (Session-Driven)

```
┌────────────────────────────────────────┐
│ ℹ️ Step 1 of 9: Welcome to MedBillDozer!│
│                                         │
│ 👋 Hi! I'm Billy, and with my partner  │
│ Billie, we'll help you find hidden     │
│ errors in medical bills. Let's get     │
│ started!                                │
│                                         │
│ [← Back] [Next →] [Skip Tour]          │
└────────────────────────────────────────┘
```

**Benefits:**
- Always visible and readable
- Integrated with Streamlit UI
- Native info box styling
- Never overlaps content

## Benefits Summary

### 1. Reliability ⭐⭐⭐⭐⭐

**Before:** 3/5
- CDN failures
- Timing issues
- Browser incompatibility

**After:** 5/5
- No external dependencies
- Reliable state management
- Works everywhere

### 2. Maintainability ⭐⭐⭐⭐⭐

**Before:** 2/5
- Complex JavaScript
- Hard to debug
- Hard to extend

**After:** 5/5
- Pure Python
- Standard debugging
- Easy to modify

### 3. Performance ⭐⭐⭐⭐⭐

**Before:** 3/5
- CDN load time
- DOM manipulation overhead
- Multiple async operations

**After:** 5/5
- Instant load
- No external requests
- Simple state updates

### 4. Developer Experience ⭐⭐⭐⭐⭐

**Before:** 2/5
- JavaScript knowledge required
- Complex integration
- Difficult testing

**After:** 5/5
- Pure Python/Streamlit
- Simple integration
- Easy testing

### 5. User Experience ⭐⭐⭐⭐

**Before:** 4/5
- Nice animations
- Professional look
- But: Sometimes buggy

**After:** 4/5
- Clean, simple
- Always works
- But: Less fancy animations

## Code Size Comparison

### guided_tour.py

| Version | Lines | Complexity |
|---------|-------|------------|
| Intro.js | 588 | High |
| Session-Driven | ~350 | Low |
| **Reduction** | **-40%** | **Much simpler** |

### Dependencies

| Version | External Deps | Risk |
|---------|---------------|------|
| Intro.js | intro.js (CDN) | Medium |
| Session-Driven | None | None |

## Rollback Plan (If Needed)

If you need to rollback to Intro.js version:

```bash
# Restore old version
cp _modules/ui/guided_tour_old.py _modules/ui/guided_tour.py

# Or restore from backup
cp _modules/ui/guided_tour.py.backup _modules/ui/guided_tour.py

# Restart app
streamlit run medBillDozer.py
```

## Testing Checklist

- [ ] Tour initializes correctly
- [ ] Tour auto-starts after splash/privacy
- [ ] "Next" button advances steps
- [ ] "Back" button goes to previous step
- [ ] "Skip Tour" exits immediately
- [ ] "Done" completes tour on last step
- [ ] Tour doesn't restart after completion
- [ ] Manual "Start Guided Tour" button works
- [ ] All 9 steps display correctly
- [ ] No Python errors in console
- [ ] No JavaScript errors in browser console

## FAQ

### Q: Will users notice the change?

**A:** Slightly different visual presentation, but same content and flow. Most users won't notice or care.

### Q: Is the session-driven tour better?

**A:** Yes, for reliability and maintainability. Trade-off: less fancy animations.

### Q: Can I customize the tour appearance?

**A:** Yes! It uses standard Streamlit components, so you can style via Streamlit themes or custom CSS.

### Q: What if I prefer the old JavaScript version?

**A:** The old version is backed up at `guided_tour_old.py`. You can restore it if needed.

### Q: Does this break existing code?

**A:** No! All public APIs remain compatible. Old function calls are no-ops.

### Q: Can I add more steps?

**A:** Yes! Edit the `TOUR_STEPS` list in `guided_tour.py`.

### Q: How do I debug tour issues?

**A:** Use standard Python debugging:
```python
# Add debug logging
current_step = get_current_step()
st.write(f"Debug: Current step = {current_step}")
st.write(f"Debug: Tour active = {st.session_state.tour_active}")
```

### Q: Can I programmatically control the tour?

**A:** Yes! Use the new API functions:
```python
# Jump to specific step
st.session_state.tour_current_step = 5

# Pause/resume
pause_tour()
resume_tour()

# Check state
if is_tour_on_step(3):
    st.write("On step 3!")
```

## Support

For issues or questions:

1. Check the [Session-Driven Tour Documentation](SESSION_DRIVEN_TOUR.md)
2. Review this migration guide
3. Check `guided_tour.py` source code (well-commented)
4. Ask the team!

## Conclusion

The migration to session-driven tours provides a **more reliable, maintainable, and Streamlit-native** solution. While it sacrifices some visual flair, it gains in **stability, simplicity, and developer experience**.

**Recommendation:** Proceed with session-driven approach for production use.

---

**Migration Status:** ✅ Complete

**Last Updated:** January 27, 2026

**Version:** 2.0.0 (Session-Driven)
