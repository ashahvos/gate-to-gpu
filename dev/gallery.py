#!/usr/bin/env python3
"""Render selected diagrams on a test page with the real stylesheet and screenshot each one.
usage: gallery.py name [name:{json args}] ... [--dark]"""
import asyncio
import importlib
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repository root
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "src"))
import dlib  # noqa: E402
for p in sorted(glob.glob(os.path.join(HERE, "src", "d[0-9]*.py"))):
    importlib.import_module(os.path.basename(p)[:-3])
import build  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402


async def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dark = "--dark" in sys.argv
    style = open(os.path.join(HERE, "src", "style.css"), encoding="utf-8").read()
    dk = ("@media (prefers-color-scheme: dark) {\n  :root:not([data-theme=\"light\"]) {" + build.DARK + "\n  }\n}\n:root[data-theme=\"dark\"] {" + build.DARK + "\n}")
    style = style.replace("/*DARK*/", dk)
    figs = []
    for a in args:
        if ":" in a:
            name, js = a.split(":", 1)
            kw = json.loads(js)
        else:
            name, kw = a, {}
        svg = dlib.REGISTRY[name](**kw)
        figs.append((name, dlib.figure(svg, name)))
    html = "<!doctype html><html><head><meta charset=utf-8><style>" + style + "</style></head><body><main style='max-width:900px;margin:0 auto;padding:16px'>" + \
        "".join(f'<div id="f{i}">{h}</div>' for i, (n, h) in enumerate(figs)) + "</main></body></html>"
    p = os.path.join(HERE, "out", "gallery.html")
    open(p, "w", encoding="utf-8").write(html)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 960, "height": 900}, color_scheme="dark" if dark else "light")
        await pg.goto("file://" + p)
        for i, (n, h) in enumerate(figs):
            await pg.locator(f"#f{i} figure").screenshot(path=os.path.join(HERE, "out", f"g_{n}{'_d' if dark else ''}.png"))
        await b.close()
    print("ok", [n for n, h in figs])


asyncio.run(main())
