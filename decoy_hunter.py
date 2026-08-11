#!/usr/bin/env python3
"""Decoy-Hunter — protocol-aware validation of deceptive network services."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional

from tqdm.asyncio import tqdm

from probes import init_probes, test_tcp_port, test_udp_port

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
logger = logging.getLogger("decoy-hunter")
logger.propagate = False

LOGO = r"""
         o                                                         o                                   o
        <|>                                                       <|>                                 <|>
        < \                                                       / >                                 < >
   o__ __o/    o__  __o       __o__    o__ __o     o      o       \o__ __o     o       o   \o__ __o    |        o__  __o   \o__ __o
  /v     |    /v      |>     />  \    /v     v\   <|>    <|>       |     v\   <|>     <|>   |     |>   o__/_   /v      |>   |     |>
 />     / \  />      //    o/        />       <\  < >    < >      / \     <\  < >     < >  / \   / \   |      />      //   / \   < >
 \      \o/  \o    o/     <|         \         /   \o    o/       \o/     o/   |       |   \o/   \o/   |      \o    o/     \o/
  o      |    v\  /v __o   \\         o       o     v\  /v         |     <|    o       o    |     |    o       v\  /v __o   |
  <\__  / \    <\/> __/>    _\o__</   <\__ __/>      <\/>         / \    / \   <\__ __/>   / \   / \   <\__     <\/> __/>  / \
                                                      /
                                                     o
                                                  __/>
  Advanced Decoy Detection Toolkit by FL3FT3Z (https://github.com/toxy4ny) versus cool man s0i37 (https://github.com/s0i37/defence)
"""

PROBE_FILE_CANDIDATES = (
    Path("nmap-service-probes"),
    Path("/usr/share/nmap/nmap-service-probes"),
    Path("/usr/local/share/nmap/nmap-service-probes"),
)


def print_logo() -> None:
    print(LOGO)


def resolve_probe_file(requested: Optional[str] = None) -> str:
    """Resolve an nmap-service-probes file without downloading at runtime."""
    if requested:
        path = Path(requested).expanduser()
        if path.is_file():
            return str(path)
        raise FileNotFoundError(f"nmap-service-probes file not found: {path}")

    for candidate in PROBE_FILE_CANDIDATES:
        if candidate.is_file():
            return str(candidate)

    checked = ", ".join(str(path) for path in PROBE_FILE_CANDIDATES)
    raise FileNotFoundError(
        "nmap-service-probes was not found. Install nmap or pass "
        f"--probe-file PATH. Checked: {checked}"
    )


async def scan_port(host: str, port: int, proto: str, timeout: int, semaphore, results):
    async with semaphore:
        if proto == "tcp":
            is_real, svc, banner, probe_used = await test_tcp_port(host, port, timeout)
        else:
            is_real, svc, banner, probe_used = await test_udp_port(host, port, timeout)

        status = "[REAL]" if is_real else "[FAKE]"
        banner_str = banner.decode("utf-8", errors="replace").strip().replace("\n", " \\n ")[:100]
        result_line = (
            f"{status} {port}/{proto} {'open' if is_real or banner else 'closed'} "
            f"{svc} (via {probe_used}) -> {banner_str}"
        )
        results.append((is_real, port, proto, result_line))


async def run_scan(host: str, ports: List[int], protocols: List[str], concurrency: int, timeout: int):
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    tasks = [
        scan_port(host, port, proto, timeout, semaphore, results)
        for port in ports
        for proto in protocols
    ]

    for task in tqdm.as_completed(
        tasks, total=len(tasks), desc=f"Scanning {host}", unit="port", colour="green"
    ):
        await task

    print("\n" + "=" * 80)
    print("RESULTS".center(80))
    print("=" * 80)
    for _, _, _, line in sorted(results, key=lambda x: (x[2], x[1])):
        print(line)


def parse_ports(port_str: str) -> List[int]:
    if port_str == "full":
        return list(range(1, 65536))
    if port_str == "top10k":
        return list(range(1, 10001))

    ports = []
    for part in port_str.split(","):
        if "-" in part:
            a, b = map(int, part.split("-"))
            ports.extend(range(a, b + 1))
        else:
            ports.append(int(part))
    return sorted(set(p for p in ports if 1 <= p <= 65535))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect fake services behind 'all ports open' deception",
        epilog="Example: ./decoy_hunter.py 192.168.1.10 -p 22,80,443 -sU",
    )
    parser.add_argument("host", help="Target IP or hostname")
    parser.add_argument(
        "-p", "--ports", default="top10k",
        help="Ports: 'top10k', 'full', or custom (e.g. 22,80,1000-2000)",
    )
    parser.add_argument("-sU", "--udp", action="store_true", help="Also scan UDP")
    parser.add_argument("-c", "--concurrency", type=int, default=15, help="Max concurrent connections")
    parser.add_argument("-t", "--timeout", type=int, default=6, help="Timeout per probe (seconds)")
    parser.add_argument(
        "--probe-file",
        default=None,
        help="Path to nmap-service-probes; defaults to local/system nmap locations",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    print_logo()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.concurrency < 1:
        raise SystemExit("--concurrency must be at least 1")
    if args.timeout < 1:
        raise SystemExit("--timeout must be at least 1 second")

    try:
        probe_file = resolve_probe_file(args.probe_file)
    except FileNotFoundError as exc:
        logger.error("[!] %s", exc)
        raise SystemExit(1) from exc

    init_probes(probe_file)

    try:
        ports = parse_ports(args.ports)
    except ValueError as exc:
        raise SystemExit(f"invalid --ports value: {args.ports}") from exc
    if not ports:
        raise SystemExit("--ports did not resolve to any valid ports")

    protocols = ["tcp"]
    if args.udp:
        protocols.append("udp")

    logger.info("[*] Target: %s", args.host)
    logger.info("[*] Ports: %d (%s)", len(ports), "TCP + UDP" if args.udp else "TCP only")
    logger.info("[*] Concurrency: %d | Timeout: %ds", args.concurrency, args.timeout)
    logger.info("[*] Probe file: %s\n", probe_file)

    try:
        asyncio.run(run_scan(args.host, ports, protocols, args.concurrency, args.timeout))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
