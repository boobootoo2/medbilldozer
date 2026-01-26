# Tour Highlight Examples

This document provides practical examples of how to use the `highlightElement()` function in the guided tour to draw user attention to interactive elements.

## Basic Usage Pattern

```javascript
// 1. Find the element you want to highlight
const element = window.parent.document.querySelector('selector-here');

// 2. Check if element exists (important!)
if (element) {
    // 3. Call the highlight function
    window.highlightElement(element);
}
```

## Example 1: Highlight Copy Buttons

Highlight the pharmacy receipt copy button when the user reaches step 3:

```javascript
// In install_copy_button_detector() or similar function
function highlightPharmacyCopyButton() {
    const iframes = window.parent.document.querySelectorAll('iframe');
    
    iframes.forEach(function(iframe) {
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            const buttons = iframeDoc.querySelectorAll('button[id^="copy_"]');
            
            buttons.forEach(function(button) {
                let nearbyText = '';
                let parent = button.parentElement;
                for (let i = 0; i < 5 && parent; i++) {
                    nearbyText += parent.textContent || '';
                    parent = parent.parentElement;
                }
                
                if (nearbyText.includes('Pharmacy') || nearbyText.includes('💊')) {
                    // Highlight this button!
                    window.highlightElement(button);
                }
            });
        } catch (e) {
            // Cross-origin iframe, skip
        }
    });
}

// Call it when step 3 loads
highlightPharmacyCopyButton();
```

## Example 2: Highlight Text Areas

Draw attention to the document input area where users should paste:

```javascript
function highlightDocumentInput() {
    // Find all textareas in the main document
    const textareas = window.parent.document.querySelectorAll('textarea');
    
    // Highlight the first visible textarea (Document 1)
    for (let i = 0; i < textareas.length; i++) {
        if (textareas[i].offsetParent !== null) {
            window.highlightElement(textareas[i]);
            break;
        }
    }
}
```

## Example 3: Highlight the Analyze Button

Emphasize the "Analyze Document" button when documents are loaded:

```javascript
function highlightAnalyzeButton() {
    // Streamlit buttons often have specific data-testid attributes
    const analyzeBtn = window.parent.document.querySelector(
        'button[data-testid="stButton"], button:has-text("Analyze")'
    );
    
    if (analyzeBtn) {
        // Wait a moment for the page to settle, then highlight
        setTimeout(() => {
            window.highlightElement(analyzeBtn);
        }, 500);
    }
}
```

## Example 4: Highlight "Add Another Document" Button

Guide users to add a second document:

```javascript
function highlightAddDocumentButton() {
    // Find button by text content
    const buttons = window.parent.document.querySelectorAll('button');
    
    for (let btn of buttons) {
        if (btn.textContent.includes('Add Another Document')) {
            window.highlightElement(btn);
            break;
        }
    }
}
```

## Example 5: Continuous Highlighting (Pulse Effect)

For elements that should remain highlighted until clicked:

```javascript
function pulseHighlight(element, intervalMs = 3000) {
    let pulseInterval;
    
    function pulse() {
        if (element && element.offsetParent !== null) {
            window.highlightElement(element);
        } else {
            // Element no longer visible, stop pulsing
            clearInterval(pulseInterval);
        }
    }
    
    // Initial highlight
    pulse();
    
    // Repeat every intervalMs
    pulseInterval = setInterval(pulse, intervalMs);
    
    // Return cleanup function
    return function stopPulse() {
        clearInterval(pulseInterval);
    };
}

// Usage:
const stopPulsing = pulseHighlight(myButton, 2500);
// When done: stopPulsing();
```

## Example 6: Highlight Multiple Elements in Sequence

Create a guided sequence through multiple UI elements:

```javascript
function highlightSequence(selectors, delayMs = 1500) {
    let index = 0;
    
    function highlightNext() {
        if (index >= selectors.length) return;
        
        const element = window.parent.document.querySelector(selectors[index]);
        if (element) {
            window.highlightElement(element);
        }
        
        index++;
        if (index < selectors.length) {
            setTimeout(highlightNext, delayMs);
        }
    }
    
    highlightNext();
}

// Usage: highlight textarea, then button, then another element
highlightSequence([
    'textarea[data-testid="doc_input_0"]',
    'button:has-text("Analyze")',
    '.stExpander'
], 2000);
```

## Example 7: Integration with Tour Step Changes

Highlight elements automatically when advancing to specific steps:

```javascript
// In check_tour_progression() or similar
function onTourStepChange(newStep) {
    switch(newStep) {
        case 'upload_prompt':
            // Highlight first textarea
            setTimeout(() => {
                const textarea = window.parent.document.querySelector('textarea');
                if (textarea) window.highlightElement(textarea);
            }, 300);
            break;
            
        case 'first_document_loaded':
            // Highlight pharmacy copy button
            highlightPharmacyCopyButton();
            break;
            
        case 'add_second_document':
            // Highlight "Add Another Document" button
            highlightAddDocumentButton();
            break;
            
        case 'second_document_loaded':
            // Highlight analyze button
            highlightAnalyzeButton();
            break;
    }
}
```

## Best Practices

1. **Always check if element exists** before highlighting to avoid errors
2. **Use setTimeout** for elements that might load asynchronously
3. **Highlight one element at a time** to avoid visual clutter
4. **Consider timing** - don't highlight immediately on page load, give it 300-500ms
5. **Stop highlighting** when user has completed the action (use event listeners)
6. **Test in both themes** to ensure proper contrast

## Troubleshooting

**Highlight doesn't appear:**
- Check if element exists: `console.log(element)`
- Verify styles loaded: `console.log(document.querySelector('style'))`
- Check z-index conflicts with parent containers

**Highlight appears but wrong color:**
- Verify theme detection is working
- Check if element has inline styles overriding the shadow
- Use `!important` in CSS if needed (already included)

**Highlight fires too early:**
- Add setTimeout delay: `setTimeout(() => window.highlightElement(el), 500)`
- Use MutationObserver to wait for element appearance

## Testing in Console

Test highlights directly in browser DevTools:

```javascript
// Test basic highlight
window.highlightElement(document.querySelector('button'));

// Test on multiple elements
document.querySelectorAll('button').forEach(btn => {
    setTimeout(() => window.highlightElement(btn), Math.random() * 3000);
});

// Test theme-specific styling
document.body.setAttribute('data-theme', 'dark');
window.highlightElement(document.querySelector('textarea'));
```
