#!/usr/bin/env python3
"""Exchange Spotify authorization code for a refresh token and update .env."""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Spotify rejects localhost; loopback must use 127.0.0.1 (see Spotify redirect URI docs).
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-currently-playing"
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
TOKEN_URL = "https://accounts.spotify.com/api/token"


def _redirect_uri() -> str:
    match = re.search(r"^SPOTIFY_REDIRECT_URI=(.*)$", ENV_PATH.read_text(), re.MULTILINE)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return DEFAULT_REDIRECT_URI


def _read_env_value(name: str) -> str:
    if not ENV_PATH.is_file():
        msg = f"Missing {ENV_PATH}"
        raise SystemExit(msg)
    match = re.search(rf"^{name}=(.*)$", ENV_PATH.read_text(), re.MULTILINE)
    if not match:
        msg = f"{name} is not set in {ENV_PATH}"
        raise SystemExit(msg)
    value = match.group(1).strip()
    if not value:
        msg = f"{name} is empty in {ENV_PATH}"
        raise SystemExit(msg)
    return value


def _write_refresh_token(refresh_token: str) -> None:
    text = ENV_PATH.read_text()
    updated, count = re.subn(
        r"^SPOTIFY_REFRESH_TOKEN=.*$",
        f"SPOTIFY_REFRESH_TOKEN={refresh_token}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        msg = "SPOTIFY_REFRESH_TOKEN line not found in .env"
        raise SystemExit(msg)
    ENV_PATH.write_text(updated)


def _exchange_code(client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    body = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
    ).encode()
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        msg = f"Token exchange failed ({exc.code}): {detail}"
        raise SystemExit(msg) from exc


class _CallbackHandler(BaseHTTPRequestHandler):
    auth_code: str | None = None
    error: str | None = None

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_error(404)
            return

        params = urllib.parse.parse_qs(parsed.query)
        if "error" in params:
            _CallbackHandler.error = params["error"][0]
            self._respond("Spotify authorization failed. You can close this tab.")
            return

        code = (params.get("code") or [None])[0]
        if not code:
            _CallbackHandler.error = "missing_code"
            self._respond("Missing authorization code. You can close this tab.")
            return

        _CallbackHandler.auth_code = code
        self._respond("Spotify authorized. Return to the terminal.")

    def _respond(self, message: str) -> None:
        body = f"<html><body><p>{message}</p></body></html>".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _authorize_url(client_id: str, redirect_uri: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": SCOPE,
            "show_dialog": "true",
        }
    )
    return f"https://accounts.spotify.com/authorize?{params}"


def _wait_for_code(redirect_uri: str) -> str:
    client_id = _read_env_value("SPOTIFY_CLIENT_ID")
    authorize_url = _authorize_url(client_id, redirect_uri)

    print(f"Using redirect_uri: {redirect_uri}", flush=True)
    print("Add that exact URI under Spotify Dashboard → your app → Settings → Redirect URIs", flush=True)
    print(f"Starting callback server on {redirect_uri}", flush=True)
    print("Opening Spotify authorization in your browser...", flush=True)
    print(f"If it does not open, visit:\n{authorize_url}\n", flush=True)

    server = HTTPServer(("127.0.0.1", 8888), _CallbackHandler)
    try:
        subprocess.Popen(["open", authorize_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        webbrowser.open(authorize_url)

    print("Waiting for authorization (approve in the browser)...", flush=True)
    while _CallbackHandler.auth_code is None and _CallbackHandler.error is None:
        server.handle_request()

    if _CallbackHandler.error:
        msg = f"Authorization error: {_CallbackHandler.error}"
        raise SystemExit(msg)

    return _CallbackHandler.auth_code or ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--code",
        help="Authorization code from the redirect URL (skips local callback server)",
    )
    args = parser.parse_args()

    client_id = _read_env_value("SPOTIFY_CLIENT_ID")
    client_secret = _read_env_value("SPOTIFY_CLIENT_SECRET")
    redirect_uri = _redirect_uri()
    code = args.code or _wait_for_code(redirect_uri)

    data = _exchange_code(client_id, client_secret, code, redirect_uri)
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        msg = f"No refresh_token in response: {json.dumps(data, indent=2)}"
        raise SystemExit(msg)

    _write_refresh_token(refresh_token)
    print("SPOTIFY_REFRESH_TOKEN saved to .env", flush=True)
    print("Restart the API server if it is already running.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelled.")
