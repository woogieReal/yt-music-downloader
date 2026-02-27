import re

def sanitize_filename(name: str) -> str:
    """Removes special characters from filenames that might be problematic."""
    # yt-dlp's restrictfilenames config does this, but keeping a helper is good
    if not name:
        return ""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()
