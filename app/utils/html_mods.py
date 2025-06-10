from typing import Optional
from bs4 import BeautifulSoup


def strip_html(text: Optional[str]) -> Optional[str]:
    """
    Remove HTML tags and decode entities from text safely.
    Returns None if input is None or empty after cleaning.

    Args:
        text: Optional string that may contain HTML

    Returns:
        Cleaned text with HTML removed or None if no text content
    """
    if not text:
        return None

    try:
        # Parse with 'html.parser' which is more lenient with malformed HTML
        soup = BeautifulSoup(text, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        # Get text and normalize whitespace
        clean_text: str = " ".join(soup.get_text().split())
        return clean_text if clean_text else None

    except Exception:
        # Return None if any parsing errors occur
        return None
