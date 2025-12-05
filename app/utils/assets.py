import os
import logging
import urllib.request
import ssl


def ensure_assets():
    """Ensure critical assets are present and up to date."""
    target_path = "assets/placeholder.svg"
    url = "https://asistencia.cloud/descargas/placeholder.svg"
    expected_size = 13969
    try:
        if os.path.exists(target_path):
            size = os.path.getsize(target_path)
            if size == expected_size:
                logging.info("✅ Asset placeholder.svg is already up to date.")
                return
        logging.info(f"📥 Downloading official Novalink logo from {url}...")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, timeout=10, context=ctx) as response:
            data = response.read()
            with open(target_path, "wb") as f:
                f.write(data)
            logging.info(
                f"✅ Asset placeholder.svg updated successfully ({len(data)} bytes)."
            )
    except Exception as e:
        logging.exception(f"⚠️ Failed to update asset placeholder.svg: {e}")