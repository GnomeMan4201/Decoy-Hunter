# Decoy-Hunter

> **Fork of [toxy4ny/Decoy-Hunter](https://github.com/toxy4ny/Decoy-Hunter) by KL3FT3Z**
> Original concept by [s0i37](https://github.com/s0i37/defence)
> This fork adds: badBANANA ecosystem plugin integrations (Blackglass_Suite, OWN, bad_BANANA), Shenron analytics integration, and extended test coverage.

---

**Bypasses "all ports open" deception infrastructure to identify real attack surfaces.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#)
[![Upstream](https://img.shields.io/badge/upstream-toxy4ny%2FDecoy--Hunter-555?style=flat-square)](https://github.com/toxy4ny/Decoy-Hunter)


**Bypasses "all ports open" deception infrastructure to identify real attack surfaces.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#)

---

Modern defensive architectures increasingly use deception layers that make every TCP port appear open — masking real services behind honeypot noise. Decoy-Hunter cuts through this by probing services for authentic behavioral signatures using nmap service probe data, distinguishing real services from fake responders.

Built in response to the work of [s0i37](https://github.com/s0i37/defence) on defensive deception.

---

## How it works

Standard port scanners see every port as open when a deception layer is active. Decoy-Hunter sends protocol-specific probes and analyzes responses against known service signatures from the nmap probe database — real services respond correctly to their protocol, fake responders do not.

---

## Usage
```bash
git clone https://github.com/GnomeMan4201/Decoy-Hunter.git
cd Decoy-Hunter
pip install -r requirements.txt
python3 decoy_hunter.py <target>
```

---

## Plugin integrations

Decoy-Hunter ships with integrations for the badBANANA toolkit ecosystem:

- `plugin_integration/badbanana/` — badBANANA integration
- `plugin_integration/blackglass/` — Blackglass Suite integration
- `plugin_integration/own/` — OWN framework integration

---

## Reference

The defensive deception technique this tool detects is documented at [s0i37's defence repository](https://github.com/s0i37/defence).

---

*Decoy-Hunter // badBANANA research // GnomeMan4201*
