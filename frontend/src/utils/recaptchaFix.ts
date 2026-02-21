/**
 * Fix autocomplete warnings in Firebase reCAPTCHA forms
 * Firebase Auth's reCAPTCHA creates forms with empty autocomplete attributes
 * This utility patches them after the reCAPTCHA loads
 */

export const fixRecaptchaAutocomplete = () => {
  // Wait for reCAPTCHA to load
  const observer = new MutationObserver(() => {
    // Find all iframes with reCAPTCHA
    const recaptchaIframes = document.querySelectorAll('iframe[src*="recaptcha"]');

    recaptchaIframes.forEach((iframe) => {
      try {
        // Try to access iframe content (may fail due to CORS)
        const iframeDoc = (iframe as HTMLIFrameElement).contentDocument;
        if (iframeDoc) {
          // Find all inputs without autocomplete
          const inputs = iframeDoc.querySelectorAll('input:not([autocomplete])');
          inputs.forEach((input) => {
            input.setAttribute('autocomplete', 'off');
          });

          // Find inputs with empty autocomplete
          const emptyAutocomplete = iframeDoc.querySelectorAll('input[autocomplete=""]');
          emptyAutocomplete.forEach((input) => {
            input.setAttribute('autocomplete', 'off');
          });
        }
      } catch (e) {
        // Ignore CORS errors - can't access cross-origin iframes
        // The CSS fixes will still help with positioning
      }
    });

    // Also fix any forms in the main document
    const allInputs = document.querySelectorAll('input:not([autocomplete])');
    allInputs.forEach((input) => {
      input.setAttribute('autocomplete', 'off');
    });

    const emptyAutocomplete = document.querySelectorAll('input[autocomplete=""]');
    emptyAutocomplete.forEach((input) => {
      input.setAttribute('autocomplete', 'off');
    });
  });

  // Observe the entire document for changes
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['autocomplete']
  });

  // Run once immediately
  setTimeout(() => {
    const allInputs = document.querySelectorAll('input:not([autocomplete]), input[autocomplete=""]');
    allInputs.forEach((input) => {
      input.setAttribute('autocomplete', 'off');
    });
  }, 100);

  return observer;
};

/**
 * Initialize reCAPTCHA fixes when DOM is ready
 */
export const initRecaptchaFixes = () => {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixRecaptchaAutocomplete);
  } else {
    fixRecaptchaAutocomplete();
  }
};
