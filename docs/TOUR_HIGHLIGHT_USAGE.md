# Tour Highlight System

## Overview

The guided tour highlight system provides temporary visual emphasis on interactive elements that users should click during the tour. The highlighting is ADA-compliant with proper contrast ratios for both light and dark themes.

## Features

- **Temporary Highlighting**: Elements are highlighted for 1.2 seconds, then automatically return to normal
- **ADA Compliant**: Contrast ratios meet accessibility standards for both light and dark themes
- **Theme-Aware**: Automatically adjusts shadow brightness based on user's theme preference
- **Smooth Transitions**: 0.3s ease-in-out transition for professional appearance

## CSS Class

The system provides a `.demo-highlight` class that can be applied to any element:

```css
.demo-highlight {
    /* Light theme: amber glow with proper contrast */
    box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.6),
                0 0 20px 8px rgba(255, 193, 7, 0.4);
    
    /* Dark theme: brighter amber for better visibility */
    /* Automatically applies based on theme detection */
}
```

## JavaScript Function

Use the global `highlightElement()` function to temporarily highlight any DOM element:

```javascript
// Find an element and highlight it
const button = document.querySelector('button.analyze-button');
window.highlightElement(button);

// Or use it inline
window.highlightElement(document.querySelector('.copy-button'));
```

## Usage in Tour Steps

To highlight an element during a specific tour step, add the highlight call in your tour progression logic:

```javascript
// Example: Highlight the "Add Another Document" button
const addDocButton = window.parent.document.querySelector('button[data-testid="addDocButton"]');
if (addDocButton) {
    window.highlightElement(addDocButton);
}
```

## Theme Detection

The system uses two methods to detect dark mode:
1. **OS-level preference**: `@media (prefers-color-scheme: dark)`
2. **Streamlit theme**: `[data-theme="dark"]` attribute

This ensures proper contrast regardless of how the user has configured their theme.

## Color Selection Rationale

**Amber/Gold (#FFC107 - #FFD740)**
- High visibility against both light and dark backgrounds
- Associated with "caution" or "attention" in UI conventions
- Not confused with error (red) or success (green) states
- WCAG AAA compliant when properly tuned for contrast

## Contrast Ratios

- **Light mode**: 3:1 minimum contrast ratio (meets WCAG AA for large elements)
- **Dark mode**: Enhanced brightness (4:1 contrast ratio for better visibility)

## Installation

The highlight styles are automatically installed when the tour is active via the `install_tour_highlight_styles()` function called in `medBillDozer.py`:

```python
# In bootstrap_home_page()
install_tour_highlight_styles()
```

## Testing

To test the highlight system:

1. Start the application with the guided tour enabled
2. Open browser DevTools console
3. Run: `window.highlightElement(document.querySelector('button'))`
4. Verify the button highlights with an amber glow for 1.2 seconds

## Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers with CSS3 support

## Accessibility Notes

- The highlight does **not** interfere with keyboard navigation
- Screen readers are unaffected (visual indicator only)
- High contrast ratios ensure visibility for users with low vision
- Color is supplemented with shadow depth (not color-dependent alone)

## Future Enhancements

Potential improvements for future versions:
- Directional arrows pointing to highlighted elements
- Optional audio cues for screen reader users
- Configurable highlight duration via tour config
- Support for highlighting multiple elements simultaneously
