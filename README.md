# subscription-2vless

A utility for downloading VPN subscriptions and extracting supported VPN configurations as links. It reads plain or Base64 link lists and converts VLESS/TCP/REALITY outbounds from Xray JSON configs into links, preserving profile remarks and outbound tags as link names.

---

## CLI Usage

```bash
uvx subscription-2vless
```

The program will ask for the subscription URL:

```text
Subscription URL: https://example.com/subscription
Fetching subscription...

Found 3 VPN URL(s):

  1. vless://...
  2. vmess://...
  3. trojan://...

Save all URLs to a file? [y/N]:
```

To save the discovered links, enter `y` or `yes`

Next, specify the output filename:

```text
Output file [links.txt]:
```

Leave it empty to save the results to `links.txt`

### Passing a subscription URL

You can pass the subscription URL directly as an argument:

```bash
uvx subscription-2vless "https://example.com/subscription"
```

### Saving results to a file

Use `-o` or `--output`:

```bash
uvx subscription-2vless "https://example.com/subscription" -o links.txt
```

You can also specify an absolute path:

```bash
uvx subscription-2vless "https://example.com/subscription" --output /tmp/vpn-links.txt
```

### Disabling file output

To display the discovered links in the console without saving them:

```bash
uvx subscription-2vless "https://example.com/subscription" --no-save
```

### Overwriting an existing file

By default, the program asks for confirmation before overwriting an existing file

To allow overwriting automatically, use `--force`:

```bash
uvx subscription-2vless "https://example.com/subscription" -o links.txt --force
```

### Help

Display all available arguments:

```bash
uvx subscription-2vless --help
```

### Available arguments

| Argument | Description |
|---|---|
| `url` | Subscription URL (optional) |
| `-h`, `--help` | Display help information |
| `-o`, `--output FILE` | Save results to the specified file |
| `--no-save` | Do not offer to save the results |
| `--force` | Overwrite an existing file without confirmation |

## Using as a Python Library

Retrieve links from a subscription:

```python
from subscription_2vless import get_vpn_links_from_subscription

links = get_vpn_links_from_subscription(
    "https://example.com/subscription"
)

for link in links:
    print(link)
```

Determine the type of a link:

```python
from subscription_2vless import parse_type_link

link = parse_type_link("vless://uuid@example.com:443")

print(type(link).__name__)  # Vless
```

## Custom HTTP Headers

The following HTTP headers are used by default:

| Header | Default value |
|---|---|
| `User-Agent` | `INCY/3.9.1/<host OS>` |
| `Accept` | `*/*` |
| `Accept-Language` | Detected device locale |
| `X-APP-VERSION` | `3.9.1` |
| `X-CLIENT` | `INCY` |
| `X-DEVICE-LOCALE` | Detected device locale |
| `X-DEVICE-OS` | Detected host OS (for example, `Windows`) |
| `X-VER-OS` | Detected host OS release |
| `X-HWID` | Stable uppercase UUID generated from host identifiers on Windows/Linux |
| `X-DEVICE-MODEL` | Detected system model; generic desktop label if unavailable |
| `X-DEVICE-ID` | Same as `X-HWID` on Android only |

On Windows and Linux, the default HWID follows INCY's documented desktop algorithm. The docs do not specify which 128 digest bits `hashToUuid` uses; this implementation uses the first 128. An Android HWID requires Android-specific device identifiers; pass that HWID explicitly if you need to identify as an existing Android device. INCY documents `Accept-Encoding` only for iOS, so this desktop client does not send it.

You can override them using `SubscriptionHeaders`:

```python
from subscription_2vless import (
    SubscriptionHeaders,
    get_vpn_links_from_subscription,
)

headers = SubscriptionHeaders(
    X_DEVICE_MODEL="Windows Desktop",
    user_agent="MyApplication/1.0",
)

links = get_vpn_links_from_subscription(
    "https://example.com/subscription",
    headers=headers,
)
```

## Supported Protocols

| Protocol | URL schemes |
|---|---|
| VLESS | `vless://` |
| VMess | `vmess://` |
| Shadowsocks | `ss://` |
| ShadowsocksR | `ssr://` |
| Trojan | `trojan://` |
| Hysteria | `hysteria://` |
| Hysteria 2 | `hysteria2://`, `hy2://` |
| TUIC | `tuic://` |
| WireGuard | `wireguard://`, `wg://` |
| SOCKS | `socks://`, `socks4://`, `socks5://` |
| HTTP Proxy | `http://` |
| HTTPS Proxy | `https://` |

## License

[MIT License](LICENSE)