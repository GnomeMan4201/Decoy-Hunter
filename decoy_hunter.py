import sys
try:
    from plugin_integration.badbanana.badbanana_main import run_badbanana
    BB_AVAILABLE = True
except Exception:
    BB_AVAILABLE = False
try:
    from plugin_integration.own.own_main import run_own
    OWN_AVAILABLE = True
except Exception:
    OWN_AVAILABLE = False
try:
    from plugin_integration.blackglass.blackglass_main import run_blackglass
    BG_AVAILABLE = True
except Exception:
    BG_AVAILABLE = False

# PLUGIN_INTEGRATION_HOOK
# Safely handle plugin flags before argparse (so unknown flags won't break the tool)
plugin_flags = ["--shenron","--badbanana","--own","--blackglass"]
requested = { 'shenron': '--shenron' in sys.argv,
              'badbanana': '--badbanana' in sys.argv,
              'own': '--own' in sys.argv,
              'blackglass': '--blackglass' in sys.argv }
# Remove plugin flags so argparse won't fail
sys.argv = [a for a in sys.argv if a not in plugin_flags]
# Auto-detect host argument (first non-flag)
host_arg = next((a for a in sys.argv[1:] if not a.startswith('-')), None)
if host_arg:
    targets = [host_arg]
else:
    targets = []

# Run plugins requested (non-blocking; order: Shenron, BadBanana, Own, BlackGlass)
if requested.get('shenron'):
    try:
        from shenron_integration.shenron_main import run_shenron_in_decoyhunter
        run_shenron_in_decoyhunter(targets)
    except Exception as e:
        print('[plugin] Shenron failed:', e)
if requested.get('badbanana') and BB_AVAILABLE:
    try:
        run_badbanana(targets)
    except Exception as e:
        print('[plugin] BadBanana failed:', e)
if requested.get('own') and OWN_AVAILABLE:
    try:
        run_own(targets)
    except Exception as e:
        print('[plugin] Own failed:', e)
if requested.get('blackglass') and BG_AVAILABLE:
    try:
        run_blackglass(targets)
    except Exception as e:
        print('[plugin] BlackGlass failed:', e)

import sys
try:
    from shenron_integration.shenron_main import run_shenron_in_decoyhunter
    SHENRON_AVAILABLE = True
except ImportError:
    SHENRON_AVAILABLE = False

# Safe Shenron hook
if '--shenron' in sys.argv and SHENRON_AVAILABLE:
    sys.argv.remove('--shenron')  # remove before argparse
    # auto-detect host argument (first positional argument)
    host_arg = next((a for a in sys.argv[1:] if not a.startswith('-')), None)
    targets = [host_arg] if host_arg else []
    run_shenron_in_decoyhunter(targets)

try:
    from shenron_integration.shenron_main import run_shenron_in_decoyhunter
    SHENRON_AVAILABLE = True
except ImportError:
    SHENRON_AVAILABLE = False

#!/usr/bin/env python3
# decoy_hunter.py

import asyncio
import sys
import argparse
import logging
import os
from typing import List
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

def print_logo():
    print(LOGO)


async def scan_port(host: str, port: int, proto: str, timeout: int, semaphore, results):
    async with semaphore:
        if proto == "tcp":
            is_real, svc, banner, probe_used = await test_tcp_port(host, port, timeout)
        else:
            is_real, svc, banner, probe_used = await test_udp_port(host, port, timeout)

        status = "[REAL]" if is_real else "[FAKE]"
        banner_str = banner.decode('utf-8', errors='replace').strip().replace('\n', ' \\n ')[:100]
        result_line = f"{status} {port}/{proto} {'open' if is_real or banner else 'closed'} {svc} (via {probe_used}) → {banner_str}"
        
        results.append((is_real, port, proto, result_line))

async def run_scan(host: str, ports: List[int], protocols: List[str], concurrency: int, timeout: int):
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    total_tasks = len(ports) * len(protocols)

    tasks = []
    for port in ports:
        for proto in protocols:
            task = scan_port(host, port, proto, timeout, semaphore, results)
            tasks.append(task)

    desc = f"Scanning {host}"
    for _ in tqdm.as_completed(tasks, total=total_tasks, desc=desc, unit="port", colour="green"):
        await _

    print("\n" + "="*80)
    print("RESULTS".center(80))
    print("="*80)
    for is_real, port, proto, line in sorted(results, key=lambda x: (x[2], x[1])):
        print(line)


def parse_ports(port_str: str) -> List[int]:
    if port_str == "full":
        return list(range(1, 65536))
    elif port_str == "top10k":
        return list(range(1, 10001))
    ports = []
    for part in port_str.split(","):
        if "-" in part:
            a, b = map(int, part.split("-"))
            ports.extend(range(a, b + 1))
        else:
            ports.append(int(part))
    return sorted(set(p for p in ports if 1 <= p <= 65535))

def main():
    print_logo()
    
    parser = argparse.ArgumentParser(
        description="Detect fake services behind 'all ports open' deception",
        epilog="Example: ./decoy_hunter.py 192.168.1.10 -p 22,80,443 -sU"
    )
    parser.add_argument("host", help="Target IP or hostname")
    parser.add_argument("-p", "--ports", default="top10k",
                        help="Ports: 'top10k', 'full', or custom (e.g. 22,80,1000-2000)")
    parser.add_argument("-sU", "--udp", action="store_true", help="Also scan UDP")
    parser.add_argument("-c", "--concurrency", type=int, default=15, help="Max concurrent connections")
    parser.add_argument("-t", "--timeout", type=int, default=6, help="Timeout per probe (seconds)")
    parser.add_argument("--probe-file", default="nmap-service-probes", help="Path to nmap-service-probes")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not os.path.exists(args.probe_file):
        logger.error(f"[!] nmap-service-probes file not found at: {args.probe_file}")
        logger.error("Download it: wget https://raw.githubusercontent.com/nmap/nmap/master/nmap-service-probes")
        sys.exit(1)

    init_probes(args.probe_file)

    ports = parse_ports(args.ports)
    protocols = ["tcp"]
    if args.udp:
        protocols.append("udp")

    logger.info(f"[*] Target: {args.host}")
    logger.info(f"[*] Ports: {len(ports)} ({' + UDP' if args.udp else 'TCP only'})")
    logger.info(f"[*] Concurrency: {args.concurrency} | Timeout: {args.timeout}s")
    logger.info("[*] Using full nmap-service-probes with traffic obfuscation\n")

    try:
        asyncio.run(run_scan(args.host, ports, protocols, args.concurrency, args.timeout))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(1)

if __name__ == "__main__":
    main()
 
# Optional Shenron analytics
if 'shenron' in sys.argv and SHENRON_AVAILABLE:
    targets = []  # TODO: replace with actual targets list in main script
    run_shenron_in_decoyhunter(targets)

