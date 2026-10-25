#!/usr/bin/env python3
"""Preview helper: wrap the page like the artifact host does, then screenshot / check it with Playwright.

usage: shot.py [--full] [--dark] [--phone] [--anchor ID] [--clip Y H] [--out NAME] [--check]
"""
import argparse
import asyncio
import os

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repository root
SKEL = ('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}'
        'img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>')


def wrap():
    src = open(os.path.join(HERE, "out", "gate-to-gpu.html"), encoding="utf-8").read()
    p = os.path.join(HERE, "out", "preview.html")
    open(p, "w", encoding="utf-8").write(SKEL + src + "</body></html>")
    return p


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dark", action="store_true")
    ap.add_argument("--phone", action="store_true")
    ap.add_argument("--anchor", default=None)
    ap.add_argument("--clip", nargs=2, type=int, default=None)
    ap.add_argument("--h", type=int, default=900)
    ap.add_argument("--out", default="shot")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--sel", default=None, help="screenshot a single element (CSS selector)")
    ap.add_argument("--nth", type=int, default=0)
    a = ap.parse_args()
    p = wrap()
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        vw = 400 if a.phone else 1280
        ctx = await b.new_context(viewport={"width": vw, "height": a.h}, color_scheme="dark" if a.dark else "light", device_scale_factor=1, reduced_motion="reduce")
        page = await ctx.new_page()
        errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
        await page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        await page.route("**/fonts.gstatic.com/**", lambda r: r.abort())
        await page.goto("file://" + p)
        await page.wait_for_timeout(400)
        if a.anchor:
            await page.evaluate(f"document.getElementById('{a.anchor}').scrollIntoView()")
            await page.wait_for_timeout(300)
        out = os.path.join(HERE, "out", a.out + ".png")
        if a.sel:
            el = page.locator(a.sel).nth(a.nth)
            await el.scroll_into_view_if_needed()
            await el.screenshot(path=out)
        elif a.clip:
            await page.screenshot(path=out, full_page=True, clip={"x": 0, "y": a.clip[0], "width": vw, "height": a.clip[1]})
        else:
            await page.screenshot(path=out, full_page=a.full)
        if a.check:
            info = await page.evaluate("""() => {
              const de = document.documentElement;
              const wide = [];
              document.querySelectorAll('main *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.right > window.innerWidth + 1 && !el.closest('.scroll, .tbl, pre, .wave, .ws, .eq, .widget .tbl, #cm-svg, #ll-w')) wide.push(el.tagName + '.' + el.className + ' ' + Math.round(r.right));
              });
              return {scrollW: de.scrollWidth, innerW: window.innerWidth, height: de.scrollHeight, wide: wide.slice(0, 15),
                      probs: document.querySelectorAll('article.prob').length, waves: document.querySelectorAll('.wave svg').length,
                      tools: document.querySelectorAll('.widget .wt').length, werr: Array.from(document.querySelectorAll('.werr')).map(e => e.textContent).slice(0, 10)};
            }""")
            print(info)
        print("console:", [e for e in errs if "fonts" not in e and "ERR_FAILED" not in e][:20])
        await b.close()


asyncio.run(main())
