import os

import httpx

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
DEFAULT_TIMEOUT = 10.0


class PushoverError(Exception):
    pass


def _credentials() -> tuple[str, str]:
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    if not token or not user:
        raise PushoverError("PUSHOVER_TOKEN and/or PUSHOVER_USER are not set in environment.")
    return token, user


def send_notification(message: str, title: str = "Digital Twin") -> dict:
    """Send a Pushover notification to Jean. Returns Pushover's response JSON."""
    token, user = _credentials()
    payload = {
        "token": token,
        "user": user,
        "message": message,
        "title": title,
    }

    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        resp = client.post(PUSHOVER_URL, data=payload)

    if resp.status_code != 200:
        raise PushoverError(f"Pushover returned {resp.status_code}: {resp.text}")
    return resp.json()
