#!/usr/bin/env python3
"""Render a Mavilo Pet Co. guide and run QC on it.

Usage:
    python3 factory/build.py <handle> [--out-dir business/products] [--json factory/qc-reports/<handle>.json]

Input : business/products/<handle>.html
Output: business/products/<handle>.pdf          (headless Chromium print)
        business/products/<handle>-cover.png    (816x1056, first page at 96 dpi)
        QC report printed as JSON, score on the last line. Exit 1 if QC < 80.

Cover: Chromium's --screenshot loses ~86 px of the viewport height to browser chrome, so we
shoot at 816x1142 and crop the top 816x1056 with Pillow.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qc  # noqa: E402  (factory/qc.py)

COVER_W, COVER_H = 816, 1056
SHOT_H = COVER_H + 86


def render(html_path: Path, pdf_path: Path, cover_path: Path) -> None:
    uri = html_path.resolve().as_uri()
    base = [qc.CHROME, *qc.CHROME_FLAGS]
    r = subprocess.run([*base, f"--print-to-pdf={pdf_path}", uri], capture_output=True, text=True, timeout=180)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise SystemExit(f"PDF render failed:\n{(r.stderr or r.stdout)[-1200:]}")

    raw = cover_path.with_name(cover_path.stem + "-raw.png")
    r = subprocess.run([*base, f"--window-size={COVER_W},{SHOT_H}", "--hide-scrollbars",
                        f"--screenshot={raw}", uri], capture_output=True, text=True, timeout=180)
    if not raw.exists():
        raise SystemExit(f"Cover screenshot failed:\n{(r.stderr or r.stdout)[-1200:]}")
    from PIL import Image

    with Image.open(raw) as im:
        im = im.convert("RGB")
        if im.size != (COVER_W, COVER_H):
            im = im.crop((0, 0, COVER_W, min(COVER_H, im.height)))
            if im.height < COVER_H:  # pad if the shot came out short
                canvas = Image.new("RGB", (COVER_W, COVER_H), "#fffaf3")
                canvas.paste(im, (0, 0))
                im = canvas
        im.save(cover_path, optimize=True)
    raw.unlink(missing_ok=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("handle", help="product handle, e.g. puppy-training-plan (or a path to the .html)")
    ap.add_argument("--out-dir", default=None, help="where to write pdf/png (default: next to the HTML)")
    ap.add_argument("--json", dest="json_out", help="write the QC report JSON here")
    ap.add_argument("--skip-qc", action="store_true")
    args = ap.parse_args(argv)

    html_path = Path(args.handle)
    if html_path.suffix != ".html":
        html_path = Path("business/products") / f"{args.handle}.html"
    if not html_path.exists():
        print(f"not found: {html_path}", file=sys.stderr)
        return 2
    handle = html_path.stem
    out_dir = Path(args.out_dir) if args.out_dir else html_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{handle}.pdf"
    cover_path = out_dir / f"{handle}-cover.png"

    render(html_path, pdf_path, cover_path)
    print(f"pdf   : {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")
    print(f"cover : {cover_path} ({COVER_W}x{COVER_H})")
    if args.skip_qc:
        return 0

    report = qc.run_qc(html_path, pdf_path)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("handle", "score", "pass", "deductions", "notes")}, indent=2, ensure_ascii=False))
    print(f"pages : {report['checks']['render'].get('page_count')}")
    print(f"QC score: {report['score']} ({'PASS' if report['pass'] else 'FAIL'})")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
