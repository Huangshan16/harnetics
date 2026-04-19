# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Current |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **sam@harnetics.dev**.

You should receive a response within 48 hours. If for some reason you do not, please follow up to ensure we received your original message.

Please include the following information (as much as you can provide):

- Type of vulnerability (e.g., buffer overflow, SQL injection, cross-site scripting)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Design

Harnetics is designed as a **local-first** application:

- **No cloud data upload by default** — all document processing happens locally
- **No multi-tenant boundaries** — single-user deployment model
- **No authentication layer in MVP** — intended for local/trusted network use
- **LLM integration is opt-in** — works offline with local models (e.g., Ollama)

## Disclosure Policy

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide an estimated timeline for a fix within 7 days
- We will notify you when the vulnerability is fixed
- We will credit you in the release notes (unless you prefer anonymity)

## Preferred Languages

We accept vulnerability reports in English or Chinese (中文).
