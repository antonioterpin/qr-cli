#!/usr/bin/env python3
"""CLI tool to generate a QR code with a logo embedded in the middle.

Usage:
    python qr_logo.py <url> <logo_path> [-o OUTPUT] [--size SIZE] [--box-size N]
                                        [--border N] [--logo-ratio R]

Example:
    python qr_logo.py "https://example.com" logo.png -o qr.png

"""
import argparse
import sys
from pathlib import Path

import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_H


def generate_qr_with_logo(
    url: str,
    logo_path: str,
    output_path: str = "qrcode.png",
    box_size: int = 10,
    border: int = 4,
    logo_ratio: float = 0.22,
    fill_color: str = "black",
    back_color: str = "white",
) -> str:
    """Generate a QR code for `url` with `logo_path` centered on top.

    Uses high error correction (H, ~30%) so the QR remains scannable
    even with a logo covering the middle.
    """
    logo_file = Path(logo_path)
    if not logo_file.exists():
        raise FileNotFoundError(f"Logo not found: {logo_path}")

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    logo = Image.open(logo_file).convert("RGBA")

    qr_w, qr_h = qr_img.size
    target = int(min(qr_w, qr_h) * logo_ratio)

    # Preserve aspect ratio of the logo
    logo.thumbnail((target, target), Image.LANCZOS)

    # Optional white pad behind logo for contrast / scannability
    pad = 8
    bg = Image.new(
        "RGBA",
        (logo.size[0] + pad * 2, logo.size[1] + pad * 2),
        (255, 255, 255, 255),
    )
    bg.paste(logo, (pad, pad), mask=logo)

    pos = ((qr_w - bg.size[0]) // 2, (qr_h - bg.size[1]) // 2)
    qr_img.paste(bg, pos, mask=bg)

    # If saving to a format without alpha (e.g. JPEG), flatten first
    out_ext = Path(output_path).suffix.lower()
    if out_ext in {".jpg", ".jpeg"}:
        flat = Image.new("RGB", qr_img.size, (255, 255, 255))
        flat.paste(qr_img, mask=qr_img.split()[-1])
        flat.save(output_path, quality=95)
    else:
        qr_img.save(output_path)

    return output_path


def main() -> int:
    """CLI entry point for QR code generation with logo embedding."""
    parser = argparse.ArgumentParser(
        description="Generate a QR code with a logo in the middle."
    )
    logos_dir = Path(__file__).resolve().parent / "logos"

    parser.add_argument("url", help="URL or text to encode in the QR code")
    parser.add_argument(
        "logo",
        nargs="?",
        default=None,
        help="Path to the logo image (png/jpg with or without alpha)",
    )

    builtin = parser.add_argument_group(
        "built-in logos (use instead of the logo argument)"
    )
    builtin.add_argument(
        "--arXiv",
        action="store_const",
        const=str(logos_dir / "arXiv.jpg"),
        dest="builtin_logo",
        help="Use the bundled arXiv logo",
    )
    builtin.add_argument(
        "--github",
        action="store_const",
        const=str(logos_dir / "github.jpg"),
        dest="builtin_logo",
        help="Use the bundled GitHub logo",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="qrcode.png",
        help="Output image path (default: qrcode.png). Extension controls format.",
    )
    parser.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="Pixel size of each QR module (default: 10)",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="QR border width in modules (default: 4, min 4 recommended)",
    )
    parser.add_argument(
        "--logo-ratio",
        type=float,
        default=0.22,
        help="Logo size as fraction of QR width (default: 0.22, keep <= 0.30)",
    )
    parser.add_argument(
        "--fill", default="black", help="QR foreground color (default: black)"
    )
    parser.add_argument(
        "--bg", default="white", help="QR background color (default: white)"
    )
    args = parser.parse_args()

    logo_path = args.builtin_logo or args.logo
    if logo_path is None:
        parser.error("provide a logo path or use a built-in logo (--arXiv, --github)")

    if not 0.05 <= args.logo_ratio <= 0.35:
        parser.error(
            "--logo-ratio should be between 0.05 and 0.35 to keep QR scannable"
        )

    try:
        out = generate_qr_with_logo(
            url=args.url,
            logo_path=logo_path,
            output_path=args.output,
            box_size=args.box_size,
            border=args.border,
            logo_ratio=args.logo_ratio,
            fill_color=args.fill,
            back_color=args.bg,
        )
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"Failed to generate QR: {e}\n")
        return 1

    print(f"Saved QR code to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
