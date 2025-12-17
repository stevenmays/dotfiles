---
name: warn-debug-code
enabled: true
event: file
pattern: "console\\.log\\(|debugger;"
glob: "*.ts"
action: warn
---

**Debug code detected** - Remove before committing.

If logging is intentional, use the file's existing logging pattern (e.g., structured logger, `console.error` for errors only).
