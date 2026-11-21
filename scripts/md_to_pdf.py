"""Convierte documentos Markdown a PDF (usando Chrome headless).

Uso:
    python scripts/md_to_pdf.py PROTOCOLO.md pdf/PROTOCOLO.pdf
    python scripts/md_to_pdf.py PROPUESTA_INVESTIGACION_EN.md pdf/PROPUESTA_INVESTIGACION_EN.pdf
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import markdown  # noqa: E402

CSS = """
body { font-family: 'DejaVu Serif', Georgia, serif; font-size: 11pt;
       line-height: 1.5; color: #1a1a1a; max-width: 45em; margin: 2em auto;
       padding: 0 1.5em; }
h1 { font-size: 1.6em; border-bottom: 2px solid #2c3e50; padding-bottom: 0.3em; }
h2 { font-size: 1.25em; color: #2c3e50; margin-top: 1.4em; }
h3 { font-size: 1.05em; color: #34495e; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 0.9em;
       background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 3px; }
pre { background: #f7f7f7; padding: 0.8em; border-radius: 5px; overflow-x: auto; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; }
th, td { border: 1px solid #ccc; padding: 0.45em 0.6em; text-align: left; }
th { background: #2c3e50; color: white; }
tr:nth-child(even) td { background: #f9f9f9; }
blockquote { border-left: 4px solid #2c3e50; margin: 1em 0; padding: 0.3em 1em;
             background: #f0f4f8; color: #333; }
hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
ul, ol { padding-left: 1.5em; }
a { color: #2c3e50; text-decoration: none; }
"""


def md_to_html(text: str) -> str:
    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists", "toc"]
    )
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<style>{CSS}</style></head>
<body>{body}</body></html>"""


def html_to_pdf(html_path: str, pdf_path: str) -> None:
    subprocess.run(
        [
            "google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
            f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer",
            f"file://{html_path}",
        ],
        check=True, capture_output=True,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Markdown a PDF")
    p.add_argument("input", help="archivo .md de entrada")
    p.add_argument("output", help="archivo .pdf de salida")
    args = p.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    html = md_to_html(text)

    with tempfile.NamedTemporaryFile(
        suffix=".html", mode="w", encoding="utf-8", delete=False
    ) as fh:
        fh.write(html)
        html_path = fh.name

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    try:
        html_to_pdf(html_path, os.path.abspath(args.output))
    finally:
        os.unlink(html_path)

    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
