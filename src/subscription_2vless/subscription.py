import base64
import binascii
import uuid

import httpx
from httpx import Headers

from subscription_2vless.schemas import VPNType, parse_type_link


class SubscriptionHeaders(Headers):
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


def get_vpn_links_from_subscription(
    url: str,
    headers: SubscriptionHeaders | None = None,
) -> list[VPNType]:
    request_headers = headers if headers else SubscriptionHeaders()
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
            links.append(parse_type_link(item))
        except ValueError:
            pass
    return links
