# Demo Vulnerable Application

This is a **safe, static demonstration repository** used to test SupplyGuard's
supply chain security analysis capabilities.

## Planted Security Signals

### npm (`package.json`)
| Signal | Type | Package |
|--------|------|---------|
| Typosquatting | Name heuristic | `expreess` (→ `express`) |
| Dependency Confusion | Namespace risk | `internal-auth-service`, `company-payments-sdk` |
| Suspicious Lifecycle | Static analysis | `postinstall` uses `child_process`, `prepare` uses `curl \| bash` |
| Known Vulnerability | OSV query | `express@4.17.1`, `lodash@4.17.20` |

### Python (`requirements.txt`)
| Signal | Type | Package |
|--------|------|---------|
| Typosquatting | Name heuristic | `reqeusts` (→ `requests`) |
| Dependency Confusion | Namespace risk | `private-config-loader` |

## Important

- **No code in this directory is executable.**
- All files are harmless static manifests for demonstration purposes.
- Never run `npm install` or `pip install` on these files.
