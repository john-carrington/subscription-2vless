import base64
import json
from typing import Any, ClassVar, Self


class VPNType(str):
    schemes: ClassVar[tuple[str, ...]] = ()

    def __new__(cls, value: str) -> Self:
        value = value.strip()
        scheme, separator, _ = value.partition("://")
        if not separator:
            raise ValueError(f"Missing URL scheme: {value[:30]!r}")
        if scheme.lower() not in cls.schemes:
            raise ValueError(f"{cls.__name__}: unsupported scheme {scheme!r}")
        return super().__new__(cls, value)

    @property
    def scheme(self) -> str:
        return str(self).partition("://")[0].lower()

    @property
    def fragment(self) -> str:
        return str(self).partition("#")[2]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str.__repr__(self)})"


class Vless(VPNType):
    schemes = ("vless",)


class Vmess(VPNType):
    schemes = ("vmess",)

    @property
    def payload(self) -> dict[str, Any]:
        encoded = str(self)[8:].partition("#")[0]
        encoded += "=" * (-len(encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(encoded))
        if not isinstance(payload, dict):
            raise TypeError("VMess payload must be a JSON object")
        return payload


class Shadowsocks(VPNType):
    schemes = ("ss",)

    @property
    def method_and_password(self) -> tuple[str, str]:
        body = str(self)[5:].partition("#")[0]
        encoded, separator, _ = body.partition("@")
        if not separator:
            encoded = body
        encoded += "=" * (-len(encoded) % 4)
        decoded = base64.urlsafe_b64decode(encoded).decode().partition("@")[0]
        method, separator, password = decoded.partition(":")
        if not separator:
            raise ValueError("SS payload is missing the method:password separator")
        return method, password


class ShadowsocksR(VPNType):
    schemes = ("ssr",)


class Trojan(VPNType):
    schemes = ("trojan",)


class Hysteria(VPNType):
    schemes = ("hysteria",)


class Hysteria2(VPNType):
    schemes = ("hysteria2", "hy2")


class Tuic(VPNType):
    schemes = ("tuic",)


class WireGuard(VPNType):
    schemes = ("wireguard", "wg")


class Socks(VPNType):
    schemes = ("socks", "socks4", "socks5")


class Http(VPNType):
    schemes = ("http",)


class Https(VPNType):
    schemes = ("https",)


_REGISTRY = {
    scheme: cls
    for cls in (
        Vless,
        Vmess,
        Shadowsocks,
        ShadowsocksR,
        Trojan,
        Hysteria,
        Hysteria2,
        Tuic,
        WireGuard,
        Socks,
        Http,
        Https,
    )
    for scheme in cls.schemes
}


def parse_type_link(value: str) -> VPNType:
    value = value.strip()
    scheme, separator, _ = value.partition("://")
    if not separator:
        raise ValueError(f"Not a valid connection URL: {value[:30]!r}")
    try:
        return _REGISTRY[scheme.lower()](value)
    except KeyError:
        raise ValueError(f"Unknown protocol: {scheme!r}") from None
