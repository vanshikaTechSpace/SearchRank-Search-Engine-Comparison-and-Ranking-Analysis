from urllib.parse import urlparse, parse_qs
import base64
import logging

def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing 'www.', trailing slashes, and protocol.
    """
    if not url: return ""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.rstrip("/")
        return f"{netloc}{path}"
    except:
        return url

def decode_bing_redirect(url: str) -> str:
    """
    Decodes Bing's tracking URLs (bing.com/ck/a?...) to get the real destination.
    Bing often encodes the target in the 'u' parameter using Base64 (minus padding).
    """
    if "bing.com/ck/a" not in url:
        return url

    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # The 'u' parameter holds the destination
        if 'u' in params:
            u_val = params['u'][0]

            # Bing uses a modified Base64 (starts with 'a1')
            if u_val.startswith('a1'):
                u_val = u_val[2:]  # Strip 'a1' prefix

            # Add padding if necessary for Base64 decoding
            missing_padding = len(u_val) % 4
            if missing_padding:
                u_val += '=' * (4 - missing_padding)

            try:
                decoded_bytes = base64.urlsafe_b64decode(u_val)
                decoded_url = decoded_bytes.decode('utf-8')
                return decoded_url
            except Exception:
                # Sometimes it's just a plain URL inside 'u'
                return u_val

    except Exception as e:
        logging.warning(f"Failed to decode Bing URL: {url} | Error: {e}")

    return url
