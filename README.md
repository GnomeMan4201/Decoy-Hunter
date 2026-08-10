# Decoy-Hunter

[![CI](https://github.com/GnomeMan4201/Decoy-Hunter/actions/workflows/ci.yml/badge.svg)](https://github.com/GnomeMan4201/Decoy-Hunter/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#requirements)
[![Upstream](https://img.shields.io/badge/upstream-toxy4ny%2FDecoy--Hunter-555?style=flat-square)](https://github.com/toxy4ny/Decoy-Hunter)

**Protocol-aware service validation for networks where deception infrastructure makes every TCP port appear open.**

> Fork of [toxy4ny/Decoy-Hunter](https://github.com/toxy4ny/Decoy-Hunter) by KL3FT3Z. Original concept by [s0i37](https://github.com/s0i37/defence). This fork adds badBANANA ecosystem integrations and Shenron-oriented analysis hooks.

---

## Why this exists

Port-level deception can make conventional scanners report an unrealistically broad attack surface by returning plausible responses across large port ranges. Decoy-Hunter goes one layer deeper: it sends service-specific probes and evaluates whether the response behaves like the protocol that should actually be listening there.

The result is a narrower, evidence-driven view of likely real services instead of treating every open-looking socket as equally trustworthy.

---

## How it works

1. Accept a target authorized for assessment.
2. Probe candidate services using protocol-aware request data derived from nmap service probes.
3. Compare returned behavior with expected service characteristics.
4. Separate likely authentic services from generic deception responders.
5. Surface the reduced set for follow-up investigation.

This is a validation layer, not a replacement for broader reconnaissance. Its useful signal is the difference between *a port answering* and *a service behaving like the protocol it claims to be*.

---

## Quick start

### Requirements

- Python 3.10+
- Linux recommended
- network access to the authorized target

### Install

```bash
git clone https://github.com/GnomeMan4201/Decoy-Hunter.git
cd Decoy-Hunter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Verify the checkout

A fast offline syntax check:

```bash
python -m py_compile decoy_hunter.py
```

The GitHub Actions workflow performs the same fail-closed smoke validation and runs pytest when repository tests are present. A green badge therefore means the checked revision passed the validation actually configured in CI; it is not presented as proof of live-target behavior.

---

## Usage

```bash
python3 decoy_hunter.py <target>
```

Use only against systems and networks you are authorized to assess. Network behavior, middleboxes, rate limiting, and deception products can all affect results, so treat classifications as evidence for follow-up rather than absolute attribution.

---

## Plugin integrations

This fork includes integrations for the wider badBANANA research toolchain:

- `plugin_integration/badbanana/` — badBANANA integration
- `plugin_integration/blackglass/` — Blackglass Suite integration
- `plugin_integration/own/` — OWN framework integration

These adapters keep the core probe logic usable independently while allowing findings to be handed into adjacent analysis workflows.

---

## Upstream and attribution

This repository builds on prior work rather than presenting the technique as original to this fork:

- upstream fork source: [toxy4ny/Decoy-Hunter](https://github.com/toxy4ny/Decoy-Hunter)
- original defensive-deception concept: [s0i37/defence](https://github.com/s0i37/defence)

Local additions should be evaluated separately from upstream behavior when comparing results or reporting bugs.

---

## Demo

<p align="center">
  <img src="assets/decoy_hunter_demo.png" alt="Decoy-Hunter scan output" width="780"/>
</p>

---

## Scope

Decoy-Hunter is intended for authorized security research, defensive validation, lab work, and red-team assessments where deception infrastructure is part of the environment. It does not establish that a discovered service is exploitable, vulnerable, or owned by a particular actor; it helps determine whether a service response appears materially more authentic than surrounding decoy noise.

---

*Decoy-Hunter // badBANANA research // GnomeMan4201*
