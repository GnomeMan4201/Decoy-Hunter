# service_probes_parser.py
import re
from typing import List, Dict, Optional

class NmapServiceProbe:
    def __init__(self, name: str, protocol: str, probe_string: str):
        self.name = name
        self.protocol = protocol 
        self.probe_string = probe_string  
        self.matches: List[Dict] = []  

    def add_match(self, pattern: str, service: str):
        self.matches.append({"pattern": re.compile(pattern.encode(), re.IGNORECASE), "service": service})

def parse_nmap_service_probes(file_path: str) -> Dict[str, List[NmapServiceProbe]]:
    
    probes = {"TCP": [], "UDP": []}
    current_probe = None

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            probe_match = re.match(r'^Probe (\w+) (\w+) (.+)$', line)
            if probe_match:
                name, proto, raw_probe = probe_match.groups()
                if proto not in ("TCP", "UDP"):
                    continue

                if raw_probe.startswith("q|") and raw_probe.endswith("|"):
                    payload = raw_probe[2:-1]
                    payload = payload.replace(r'\r', '\r').replace(r'\n', '\n')
                    payload = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), payload)
                    current_probe = NmapServiceProbe(name, proto, payload)
                    probes[proto].append(current_probe)
                continue

           
            if line.startswith("match ") or line.startswith("softmatch "):
                parts = line.split(maxsplit=2)
                if len(parts) < 3:
                    continue
                _, service, pattern_raw = parts
                
                pattern = pattern_raw
                if pattern.startswith("/") and "/" in pattern[1:]:
                    pattern = pattern[1:pattern.find("/", 1)]
                if current_probe:
                    current_probe.add_match(pattern, service)

    return probes