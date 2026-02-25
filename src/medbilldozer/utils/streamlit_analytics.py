"""
Google Analytics integration for Streamlit app
"""
import streamlit.components.v1 as components
import os
from typing import Dict, Optional

# Get GA4 Measurement ID from environment variable
GA_MEASUREMENT_ID = os.getenv('GA_MEASUREMENT_ID', 'G-XXXXXXXXXX')


def inject_ga() -> None:
    """
    Inject Google Analytics 4 tracking code into Streamlit app.
    Should be called once at the top of the main Streamlit app.
    """
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """
    components.html(ga_code, height=0)


def track_event(event_name: str, event_params: Optional[Dict] = None) -> None:
    """
    Track custom events in Google Analytics.

    Args:
        event_name: Name of the event (e.g., 'analysis_started', 'file_uploaded')
        event_params: Dictionary of event parameters (e.g., {'file_type': 'pdf'})

    Example:
        track_event('file_uploaded', {'file_type': 'pdf', 'file_size_mb': 2.5})
    """
    if event_params is None:
        event_params = {}

    # Convert Python dict to JavaScript object notation
    params_str = str(event_params).replace("'", '"')

    event_code = f"""
    <script>
      if (typeof gtag !== 'undefined') {{
        gtag('event', '{event_name}', {params_str});
      }}
    </script>
    """
    components.html(event_code, height=0)


def track_page_view(page_name: str, page_path: Optional[str] = None) -> None:
    """
    Track page views in Google Analytics.

    Args:
        page_name: Human-readable page name
        page_path: Optional custom page path
    """
    params = {'page_title': page_name}
    if page_path:
        params['page_path'] = page_path

    track_event('page_view', params)
