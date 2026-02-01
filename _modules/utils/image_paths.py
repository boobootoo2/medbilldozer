"""Image path utilities for handling local vs production CDN URLs.

Provides functionality to determine if the app is running locally and return
appropriate image paths (local static files vs GitHub CDN URLs).
"""
import os
import re


def is_local_environment() -> bool:
    """Check if the app is running in a local environment.

    Returns:
        bool: True if running on localhost/127.0.0.1 or any IP address, False otherwise
    """
    # Check common environment indicators
    hostname = os.environ.get('HOSTNAME', '').lower()
    streamlit_server = os.environ.get('STREAMLIT_SERVER_ADDRESS', '').lower()
    server_address = os.environ.get('SERVER_ADDRESS', '').lower()

    # Combine all server indicators
    all_addresses = f"{hostname} {streamlit_server} {server_address}".lower()

    # nosec B104 - checking string indicators only, not binding to interfaces
    is_localhost = (
        'localhost' in all_addresses
        or '127.0.0.1' in all_addresses
        or '0.0.0.0' in all_addresses
    )

    # Check if it's an IP address pattern (e.g., 192.168.x.x, 10.x.x.x)
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    has_ip_address = bool(re.search(ip_pattern, all_addresses))

    # Default to local if we can't determine (safer for development)
    if not all_addresses.strip():
        return True

    return is_localhost or has_ip_address


def get_image_url(relative_path: str) -> str:
    """Get the appropriate image URL based on environment.

    Args:
        relative_path: Relative path from project root (e.g., 'images/avatars/billy.png')

    Returns:
        str: Full GitHub CDN URL (works for both local and production)

    Example:
        >>> get_image_url('images/avatars/billie__eyes_open__ready.png')
        # Returns: 'https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/billie__eyes_open__ready.png'
    """
    # Clean up the path
    clean_path = relative_path.strip('/')

    # Remove 'static/' prefix if present (for consistent paths)
    if clean_path.startswith('static/'):
        clean_path = clean_path[7:]

    # Remove 'app/static/' prefix if present
    if clean_path.startswith('app/static/'):
        clean_path = clean_path[11:]

    # Always use GitHub CDN (works for both local and production)
    # This is necessary because Streamlit's static file serving doesn't work inside iframes
    # Images are stored in the static/ directory in the repo
    base_cdn_url = "https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static"
    return f"{base_cdn_url}/{clean_path}"


def get_avatar_url(avatar_filename: str) -> str:
    """Get the appropriate avatar image URL.

    Args:
        avatar_filename: Just the filename (e.g., 'billie__eyes_open__ready.png')

    Returns:
        str: Full URL for the avatar image
    """
    return get_image_url(f"images/avatars/{avatar_filename}")


def get_transparent_avatar_url(avatar_filename: str) -> str:
    """Get the appropriate transparent avatar image URL.

    Args:
        avatar_filename: Just the filename (e.g., 'billie__eyes_closed__billdozer_down.png')

    Returns:
        str: Full URL for the transparent avatar image
    """
    return get_image_url(f"images/avatars/transparent/{avatar_filename}")

