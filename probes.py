# probes.py
import asyncio
import socket
import ssl
import random
import logging
from typing import Tuple, Optional, List

from service_probes_parser import NmapServiceProbe

logger = logging.getLogger("decoy-hunter")

TCP_PROBES: List[NmapServiceProbe] = []
UDP_PROBES: List[NmapServiceProbe] = []

def init_probes(probe_file: str):
    global TCP_PROBES, UDP_PROBES
    from service_probes_parser import parse_nmap_service_probes
    parsed = parse_nmap_service_probes(probe_file)
    TCP_PROBES = parsed["TCP"]
    UDP_PROBES = parsed["UDP"]
    logger.debug(f"Loaded {len(TCP_PROBES)} TCP and {len(UDP_PROBES)} UDP probes")

async def test_tcp_port(host: str, port: int, timeout: int = 8) -> Tuple[bool, str, bytes, str]:
    """
    Returns: (is_real, detected_service, banner, probe_used)
    """
    await asyncio.sleep(random.uniform(0.2, 1.8))  

    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        try:
            banner = await asyncio.wait_for(reader.read(512), timeout=2)
        except asyncio.TimeoutError:
            banner = b""
        writer.close()
        await writer.wait_closed()

        for probe in TCP_PROBES:
            for match in probe.matches:
                if match["pattern"].search(banner):
                    return True, match["service"], banner, f"passive/{probe.name}"
    except:
        pass

    for probe in TCP_PROBES[:5]:  
        try:
            use_tls = port in [443, 993, 995, 465, 8443, 8081]
            if use_tls:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port, ssl=ctx), timeout=timeout
                )
            else:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=timeout
                )

            writer.write(probe.probe_string.encode() if isinstance(probe.probe_string, str) else probe.probe_string)
            await writer.drain()

            try:
                response = await asyncio.wait_for(reader.read(1024), timeout=3)
            except asyncio.TimeoutError:
                response = b""

            writer.close()
            await writer.wait_closed()

            for match in probe.matches:
                if match["pattern"].search(response):
                    return True, match["service"], response, probe.name

        except Exception:
            continue

    return False, "unknown", b"", "none"

async def test_udp_port(host: str, port: int, timeout: int = 5) -> Tuple[bool, str, bytes, str]:
    await asyncio.sleep(random.uniform(0.5, 2.0))

    for probe in UDP_PROBES[:4]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(probe.probe_string.encode() if isinstance(probe.probe_string, str) else probe.probe_string, (host, port))
            try:
                data, _ = sock.recvfrom(1024)
            except socket.timeout:
                data = b""
            sock.close()

            for match in probe.matches:
                if match["pattern"].search(data):
                    return True, match["service"], data, probe.name

        except Exception:
            continue

    return False, "unknown", b"", "none"