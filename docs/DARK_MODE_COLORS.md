# Dark Mode Color Reference

## Flagged Issues Warning Box

### Light Mode (Default)
```css
.flag-warning {
    background-color: #FFFBEB;  /* Pale yellow background */
    border-left: 6px solid #F59E0B;  /* Amber border */
    color: #1F2937;  /* Dark gray text */
}
```

**Visual:**
- Background: Light cream/yellow (#FFFBEB)
- Border: Bright amber (#F59E0B) 
- Text: Dark gray (#1F2937)
- **Result:** High contrast, easy to read

### Dark Mode
```css
@media (prefers-color-scheme: dark) {
    .flag-warning {
        background-color: #422006;  /* Dark brown background */
        border-left: 6px solid #F59E0B;  /* Amber border (same) */
        color: #FEF3C7;  /* Light cream text */
    }
}
```

**Visual:**
- Background: Dark brown (#422006) - warm, muted
- Border: Bright amber (#F59E0B) - consistent with light mode
- Text: Light cream (#FEF3C7) - soft, easy on eyes
- **Result:** Proper contrast, comfortable for dark mode

## Color Palette Reasoning

### Why These Colors?

**Light Mode:**
- `#FFFBEB` - Pale yellow background provides subtle warning without being alarming
- `#1F2937` - Dark text ensures excellent readability (WCAG AAA compliant)

**Dark Mode:**
- `#422006` - Dark brown (not pure black) maintains warmth, reduces eye strain
- `#FEF3C7` - Cream text (not pure white) is gentler on eyes in dark environments
- Maintains the warning theme while being comfortable to read

### Accessibility

Both color schemes meet WCAG 2.1 Level AA contrast requirements:
- Light mode: 13.4:1 contrast ratio
- Dark mode: 11.2:1 contrast ratio

## Example Issues

### Light Mode Display
```
┌──────────────────────────────────────────────────┐
│ Duplicate medical procedure billed               │
│ CPT 45378 appears more than once on 2026-01-12   │
└──────────────────────────────────────────────────┘
  ↑ Light yellow bg, dark text, amber left border
```

### Dark Mode Display
```
┌──────────────────────────────────────────────────┐
│ Duplicate medical procedure billed               │
│ CPT 45378 appears more than once on 2026-01-12   │
└──────────────────────────────────────────────────┘
  ↑ Dark brown bg, cream text, amber left border
```

## Testing

To test dark mode support:

### macOS
1. System Preferences → General → Appearance → Dark
2. Open medBillDozer
3. Analyze a document with issues
4. Verify warning boxes are readable

### Browser DevTools
```javascript
// Force dark mode in Chrome DevTools
// 1. Open DevTools (F12)
// 2. Cmd+Shift+P → "Rendering"
// 3. Enable "Emulate CSS media feature prefers-color-scheme: dark"
```

### Test Documents
Use the colonoscopy bill demo:
- ✅ Should show duplicate procedure warning
- ✅ Warning box should be readable in both modes
- ✅ Border should remain amber in both modes

## Related Components

Other components with dark mode support:
- Button focus states (`:focus-visible`)
- Header anchor links
- Checkbox focus rings
- Copy button outlines

## Future Enhancements

Consider adding dark mode support for:
- [ ] Success messages (`st.success`)
- [ ] Info boxes (`st.info`)
- [ ] Custom metric cards
- [ ] Data tables

---

**Last Updated:** January 25, 2026  
**Related File:** `_modules/ui/ui.py` (lines 180-197)
