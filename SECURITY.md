# Security Policy

## Reporting a vulnerability

Do **not** disclose a suspected vulnerability publicly before review.

Preferred reporting path:

1. Use **Security → Report a vulnerability** for this repository when GitHub private vulnerability reporting is available.
2. Otherwise email **badbanana@proton.me** with the subject `Decoy-Hunter security report`.

Include the affected commit/version, exact code path, minimal reproduction, expected and observed behavior, impact, and any proposed mitigation. Do not send unrelated credentials or third-party private data.

## Security-relevant scope

Decoy-Hunter is a network-validation tool derived from upstream work. Reports are especially useful for issues involving:

- command or subprocess execution outside the documented CLI behavior;
- unsafe parsing or loading of `nmap-service-probes` data;
- target/scope handling that causes unintended scanning beyond the operator-selected host/ports;
- malformed network responses causing unsafe local behavior;
- local path traversal or unintended file access;
- dependency issues with a meaningful exploit path.

Classification mistakes on deceptive services are accuracy issues unless they also create a security boundary failure. A `[REAL]` or `[FAKE]` result should never be treated as proof that a service is safe, exploitable, or attributable to a specific actor.

## Upstream boundary

When a finding appears to originate in the upstream Decoy-Hunter implementation rather than a local modification, please identify that if known. Local and upstream remediation responsibilities may differ.

## Supported state

Report findings against the current default branch or name the exact historical revision involved. Historical upstream behavior is not assumed to receive backported fixes in this fork.

## Disclosure

I aim to acknowledge reproducible reports within seven days. Validation and remediation timing depends on severity, reproducibility, and whether the issue is local or upstream; no fixed patch deadline is promised before triage.

Reporter credit is welcome unless anonymity is requested.
