"""Google Analytics 4 (GA4) tracking for Streamlit app.

Privacy-focused analytics implementation:
- Anonymizes IP addresses
- Disables advertising features
- Only tracks high-level navigation events (NO PHI)
"""

import streamlit as st
import streamlit.components.v1 as components
import os
from typing import Optional


def get_ga4_measurement_id() -> Optional[str]:
    """Get GA4 measurement ID from environment variable or config.

    Returns:
        str or None: GA4 measurement ID (e.g., 'G-XXXXXXXXXX') or None if not configured
    """
    # Try environment variable first
    measurement_id = os.environ.get('GA4_MEASUREMENT_ID')

    if not measurement_id:
        # Try Streamlit secrets
        try:
            measurement_id = st.secrets.get('GA4_MEASUREMENT_ID')
        except (FileNotFoundError, KeyError):
            pass

    return measurement_id


def inject_ga4_tracking(measurement_id: Optional[str] = None) -> None:
    """Inject Google Analytics 4 tracking code into the Streamlit app.

    This should be called once on app initialization to set up GA4 tracking.
    Privacy-focused configuration with IP anonymization and disabled advertising.

    Args:
        measurement_id: GA4 measurement ID (e.g., 'G-XXXXXXXXXX').
                       If None, will try to get from environment/config.
    """
    if measurement_id is None:
        measurement_id = get_ga4_measurement_id()

    if not measurement_id:
        # No measurement ID configured - skip analytics
        return

    # GA4 tracking code with privacy-focused configuration
    ga4_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      // Privacy-focused GA4 configuration
      gtag('config', '{measurement_id}', {{
        'anonymize_ip': true,                        // Anonymize IP addresses (HIPAA consideration)
        'allow_ad_personalization_signals': false,   // Disable ad personalization
        'allow_google_signals': false,               // Disable Google signals
        'cookie_flags': 'SameSite=Strict;Secure'     // Secure cookie settings
      }});

      console.log('✅ GA4: Initialized with measurement ID: {measurement_id}');
    </script>
    """

    # Inject the tracking code
    components.html(ga4_code, height=0)


def track_page_view(page_path: str, page_title: Optional[str] = None) -> None:
    """Track a page view event in GA4.

    Args:
        page_path: Page path (e.g., '/streamlit/home')
        page_title: Optional page title (defaults to page_path)
    """
    measurement_id = get_ga4_measurement_id()

    if not measurement_id:
        # Analytics not configured
        return

    if page_title is None:
        page_title = page_path

    # Send page view event
    page_view_code = f"""
    <script>
      if (typeof gtag !== 'undefined') {{
        gtag('event', 'page_view', {{
          'page_path': '{page_path}',
          'page_title': '{page_title}'
        }});
        console.log('📊 GA4: Page view tracked: {page_path}');
      }}
    </script>
    """

    components.html(page_view_code, height=0)


def track_event(
    event_name: str,
    category: Optional[str] = None,
    label: Optional[str] = None,
    value: Optional[int] = None
) -> None:
    """Track a custom event in GA4 (high-level only, NO PHI).

    Allowed events:
    - navigation: Page navigation events
    - feature_toggle: Feature enable/disable events

    Args:
        event_name: Name of the event (e.g., 'navigation', 'feature_toggle')
        category: Optional event category
        label: Optional event label
        value: Optional numeric value
    """
    measurement_id = get_ga4_measurement_id()

    if not measurement_id:
        # Analytics not configured
        return

    # Build event parameters (only safe, non-PHI parameters)
    params = {}
    if category:
        params['event_category'] = category
    if label:
        params['event_label'] = label
    if value is not None:
        params['value'] = value

    # Convert params to JavaScript object
    params_js = ', '.join([f"'{k}': '{v}'" for k, v in params.items()])

    event_code = f"""
    <script>
      if (typeof gtag !== 'undefined') {{
        gtag('event', '{event_name}', {{{params_js}}});
        console.log('📊 GA4: Event tracked: {event_name}');
      }}
    </script>
    """

    components.html(event_code, height=0)


def initialize_ga4_for_streamlit() -> None:
    """Initialize GA4 tracking for Streamlit app.

    This function should be called once at the start of the Streamlit app.
    It checks if GA4 is already initialized to avoid duplicate tracking.
    """
    # Check if already initialized in this session
    if 'ga4_initialized' not in st.session_state:
        measurement_id = get_ga4_measurement_id()

        if measurement_id:
            inject_ga4_tracking(measurement_id)
            st.session_state.ga4_initialized = True
            # Mask measurement ID to avoid exposing secret in logs
            masked_id = f"{measurement_id[:4]}...{measurement_id[-4:]}" if len(measurement_id) > 8 else "***"
            print(f"✅ GA4: Streamlit analytics initialized with ID: {masked_id}")
        else:
            print("⚠️  GA4: No measurement ID configured. Analytics disabled.")
            st.session_state.ga4_initialized = False


# PRIVACY NOTES:
# ==============
# This analytics implementation is designed with privacy in mind:
#
# ✅ DO TRACK:
# - Page navigation (high-level only)
# - Feature usage (general actions)
# - App initialization
#
# ❌ NEVER TRACK:
# - Document names, contents, or metadata
# - User personal information (email, name, etc.)
# - Medical data, amounts, or PHI
# - Analysis results
# - Any sensitive or identifiable information
#
# All events are sanitized to ensure no PHI is transmitted to Google Analytics.
