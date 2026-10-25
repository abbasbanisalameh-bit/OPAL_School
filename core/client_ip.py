"""Trusted client-IP resolution for audit logs and rate limiting.

Forwarded headers are user-controlled unless the immediate peer is a configured
trusted reverse proxy. By default, only REMOTE_ADDR is used.
"""
from __future__ import annotations

import ipaddress
import os


def _parse_ip(value: object):
    try:
        return ipaddress.ip_address(str(value).strip())
    except (TypeError, ValueError):
        return None


def _trusted_networks():
    networks = []
    for raw in os.environ.get("OPAL_TRUSTED_PROXY_IPS", "").split(","):
        value = raw.strip()
        if not value:
            continue
        try:
            networks.append(ipaddress.ip_network(value, strict=False))
        except ValueError:
            # Ignore malformed deployment configuration rather than trusting it.
            continue
    return networks


def _is_trusted(ip, networks):
    return ip is not None and any(ip in network for network in networks)


def get_client_ip(request):
    """Return the best client IP only when the proxy chain is trusted.

    If OPAL_TRUSTED_PROXY_IPS is empty, or REMOTE_ADDR is not in that allowlist,
    X-Forwarded-For is ignored. For a trusted peer, walk the chain from the
    server side toward the client and stop at the first untrusted address.
    """
    if request is None:
        return None
    meta = getattr(request, "META", {}) or {}
    remote_raw = meta.get("REMOTE_ADDR")
    remote = _parse_ip(remote_raw)
    if remote is None:
        return None

    networks = _trusted_networks()
    if not networks or not _is_trusted(remote, networks):
        return str(remote)

    forwarded = meta.get("HTTP_X_FORWARDED_FOR", "")
    chain = []
    for item in str(forwarded or "").split(","):
        parsed = _parse_ip(item)
        if parsed is not None:
            chain.append(parsed)
    chain.append(remote)

    for candidate in reversed(chain):
        if not _is_trusted(candidate, networks):
            return str(candidate)
    # A malformed/incomplete chain must not displace the actual peer address.
    return str(remote)
