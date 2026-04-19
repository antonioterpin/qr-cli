# QR-cli

A small CLI that generates a QR code with a logo embedded in the middle.
Uses error correction level H so the QR stays scannable with the logo on top.

## Requirements

- [uv](https://docs.astral.sh/uv/) installed (`brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Run without installing

```bash
uv run qr_logo.py \
  "https://arxiv.org/abs/2508.10480" \
  /Users/antonioterpin/Downloads/logo_arXiv.jpg \
  -o /Users/antonioterpin/Downloads/arxiv_qr.png
```

`uv run` creates an ephemeral env with the dependencies declared in
`pyproject.toml` the first time, then reuses it on subsequent runs.

## Install as a persistent tool

```bash
uv tool install .

# Now `qr-logo` is on your PATH:
qr-logo "https://arxiv.org/abs/2508.10480" \
  /Users/antonioterpin/Downloads/logo_arXiv.jpg \
  -o /Users/antonioterpin/Downloads/arxiv_qr.png
```

Upgrade later after editing the code:

```bash
uv tool install . --reinstall
```

## Options

```
qr-logo <url> <logo> [-o OUTPUT] [--box-size N] [--border N]
                     [--logo-ratio R] [--fill COLOR] [--bg COLOR]
```

- `--logo-ratio` — logo size as fraction of QR width (default 0.22, max 0.35).
  Keep it ≤ 0.30 so scanners stay happy.
- `--box-size` — pixel size per QR module (default 10).
- `--border` — border width in modules (default 4; spec minimum).
- Output format is inferred from the `-o` extension (`.png`, `.jpg`, …).

## Development

```bash
uv sync                 # create .venv and install deps
uv run qr_logo.py ...   # run inside the managed env
```
