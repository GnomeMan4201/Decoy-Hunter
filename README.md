The defensive idea belongs to https://t.me/s0i37_channel

![Tests](https://github.com/GnomeMan4201/Decoy-Hunter/workflows/Tests/badge.svg) ![Python](https://img.shields.io/badge/python-3.8+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Stars](https://img.shields.io/github/stars/GnomeMan4201/Decoy-Hunter?style=social)


# 🛡️→⚔️ Decoy-Hunter: Bypassing "All Ports Open" Deception in Offensive Security

> **Defensive deception is powerful — but not invisible.**  
> This tool helps red teams and penetration testers cut through the noise of fake services and find real attack surfaces.

---

## 🔥 The Problem: "All Ports Are Open" Deception

In modern defensive architectures, it's becoming common to **confuse attackers** by making *every TCP port appear open*. This is often achieved with simple `iptables` rules:

```bash
iptables -t nat -A PREROUTING -i eth0 -p tcp -m conntrack --ctstate NEW -j REDIRECT --to-ports 1234
while sleep 1; do nc -nv -lp 1234; done
```

Or more advanced tools like [`portspoof`](https://github.com/droberson/portspoof), which return **random service banners** on every port.

The goal? **Waste the attacker’s time**, trigger false positives in scanners, and hide real services among thousands of decoys.

But here’s the catch: **most deception implementations are flawed**.

- `portspoof` returns **different banners on each scan** → easily detectable.
- Static banner emulators (e.g., using `nmap-service-probes` responses) **lack protocol logic**.
- Fake services often **respond to any input** with the same static string — real services don’t work that way.

This creates an opportunity for **offensive counter-deception**.

---

## 🕵️‍♂️ Introducing `decoy-hunter`

`decoy-hunter` is a **stealthy, protocol-aware scanner** designed to:
- Detect fake services behind "all ports open" traps,
- Identify **real, exploitable services** hidden in the noise,
- Operate with **traffic obfuscation** to avoid detection by the defender.

Unlike `nmap -sV`, which can be fooled by consistent fake banners, `decoy-hunter`:
- Uses **real `nmap-service-probes`** to send legitimate client requests,
- Validates **protocol behavior**, not just banners,
- Supports **TCP + UDP** up to port 10,000 (or full range),
- Mimics **human-like timing and request patterns**.

---

## 🧠 How It Works

### 1. **Realistic Probing**
Instead of sending raw strings, `decoy-hunter`:
- Sends **valid HTTP requests** with real `User-Agent`,
- Initiates **TLS handshakes** on HTTPS ports,
- Uses **SMTP `EHLO`**, **FTP `USER`**, **Redis `PING`**, etc.,
- Leverages the **official `nmap-service-probes`** database for accuracy.

### 2. **Protocol Validation**
A fake SSH service might return `SSH-2.0-OpenSSH_8.9`, but:
- It won’t complete a key exchange,
- It won’t respond correctly to malformed packets,
- It may reply with an SSH banner on **port 8080** — which is suspicious.

`decoy-hunter` checks:
- Does the response match the **expected protocol state**?
- Is the service **consistent across multiple probes**?
- Does it **only respond to one probe type**, ignoring others?

### 3. **Traffic Obfuscation (Anti-Detection)**
To avoid being flagged as a scanner:
- Random delays between connections (`0.2–2.0s`),
- Limited concurrency (default: 15),
- No aggressive payload spraying,
- TLS used where expected (e.g., port 443),
- No repeated identical patterns.

> 🔒 **Goal**: Make traffic look like a curious user or misconfigured client — not a pentest tool.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install tqdm
```

### 2. Download `nmap-service-probes`
```bash
wget https://raw.githubusercontent.com/nmap/nmap/master/nmap-service-probes
```

### 3. Run a scan
```bash
# Scan top 10k TCP ports
python3 decoy_hunter.py 192.168.1.10

# Include UDP (slower)
python3 decoy_hunter.py target.com -sU -c 5

# Custom ports
python3 decoy_hunter.py 10.0.0.5 -p 22,80,443,8080,1234
```

### Sample Output
```
[REAL] 22/tcp open ssh (via passive/NULL) → SSH-2.0-OpenSSH_8.9p1
[FAKE] 8080/tcp open http (via GetRequest) → SSH-2.0-OpenSSH_8.9p1  ← 🚩 Mismatch!
[REAL] 443/tcp open http (via GetRequest) → HTTP/1.1 200 OK
```

> Notice: **SSH banner on port 8080** → clear sign of deception.

---

## 🛠️ Technical Highlights

| Feature | Description |
|--------|-------------|
| **Full `nmap-service-probes` support** | Accurate service detection using Nmap’s official database |
| **Async I/O with `asyncio`** | Fast, scalable scanning without blocking |
| **UDP + TCP scanning** | Covers both transport layers |
| **Stealth mode** | Randomized timing, realistic requests, low concurrency |
| **Progress bar** | Visual feedback with `tqdm` |
| **No external dependencies** (except `tqdm`) | Pure Python, easy to run anywhere |

---

## 📚 Why This Matters

Defensive deception is a **valid and useful tactic** — but it shouldn’t create a false sense of security. As red teamers and ethical hackers, we must:
- Understand defensive tricks,
- Develop tools to **see through them**,
- Help organizations **test the effectiveness** of their deception layers.

`decoy-hunter` is not just a scanner — it’s a **counter-deception framework** for the modern attack surface.

---

## 🤝 Contributing

Found a fake service that `decoy-hunter` missed?  
Have an idea to improve obfuscation or probe coverage?

→ **Pull requests welcome!**  
→ Issues and feature requests encouraged.

---

## ⚠️ Legal & Ethical Note

This tool is for **authorized penetration testing and research only**.  
Never scan systems you don’t own or don’t have explicit permission to test.

---

## 📦 Repository Structure

```
decoy-hunter/
├── decoy_hunter.py          # Main CLI tool
├── probes.py                # Probe logic & obfuscation
├── service_probes_parser.py # Parses nmap-service-probes
├── nmap-service-probes      # (Download separately)
├── README.md                # This file
└── requirements.txt         # tqdm
```

---

## 💡 Inspired By

- [portspoof](https://github.com/droberson/portspoof)
- [Nmap Service Detection](https://nmap.org/book/vscan.html)
- Defensive deception research by MITRE Engenuity, CrowdStrike, and others

---

> 🔍 **Real security isn’t about hiding — it’s about resilience.**  
> Use `decoy-hunter` to ensure your defenses are **tested, not just decorated**.

---

**Author**: [KL3FT3Z]  
**License**: MIT  
**GitHub**: [github.com/toxy4ny/decoy-hunter](https://github.com/toxy4ny/decoy-hunter)

---
