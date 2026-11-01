import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx

from .subscription import get_vpn_links_from_subscription

_DEFAULT_OUTPUT_FILE = Path("vpn-links.txt")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vpn-links",
        description=(
            "Fetch a VPN subscription, display all supported connection URLs, "
            "and optionally save them to a text file."
        ),
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Subscription URL. If omitted, the CLI asks for it interactively.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="FILE",
        help="Save all discovered URLs to FILE without asking for a filename.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not offer to save the discovered URLs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists (requires --output).",
    )
    return parser


def _ask_to_save() -> bool:
    try:
        answer = input("\nSave all URLs to a file? [y/N]: ").strip().casefold()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def _ask_for_output_path() -> Path | None:
    try:
        value = input(f"Output file [{_DEFAULT_OUTPUT_FILE}]: ").strip()
    except EOFError:
        return None
    return Path(value) if value else _DEFAULT_OUTPUT_FILE


def _write_urls(urls: Sequence[str], output: Path, *, force: bool) -> int:
    if output.exists() and not force:
        try:
            answer = (
                input(f"File '{output}' already exists. Overwrite it? [y/N]: ")
                .strip()
                .casefold()
            )
        except EOFError:
            answer = ""
        if answer not in {"y", "yes"}:
            print("File was not changed.")
            return 0

    try:
        output.write_text("\n".join(urls) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"Could not write '{output}': {exc}", file=sys.stderr)
        return 1

    print(f"Saved {len(urls)} URL(s) to '{output}'.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``vpn-links`` command-line application."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.force and args.output is None:
        parser.error("--force can only be used together with --output")
    if args.no_save and args.output is not None:
        parser.error("--no-save cannot be used together with --output")

    url = args.url
    if url is None:
        try:
            url = input("Subscription URL: ").strip()
        except EOFError:
            url = ""

    if not url:
        print("A subscription URL is required.", file=sys.stderr)
        return 2

    print("Fetching subscription...")
    try:
        links = get_vpn_links_from_subscription(url)
    except (httpx.HTTPError, httpx.InvalidURL, ValueError, UnicodeError) as exc:
        print(f"Failed to fetch or parse the subscription: {exc}", file=sys.stderr)
        return 1

    if not links:
        print("No supported VPN URLs were found.")
        return 0

    urls = [str(link) for link in links]
    print(f"\nFound {len(urls)} VPN URL(s):\n")
    for index, item in enumerate(urls, start=1):
        print(f"{index:>3}. {item}")

    if args.no_save:
        return 0

    if args.output is not None:
        return _write_urls(urls, args.output, force=args.force)

    if not _ask_to_save():
        print("No file was created.")
        return 0

    output = _ask_for_output_path()
    if output is None:
        print("No file was created.")
        return 0
    return _write_urls(urls, output, force=False)


if __name__ == "__main__":
    raise SystemExit(main())
