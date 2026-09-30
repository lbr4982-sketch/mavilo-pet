#!/usr/bin/env python3
"""Quality control for a Mavilo Pet Co. printable guide (product HTML).

Usage:
    python3 factory/qc.py business/products/<handle>.html [--pdf existing.pdf] [--json out.json] [--quiet]

Prints a JSON report with a 0-100 score. Exit code 1 when the score is below 80
(or the HTML cannot be rendered), otherwise 0.

Checks
  a. render      : HTML -> PDF with headless Chromium, page count
  b. layout      : text blocks outside the page rect, near-empty "spill" pages
  c. forbidden   : dosing numbers, cure/guarantee claims, vet-approved, FDA
  d. required    : vet disclaimer, "consult your veterinarian", personal-use line, brand
  e. spelling    : small built-in typo list + doubled words ("the the")
  f. similarity  : Jaccard over word 5-grams vs. every other business/products/*.html
  g. sources     : >= 5 health sentences require a "Sources"/"References" section (small weight)

No product HTML is modified. The PDF is rendered into a temp dir unless --pdf is given.
"""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

CHROME = os.environ.get("MAVILO_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
CHROME_FLAGS = ["--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer"]
PASS_SCORE = 80

# ---------------------------------------------------------------- rules ----
FORBIDDEN = [
    # (label, compiled regex)
    ("mg/kg dosing", re.compile(r"\bmg\s*/\s*kg\b|\bmg\s+per\s+(kg|kilogram|pound|lb)\b", re.I)),
    ("dosage number with unit", re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ml|mL|cc|IU|units?)\b(?!\s*of\s+(?:water|shampoo))", re.I)),
    ("'cure'/'cures'", re.compile(r"\bcures?\b", re.I)),
    ("'treat your pet's'", re.compile(r"\btreat\s+your\s+(?:pet|dog|cat|puppy|kitten)['’]s\b", re.I)),
    ("'guaranteed'", re.compile(r"\bguarantee[ds]?\b", re.I)),
    ("'vet-approved'", re.compile(r"\bvet[\s-]*approved\b", re.I)),
    ("'veterinarian approved'", re.compile(r"\bveterinarian[\s-]*approved\b", re.I)),
    ("'FDA'", re.compile(r"\bFDA\b")),
]

REQUIRED = [
    ("vet disclaimer", re.compile(r"not veterinary advice|not a substitute for veterinary", re.I)),
    ("consult your veterinarian", re.compile(r"consult your veterinarian", re.I)),
    ("personal-use license", re.compile(r"for personal use only", re.I)),
    ("brand name", re.compile(r"Mavilo Pet Co\.")),
]

TYPOS = {
    "teh": "the", "recieve": "receive", "seperate": "separate", "occured": "occurred",
    "definately": "definitely", "accomodate": "accommodate", "untill": "until", "wich": "which",
    "alot": "a lot", "becuase": "because", "thier": "their", "occassion": "occasion",
    "neccessary": "necessary", "adress": "address", "begining": "beginning", "beleive": "believe",
    "calender": "calendar", "commited": "committed", "enviroment": "environment",
    "exercize": "exercise", "freind": "friend", "happend": "happened", "immediatly": "immediately",
    "independant": "independent", "knowlege": "knowledge", "maintainance": "maintenance",
    "noticable": "noticeable", "occurence": "occurrence", "posession": "possession",
    "prefered": "preferred", "reccomend": "recommend", "recomend": "recommend", "refered": "referred",
    "relevent": "relevant", "succesful": "successful", "tommorow": "tomorrow", "truely": "truly",
    "unfortunatly": "unfortunately", "vetinarian": "veterinarian", "veterinarion": "veterinarian",
    "vetrinarian": "veterinarian", "vaccinaton": "vaccination", "vaccinatons": "vaccinations",
    "diarrhoea": "diarrhea", "diarhea": "diarrhea", "dehydrated": None, "puppys": "puppies",
    "kittys": "kitties", "groomming": "grooming", "shedding": None, "itchyness": "itchiness",
    "aggresive": "aggressive", "agressive": "aggressive", "behaviour": "behavior (US spelling)",
    "colour": "color (US spelling)", "favourite": "favorite (US spelling)", "litre": "liter (US spelling)",
    "publically": "publicly", "existance": "existence", "arguement": "argument", "wierd": "weird",
    "acheive": "achieve", "acheived": "achieved", "recieved": "received", "seperately": "separately",
    "usefull": "useful", "harmfull": "harmful", "carefull": "careful", "playfull": "playful",
}
TYPOS = {k: v for k, v in TYPOS.items() if v is not None}

DOUBLED_OK = {"had", "that", "is", "do", "no", "very", "bye", "go", "so", "on"}

HEALTH_KEYWORDS = re.compile(
    r"\b(vaccin\w*|medicat\w*|symptom\w*|poison\w*|toxic\w*|weight|parasit\w*)\b", re.I)
SOURCES_HEADING = re.compile(r"^\s*(sources?|references?|further reading|where this comes from)\b", re.I)


# ------------------------------------------------------------ html text ----
class _Text(HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "tr",
             "td", "th", "br", "ul", "ol", "table", "header", "footer", "blockquote", "dd", "dt", "figcaption"}
    SKIP = {"style", "script", "head", "title"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self.buf: list[str] = []
        self.headings: list[str] = []
        self._skip = 0
        self._heading: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        self.buf.append(" ")  # every tag boundary separates words (<span>Basics</span><span>Yes)
        if tag in self.BLOCK:
            self._flush()
        if tag in {"h1", "h2", "h3", "h4"}:
            self._heading = []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        self.buf.append(" ")
        if tag in {"h1", "h2", "h3", "h4"} and self._heading is not None:
            self.headings.append(" ".join("".join(self._heading).split()))
            self._heading = None
        if tag in self.BLOCK:
            self._flush()

    def handle_data(self, data):
        if self._skip:
            return
        self.buf.append(data)
        if self._heading is not None:
            self._heading.append(data)

    def _flush(self):
        text = " ".join("".join(self.buf).split())
        if text:
            self.lines.append(text)
        self.buf = []

    def close(self):
        super().close()
        self._flush()


def extract_text(html_src: str) -> tuple[list[str], list[str]]:
    p = _Text()
    p.feed(html_src)
    p.close()
    return p.lines, p.headings


def sentences(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        out.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if s.strip())
    return out


def word_ngrams(text: str, n: int = 5) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


# --------------------------------------------------------------- render ----
def render_pdf(html_path: Path, out_pdf: Path) -> tuple[bool, str]:
    if not Path(CHROME).exists():
        return False, f"chrome not found at {CHROME} (set MAVILO_CHROME)"
    cmd = [CHROME, *CHROME_FLAGS, f"--print-to-pdf={out_pdf}", html_path.resolve().as_uri()]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, "chrome timed out after 120s"
    if not out_pdf.exists() or out_pdf.stat().st_size == 0:
        return False, (proc.stderr or proc.stdout)[-800:]
    return True, ""


def analyze_pdf(pdf_path: Path) -> dict:
    try:
        import pymupdf as fitz  # >= 1.24
    except ImportError:  # pragma: no cover - older installs
        import fitz  # noqa: F401  (legacy name; prints a deprecation notice on stdout)

    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        rect = page.rect
        blocks = page.get_text("blocks")
        overflow = []
        for b in blocks:
            x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
            if not str(txt).strip():
                continue
            if x0 < rect.x0 - 2 or y0 < rect.y0 - 2 or x1 > rect.x1 + 2 or y1 > rect.y1 + 2:
                overflow.append({"bbox": [round(x0), round(y0), round(x1), round(y1)],
                                 "text": " ".join(str(txt).split())[:80]})
        words = len(page.get_text().split())
        pages.append({"page": i + 1, "words": words, "overflow_blocks": overflow})
    n = len(doc)
    all_text = "\n".join(page.get_text() for page in doc)
    spill = [p["page"] for p in pages if p["words"] < 40 and p["page"] not in (1, n)]
    blank = [p["page"] for p in pages if p["words"] == 0]
    return {
        "page_count": n,
        "page_size_pt": [round(doc[0].rect.width), round(doc[0].rect.height)] if n else None,
        "overflow_pages": [p["page"] for p in pages if p["overflow_blocks"]],
        "overflow_detail": [{"page": p["page"], "blocks": p["overflow_blocks"]} for p in pages if p["overflow_blocks"]],
        "spill_pages": spill,
        "blank_pages": blank,
        "words_per_page": [p["words"] for p in pages],
        "_text": all_text,
    }


# ----------------------------------------------------------------- main ----
def run_qc(html_path: Path, pdf_path: Path | None = None, keep_pdf: bool = False) -> dict:
    src = html_path.read_text(encoding="utf-8", errors="replace")
    lines, headings = extract_text(src)
    full_text = "\n".join(lines)
    sents = sentences(lines)
    word_count = len(re.findall(r"\w+", full_text))

    report: dict = {"file": str(html_path), "handle": html_path.stem, "word_count": word_count,
                    "checks": {}, "deductions": [], "notes": []}
    checks = report["checks"]

    def deduct(points: int, reason: str):
        report["deductions"].append({"points": points, "reason": reason})

    # a. render + b. layout --------------------------------------------------
    tmpdir = None
    if pdf_path is None:
        tmpdir = tempfile.TemporaryDirectory(prefix="mavilo-qc-")
        pdf_path = Path(tmpdir.name) / f"{html_path.stem}.pdf"
        ok, err = render_pdf(html_path, pdf_path)
    else:
        ok, err = pdf_path.exists(), "" if pdf_path.exists() else f"{pdf_path} missing"
    checks["render"] = {"ok": ok, "pdf": str(pdf_path) if ok else None, "error": err or None}
    if ok:
        layout = analyze_pdf(pdf_path)
        checks["render"]["page_count"] = layout["page_count"]
        # Chromium CLIPS text that runs past the printable area instead of spilling it, so the
        # most reliable overflow signal is HTML words that never reach the PDF.
        pdf_text = layout.pop("_text").lower()
        html_counts = Counter(re.findall(r"[a-z]{3,}", full_text.lower()))
        pdf_counts = Counter(re.findall(r"[a-z]{3,}", pdf_text))
        collapsed = re.sub(r"\s+", "", pdf_text)  # letter-spaced cover text extracts as "H A P P Y"
        lost: dict[str, int] = {}
        for word, n_html in html_counts.items():
            deficit = n_html - pdf_counts.get(word, 0)
            if deficit <= 0:
                continue
            if collapsed.count(word) >= n_html:
                continue  # present, just letter-spaced (cover eyebrows extract as "H A P P Y")
            lost[word] = deficit
        total_html = sum(html_counts.values())
        lost_total = sum(lost.values())
        lost_ratio = lost_total / total_html if total_html else 0.0
        layout["lost_words"] = {"count": lost_total, "ratio": round(lost_ratio, 4),
                                "samples": sorted(lost, key=lost.get, reverse=True)[:15]}
        checks["layout"] = layout
        if lost_ratio > 0.01:
            deduct(min(30, 10 + int(lost_ratio * 200)),
                   f"{len(lost)} HTML words missing from PDF ({lost_ratio:.1%}) - text clipped/overflowing")
        if layout["overflow_pages"]:
            deduct(min(30, 10 * len(layout["overflow_pages"])),
                   f"text blocks outside page rect on pages {layout['overflow_pages']}")
        if layout["spill_pages"]:
            deduct(min(24, 8 * len(layout["spill_pages"])),
                   f"near-empty pages (<40 words, likely overflow spill) {layout['spill_pages']}")
        if layout["blank_pages"]:
            deduct(min(20, 10 * len(layout["blank_pages"])), f"blank pages {layout['blank_pages']}")
        if layout["page_count"] < 2:
            deduct(20, "PDF has fewer than 2 pages")
    else:
        deduct(100, f"render failed: {err}")
        checks["layout"] = None
    if tmpdir and not keep_pdf:
        tmpdir.cleanup()
        checks["render"]["pdf"] = None

    # c. forbidden -----------------------------------------------------------
    hits = []
    for label, rx in FORBIDDEN:
        for s in sents:
            m = rx.search(s)
            if m:
                hits.append({"rule": label, "match": m.group(0), "sentence": s[:160]})
    checks["forbidden"] = {"ok": not hits, "hits": hits}
    if hits:
        deduct(min(45, 15 * len(hits)), f"{len(hits)} forbidden phrase(s): " +
               ", ".join(sorted({h['rule'] for h in hits})))

    # d. required ------------------------------------------------------------
    missing = [label for label, rx in REQUIRED if not rx.search(full_text)]
    checks["required"] = {"ok": not missing, "missing": missing,
                          "present": [label for label, _ in REQUIRED if label not in missing]}
    for label in missing:
        deduct(15, f"required phrase missing: {label}")

    # e. spelling ------------------------------------------------------------
    typo_hits = []
    for w in re.findall(r"[A-Za-z']+", full_text):
        lw = w.lower().strip("'")
        if lw in TYPOS:
            typo_hits.append({"word": w, "suggest": TYPOS[lw]})
    doubled = []
    for line in lines:
        for m in re.finditer(r"\b([A-Za-z]+)\s+\1\b", line, re.I):
            if m.group(1).lower() not in DOUBLED_OK:
                doubled.append({"words": m.group(0), "context": line[max(0, m.start() - 30):m.end() + 30]})
    checks["spelling"] = {"ok": not typo_hits and not doubled, "typos": typo_hits, "doubled_words": doubled}
    if typo_hits:
        deduct(min(10, 2 * len(typo_hits)), f"{len(typo_hits)} likely typo(s)")
    if doubled:
        deduct(min(5, len(doubled)), f"{len(doubled)} doubled word(s)")

    # f. similarity ----------------------------------------------------------
    mine = word_ngrams(full_text)
    sims = []
    for other in sorted(html_path.parent.glob("*.html")):
        if other.resolve() == html_path.resolve():
            continue
        o_lines, _ = extract_text(other.read_text(encoding="utf-8", errors="replace"))
        theirs = word_ngrams("\n".join(o_lines))
        union = len(mine | theirs)
        j = len(mine & theirs) / union if union else 0.0
        sims.append({"file": other.name, "jaccard_5gram": round(j, 4)})
    too_close = [s for s in sims if s["jaccard_5gram"] >= 0.6]
    checks["similarity"] = {"ok": not too_close, "threshold": 0.6, "compared": sims,
                            "max": max((s["jaccard_5gram"] for s in sims), default=0.0)}
    if too_close:
        deduct(30, "near-duplicate of " + ", ".join(s["file"] for s in too_close))

    # g. health claims need a Sources section --------------------------------
    health_sents = [s for s in sents if HEALTH_KEYWORDS.search(s)]
    has_sources = any(SOURCES_HEADING.search(h) for h in headings) or bool(
        re.search(r"^\s*(sources|references)\s*:?\s*$", full_text, re.I | re.M))
    needs = len(health_sents) >= 5
    checks["sources"] = {"ok": (not needs) or has_sources, "health_sentences": len(health_sents),
                         "sources_section_found": has_sources, "required": needs,
                         "samples": [s[:140] for s in health_sents[:5]]}
    if needs and not has_sources:
        deduct(5, f"{len(health_sents)} health sentences but no Sources/References section (low weight; "
                  "existing guides predate this rule)")
        report["notes"].append("Add a short 'Sources' section (AVMA/AAHA/ASPCA URLs) for new guides; "
                               "the review Routine verifies health sentences against them.")

    score = max(0, 100 - sum(d["points"] for d in report["deductions"]))
    report["score"] = score
    report["pass"] = score >= PASS_SCORE and checks["render"]["ok"]
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", help="business/products/<handle>.html")
    ap.add_argument("--pdf", help="use this already-rendered PDF instead of rendering")
    ap.add_argument("--json", dest="json_out", help="also write the report to this path")
    ap.add_argument("--quiet", action="store_true", help="print only 'handle score PASS/FAIL'")
    args = ap.parse_args(argv)

    html_path = Path(args.html)
    if not html_path.exists():
        print(json.dumps({"error": f"{html_path} not found"}))
        return 1
    report = run_qc(html_path, Path(args.pdf) if args.pdf else None)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.quiet:
        print(f"{report['handle']} {report['score']} {'PASS' if report['pass'] else 'FAIL'}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
