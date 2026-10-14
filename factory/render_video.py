#!/usr/bin/env python3
"""Render a faceless short-form video (1080x1920 MP4) from PDF-page frames + captions.

Usage:
  python3 factory/render_video.py SPEC.json OUT.mp4

SPEC.json:
{
  "slides": [
    {"pdf": "business/products/cat-enrichment-guide.pdf", "page": 1,
     "caption": "Your indoor cat isn't lazy. They're bored.", "seconds": 3, "zoom": 1.06,
     "label": "MYTH", "shift": 0},
    {"image": "path/to/any.png", "caption": "...", "seconds": 5},
    ...
  ],
  "fps": 30
}

Each slide is composed as an HTML page (brand colors, big caption) and screenshotted with
headless Chromium at 1080x1920, then ffmpeg applies a slow zoom and concatenates everything
into one H.264 MP4 with silent AAC audio (platforms prefer a stereo track). No external deps
beyond Pillow, imageio-ffmpeg and the bundled Chromium.
"""
import base64, json, os, subprocess, sys, tempfile
from PIL import Image

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
W, H = 1080, 1920
BRAND = {"green": "#2f6f5e", "orange": "#f2a65a", "blue": "#7aa7c7", "cream": "#fffaf3", "text": "#22312c"}


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def page_png(pdf, page, tmp):
    """Render one PDF page (1-based) to a PNG at ~2x and return its path."""
    import pymupdf
    doc = pymupdf.open(pdf)
    pix = doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2), alpha=False)
    out = os.path.join(tmp, f"{os.path.basename(pdf)}-p{page:02d}.png")
    pix.save(out)
    return out


SLIDE_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:{green};font-family:"Liberation Sans",Arial,sans-serif}}
.top{{position:absolute;left:0;right:0;top:0;height:640px;background:{green}}}
.lab{{position:absolute;left:70px;top:96px;background:{orange};color:{text};font-weight:800;font-size:30px;letter-spacing:3px;padding:12px 22px;border-radius:999px}}
.cap{{position:absolute;left:70px;right:70px;top:190px;color:{cream};font-weight:800;font-size:{fs}px;line-height:1.1;letter-spacing:-1px}}
.card{{position:absolute;left:90px;right:90px;top:620px;bottom:150px;background:#fff;border-radius:28px;overflow:hidden;box-shadow:0 30px 60px rgba(0,0,0,.35)}}
.card img{{width:100%;display:block;transform:translateY({shift}px)}}
.fade{{position:absolute;left:90px;right:90px;bottom:150px;height:220px;background:linear-gradient(0deg,{green} 10%,rgba(47,111,94,0));}}
.brand{{position:absolute;left:70px;bottom:52px;color:{cream};font-weight:800;font-size:34px;display:flex;align-items:center;gap:14px}}
.pill{{position:absolute;right:70px;bottom:60px;background:{orange};color:{text};font-weight:800;font-size:26px;letter-spacing:2px;padding:10px 20px;border-radius:999px}}
.paw{{position:absolute;right:60px;top:70px;opacity:.35}}
</style></head><body>
<div class="top"></div>
<svg class="paw" width="150" height="150" viewBox="0 0 100 100" style="transform:rotate(18deg)"><g fill="{orange}"><ellipse cx="50" cy="66" rx="22" ry="19"/><ellipse cx="22" cy="40" rx="9" ry="12" transform="rotate(-20 22 40)"/><ellipse cx="39" cy="23" rx="9" ry="12" transform="rotate(-6 39 23)"/><ellipse cx="61" cy="23" rx="9" ry="12" transform="rotate(6 61 23)"/><ellipse cx="78" cy="40" rx="9" ry="12" transform="rotate(20 78 40)"/></g></svg>
{label}
<div class="cap">{caption}</div>
<div class="card"><img src="{img}"></div>
<div class="fade"></div>
<div class="brand"><svg width="44" height="44" viewBox="0 0 100 100" style="transform:rotate(12deg)"><g fill="{orange}"><ellipse cx="50" cy="66" rx="22" ry="19"/><ellipse cx="22" cy="40" rx="9" ry="12" transform="rotate(-20 22 40)"/><ellipse cx="39" cy="23" rx="9" ry="12" transform="rotate(-6 39 23)"/><ellipse cx="61" cy="23" rx="9" ry="12" transform="rotate(6 61 23)"/><ellipse cx="78" cy="40" rx="9" ry="12" transform="rotate(20 78 40)"/></g></svg>Mavilo Pet Co.</div>
<div class="pill">PRINTABLE PDF</div>
</body></html>"""


def render_slide(slide, out_png, tmp):
    cap = slide["caption"]
    fs = 96 if len(cap) <= 36 else 80 if len(cap) <= 52 else 66
    label = f'<div class="lab">{slide["label"]}</div>' if slide.get("label") else ""
    img = page_png(slide["pdf"], slide["page"], tmp) if "pdf" in slide else slide["image"]
    html = SLIDE_HTML.format(w=W, h=H, img=b64(img), fs=fs, caption=cap, label=label,
                             shift=-int(slide.get("shift", 0)), **BRAND)
    hp = os.path.join(tmp, os.path.basename(out_png) + ".html")
    open(hp, "w").write(html)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--screenshot={out_png}", f"--window-size={W},{H + 86}", "file://" + hp],
                   check=True, capture_output=True)
    im = Image.open(out_png)
    if im.size != (W, H):
        im.crop((0, 0, W, H)).save(out_png)


def main(spec_path, out_mp4):
    spec = json.load(open(spec_path))
    fps = spec.get("fps", 30)
    tmp = tempfile.mkdtemp(prefix="video-")
    parts = []
    for i, s in enumerate(spec["slides"]):
        png = os.path.join(tmp, f"slide{i:02d}.png")
        render_slide(s, png, tmp)
        frames = int(round(s["seconds"] * fps))
        zoom = s.get("zoom", 1.06)
        part = os.path.join(tmp, f"part{i:02d}.mp4")
        # slow push-in: zoom from 1.0 to `zoom` over the slide, centred
        vf = (f"scale={W*2}:{H*2},zoompan=z='1+({zoom}-1)*on/{frames}':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps},format=yuv420p")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-vf", vf,
                        "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "18", part],
                       check=True)
        parts.append(part)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    total = sum(s["seconds"] for s in spec["slides"])
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-t", str(total), "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-shortest",
                    "-movflags", "+faststart", out_mp4], check=True)
    print(f"wrote {out_mp4} ({total}s, {len(parts)} slides)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
