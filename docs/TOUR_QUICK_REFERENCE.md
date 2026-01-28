# Guided Tour Quick Reference

## 🚀 Quick Start

```python
from _modules.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
    run_guided_tour_runtime,
    tour_step_marker
)

# 1. Initialize (early in app)
initialize_tour_state()

# 2. Auto-launch check (after splash/privacy)
maybe_launch_tour()

# 3. Render your UI
st.title("My App")
tour_step_marker("logo")
st.image("logo.png")

# 4. Show tour controls (at the end)
run_guided_tour_runtime()
```

## 📋 Core Functions

| Function | When to Call | Purpose |
|----------|-------------|---------|
| `initialize_tour_state()` | App startup | Initialize session state |
| `maybe_launch_tour()` | After splash/privacy | Auto-start if conditions met |
| `activate_tour()` | Manual start | Force start tour |
| `run_guided_tour_runtime()` | End of render | Display tour UI |

## 🎯 Highlighting Elements

```python
# Method 1: Inline marker
tour_step_marker("text_input")
st.text_area("Enter text")

# Method 2: Conditional highlighting
if is_tour_on_target("analyze_button"):
    st.info("Click this button to analyze!")
st.button("Analyze")
```

## 🔍 Query Functions

```python
# Check current step
if is_tour_on_step(3):
    st.write("User is on step 3")

# Check current target
if is_tour_on_target("logo"):
    st.write("Tour is showing logo step")

# Get progress
current, total = get_tour_progress()
st.write(f"Progress: {current}/{total}")

# Check if active
if st.session_state.get('tour_active', False):
    st.write("Tour is running")

# Check if completed
if st.session_state.get('tour_completed', False):
    st.write("Tour was completed")
```

## ⚙️ Control Functions

```python
# Pause/Resume
pause_tour()
resume_tour()
if is_tour_paused():
    st.write("Tour is paused")

# Complete/Skip
complete_tour()
skip_tour()

# Navigate
advance_tour_step()
previous_tour_step()
```

## 🏗️ Tour Steps Structure

```python
from dataclasses import dataclass

@dataclass
class TourStep:
    id: int           # Step number (1-based)
    title: str        # Step title
    description: str  # Step description (supports markdown/emojis)
    target: str       # UI element identifier
    position: str     # Display position (for future use)
```

## 📝 Adding New Steps

Edit `TOUR_STEPS` in `guided_tour.py`:

```python
TOUR_STEPS = [
    TourStep(
        id=10,
        title="New Feature",
        description="🎉 Check out this new feature!",
        target="new_feature_button",
        position="top"
    ),
]
```

## 🎨 Custom Styling

```python
# Option 1: Use tour_step_marker (built-in)
tour_step_marker("my_element")

# Option 2: Custom conditional styling
if is_tour_on_target("my_element"):
    st.markdown("""
    <div style="border: 2px solid blue; padding: 10px;">
        Custom highlight!
    </div>
    """, unsafe_allow_html=True)
```

## 🧪 Testing & Debugging

```python
# Force tour to specific step
st.session_state.tour_active = True
st.session_state.tour_current_step = 5

# Reset tour
if st.sidebar.button("Reset Tour"):
    st.session_state.tour_completed = False
    st.session_state.tour_active = False
    st.rerun()

# Debug info
if st.sidebar.checkbox("Show Tour Debug"):
    st.sidebar.json({
        "active": st.session_state.get('tour_active'),
        "completed": st.session_state.get('tour_completed'),
        "current_step": st.session_state.get('tour_current_step'),
        "paused": st.session_state.get('tour_paused'),
    })
```

## 🔧 Common Patterns

### Pattern 1: Section with Tour

```python
def render_analysis_section():
    tour_step_marker("analyze_button")
    
    st.header("Analysis")
    text = st.text_area("Enter bill")
    
    if st.button("Analyze"):
        if is_tour_on_target("analyze_button"):
            st.success("Great! Analysis starting...")
        analyze(text)
```

### Pattern 2: Conditional Features During Tour

```python
# Disable certain features during tour
if st.session_state.get('tour_active', False):
    st.info("Some features disabled during tour")
else:
    show_advanced_features()
```

### Pattern 3: Tour-Aware Help Text

```python
if is_tour_on_target("settings"):
    help_text = "⬇️ Tour: Check out these settings!"
else:
    help_text = "Configure your preferences"

st.text_input("Setting", help=help_text)
```

## 📱 Session State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `tour_active` | bool | Tour is running |
| `tour_completed` | bool | Tour was finished |
| `tour_current_step` | int | Current step (1-based) |
| `tour_paused` | bool | Tour is paused |
| `start_tour_now` | bool | Trigger flag |

## ⚠️ Common Pitfalls

### ❌ Don't: Call run_guided_tour_runtime() multiple times

```python
# BAD
run_guided_tour_runtime()
st.write("Content")
run_guided_tour_runtime()  # Duplicate!
```

### ✅ Do: Call once at the end

```python
# GOOD
st.write("Content")
run_guided_tour_runtime()  # Once, at end
```

### ❌ Don't: Modify tour state directly in render logic

```python
# BAD
st.session_state.tour_current_step += 1  # Causes rerun loop!
```

### ✅ Do: Use provided functions

```python
# GOOD
if st.button("Next"):
    advance_tour_step()
    st.rerun()
```

### ❌ Don't: Forget to initialize

```python
# BAD - Will cause KeyError
if st.session_state.tour_active:  # tour_active not initialized!
    ...
```

### ✅ Do: Always initialize first

```python
# GOOD
initialize_tour_state()  # Call this first!
if st.session_state.get('tour_active', False):
    ...
```

## 🎯 Target Names Reference

Current built-in targets:

1. `"logo"` - App logo/mascot
2. `"demo_section"` - Demo documents
3. `"text_input"` - Bill text input
4. `"add_document"` - Add document button
5. `"analyze_button"` - Analyze button
6. `"sidebar"` - Sidebar navigation
7. `"profile_button"` - Profile button
8. `"profile_section"` - Profile view
9. `"api_button"` - API documentation button

## 📊 Performance Tips

### ✅ Good: Early returns

```python
def tour_step_marker(target: str):
    if not st.session_state.get('tour_active', False):
        return  # Fast exit if tour not active
    # ... rest of logic
```

### ✅ Good: Conditional rendering

```python
# Only render tour controls if active
if st.session_state.get('tour_active', False):
    render_tour_ui()
```

### ❌ Bad: Unnecessary checks every render

```python
# Don't do this in a loop
for item in items:
    tour_step_marker("item")  # Called too many times!
```

## 🔗 See Also

- [Complete Documentation](SESSION_DRIVEN_TOUR.md)
- [Migration Guide](TOUR_MIGRATION_GUIDE.md)
- [Source Code](_modules/ui/guided_tour.py)

---

**Quick Reference Version:** 1.0

**Last Updated:** January 27, 2026
