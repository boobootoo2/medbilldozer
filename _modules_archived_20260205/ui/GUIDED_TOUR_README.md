# Guided Tour System

## Overview

The guided tour provides an interactive, state-driven tutorial for first-time users. Billy and Billie narrate the experience, guiding users through the app's features with contextual messages that appear at the right moments.

## Key Concepts

### State-Based (Not Click-Based)

The tour tracks **app state**, not DOM elements or clicks. This makes it more robust and less brittle than traditional tooltip tours.

### Tutorial Steps

```python
TUTORIAL_STEPS = [
    "welcome",           # Initial greeting
    "upload_prompt",     # Prompt to upload/select document
    "document_loaded",   # Document ready for analysis
    "analysis_running",  # Analysis in progress
    "review_issues",     # Results displayed
    "coverage_matrix",   # Matrix feature explanation
    "next_actions",      # What to do next
    "tour_complete",     # Farewell message
]
```

### Automatic Progression

The tour automatically advances when certain state conditions are met:

- **upload_prompt → document_loaded**: When `st.session_state.active_doc_text` or `selected_demo` is set
- **document_loaded → analysis_running**: When `st.session_state.analyzing = True`
- **analysis_running → review_issues**: When `st.session_state.doc_results = True` and `analyzing = False`

### Manual Progression

For exploratory steps (review_issues, coverage_matrix, next_actions), users click "Continue ▶" when ready to advance.

## Configuration

In `app_config.yaml`:

```yaml
features:
  guided_tour:
    enabled: true
    auto_launch_for_new_users: true
    default_narrator: "billie"  # "billy" or "billie"
    widget_position: "top"       # "top" or "floating"
    show_skip_button: true
```

## Usage

### In app.py

```python
from _modules.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
    check_tour_progression,
    render_tour_widget,
    render_tour_controls,
)

# Initialize at app start
if is_guided_tour_enabled():
    initialize_tour_state()
    maybe_launch_tour()

# Render widget at top of page
if is_guided_tour_enabled():
    render_tour_widget()

# Render controls in sidebar
if is_guided_tour_enabled():
    render_tour_controls()

# Check progression after state changes
check_tour_progression()
```

### Key State Variables

- `st.session_state.tour_active` - Boolean, tour is running
- `st.session_state.tutorial_step` - Current step name
- `st.session_state.tour_completed` - User has finished tour
- `st.session_state.is_first_visit` - First time user

### Trigger Points

Add `check_tour_progression()` after:
- Document selection/input
- Analysis start (set `analyzing = True`)
- Analysis complete (set `analyzing = False`, `doc_results = True`)

## Customization

### Adding New Steps

1. Add step to `TUTORIAL_STEPS` list
2. Add message to `TUTORIAL_MESSAGES` dict:

```python
"new_step": {
    "character": "billie",  # or "billy"
    "message": "Your guidance message here",
    "action_prompt": "What user should do next",
}
```

3. Update auto-progression logic in `check_tour_progression()` if needed

### Changing Narrators

Messages alternate between Billy and Billie. Each step specifies which character speaks:

```python
"character": "billie"  # 👷‍♀️
"character": "billy"   # 👷‍♂️
```

## Design Principles

1. **State-driven, not click-driven**: Track what the user has done, not where they clicked
2. **Action-focused guidance**: Tell users what to do ("Select a demo document"), not where to click ("Click the dropdown")
3. **Progressive disclosure**: Show guidance when relevant, not all at once
4. **Skippable**: Always allow users to skip or exit the tour
5. **Non-blocking**: Tour doesn't prevent normal app usage

## Examples

### Welcome Step
```
Character: Billie
Message: "Hi! I'm Billie D., your guide to finding hidden errors in medical bills. Let me show you how this works!"
Action: Ready to begin
```

### Upload Prompt Step
```
Character: Billie
Message: "I'll guide you through checking a medical bill for hidden errors. Let's start by uploading a document or trying one of our demo examples."
Action: Select a demo document or paste your bill text
```

### Review Issues Step
```
Character: Billy
Message: "Here are the results! Each issue shows what might be wrong and how much you could save. Expand any section to see more details."
Action: Review the findings
```

## Testing

To test the tour:

1. Clear browser cookies/storage to trigger "first visit"
2. Set `auto_launch_for_new_users: true` in config
3. Reload app - tour should auto-start
4. Progress through steps by following prompts

Or manually start:

```python
from _modules.ui.guided_tour import start_tour
start_tour()
```

## Disabling

Set in `app_config.yaml`:

```yaml
features:
  guided_tour:
    enabled: false
```

Or for development, disable auto-launch but keep manual start available:

```yaml
features:
  guided_tour:
    enabled: true
    auto_launch_for_new_users: false
```
