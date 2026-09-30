#!/usr/bin/env python3
"""Render 1000x1500 Pinterest pins (and 1080x1920 video frames) for Mavilo Pet Co.

Usage:
    python3 factory/render_pins.py factory/queue/pins/2026-10-02/pins.json
    python3 factory/render_pins.py <pins.json> --only 03,14
    python3 factory/render_pins.py --frames cat-enrichment-guide 1,4,5,10 factory/queue/videos/2026-10-02/frames

Same pipeline as factory/render_mockups.py (whose helpers are imported here):
    1. PDF pages -> PNG with pymupdf.
    2. Each pin is a self-contained HTML page (inline CSS, base64 images).
    3. Headless Chromium screenshot at 1000x1586, cropped to 1000x1500 with Pillow.

pins.json is a list of objects. Fields used for rendering:
    file            output PNG name (written next to pins.json)
    layout          hook | checklist | tip | before-after | worksheet
    product_handle  key of render_mockups.PRODUCTS or the bundle handle
    headline        big text (hook / checklist title / tip text / worksheet title)
    sub             smaller line under the headline (optional)
    kicker          small pill text at the top (optional)
    items           list of strings (checklist layout)
    before, after   dicts {"label", "text"} (before-after layout)
    callout         text of the orange callout bubble (worksheet layout)
    preview_page    1-based PDF page to show (hook / tip / worksheet / after panel)
    preview_from    handle whose PDF supplies the preview (bundle only; it has no PDF)
    headline_size   px override for the big text
The other fields (title, description, alt_text, link, board, keywords) are Pinterest copy
and are ignored by this script.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_mockups import (  # noqa: E402
    BG, BLUE, BUNDLE, CHROME, FONT, GREEN, GREEN_DARK, INK, MUTED, ORANGE, PRODUCTS,
    PRODUCTS_DIR, check_icon, data_uri, esc, paw, render_pdf_page,
)

PIN_W, PIN_H = 1000, 1500
FRAME_W, FRAME_H = 1080, 1920
CHROME_PAD = 86  # headless window includes ~86px of chrome on some builds; we crop anyway

TITLES = {h: p["title"] for h, p in PRODUCTS.items()}
TITLES[BUNDLE["handle"]] = BUNDLE["title"]


# --------------------------------------------------------------------------
# Shared pieces
# --------------------------------------------------------------------------
def css(w: int, h: int) -> str:
    return f"""
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ width: {w}px; height: {h}px; overflow: hidden; }}
    body {{ background: {BG}; font-family: {FONT}; color: {INK}; position: relative;
            -webkit-font-smoothing: antialiased; }}
    .pill {{ display:inline-block; background:{ORANGE}; color:{GREEN_DARK}; font-weight:700;
             letter-spacing:2.5px; font-size:22px; padding:12px 26px; border-radius:999px;
             text-transform:uppercase; }}
    .pill.green {{ background:{GREEN}; color:#fff; }}
    .pill.blue {{ background:{BLUE}; color:#fff; }}
    .pill.light {{ background:rgba(255,255,255,.18); color:#fff; }}
    .shadow {{ box-shadow: 0 30px 70px rgba(47,111,94,0.25), 0 8px 20px rgba(0,0,0,0.10); }}
    .page {{ display:block; background:#fff; border-radius:12px; }}
    .footer {{ position:absolute; left:0; right:0; bottom:0; height:96px; background:{GREEN_DARK};
               display:flex; align-items:center; justify-content:space-between; padding:0 48px;
               color:#fff; font-weight:700; font-size:28px; letter-spacing:-0.3px; }}
    .footer .brand {{ display:flex; align-items:center; gap:14px; }}
    .footer .tag {{ background:{ORANGE}; color:{GREEN_DARK}; font-size:20px; letter-spacing:2px;
                    text-transform:uppercase; padding:10px 20px; border-radius:999px; }}
    .stripe {{ position:absolute; left:0; right:0; bottom:96px; height:14px; display:flex; }}
    .stripe i {{ flex:1; display:block; }}
    h1 {{ font-weight:700; letter-spacing:-1.5px; line-height:1.06; }}
    .fade {{ position:absolute; left:0; right:0; bottom:0; height:140px;
             background:linear-gradient(rgba(255,250,243,0), {BG}); }}
    """


def footer() -> str:
    return (
        f'<div class="stripe"><i style="background:{ORANGE}"></i>'
        f'<i style="background:{BLUE}"></i><i style="background:{GREEN}"></i></div>'
        f'<div class="footer"><div class="brand">{paw(ORANGE, 40)}Mavilo Pet Co.</div>'
        '<div class="tag">Printable PDF</div></div>'
    )


def wrap(body: str, w: int = PIN_W, h: int = PIN_H, extra_css: str = "") -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{css(w, h)}{extra_css}</style></head><body>{body}</body></html>"
    )


def page_png(handle: str, page_no: int, width_px: int = 1200) -> bytes:
    return render_pdf_page(PRODUCTS_DIR / f"{handle}.pdf", page_no, width_px)


def screenshot(html_str: str, out_png: Path, workdir: Path, w: int, h: int) -> None:
    html_path = workdir / (out_png.stem + ".html")
    html_path.write_text(html_str, encoding="utf-8")
    raw = workdir / (out_png.stem + ".raw.png")
    cmd = [
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--screenshot={raw}",
        f"--window-size={w},{h + CHROME_PAD}", f"file://{html_path}",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(raw).convert("RGB")
    if im.size != (w, h):
        im = im.crop((0, 0, w, h))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_png, optimize=True)
    assert Image.open(out_png).size == (w, h), out_png


# --------------------------------------------------------------------------
# Pin layouts
# --------------------------------------------------------------------------
def _src(p: dict) -> str:
    """PDF to take previews from (the bundle has no PDF of its own -> preview_from)."""
    return p.get("preview_from", p["product_handle"])


def _title_line(handle: str) -> str:
    return f'<div style="font-size:26px;font-weight:700;color:{MUTED};">From <span style="color:{GREEN}">{esc(TITLES[handle])}</span></div>'


def pin_hook(p: dict) -> str:
    """(i) Bold text hook on brand green, page preview peeking at the bottom."""
    size = p.get("headline_size", 92)
    prev = data_uri(page_png(_src(p), p.get("preview_page", 1)))
    kicker = p.get("kicker", "Printable guide")
    sub = p.get("sub", "")
    return wrap(f"""
    <div style="position:absolute;inset:0 0 auto 0;height:780px;background:{GREEN};padding:80px 72px 0;">
      {paw(BLUE, 220, "position:absolute;right:-30px;top:-40px;opacity:.35;transform:rotate(18deg)")}
      {paw(ORANGE, 120, "position:absolute;left:760px;top:560px;opacity:.35;transform:rotate(-14deg)")}
      <span class="pill">{esc(kicker)}</span>
      <h1 style="color:#fff;font-size:{size}px;margin-top:44px;max-width:860px;">{esc(p['headline'])}</h1>
      <div style="color:{ORANGE};font-size:36px;font-weight:700;margin-top:34px;max-width:820px;line-height:1.3;">{esc(sub)}</div>
    </div>
    <div style="position:absolute;top:780px;left:0;right:0;bottom:110px;overflow:hidden;">
      <img class="page shadow" src="{prev}" style="position:absolute;left:150px;top:44px;width:700px;">
      <div class="fade"></div>
    </div>
    <div style="position:absolute;right:56px;top:820px;background:{ORANGE};color:{GREEN_DARK};font-weight:700;
                font-size:24px;padding:14px 22px;border-radius:14px;transform:rotate(3deg);box-shadow:0 8px 20px rgba(0,0,0,.15);">Peek inside ↓</div>
    {footer()}
    """)


def pin_checklist(p: dict) -> str:
    """(ii) "X things inside" checklist with a small cover."""
    items = p["items"]
    size = p.get("headline_size", 74)
    n = len(items)
    item_size = 38 if n <= 6 else 34
    cover = data_uri(page_png(_src(p), 1, 700))
    rows = "".join(
        f'<li style="display:flex;align-items:flex-start;gap:20px;font-size:{item_size}px;font-weight:700;'
        f'line-height:1.25;color:{INK};">{check_icon(GREEN if i % 2 == 0 else ORANGE, 46)}<span style="flex:1;padding-top:2px;">{esc(t)}</span></li>'
        for i, t in enumerate(items)
    )
    return wrap(f"""
    <div style="position:absolute;left:0;right:0;top:0;height:22px;background:{GREEN};"></div>
    <div style="padding:76px 68px 0;">
      <span class="pill green">{esc(p.get('kicker', "What's inside"))}</span>
      <h1 style="font-size:{size}px;color:{GREEN_DARK};margin-top:34px;max-width:880px;">{esc(p['headline'])}</h1>
    </div>
    <ul style="list-style:none;position:absolute;left:68px;right:68px;top:{p.get('list_top', 420)}px;display:flex;flex-direction:column;gap:26px;">{rows}</ul>
    <div style="position:absolute;left:68px;right:68px;bottom:130px;display:flex;align-items:center;gap:28px;">
      <img class="page shadow" src="{cover}" style="width:150px;border-radius:8px;">
      <div>
        {_title_line(p['product_handle'])}
        <div style="font-size:30px;font-weight:700;color:{INK};margin-top:10px;">{esc(p.get('sub', 'Instant download • print at home'))}</div>
      </div>
    </div>
    {footer()}
    """)


def pin_tip(p: dict) -> str:
    """(iii) Tip / quote card with a page thumbnail."""
    size = p.get("headline_size", 78)
    prev = data_uri(page_png(_src(p), p.get("preview_page", 1), 900))
    return wrap(f"""
    <div style="position:absolute;inset:0;background:{BLUE};"></div>
    {paw("#fff", 260, "position:absolute;left:-60px;bottom:180px;opacity:.18;transform:rotate(-16deg)")}
    <div class="shadow" style="position:absolute;left:56px;right:56px;top:90px;background:{BG};border-radius:34px;padding:64px 60px 70px;">
      <span class="pill">{esc(p.get('kicker', 'Quick tip'))}</span>
      <div style="font-size:170px;line-height:.6;color:{ORANGE};font-weight:700;margin-top:70px;font-family:Georgia,serif;">“</div>
      <h1 style="font-size:{size}px;color:{GREEN_DARK};margin-top:0;">{esc(p['headline'])}</h1>
      <div style="font-size:36px;color:{MUTED};margin-top:40px;line-height:1.35;font-weight:700;">{esc(p.get('sub', ''))}</div>
      <div style="display:flex;gap:12px;margin-top:48px;">{check_icon(GREEN, 40)}<span style="font-size:28px;font-weight:700;color:{GREEN};padding-top:4px;">General education, not veterinary advice</span></div>
    </div>
    <div style="position:absolute;left:56px;right:56px;bottom:124px;height:150px;display:flex;align-items:center;gap:26px;color:#fff;">
      <img class="page shadow" src="{prev}" style="width:120px;border-radius:8px;">
      <div style="font-size:28px;font-weight:700;line-height:1.3;">More in the<br><span style="font-size:34px;">{esc(TITLES[p['product_handle']])}</span></div>
    </div>
    {footer()}
    """)


def pin_before_after(p: dict) -> str:
    """(iv) Before / after: chaos -> routine."""
    b, a = p["before"], p["after"]
    size = p.get("headline_size", 66)
    prev = data_uri(page_png(_src(p), p.get("preview_page", 1), 900))
    return wrap(f"""
    <div style="position:absolute;left:0;right:0;top:0;height:560px;background:#e9e2d6;padding:72px 68px 0;">
      <span class="pill" style="background:{MUTED};color:#fff;">{esc(b.get('label', 'Before'))}</span>
      <h1 style="font-size:{size}px;color:{INK};margin-top:36px;max-width:860px;line-height:1.1;opacity:.85;">{esc(b['text'])}</h1>
      <div style="position:absolute;right:70px;bottom:28px;font-size:34px;font-weight:700;color:{MUTED};letter-spacing:1px;">{esc(p.get('kicker', 'Day 1'))}</div>
    </div>
    <div style="position:absolute;left:0;right:0;top:560px;bottom:96px;background:{GREEN};padding:110px 68px 0;">
      <span class="pill">{esc(a.get('label', 'After'))}</span>
      <h1 style="font-size:{size}px;color:#fff;margin-top:36px;max-width:560px;">{esc(a['text'])}</h1>
      <div style="font-size:30px;font-weight:700;color:{ORANGE};margin-top:30px;max-width:540px;line-height:1.3;">{esc(p.get('sub', ''))}</div>
      <img class="page shadow" src="{prev}" style="position:absolute;right:50px;top:330px;width:320px;transform:rotate(6deg);">
    </div>
    <div style="position:absolute;left:0;right:0;top:500px;text-align:center;">
      <div class="shadow" style="display:inline-flex;align-items:center;justify-content:center;width:120px;height:120px;border-radius:50%;
           background:{ORANGE};color:{GREEN_DARK};font-size:70px;font-weight:700;">↓</div>
    </div>
    {footer()}
    """)


def pin_worksheet(p: dict) -> str:
    """(v) Big worksheet preview with a "Free-form fill-in" callout."""
    size = p.get("headline_size", 60)
    prev = data_uri(page_png(_src(p), p.get("preview_page", 1), 1500))
    return wrap(f"""
    <div style="padding:64px 68px 0;">
      <span class="pill blue">{esc(p.get('kicker', 'Printable worksheet'))}</span>
      <h1 style="font-size:{size}px;color:{GREEN_DARK};margin-top:28px;max-width:880px;">{esc(p['headline'])}</h1>
    </div>
    <div style="position:absolute;left:0;right:0;top:{p.get('preview_top', 400)}px;bottom:110px;overflow:hidden;">
      <img class="page shadow" src="{prev}" style="position:absolute;left:100px;top:40px;width:800px;">
      <div class="fade"></div>
    </div>
    <div class="shadow" style="position:absolute;right:40px;top:{p.get('callout_top', 470)}px;width:330px;background:{ORANGE};color:{GREEN_DARK};
         padding:26px 28px;border-radius:24px;font-size:30px;font-weight:700;line-height:1.25;transform:rotate(-3deg);">
      {esc(p.get('callout', 'Free-form fill-in — print as many copies as you need'))}
      <div style="position:absolute;left:40px;bottom:-22px;width:0;height:0;border-left:20px solid transparent;border-right:20px solid transparent;border-top:26px solid {ORANGE};"></div>
    </div>
    <div style="position:absolute;left:68px;bottom:122px;">{_title_line(p['product_handle'])}</div>
    {footer()}
    """)


LAYOUTS = {
    "hook": pin_hook,
    "checklist": pin_checklist,
    "tip": pin_tip,
    "before-after": pin_before_after,
    "worksheet": pin_worksheet,
}


# --------------------------------------------------------------------------
# Video frames (1080x1920)
# --------------------------------------------------------------------------
def frame_html(handle: str, page_no: int) -> str:
    prev = data_uri(page_png(handle, page_no, 1800))
    total = len(__import__("pymupdf").open(PRODUCTS_DIR / f"{handle}.pdf"))
    return wrap(f"""
    <div style="position:absolute;left:0;right:0;top:0;height:20px;background:{GREEN};"></div>
    <div style="position:absolute;left:70px;right:70px;top:70px;display:flex;justify-content:space-between;align-items:center;">
      <div style="display:flex;align-items:center;gap:16px;font-size:34px;font-weight:700;color:{GREEN};">{paw(ORANGE, 44)}Mavilo Pet Co.</div>
      <span class="pill" style="font-size:22px;">Page {page_no} of {total}</span>
    </div>
    <div style="position:absolute;left:70px;right:70px;top:150px;font-size:30px;font-weight:700;color:{MUTED};">{esc(TITLES[handle])}</div>
    <img class="page shadow" src="{prev}" style="position:absolute;left:70px;top:330px;width:940px;">
    {footer()}
    """, FRAME_W, FRAME_H)


# --------------------------------------------------------------------------
def render_pins(spec_path: Path, only: set[str] | None, workdir: Path) -> list[Path]:
    pins = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = spec_path.parent
    done = []
    for p in pins:
        if only and p["file"][:2] not in only:
            continue
        layout = LAYOUTS[p["layout"]]
        out = out_dir / p["file"]
        screenshot(layout(p), out, workdir, PIN_W, PIN_H)
        print(f"  {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}  {PIN_W}x{PIN_H}")
        done.append(out)
    return done


def render_frames(handle: str, pages: list[int], out_dir: Path, workdir: Path) -> list[Path]:
    done = []
    for n in pages:
        out = out_dir / f"{handle}-p{n:02d}.png"
        screenshot(frame_html(handle, n), out, workdir, FRAME_W, FRAME_H)
        print(f"  {out}  {FRAME_W}x{FRAME_H}")
        done.append(out)
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="pins.json to render (PNGs land next to it)")
    ap.add_argument("--only", help="comma-separated 2-digit pin numbers")
    ap.add_argument("--frames", nargs=3, metavar=("HANDLE", "PAGES", "OUT_DIR"),
                    help="render 1080x1920 frames instead: handle, comma-separated pages, output dir")
    ap.add_argument("--keep-html", action="store_true")
    args = ap.parse_args()
    workdir = Path(tempfile.mkdtemp(prefix="mavilo-pins-"))
    try:
        if args.frames:
            handle, pages, out_dir = args.frames
            render_frames(handle, [int(x) for x in pages.split(",")], Path(out_dir), workdir)
        elif args.spec:
            only = set(args.only.split(",")) if args.only else None
            render_pins(Path(args.spec), only, workdir)
        else:
            ap.error("give a pins.json or --frames")
    finally:
        if args.keep_html:
            print(f"intermediate files kept in {workdir}")
        else:
            shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
