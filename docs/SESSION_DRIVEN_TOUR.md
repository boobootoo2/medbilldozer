# Session-Driven Tour Implementation

## Overview

The new guided tour implementation uses **Streamlit Session State** exclusively, eliminating all JavaScript dependencies (Intro.js). This provides a more reliable, maintainable, and Streamlit-native experience.

## Architecture

### Key Components

1. **TourStep Dataclass**: Defines the structure for each tour step
2. **Session State Management**: All tour state stored in `st.session_state`
3. **Pure Python Logic**: No JavaScript injection or DOM manipulation
4. **Streamlit UI Components**: Native info boxes and buttons for tour navigation

### Session State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `tour_active` | bool | Whether the tour is currently active |
| `tour_completed` | bool | Whether the user has completed the tour |
| `tour_current_step` | int | Current step number (1-based) |
| `tour_paused` | bool | Whether the tour is temporarily paused |
| `start_tour_now` | bool | Flag to trigger tour start |

## Tour Steps

The tour includes 9 steps covering all major features:

1. **Welcome** - Introduction to Billy and Billie
2. **Demo Documents** - Sample bills section
3. **Document Input** - Text input area
4. **Add Multiple Documents** - Multi-document feature
5. **Start Analysis** - Analyze button
6. **Sidebar Navigation** - Sidebar features overview
7. **Your Profile** - Profile button
8. **Profile Management** - Profile view details
9. **API Integration** - API documentation button

## Implementation Details

### Tour Display

Instead of a floating JavaScript overlay, the tour displays an info box at the top of the main content area:

```python
st.info(f"""
**Step {current_step.id} of {len(TOUR_STEPS)}: {current_step.title}**

{current_step.description}
""")
```

### Navigation Controls

Tour controls are rendered as Streamlit columns with buttons:

- **← Back**: Go to previous step (disabled on first step)
- **Next →**: Advance to next step (changes to "Done! 🎉" on last step)
- **Skip Tour**: Exit the tour immediately

### Element Highlighting

Two helper functions are provided for highlighting tour targets:

#### `tour_step_marker(step_target: str)`

Displays an inline highlighted box when the tour focuses on a specific target:

```python
# In your app code
tour_step_marker("logo")
st.image("logo.png")  # Your logo component
```

This will show a bordered, highlighted box with the step info when that step is active.

#### `show_tour_step_hint(step_target: str)`

Shows a simple info box for the target:

```python
show_tour_step_hint("demo_section")
```

## Integration Guide

### Basic Setup

1. **Import the module**:
```python
from _modules.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
    run_guided_tour_runtime,
    tour_step_marker
)
```

2. **Initialize state early** (before main UI):
```python
initialize_tour_state()
```

3. **Check launch conditions** (after splash/privacy):
```python
maybe_launch_tour()
```

4. **Render tour controls** (after main UI):
```python
run_guided_tour_runtime()
```

### Adding Tour Markers

To highlight specific UI elements during the tour:

```python
# Step 1: Logo
tour_step_marker("logo")
st.image("images/logo.png")

# Step 3: Text Input
tour_step_marker("text_input")
text_input = st.text_area("Paste your medical bill here")

# Step 5: Analyze Button
tour_step_marker("analyze_button")
if st.button("Analyze"):
    # ... analysis logic
```

### Manual Tour Control

Users can manually start the tour via a sidebar button:

```python
# This is already included in run_guided_tour_runtime()
if st.sidebar.button("🚀 Start Guided Tour"):
    activate_tour()
    st.rerun()
```

## API Reference

### Core Functions

#### `initialize_tour_state()`
Initializes all tour-related session state variables. Call this once at app startup.

#### `activate_tour()`
Starts the tour from step 1. Sets `tour_active=True` and `tour_current_step=1`.

#### `maybe_launch_tour()`
Automatically launches the tour if conditions are met:
- Splash dismissed
- Privacy acknowledged
- Tour not completed
- Tour not already active

#### `run_guided_tour_runtime()`
Main tour rendering function. Call this ONCE per page render, AFTER your main UI.
Displays tour info box and navigation controls when tour is active.

### Navigation Functions

#### `advance_tour_step()`
Moves to the next step. Completes tour if on last step.

#### `previous_tour_step()`
Goes back to the previous step.

#### `complete_tour()`
Marks tour as completed and deactivates it.

#### `skip_tour()`
Exits the tour immediately (same as `complete_tour()`).

### Helper Functions

#### `tour_step_marker(step_target: str)`
Displays a highlighted box with step info when the tour is on the specified target.

**Parameters:**
- `step_target` (str): The target identifier (e.g., "logo", "demo_section", "text_input")

**Usage:**
```python
tour_step_marker("analyze_button")
if st.button("Analyze"):
    # ...
```

#### `show_tour_step_hint(step_target: str)`
Shows a simple info box for the target when the tour is focused on it.

#### `get_current_step() -> Optional[TourStep]`
Returns the current TourStep object or None if tour is inactive.

### Query Functions

#### `is_tour_on_step(step_id: int) -> bool`
Check if tour is on a specific step number.

```python
if is_tour_on_step(3):
    st.write("User is learning about text input!")
```

#### `is_tour_on_target(target: str) -> bool`
Check if tour is focused on a specific target.

```python
if is_tour_on_target("analyze_button"):
    # Highlight or emphasize the analyze button
    pass
```

#### `get_tour_progress() -> Tuple[int, int]`
Returns `(current_step, total_steps)` tuple.

```python
current, total = get_tour_progress()
st.write(f"Tour progress: {current}/{total}")
```

#### `is_tour_paused() -> bool`
Check if tour is currently paused.

#### `pause_tour()` / `resume_tour()`
Pause or resume the tour.

## Benefits Over JavaScript Approach

### 1. **Reliability**
- No dependency on external CDN libraries
- No browser compatibility issues
- No iframe/DOM access problems

### 2. **Maintainability**
- Pure Python code
- Easy to debug with standard Python tools
- No complex JavaScript injection

### 3. **Simplicity**
- Native Streamlit components
- Familiar API for Streamlit developers
- Less code overall

### 4. **Performance**
- No external library loading
- No DOM manipulation overhead
- Faster initial render

### 5. **Accessibility**
- Native Streamlit accessibility features
- Screen reader compatible
- Keyboard navigation built-in

## Migration from Intro.js

### Removed Functions (Compatibility Stubs)

The following functions are now no-ops for backward compatibility:

- `install_introjs_library()`
- `render_tour_steps()`
- `start_introjs_tour()`
- `install_paste_detector()`
- `install_copy_button_detector()`
- `check_pharmacy_copy_click()`
- `install_tour_highlight_styles()`
- `highlight_tour_elements()`
- `open_and_scroll_pipeline_workflow_step6()`

### What Changed

**Before (Intro.js):**
```python
install_introjs_library()
render_tour_steps()
if start_now:
    start_introjs_tour()
```

**After (Session-Driven):**
```python
# Just call this once after UI render
run_guided_tour_runtime()
```

### Updating Your Code

1. Remove all JavaScript-related tour calls
2. Keep `initialize_tour_state()` call
3. Keep `maybe_launch_tour()` call
4. Replace old tour rendering with `run_guided_tour_runtime()`
5. Add `tour_step_marker()` calls where you want highlights

## Customization

### Modifying Tour Steps

Edit the `TOUR_STEPS` list in `guided_tour.py`:

```python
TOUR_STEPS = [
    TourStep(
        id=1,
        title="Your Title",
        description="Your description with emojis 🎉",
        target="ui_element_id",
        position="top"  # Currently not used, but kept for future
    ),
    # ... more steps
]
```

### Custom Styling

The tour uses standard Streamlit components, so you can customize via:

1. **Streamlit theme configuration** (`config.toml`)
2. **Custom CSS** via `st.markdown()` with `unsafe_allow_html=True`
3. **Modifying the `tour_step_marker()` function** for different highlight styles

### Example Custom Highlight

```python
def custom_tour_highlight(target: str):
    """Custom highlight with different colors."""
    if not st.session_state.get('tour_active', False):
        return
    
    current_step = get_current_step()
    if not current_step or current_step.target != target:
        return
    
    st.markdown(f"""
    <div style="
        border: 4px dashed #FF6B6B;
        border-radius: 12px;
        padding: 15px;
        background: rgba(255, 107, 107, 0.1);
        animation: pulse 2s infinite;
    ">
        <h3 style="color: #FF6B6B;">🎯 {current_step.title}</h3>
        <p>{current_step.description}</p>
    </div>
    """, unsafe_allow_html=True)
```

## Testing

### Manual Testing

1. Start the app with `GUIDED_TOUR=TRUE`
2. Complete splash screen and privacy acknowledgment
3. Tour should auto-start
4. Test all navigation buttons
5. Test skip functionality
6. Verify tour completion state persists

### Testing Specific Steps

```python
# Force tour to specific step for testing
st.session_state.tour_active = True
st.session_state.tour_current_step = 5  # Test step 5
run_guided_tour_runtime()
```

### Resetting Tour

```python
# Add debug button
if st.sidebar.button("Reset Tour"):
    st.session_state.tour_completed = False
    st.session_state.tour_active = False
    st.session_state.tour_current_step = 1
    st.rerun()
```

## Troubleshooting

### Tour Not Starting

**Check:**
1. Is `GUIDED_TOUR=TRUE` in environment or config?
2. Has splash been dismissed?
3. Has privacy been acknowledged?
4. Is `initialize_tour_state()` called?
5. Is `maybe_launch_tour()` called after privacy/splash?

### Tour Controls Not Appearing

**Check:**
1. Is `run_guided_tour_runtime()` called?
2. Is it called AFTER main UI rendering?
3. Are there any Python exceptions?

### Highlights Not Showing

**Check:**
1. Is `tour_step_marker()` called with correct target?
2. Is it called in the right order with your UI component?
3. Does the target match the TourStep target exactly?

## Future Enhancements

Potential improvements for the session-driven tour:

1. **Progress Bar**: Visual progress indicator
2. **Branching Tours**: Different paths based on user actions
3. **Interactive Tutorials**: Require user to complete actions
4. **Tour Analytics**: Track completion rates and drop-off points
5. **Localization**: Multi-language support
6. **Step Persistence**: Remember progress across sessions
7. **Contextual Tours**: Different tours for different user roles

## Example Integration

Complete example of integrating the tour into `app.py`:

```python
import streamlit as st
from _modules.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
    run_guided_tour_runtime,
    tour_step_marker,
    is_tour_on_target
)

def main():
    # Initialize session state
    initialize_tour_state()
    
    # Check if tour should launch
    maybe_launch_tour()
    
    # Render main UI
    st.title("MedBillDozer")
    
    # Add tour markers
    tour_step_marker("logo")
    st.image("logo.png")
    
    tour_step_marker("text_input")
    bill_text = st.text_area("Paste your bill")
    
    tour_step_marker("analyze_button")
    if st.button("Analyze"):
        # Highlight button during tour
        if is_tour_on_target("analyze_button"):
            st.success("Great! Now click this button to analyze.")
        analyze_bill(bill_text)
    
    # Render tour controls (at the end)
    run_guided_tour_runtime()

if __name__ == "__main__":
    main()
```

## Conclusion

The session-driven tour provides a robust, maintainable, and purely Python-based solution for guided tours in Streamlit apps. By leveraging Streamlit's native session state and UI components, it eliminates JavaScript dependencies while providing a better user experience.
