# subscription-2vless

A utility for downloading VPN subscriptions and extracting supported VPN configurations as links

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
| `X-DEVICE-OS` | `Android` |
| `X-VER-OS` | `14` |
| `X-HWID` | `6ba7b811-9dad-11d1-80b4-00c04fd430c8` |
| `User-Agent` | `Incy/1.2.0 (Android; 14)` |

You can override them using `SubscriptionHeaders`:

```python
from subscription_2vless import (
    SubscriptionHeaders,
    get_vpn_links_from_subscription,
)

headers = SubscriptionHeaders(
    X_DEVICE_OS="Android",
    X_VER_OS="14",
    HWID=None,  # Generate a random UUID
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