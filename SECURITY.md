# Security Policy

## Reporting a Vulnerability

Please report security issues privately through GitHub Security Advisories for this repository. If advisories are unavailable, contact the maintainer through the repository owner profile.

Do not open a public issue for vulnerabilities involving credential handling, arbitrary file access, dependency supply chain concerns, or provider/API abuse paths.

## Scope

Finance CLI reads local files and URLs that users explicitly pass to commands. Treat untrusted documents and URLs with the same care you would use for any local parser or web fetcher.

## Credentials

Finance CLI reads API keys from environment variables at runtime. The CLI should not write API keys to disk.
