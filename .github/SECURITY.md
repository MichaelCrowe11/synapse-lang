# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for
receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 2.3.x   | ✅ Current version |
| 2.2.x   | ⚠️ Security fixes only |
| 2.1.x   | ⚠️ Security fixes only |
| 2.0.x   | ❌ No longer supported |
| < 2.0   | ❌ No longer supported |

## Reporting a Vulnerability

Please report security vulnerabilities to: synapse-security@outlook.com

You should receive a response within 48 hours. If the issue is confirmed, we will
release a patch as soon as possible depending on complexity.

Please include:
- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

## Disclosure Policy

When we receive a security bug report, we will:
1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported releases
4. Release new versions and announce the vulnerability

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a
pull request or open an issue to discuss.
