# Splash Screen Transcript Accordion

## What Changed

The transcript in the splash screen is now **hidden inside a collapsible accordion** labeled "Transcript".

### Before
```
┌─────────────────────────────┐
│   Billy & Billie Animation  │
│                              │
│  Hi! We're Billy and Billie  │
│  We scan medical bills...    │
│  Ready to see how easy...    │
└─────────────────────────────┘
```

### After
```
┌─────────────────────────────┐
│   Billy & Billie Animation  │
│                              │
│   [▶ Transcript] ← Click     │
└─────────────────────────────┘

When clicked:
┌─────────────────────────────┐
│   Billy & Billie Animation  │
│                              │
│   [▼ Transcript]             │
│   Hi! We're Billy and Billie │
│   We scan medical bills...   │
│   Ready to see how easy...   │
└─────────────────────────────┘
```

## Implementation

### HTML Structure

```html
<details class="transcript-accordion">
  <summary>Transcript</summary>
  <div class="transcript-content">
    <div id="splash-transcript">
      <p class="transcript-line" data-index="0">...</p>
      <p class="transcript-line" data-index="1">...</p>
      <p class="transcript-line" data-index="2">...</p>
    </div>
  </div>
</details>
```

### CSS Styling

**Button/Summary**:
- Semi-transparent white background
- White border with hover effects
- Triangle arrow (▶) that rotates when opened
- Smooth transitions

**Content**:
- Max height: 70px
- Auto scroll if content exceeds height
- Centered text
- Smooth reveal animation

## User Experience

1. **Initial State**: Accordion closed, transcript hidden
2. **Click "Transcript"**: Accordion opens smoothly
3. **View Content**: Can read full transcript with scroll
4. **Audio Sync**: Active line still highlights (even when closed)
5. **Click Again**: Closes accordion

## Benefits

✅ **Cleaner UI** - Less visual clutter on splash screen  
✅ **Optional viewing** - Users can choose to read transcript  
✅ **Accessibility** - Screen readers can still access content  
✅ **Mobile friendly** - Takes less vertical space  
✅ **Audio sync works** - Highlighting still functions  

## Technical Details

### File Changed
- `_modules/ui/splash_screen.py`

### Changes Made
1. Added `.transcript-accordion` CSS styling
2. Added `.transcript-accordion summary` button styling
3. Added arrow rotation animation
4. Wrapped transcript HTML in `<details>` element
5. Added `<summary>` element with "Transcript" label

### CSS Features
- `::before` pseudo-element for arrow icon (▶)
- `:hover` state for interactive feedback
- `[open]` attribute for expanded state
- `transform: rotate(90deg)` for arrow animation
- Webkit scrollbar styling for content

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| `<details>` element | ✅ | ✅ | ✅ | ✅ |
| CSS animations | ✅ | ✅ | ✅ | ✅ |
| Arrow rotation | ✅ | ✅ | ✅ | ✅ |
| Scrollbar styling | ✅ | ✅ | ⚠️ Partial | ✅ |

Note: Safari uses native scrollbar (can't customize), but functionality works fine.

## Testing

### Manual Test
1. Start app: `streamlit run app.py`
2. Splash screen appears
3. Look for "▶ Transcript" button below animation
4. Click button
5. Transcript expands with arrow rotating to ▼
6. Content is visible with scroll
7. Click again to collapse

### Accessibility Test
- Use keyboard: Tab to button, Enter to toggle
- Use screen reader: Should announce "Transcript" button
- Content should be readable when expanded

## Future Enhancements

Possible improvements:
1. **Default open** option in config
2. **Remember state** across sessions (localStorage)
3. **Auto-open on first visit** for accessibility
4. **Keyboard shortcut** (T for Transcript)
5. **Smooth scroll to active line** when opened

## Summary

The transcript is now hidden in a collapsible accordion, providing a cleaner splash screen while keeping the content accessible for users who want to read along. The accordion works with standard HTML `<details>` and `<summary>` elements for maximum compatibility and accessibility. 📝✨
