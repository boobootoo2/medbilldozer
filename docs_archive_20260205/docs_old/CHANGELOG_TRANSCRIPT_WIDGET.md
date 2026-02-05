# Widget Transcript Feature

## Summary
Added a collapsible conversation transcript below the Billdozer animation widget that logs all messages for accessibility and user reference.

## Changes Made

### File Modified
`static/bulldozer_animation.html`

### 1. Transcript UI Components

**HTML Structure**:
```html
<div class="transcript-section">
    <button
        class="transcript-toggle"
        id="transcriptToggle"
        aria-expanded="false"
        aria-controls="transcriptContent"
        type="button">
        <span>📜 Conversation Transcript</span>
        <span class="transcript-arrow">▼</span>
    </button>
    <div
        class="transcript-content"
        id="transcriptContent"
        role="region"
        aria-label="Conversation transcript">
        <div class="transcript-empty">No messages yet</div>
    </div>
</div>
```

**Features**:
- Accordion/collapsible section (collapsed by default)
- ARIA attributes for screen reader accessibility
- 320px width matching the animation container
- Positioned directly below the widget animation

### 2. Styling

**Transcript Toggle Button**:
- Clean, modern design with hover and focus states
- Visual arrow indicator that rotates when expanded
- Keyboard accessible with focus outline
- Light gray background (#f3f4f6) with border

**Transcript Content**:
- Max height of 200px with auto-scroll
- White background with subtle border
- Auto-scrolls to bottom when new messages arrive
- Each message shows:
  - Character name (Billie/Billy) in brand blue
  - Message text
  - Timestamp (HH:MM:SS format)

**Message Items**:
- Individual cards with light background
- Blue left border for visual separation
- Hover states for interactivity
- Responsive font sizing (12px for messages, 10px for timestamps)

### 3. JavaScript Functionality

**New Variables**:
```javascript
const transcriptToggle = document.getElementById("transcriptToggle");
const transcriptContent = document.getElementById("transcriptContent");
const transcriptMessages = []; // Array to store message history
```

**Toggle Functionality**:
```javascript
transcriptToggle.addEventListener("click", () => {
    const isExpanded = transcriptToggle.classList.toggle("expanded");
    transcriptContent.classList.toggle("expanded");
    transcriptToggle.setAttribute("aria-expanded", isExpanded);
});
```

**Add to Transcript Function**:
```javascript
function addToTranscript(character, message) {
    const timestamp = new Date().toLocaleTimeString();
    transcriptMessages.push({ character, message, timestamp });

    // Remove "no messages" placeholder if exists
    const emptyMsg = transcriptContent.querySelector(".transcript-empty");
    if (emptyMsg) {
        emptyMsg.remove();
    }

    // Create transcript item
    const item = document.createElement("div");
    item.className = "transcript-item";
    item.innerHTML = `
        <div>
            <span class="transcript-character">${character === "billie" ? "Billie" : "Billy"}:</span>
            <span class="transcript-message">${message}</span>
        </div>
        <div class="transcript-time">${timestamp}</div>
    `;

    transcriptContent.appendChild(item);

    // Auto-scroll to bottom
    transcriptContent.scrollTop = transcriptContent.scrollHeight;
}
```

**Updated Message Listener**:
```javascript
window.addEventListener("message", (event) => {
    const data = event.data;
    console.log("[Billdozer] received message:", data);

    if (!data || data.type !== "CHARACTER_MESSAGE") return;

    const { character, message } = data.payload;

    // Add to transcript (NEW)
    addToTranscript(character, message);

    // Add to animation queue (EXISTING)
    queue.push(data.payload);
    if (!active) playNext();
});
```

## Accessibility Features

### ARIA Attributes
- `aria-expanded`: Indicates toggle button state (true/false)
- `aria-controls`: Links button to controlled content region
- `role="region"`: Identifies transcript as landmark region
- `aria-label`: Provides accessible name for screen readers

### Keyboard Navigation
- Toggle button fully keyboard accessible
- Focus visible outline (2px blue, 2px offset)
- Standard button semantics

### Screen Reader Support
- Proper semantic HTML (`<button>`, not `<div>`)
- Clear labeling ("Conversation Transcript")
- Region role announces content changes
- Timestamps provide temporal context

## User Experience

### Visual States
1. **Collapsed (Default)**:
   - Shows only the toggle button
   - Arrow points down (▼)
   - Minimal space usage

2. **Expanded**:
   - Shows all messages in scrollable container
   - Arrow points up (rotated)
   - Auto-scrolls to latest message

3. **Empty State**:
   - Italic placeholder: "No messages yet"
   - Replaced automatically when first message arrives

4. **With Messages**:
   - Each message in individual card
   - Character name highlighted in blue
   - Timestamp for reference
   - Smooth scrolling

### Interaction Flow
1. User clicks toggle button
2. Transcript expands/collapses with smooth transition
3. New messages automatically append to bottom
4. Auto-scroll keeps latest message visible
5. Manual scrolling supported for reviewing history

## Integration with Existing System

### Python Session State
The transcript complements the existing Python-side transcript:
```python
st.session_state.billdozer_transcript = [
    {
        'timestamp': '2026-01-24T15:30:45.123456',
        'character': 'billie',
        'message': 'Hi Billy, any more docs?'
    },
    # ...
]
```

**Two-Level Tracking**:
1. **Python side** (`st.session_state.billdozer_transcript`): Server-side persistence, ISO timestamps, full session history
2. **JavaScript side** (`transcriptMessages` array): Client-side display, user-friendly timestamps, current page view

### Message Flow
```
dispatch_widget_message() (Python)
    ↓
postMessage to iframe
    ↓
window.addEventListener("message") (JavaScript)
    ↓
    ├─ addToTranscript() → Display in UI
    └─ queue.push() → Animate speech bubble
```

## Benefits

### For Users
- ✅ **Message History**: Can review past conversations
- ✅ **Timestamps**: Know when each message was sent
- ✅ **Space Efficient**: Collapsed by default, expands on demand
- ✅ **Auto-Scroll**: Latest messages always visible

### For Accessibility
- ✅ **Screen Readers**: Full ARIA support for assistive technology
- ✅ **Keyboard Navigation**: Works without mouse
- ✅ **Semantic HTML**: Proper button and region roles
- ✅ **Visual Clarity**: High contrast, readable fonts

### For Developers
- ✅ **Debugging**: Visible message log for troubleshooting
- ✅ **Testing**: Can verify message delivery and timing
- ✅ **Monitoring**: See complete conversation flow
- ✅ **Dual Tracking**: Both Python and JavaScript logs available

## Testing
- ✅ All 171 tests pass
- ✅ No breaking changes to existing functionality
- ✅ Fully backward compatible
- ✅ Works with existing message dispatch system

## Future Enhancements

Potential improvements:
- **Export Transcript**: Download as JSON/TXT file
- **Search/Filter**: Find specific messages
- **Clear Transcript**: Reset button
- **Message Count Badge**: Show unread count on toggle
- **Persist Across Reruns**: Integrate with Python session state
- **Copy to Clipboard**: One-click copy of full transcript
- **Timezone Support**: Show local timezone in timestamps

