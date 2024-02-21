# Systema (Work-in-Progress)

## Summary

> "You do not rise to the level of your goals. You fall to the level of your systems."
>
> - James Clear

This project is intended to be my "Productivity System".

## Planned components

- Web server
  - FastAPI
  - SQLModel
  - FastUI
- CLI client and manager
  - Typer
- TUI client
  - Textual

## Planned features

- Project Manager
- Diagrams

## Setup

### Termux

```bash
cd
mkdir -p .termux
echo "enforce-char-based-input=true" > .termux/termux.properties
termux-reload-settings

pkg update && pkg upgrade -y
pkg install python -y
pkg install python-cryptography -y
pkg install binutils -y
apt update && apt upgrade -y
apt install rust -y
```
