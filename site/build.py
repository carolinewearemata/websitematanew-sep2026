#!/usr/bin/env python3
"""Monta a abertura (site/v3) do novo site da MATA em um arquivo único (preview/index.html).

Uso: python3 site/build.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V3 = ROOT / "site" / "v3"
ASSETS = ROOT / "site" / "assets"
THREE_CDN = "https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def fonts():
    faces = [("Stack Sans Headline", "stack-sans-headline"), ("Stack Sans Text", "stack-sans-text"), ("Stack Sans Notch", "stack-sans-notch")]
    css = [f'@font-face{{font-family:"{fam}";src:url("{data_uri(ASSETS / "fontes" / (f + ".woff2"), "font/woff2")}") format("woff2");font-weight:200 700;font-display:swap}}'
           for fam, f in faces]
    css.append(f':root{{--grad:url("{data_uri(ASSETS / "mata-gradiente.webp", "image/webp")}")}}')
    return "\n".join(css)


def logo():
    raw = (ASSETS / "logos" / "mata-logo-preto.svg").read_text()
    paths = "".join(f'<path d="{d}"/>' for d in re.findall(r'<path d="([^"]+)"', raw))
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    return f'<svg viewBox="{vb}" role="img" aria-label="MATA">{paths}</svg>'


def main():
    page = (V3 / "index.html").read_text()
    page = (page.replace("/*__FONTS__*/", fonts())
                .replace("__LOGO__", logo())
                .replace("__IMG_PILOTO__", data_uri(ASSETS / "mata-3d-piloto.webp", "image/webp"))
                .replace("__IMG_ACOPLAMENTO__", data_uri(ASSETS / "mata-3d-acoplamento.webp", "image/webp"))
                .replace("__THREE__", THREE_CDN)
                .replace("__IMG_GRAD__", data_uri(ASSETS / "mata-gradiente.webp", "image/webp"))
                .replace("/*__SCENE__*/", (V3 / "scene.js").read_text()))
    out = ROOT / "preview"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page)
    print(f"preview/index.html: {len(page) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
