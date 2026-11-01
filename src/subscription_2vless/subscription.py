import base64
import binascii
import uuid
from collections.abc import Mapping

import httpx

from .links import VPN, Vless, parse_vpn_link


class SubscriptionHeaders(dict[str, str]):
    def __init__(
        self,
        *,
        HWID: str | None = None,
        user_agent: str = "Incy/1.2.0 (Android; 14)",
    ) -> None:
        super().__init__(
            {
                "X-HWID": HWID or str(uuid.uuid4()),
                "User-Agent": user_agent,
            }
        )


VlessHeader = SubscriptionHeaders


def get_vpn_links_from_subscription(
    url: str,
    headers: Mapping[str, str] | None = None,
) -> list[VPN]:
    request_headers = headers if headers is not None else SubscriptionHeaders()
    with httpx.Client(timeout=10.0, follow_redirects=True) as session:
        response = session.get(str(url), headers=request_headers)

    response.raise_for_status()
    content = response.content

    try:
        text = base64.b64decode(content, validate=True).decode()
    except (binascii.Error, UnicodeDecodeError):
        text = content.decode()

    links = []
    for item in text.split():
        try:
            links.append(parse_vpn_link(item))
        except ValueError:
            pass
    return links


def get_vless_from_subscription(
    url: str,
    headers: Mapping[str, str] | None = None,
    *,
    client: httpx.Client | None = None,
) -> list[Vless]:
    return [
        link
        for link in get_vpn_links_from_subscription(url, headers)
        if isinstance(link, Vless)
    ]
