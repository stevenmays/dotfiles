---
description: Audit home-directory dotfiles for security issues — package cooldown config, secrets, permissions, shell hygiene, supply-chain settings
---

# Security Audit

Audit the user's home-directory dotfiles for security problems. This is a **read-only review**: gather all findings first, present a severity-ranked report, and only modify files after the user approves a specific fix.

Never print secret values. When a finding involves a token or key, show the file, line number, and a redacted form (first 4 chars + `…`) only.

## Files in scope

Examine whichever of these exist in `$HOME` (including `.backup`/`.bak`/`.tmp` copies of rc files):

- Package managers: `.npmrc`, `.yarnrc`, `.yarnrc.yml`, `.bunfig.toml`, pnpm global config
- Shell: `.zshrc`, `.zprofile`, `.zshenv`, `.bashrc`, `.bash_profile`, `.profile`
- Credentials: `.netrc`, `.aws/credentials`, `.ssh/`, `.sentryclirc`, `.gitconfig`
- Network tools: `.curlrc`, `.wgetrc`

## Checks

### 1. Package cooldown — the 7-day rule

Verify each **installed** package manager enforces a minimum release age of at least 7 days, so freshly published (potentially compromised) versions are never installed. The config key, file, and unit differ per tool:

| Tool | Key | Where | Unit | 7 days | Min version |
|------|-----|-------|------|--------|-------------|
| npm | `min-release-age` | `~/.npmrc` | days | `7` | 11.10.0 |
| pnpm | `minimum-release-age` | global config (`pnpm config get minimum-release-age`) | minutes | `10080` | 10.16 |
| Yarn Berry | `npmMinimalAgeGate` | `~/.yarnrc.yml` | minutes | `10080` | 4.10.0 |
| Bun | `minimumReleaseAge` under `[install]` | `bunfig.toml` | seconds | `604800` | 1.3.0 |

For each package manager found on PATH:

- **Missing or below 7 days** → High finding. Offer the exact fix (e.g., `npm config set min-release-age 7 --location=user`).
- **Package manager too old to support the setting** → High finding; the fix is upgrading the package manager first.
- Yarn note: use a plain number of minutes — duration suffixes like `"7d"` are silently ignored due to a parsing bug.
- Bun note: user-wide config is not supported; report as Info that each project's `bunfig.toml` needs it.

### 2. Secrets & tokens

Grep the in-scope files for plaintext credentials:

- `_authToken=`, `_password=`, `always-auth` with embedded creds in `.npmrc` / `.yarnrc*`
- `token`, `api_key`, `secret`, `password` assignments in rc files and `.sentryclirc`
- `export FOO_KEY=...` / `export *_TOKEN=...` / `export *_SECRET=...` with literal values in shell rc files
- Credentials embedded in remote URLs in `.gitconfig` (`https://user:pass@`)
- Don't forget rc-file backups (`.zshrc.backup*`, `.zshrc.bak.*`, `.zshrc.tmp`) — stale copies often retain secrets that were removed from the live file.

Any literal secret → Critical. Suggest moving it to the macOS Keychain, an env-loading tool, or at minimum a `chmod 600` untracked file sourced from the rc.

### 3. File permissions

- `~/.ssh` must be `700`; private keys and `authorized_keys` must be `600`. Anything looser → Critical.
- Credential files (`.npmrc`, `.netrc`, `.aws/credentials`, `.sentryclirc`) readable by group/other → High. Fix: `chmod 600`.
- Walk every directory on `$PATH`: world- or group-writable directories → High (binary-planting risk). Nonexistent PATH entries → Info.

### 4. Shell config hygiene

In every shell rc file (and backups):

- `curl … | bash`, `curl … | sh`, `wget … | sh` patterns → High. Suggest download-then-inspect-then-run instead.
- `.` or an empty entry (`::`, leading/trailing `:`) in `$PATH` → High.
- `source`/`.` of files in `/tmp` or other world-writable locations → High.
- Aliases or functions shadowing security-relevant binaries (`sudo`, `ssh`, `git`, `curl`) → Medium; flag for review, they may be legitimate.
- `eval` of command output from the network → High.

### 5. Supply-chain config

- `registry=` in `.npmrc`/`.yarnrc*` pointing anywhere other than `https://registry.npmjs.org/` (or a known corporate proxy the user confirms) → High. Any `http://` registry → Critical.
- Scoped registry overrides (`@scope:registry=`) → list them as Info for the user to confirm.
- `ignore-scripts` not set to `true` in `~/.npmrc` → Medium. Lifecycle scripts are the main supply-chain execution vector; recommend `ignore-scripts=true` user-wide with per-project opt-out.
- `.gitconfig`: `credential.helper = store` (plaintext credentials on disk) → High; recommend `osxkeychain`. `url.insteadOf` rewrites → Info, list for confirmation.
- `.curlrc`/`.wgetrc` containing `insecure` / `check-certificate = off` → High.

## Report format

Group findings by severity — Critical, High, Medium, Info — each with:

1. **What**: one line describing the issue and the file/line
2. **Why it matters**: one line
3. **Fix**: the exact command or config line

End with a summary count per severity. If everything passes, say so explicitly per category.

## Applying fixes

After the report, ask which fixes to apply (the cooldown config is the most common one). Rules:

- Back up any file before editing it (`cp file file.pre-audit`)
- Apply only the fixes the user selected, one at a time
- Show a diff of each change
- Never delete or rewrite secret values — only the user moves secrets
