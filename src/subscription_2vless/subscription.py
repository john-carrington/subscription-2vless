from __future__ import annotations

import base64
import binascii
import json
import platform
import uuid
from urllib.parse import quote, urlencode

import httpx
from httpx import Headers

from subscription_2vless.schemas import VPNType, parse_type_link

_MAX_SUBSCRIPTION_BYTES = 10 * 1024 * 1024


class SubscriptionHeaders(Headers):
    def __init__(
        self,
        *,
        X_DEVICE_OS: str | None = None,
        X_VER_OS: str | None = None,
        HWID: str | None = None,
        X_DEVICE_MODEL: str | None = None,
        app_version: str = "3.9.1",
        user_agent: str | None = None,
    ) -> None:
        device_os = X_DEVICE_OS or platform.system()
        hwid = HWID or str(uuid.uuid4()).upper()
        headers = {
            "X-DEVICE-OS": device_os,
            "X-VER-OS": X_VER_OS or platform.release(),
            "X-HWID": hwid,
            "User-Agent": user_agent or f"INCY/{app_version}/{device_os}",
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "X-APP-VERSION": app_version,
            "X-DEVICE-LOCALE": "en-US",
            "X-CLIENT": "INCY",
        }
        if X_DEVICE_MODEL:
            headers["X-DEVICE-MODEL"] = X_DEVICE_MODEL
        if device_os.casefold() == "android":
            headers["X-DEVICE-ID"] = hwid
        super().__init__(headers)


def _decode_subscription_content(content: bytes) -> str:
    encoded = content + b"=" * (-len(content) % 4)
    try:
        return base64.b64decode(encoded, altchars=b"-_", validate=True).decode()
    except (binascii.Error, UnicodeDecodeError):
        return content.decode()


def _links_from_xray_json(data: object) -> list[VPNType]:
    links = []
    for config in data if isinstance(data, list) else [data]:
        if not isinstance(config, dict):
            continue
        outbounds = config.get("outbounds", [])
        for outbound in outbounds if isinstance(outbounds, list) else []:
            if not isinstance(outbound, dict) or outbound.get("protocol") != "vless":
                continue

            stream = outbound.get("streamSettings", {})
            stream = stream if isinstance(stream, dict) else {}
            if stream.get("network") != "tcp" or stream.get("security") != "reality":
                continue
            reality = stream.get("realitySettings", {})
            reality = reality if isinstance(reality, dict) else {}
            server_name, fingerprint, public_key = (
                reality.get("serverName"),
                reality.get("fingerprint"),
                reality.get("publicKey"),
            )
            if not all(
                isinstance(value, str) and value
                for value in (server_name, fingerprint, public_key)
            ):
                continue

            settings = outbound.get("settings", {})
            settings = settings if isinstance(settings, dict) else {}
            labels = [
                value.strip()
                for value in (config.get("remarks"), outbound.get("tag"))
                if isinstance(value, str) and value.strip()
            ]
            label = " - ".join(dict.fromkeys(labels)) or "VLESS"
            servers = settings.get("vnext", [])
            for server in servers if isinstance(servers, list) else []:
                if not isinstance(server, dict):
                    continue
                address, port = server.get("address"), server.get("port")
                if (
                    not isinstance(address, str)
                    or not address
                    or type(port) is not int
                    or not 1 <= port <= 65535
                ):
                    continue
                host = (
                    f"[{address}]"
                    if ":" in address and not address.startswith("[")
                    else address
                )
                users = server.get("users", [])
                for user in users if isinstance(users, list) else []:
                    if not isinstance(user, dict):
                        continue
                    user_id = user.get("id")
                    if not isinstance(user_id, str):
                        continue
                    query = {
                        "encryption": user.get("encryption") or "none",
                        "security": "reality",
                        "sni": server_name,
                        "fp": fingerprint,
                        "pbk": public_key,
                        "type": "tcp",
                    }
                    if user.get("flow"):
                        query["flow"] = user["flow"]
                    if reality.get("shortId"):
                        query["sid"] = reality["shortId"]
                    link = (
                        f"vless://{quote(user_id, safe='')}@{host}:{port}?"
                        f"{urlencode(query)}#{quote(label, safe='')}"
                    )
                    try:
                        links.append(parse_type_link(link))
                    except ValueError:
                        pass
    return links


def get_vpn_links_from_subscription(
    url: str,
    headers: SubscriptionHeaders | None = None,
) -> list[VPNType]:
    request_headers = headers if headers is not None else SubscriptionHeaders()
    current_url = httpx.URL(str(url))
    with httpx.Client(timeout=20.0, follow_redirects=False) as session:
        for redirect_count in range(21):
            with session.stream(
                "GET", current_url, headers=request_headers
            ) as response:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise ValueError("Subscription redirect has no destination")
                    next_url = response.url.join(location)
                    origin = (response.url.scheme, response.url.host, response.url.port)
                    next_origin = (next_url.scheme, next_url.host, next_url.port)
                    if next_origin != origin:
                        raise ValueError("Subscription redirected to a different host")
                    if redirect_count == 20:
                        raise ValueError("Too many subscription redirects")
                    current_url = next_url
                    continue

                response.raise_for_status()
                if "text/html" in response.headers.get("content-type", "").lower():
                    raise ValueError("Subscription URL returned an HTML page")
                body = bytearray()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > _MAX_SUBSCRIPTION_BYTES:
                        raise ValueError("Subscription response exceeds 10 MiB")
                content = bytes(body)
                if content.lstrip().lower().startswith((b"<!doctype html", b"<html")):
                    raise ValueError("Subscription URL returned an HTML page")
                break
    text = _decode_subscription_content(content)
    try:
        json_data = json.loads(text)
    except json.JSONDecodeError:
        json_data = None
    if isinstance(json_data, (dict, list)):
        json_links = _links_from_xray_json(json_data)
        if json_links:
            return json_links

    links = []
    for item in text.split():
        try:
            links.append(parse_type_link(item))
        except ValueError:
            pass
    return links
