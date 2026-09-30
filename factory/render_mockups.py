#!/usr/bin/env python3
"""Render 2000x2000 Etsy listing images for a Mavilo Pet Co. product.

Usage:
    python3 factory/render_mockups.py puppy-training-plan
    python3 factory/render_mockups.py --all
    python3 factory/render_mockups.py cat-enrichment-guide --only 02,05

Pipeline (no external services, no build step):
    1. Render PDF pages to PNG with pymupdf (cover + selected interior pages).
    2. Compose each listing image as a self-contained HTML page
       (inline CSS, base64 images) in a scratch dir.
    3. Screenshot it with headless Chromium at 2000x2086 and crop to 2000x2000
       with Pillow (headless Chromium's window-size includes ~86px of chrome
       on some builds; we always crop from the top-left to be safe).

Output: business/etsy/listings/<handle>/images/NN-name.png

Add a new product by appending an entry to PRODUCTS below.
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "business" / "products"
OUT_ROOT = ROOT / "business" / "etsy" / "listings"
CHROME = os.environ.get(
    "CHROME_BIN", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
)
SIZE = 2000
SHOT_H = 2086  # headless window height; we crop to SIZE anyway

# Brand
BG = "#fffaf3"
GREEN = "#2f6f5e"
GREEN_DARK = "#255a4c"
ORANGE = "#f2a65a"
BLUE = "#7aa7c7"
INK = "#1f2d2a"
MUTED = "#5c6b67"
FONT = '"Liberation Sans", "Helvetica Neue", Arial, "DejaVu Sans", sans-serif'

# --------------------------------------------------------------------------
# Product catalogue: what to show on the listing images.
# pages: list of (1-based page number, short caption)
# --------------------------------------------------------------------------
PRODUCTS: dict[str, dict] = {
    "puppy-training-plan": {
        "title": "The 30-Day Puppy Training Plan",
        "kicker": "Positive-reinforcement program",
        "tagline": "Short daily sessions that build a confident, polite puppy.",
        "pages_total": 19,
        "contents": [
            "Week-by-week skill plan (4 weeks)",
            "30-day daily plan table",
            "Potty & crate training schedules",
            "Socialization checklist + experience log",
            "Bite inhibition & nipping plan",
            "Troubleshooting FAQ",
            "Printable progress tracker & potty log",
        ],
        "stats": [("30", "days"), ("3–5 min", "sessions"), ("19", "pages")],
        "pages": [
            (14, "The 30-day daily plan"),
            (9, "Potty training schedule"),
            (17, "Printable progress tracker"),
            (12, "Socialization checklist"),
            (5, "Week 1: Foundations"),
        ],
    },
    "new-pet-starter-checklist": {
        "title": "New Pet Starter Checklist Kit",
        "kicker": "For dogs & cats",
        "tagline": "Shop smart, pet-proof your home and settle in with confidence.",
        "pages_total": 12,
        "contents": [
            "Dog shopping checklist",
            "Cat shopping checklist",
            "Room-by-room pet-proofing checklist",
            "First 24 hours, first week, first month plan",
            "First vet visit question list",
            "Budget planner worksheet",
            "Emergency contacts sheet",
        ],
        "stats": [("9", "checklists"), ("2", "species"), ("12", "pages")],
        "pages": [
            (5, "Dog shopping checklist"),
            (7, "Home pet-proofing, room by room"),
            (8, "First 24 hours to first month"),
            (10, "Budget planner worksheet"),
            (11, "Emergency contacts sheet"),
        ],
    },
    "pet-health-record-book": {
        "title": "Pet Health & Care Record Book",
        "kicker": "For dogs & cats",
        "tagline": "Vaccines, vet visits, meds and weight — all in one place.",
        "pages_total": 14,
        "contents": [
            "Pet profile with microchip & insurance",
            "Vaccination log",
            "Vet visit log",
            "Medication log",
            "Weight tracker & chart",
            "Parasite prevention log",
            "Grooming log, allergies & diet notes",
            "Emergency info cards + annual summary",
        ],
        "stats": [("11", "logs"), ("∞", "reprints"), ("14", "pages")],
        "pages": [
            (4, "Pet profile"),
            (5, "Vaccination log"),
            (6, "Vet visit log"),
            (7, "Medication log"),
            (8, "Weight tracker"),
        ],
    },
    "dog-grooming-guide": {
        "title": "At-Home Dog Grooming Guide",
        "kicker": "Step-by-step",
        "tagline": "Brush, bathe, trim and clean the calm, low-stress way.",
        "pages_total": 13,
        "contents": [
            "Coat types & brushing tools",
            "Brushing technique by coat",
            "Bathing step by step",
            "Nail trimming (finding the quick)",
            "Ear cleaning & teeth brushing",
            "Stress-free desensitization plan",
            "Grooming schedule by coat type",
            "Printable monthly grooming checklist",
        ],
        "stats": [("5", "coat types"), ("6", "routines"), ("13", "pages")],
        "pages": [
            (4, "Coat types & brushing tools"),
            (7, "Nail trimming step by step"),
            (10, "Making grooming stress-free"),
            (11, "Grooming schedule by coat type"),
            (12, "Printable monthly checklist"),
        ],
    },
    "cat-enrichment-guide": {
        "title": "Indoor Cat Enrichment & Play Guide",
        "kicker": "30 DIY ideas",
        "tagline": "Easy, low-cost ways to let your cat hunt, climb and play.",
        "pages_total": 12,
        "contents": [
            "30 DIY enrichment ideas",
            "Play styles & the prey sequence",
            "Vertical space & environment checklist",
            "Food puzzles & foraging",
            "Clicker training basics for cats",
            "Multi-cat tips & signs of boredom",
            "4-week enrichment calendar",
            "Printable play log",
        ],
        "stats": [("30", "ideas"), ("4", "week plan"), ("12", "pages")],
        "pages": [
            (5, "30 DIY enrichment ideas"),
            (4, "Play styles & the prey sequence"),
            (7, "Food puzzles & foraging"),
            (10, "4-week enrichment calendar"),
            (11, "Printable play log"),
        ],
    },
}

BUNDLE = {
    "handle": "complete-pet-parent-bundle",
    "title": "Complete Pet Parent Bundle",
    "kicker": "All 5 guides • Save $16",
    "tagline": "Train, care for and track your pet with one download.",
    "items": [  # (handle, price, best preview page, caption)
        ("puppy-training-plan", 14, 14, "Puppy plan — 30-day daily table"),
        ("new-pet-starter-checklist", 7, 10, "Starter kit — budget planner"),
        ("pet-health-record-book", 9, 5, "Record book — vaccination log"),
        ("dog-grooming-guide", 12, 11, "Grooming — schedule by coat type"),
        ("cat-enrichment-guide", 9, 10, "Cat guide — 4-week calendar"),
    ],
    "stats": [("5", "guides"), ("70", "pages"), ("$51", "value for $35")],
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def render_pdf_page(pdf: Path, page_no: int, width_px: int = 1400) -> bytes:
    """Render a 1-based page to PNG bytes at roughly width_px wide."""
    doc = pymupdf.open(pdf)
    page = doc[page_no - 1]
    zoom = width_px / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    return pix.tobytes("png")


def data_uri(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode()


def esc(s: str) -> str:
    return html.escape(s, quote=False)


PAW_SVG = (
    '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="{c}">'
    '<ellipse cx="50" cy="66" rx="24" ry="20"/>'
    '<circle cx="22" cy="42" r="11"/><circle cx="40" cy="26" r="11"/>'
    '<circle cx="60" cy="26" r="11"/><circle cx="78" cy="42" r="11"/></svg>'
)


def paw(color: str, size: int, extra_style: str = "") -> str:
    return (
        f'<div style="width:{size}px;height:{size}px;{extra_style}">'
        + PAW_SVG.format(c=color)
        + "</div>"
    )


def check_icon(color: str = GREEN, size: int = 64) -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="32" cy="32" r="30" fill="{color}"/>'
        '<path d="M18 33 L28 43 L47 22" stroke="#fff" stroke-width="7" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def base_css() -> str:
    return f"""
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ width: {SIZE}px; height: {SIZE}px; overflow: hidden; }}
    body {{ background: {BG}; font-family: {FONT}; color: {INK};
            position: relative; -webkit-font-smoothing: antialiased; }}
    .brand {{ position:absolute; display:flex; align-items:center; gap:18px;
              font-weight:700; font-size:40px; color:{GREEN}; letter-spacing:-0.5px; }}
    .brand small {{ display:block; font-size:19px; letter-spacing:4px; font-weight:700;
                    color:{ORANGE}; margin-top:6px; }}
    .pill {{ display:inline-block; background:{ORANGE}; color:{GREEN_DARK};
             font-weight:700; letter-spacing:3px; font-size:28px; padding:16px 34px;
             border-radius:999px; text-transform:uppercase; }}
    .pill.green {{ background:{GREEN}; color:#fff; }}
    .pill.blue {{ background:{BLUE}; color:#fff; }}
    .shadow {{ box-shadow: 0 40px 90px rgba(47,111,94,0.22), 0 10px 24px rgba(0,0,0,0.10); }}
    .stripe {{ position:absolute; left:0; right:0; bottom:0; height:22px; display:flex; }}
    .stripe i {{ flex:1; display:block; }}
    h1 {{ font-size:104px; line-height:1.05; letter-spacing:-2px; color:{GREEN_DARK}; }}
    """


def stripe() -> str:
    return (
        f'<div class="stripe"><i style="background:{ORANGE}"></i>'
        f'<i style="background:{BLUE}"></i><i style="background:{GREEN}"></i></div>'
    )


def brand(top: int = 90, left: int = 100) -> str:
    return (
        f'<div class="brand" style="top:{top}px;left:{left}px">'
        + paw(ORANGE, 62)
        + "<div>Mavilo Pet Co.<small>HAPPY PETS, PRACTICAL CARE</small></div></div>"
    )


def deco_paws() -> str:
    """Faint decorative paws in the corners."""
    return (
        paw(BLUE, 170, f"position:absolute;right:130px;top:120px;opacity:.28;transform:rotate(18deg)")
        + paw(ORANGE, 110, "position:absolute;right:340px;top:300px;opacity:.28;transform:rotate(-12deg)")
        + paw(GREEN, 130, "position:absolute;left:110px;bottom:120px;opacity:.16;transform:rotate(-20deg)")
    )


def wrap(body: str, extra_css: str = "") -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{base_css()}{extra_css}</style></head><body>{body}{stripe()}</body></html>"
    )


def screenshot(html_str: str, out_png: Path, workdir: Path) -> None:
    html_path = workdir / (out_png.stem + ".html")
    html_path.write_text(html_str, encoding="utf-8")
    raw = workdir / (out_png.stem + ".raw.png")
    cmd = [
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--screenshot={raw}",
        f"--window-size={SIZE},{SHOT_H}", f"file://{html_path}",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(raw).convert("RGB")
    if im.size != (SIZE, SIZE):
        im = im.crop((0, 0, SIZE, SIZE))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_png, optimize=True)
    assert Image.open(out_png).size == (SIZE, SIZE), out_png


# --------------------------------------------------------------------------
# Image templates
# --------------------------------------------------------------------------
def img_cover(cover_png: bytes, kicker: str) -> str:
    # Cover 1150x1489 (Letter ratio), centered, on brand bg with soft shadow.
    body = f"""
    {deco_paws()}
    <div style="position:absolute;top:70px;left:0;right:0;text-align:center;">
      <span class="pill">{esc(kicker)}</span>
    </div>
    <img class="shadow" src="{data_uri(cover_png)}"
         style="position:absolute;left:{(SIZE-1160)//2}px;top:190px;width:1160px;border-radius:14px;">
    <div style="position:absolute;bottom:60px;left:0;right:0;text-align:center;
                font-size:38px;font-weight:700;color:{GREEN};letter-spacing:1px;">
      Instant Download &nbsp;•&nbsp; Printable PDF &nbsp;•&nbsp; US Letter
    </div>
    """
    return wrap(body)


def img_whats_inside(p: dict) -> str:
    items = "".join(
        f'<li>{check_icon(GREEN if i % 3 == 0 else (ORANGE if i % 3 == 1 else BLUE), 66)}'
        f"<span>{esc(t)}</span></li>"
        for i, t in enumerate(p["contents"])
    )
    stats = "".join(
        f'<div class="stat" style="border-top-color:{c}"><b>{esc(v)}</b><span>{esc(l)}</span></div>'
        for (v, l), c in zip(p["stats"], [GREEN, ORANGE, BLUE])
    )
    css = f"""
    ul {{ list-style:none; position:absolute; left:120px; top:450px; width:1760px; height:1160px;
          display:flex; flex-direction:column; justify-content:space-evenly; }}
    li {{ display:flex; align-items:center; gap:36px; font-size:58px; font-weight:600;
          padding:10px 0 26px; border-bottom:3px dashed #e6dccb; }}
    li:last-child {{ border-bottom:none; }}
    li svg {{ flex:none; }}
    .stats {{ position:absolute; left:120px; right:120px; bottom:120px; display:flex; gap:40px; }}
    .stat {{ flex:1; background:#fff; border-radius:22px; border-top:14px solid; padding:30px 40px;
             box-shadow:0 12px 30px rgba(0,0,0,.06); }}
    .stat b {{ display:block; font-size:72px; color:{GREEN_DARK}; letter-spacing:-1px; }}
    .stat span {{ font-size:32px; color:{MUTED}; font-weight:600; }}
    """
    body = f"""
    {brand()}
    <div style="position:absolute;top:95px;right:100px;"><span class="pill">What's inside</span></div>
    <h1 style="position:absolute;left:120px;top:230px;width:1760px;font-size:96px;">{esc(p['title'])}</h1>
    <div style="position:absolute;left:120px;top:355px;font-size:40px;color:{MUTED};">{esc(p['tagline'])}</div>
    <ul>{items}</ul>
    <div class="stats">{stats}</div>
    <div style="position:absolute;bottom:52px;left:0;right:0;text-align:center;font-size:32px;
                font-weight:700;color:{GREEN};letter-spacing:1px;">
      Instant Download • Printable PDF • US Letter</div>
    """
    return wrap(body, css)


def img_page_preview(page_png: bytes, caption: str, page_no: int, total: int,
                     tilt_deg: float, label: str = "Inside look") -> str:
    w = 1180
    left = (SIZE - w) // 2
    body = f"""
    {brand()}
    <div style="position:absolute;top:95px;right:100px;"><span class="pill blue">{esc(label)}</span></div>
    {paw(ORANGE, 150, "position:absolute;left:120px;top:900px;opacity:.25;transform:rotate(-18deg)")}
    {paw(BLUE, 130, "position:absolute;right:130px;top:560px;opacity:.28;transform:rotate(14deg)")}
    {paw(GREEN, 110, "position:absolute;right:170px;bottom:330px;opacity:.16;transform:rotate(-8deg)")}
    <img class="shadow" src="{data_uri(page_png)}"
         style="position:absolute;left:{left}px;top:230px;width:{w}px;border-radius:12px;
                transform:rotate({tilt_deg}deg);transform-origin:center center;border:2px solid #eee4d4;">
    <div style="position:absolute;left:0;right:0;bottom:70px;text-align:center;">
      <span style="display:inline-block;background:{GREEN};color:#fff;font-size:40px;font-weight:700;
                   padding:22px 48px;border-radius:999px;box-shadow:0 12px 28px rgba(47,111,94,.28);">
        Page {page_no} of {total} &nbsp;—&nbsp; {esc(caption)}</span>
    </div>
    """
    return wrap(body)


def img_how_it_works() -> str:
    steps = [
        (ORANGE, "1", "Buy",
         "Check out on Etsy. No shipping, nothing to wait for."),
        (BLUE, "2", "Download instantly",
         "Your PDF appears under Purchases & Reviews, plus a download email."),
        (GREEN, "3", "Print or use on tablet",
         "Print at home on US Letter, or fill it in with any PDF annotation app."),
    ]
    cards = ""
    for c, n, t, d in steps:
        cards += f"""
        <div class="card">
          <div class="num" style="background:{c}">{n}</div>
          <h2>{esc(t)}</h2><p>{esc(d)}</p>
        </div>"""
    css = f"""
    .cards {{ position:absolute; left:120px; right:120px; top:560px; bottom:210px; display:flex; gap:44px; }}
    .card {{ flex:1; background:#fff; border-radius:34px; padding:60px 48px;
             box-shadow:0 20px 50px rgba(0,0,0,.07); text-align:center;
             display:flex; flex-direction:column; justify-content:center; }}
    .num {{ width:200px; height:200px; border-radius:50%; margin:0 auto 56px; color:#fff;
            font-size:110px; font-weight:800; line-height:200px; flex:none; }}
    h2 {{ font-size:64px; color:{GREEN_DARK}; line-height:1.1; margin-bottom:34px; letter-spacing:-1px; }}
    p {{ font-size:40px; line-height:1.4; color:{MUTED}; }}
    """
    body = f"""
    {brand()}
    <div style="position:absolute;top:95px;right:100px;"><span class="pill">Digital download</span></div>
    <h1 style="position:absolute;left:120px;top:260px;">How it works</h1>
    <div style="position:absolute;left:120px;top:400px;font-size:44px;color:{MUTED};">
      Three steps from checkout to your printed guide.</div>
    <div class="cards">{cards}</div>
    <div style="position:absolute;bottom:70px;left:0;right:0;text-align:center;font-size:34px;
                font-weight:700;color:{GREEN};">
      Instant Download • Printable PDF • US Letter (8.5 × 11 in) • Personal use</div>
    """
    return wrap(body, css)


def img_made_with_care() -> str:
    points = [
        (GREEN, "Original direction by a small pet-loving shop.",
         "Every guide starts from our own outline, structure and design system — not a template."),
        (ORANGE, "Designed and written with AI assistance, reviewed by a human.",
         "We use generative AI tools to help draft text and layouts; a person edits, fact-checks and approves every page before it is sold."),
        (BLUE, "Not veterinary advice.",
         "Educational content only. Always consult your veterinarian or a certified trainer for your own pet."),
    ]
    rows = ""
    for c, t, d in points:
        rows += f"""
        <div class="row">
          <div class="dot" style="background:{c}">{check_icon(c, 92)}</div>
          <div><h2>{esc(t)}</h2><p>{esc(d)}</p></div>
        </div>"""
    css = f"""
    .panel {{ position:absolute; left:120px; right:120px; top:540px; bottom:170px; background:#fff;
              border-radius:40px; padding:40px 90px; box-shadow:0 20px 50px rgba(0,0,0,.07);
              display:flex; flex-direction:column; justify-content:space-evenly; }}
    .row {{ display:flex; gap:48px; align-items:flex-start; padding:36px 0; border-bottom:3px dashed #e6dccb; }}
    .row:last-child {{ border-bottom:none; }}
    .dot {{ flex:none; width:100px; height:100px; border-radius:50%; overflow:hidden; margin-top:6px; }}
    .dot svg {{ width:100px; height:100px; }}
    h2 {{ font-size:58px; line-height:1.12; color:{GREEN_DARK}; margin-bottom:22px; letter-spacing:-0.5px; }}
    p {{ font-size:40px; line-height:1.4; color:{MUTED}; }}
    """
    body = f"""
    {brand()}
    <div style="position:absolute;top:95px;right:100px;"><span class="pill green">Made with care</span></div>
    <h1 style="position:absolute;left:120px;top:240px;">Honest about how<br>we make these</h1>
    <div class="panel">{rows}</div>
    <div style="position:absolute;bottom:60px;left:0;right:0;text-align:center;font-size:32px;
                color:{MUTED};font-weight:600;">
      Personal-use license • Reprint for your own household as often as you like</div>
    """
    return wrap(body, css)


def img_bundle_collage(covers: list[bytes]) -> str:
    # 5 covers fanned: back row 2, front row 3, overlapping.
    w = 640
    layout = [  # (left, top, rotate, z)
        (250, 430, -9, 1),
        (1110, 430, 9, 1),
        (90, 700, -5, 2),
        (1270, 700, 5, 2),
        (680, 620, 0, 3),
    ]
    imgs = ""
    for png, (l, t, r, z) in zip(covers, layout):
        imgs += (
            f'<img class="shadow" src="{data_uri(png)}" style="position:absolute;left:{l}px;top:{t}px;'
            f'width:{w}px;border-radius:12px;transform:rotate({r}deg);z-index:{z};border:3px solid #fff;">'
        )
    body = f"""
    {brand()}
    <div style="position:absolute;top:95px;right:100px;"><span class="pill">All 5 guides</span></div>
    <h1 style="position:absolute;left:0;right:0;top:230px;text-align:center;font-size:90px;">
      Complete Pet Parent Bundle</h1>
    <div style="position:absolute;left:0;right:0;top:350px;text-align:center;font-size:40px;color:{MUTED};">
      Train, care for and track your pet with one download.</div>
    {imgs}
    <div style="position:absolute;left:0;right:0;bottom:170px;text-align:center;z-index:5;">
      <span style="display:inline-block;background:{GREEN};color:#fff;font-size:46px;font-weight:700;
                   padding:26px 60px;border-radius:999px;box-shadow:0 12px 28px rgba(47,111,94,.28);">
        $51 value &nbsp;→&nbsp; $35 &nbsp;•&nbsp; Save $16</span>
    </div>
    <div style="position:absolute;bottom:70px;left:0;right:0;text-align:center;font-size:36px;
                font-weight:700;color:{GREEN};letter-spacing:1px;">
      Instant Download • 5 Printable PDFs • US Letter</div>
    """
    return wrap(body)


def img_bundle_inside() -> str:
    rows = ""
    for (h, price, _, _), c in zip(BUNDLE["items"], [GREEN, ORANGE, BLUE, GREEN, ORANGE]):
        p = PRODUCTS[h]
        rows += f"""
        <li>{check_icon(c, 70)}
            <div><b>{esc(p['title'])}</b><span>{esc(p['tagline'])}</span></div>
            <em>${price}</em></li>"""
    stats = "".join(
        f'<div class="stat" style="border-top-color:{c}"><b>{esc(v)}</b><span>{esc(l)}</span></div>'
        for (v, l), c in zip(BUNDLE["stats"], [GREEN, ORANGE, BLUE])
    )
    css = f"""
    ul {{ list-style:none; position:absolute; left:120px; top:400px; width:1760px; height:1210px;
          display:flex; flex-direction:column; justify-content:space-evenly; }}
    li {{ display:flex; align-items:center; gap:36px; padding:10px 0 30px; border-bottom:3px dashed #e6dccb; }}
    li:last-child {{ border-bottom:none; }}
    li svg {{ flex:none; }}
    li div {{ flex:1; }}
    li b {{ display:block; font-size:50px; color:{GREEN_DARK}; letter-spacing:-0.5px; }}
    li span {{ display:block; font-size:30px; color:{MUTED}; margin-top:6px; }}
    li em {{ font-style:normal; font-size:46px; font-weight:700; color:{MUTED}; text-decoration:line-through; }}
    .stats {{ position:absolute; left:120px; right:120px; bottom:120px; display:flex; gap:40px; }}
    .stat {{ flex:1; background:#fff; border-radius:22px; border-top:14px solid; padding:30px 40px;
             box-shadow:0 12px 30px rgba(0,0,0,.06); }}
    .stat b {{ display:block; font-size:72px; color:{GREEN_DARK}; }}
    .stat span {{ font-size:30px; color:{MUTED}; font-weight:600; }}
    """
    body = f"""
    {brand()}
    <div style="position:absolute;top:95px;right:100px;"><span class="pill">What's inside</span></div>
    <h1 style="position:absolute;left:120px;top:230px;font-size:96px;">Five guides, one download</h1>
    <ul>{rows}</ul>
    <div class="stats">{stats}</div>
    <div style="position:absolute;bottom:52px;left:0;right:0;text-align:center;font-size:32px;
                font-weight:700;color:{GREEN};letter-spacing:1px;">
      Instant Download • Printable PDF • US Letter</div>
    """
    return wrap(body, css)


# --------------------------------------------------------------------------
# Drivers
# --------------------------------------------------------------------------
def slug(s: str) -> str:
    import re
    return re.sub(r"-+", "-", "".join(ch if ch.isalnum() else "-" for ch in s.lower())).strip("-")[:32]


def render_product(handle: str, only: set[str] | None, workdir: Path) -> list[Path]:
    p = PRODUCTS[handle]
    pdf = PRODUCTS_DIR / f"{handle}.pdf"
    out_dir = OUT_ROOT / handle / "images"
    total = pymupdf.open(pdf).page_count
    jobs: list[tuple[str, str]] = []  # (filename, html)

    jobs.append(("01-cover.png", img_cover(render_pdf_page(pdf, 1, 1400), p["kicker"])))
    jobs.append(("02-whats-inside.png", img_whats_inside(p)))
    for i, (pg, cap) in enumerate(p["pages"]):
        tilt = (-2.5, 2.5, 0, -2, 2)[i % 5]
        fname = f"{i+3:02d}-page-{pg:02d}-{slug(cap)}.png"
        jobs.append((fname, img_page_preview(render_pdf_page(pdf, pg, 1400), cap, pg, total, tilt)))
    jobs.append(("08-how-it-works.png", img_how_it_works()))
    jobs.append(("09-made-with-care.png", img_made_with_care()))
    return _run_jobs(jobs, out_dir, only, workdir)


def render_bundle(only: set[str] | None, workdir: Path) -> list[Path]:
    out_dir = OUT_ROOT / BUNDLE["handle"] / "images"
    covers = [render_pdf_page(PRODUCTS_DIR / f"{h}.pdf", 1, 900) for h, *_ in BUNDLE["items"]]
    jobs = [("01-cover-collage.png", img_bundle_collage(covers)),
            ("02-whats-inside.png", img_bundle_inside())]
    for i, (h, _, pg, cap) in enumerate(BUNDLE["items"]):
        pdf = PRODUCTS_DIR / f"{h}.pdf"
        total = pymupdf.open(pdf).page_count
        tilt = (-2.5, 2.5, 0, -2, 2)[i % 5]
        fname = f"{i+3:02d}-{h}-page-{pg:02d}.png"
        jobs.append((fname, img_page_preview(render_pdf_page(pdf, pg, 1400), cap, pg, total, tilt,
                                             label=f"Guide {i+1} of 5")))
    jobs.append(("08-how-it-works.png", img_how_it_works()))
    jobs.append(("09-made-with-care.png", img_made_with_care()))
    return _run_jobs(jobs, out_dir, only, workdir)


def _run_jobs(jobs, out_dir: Path, only, workdir: Path) -> list[Path]:
    done = []
    for fname, html_str in jobs:
        if only and fname[:2] not in only:
            continue
        out = out_dir / fname
        screenshot(html_str, out, workdir)
        print(f"  wrote {out.relative_to(ROOT)}  {Image.open(out).size}")
        done.append(out)
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("handle", nargs="?", help="product handle (or complete-pet-parent-bundle)")
    ap.add_argument("--all", action="store_true", help="render every product and the bundle")
    ap.add_argument("--only", help="comma-separated image numbers to (re)render, e.g. 01,02")
    ap.add_argument("--keep-html", action="store_true", help="keep intermediate HTML in the scratch dir")
    args = ap.parse_args()
    if not args.handle and not args.all:
        ap.error("give a handle or --all")
    if not Path(CHROME).exists():
        sys.exit(f"Chromium not found at {CHROME}; set CHROME_BIN")
    only = set(args.only.split(",")) if args.only else None

    handles = list(PRODUCTS) + [BUNDLE["handle"]] if args.all else [args.handle]
    workdir = Path(tempfile.mkdtemp(prefix="mavilo-mockups-"))
    try:
        for h in handles:
            print(f"[{h}]")
            if h == BUNDLE["handle"]:
                render_bundle(only, workdir)
            elif h in PRODUCTS:
                render_product(h, only, workdir)
            else:
                sys.exit(f"unknown handle {h!r}; known: {', '.join(list(PRODUCTS) + [BUNDLE['handle']])}")
    finally:
        if args.keep_html:
            print(f"intermediate files kept in {workdir}")
        else:
            shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
