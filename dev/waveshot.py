#!/usr/bin/env python3
"""Screenshot rendered timing diagrams by index (after shot.py has written out/preview.html). usage: waveshot.py [--dark] i j k ..."""
import asyncio, os, sys
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repository root
async def main():
    idx = [int(a) for a in sys.argv[1:] if not a.startswith("--")]
    dark = "--dark" in sys.argv
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce", color_scheme="dark" if dark else "light")
        page = await ctx.new_page()
        await page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        await page.route("**/fonts.gstatic.com/**", lambda r: r.abort())
        await page.goto("file://" + os.path.join(HERE, "out", "preview.html"))
        await page.wait_for_timeout(500)
        waves = page.locator(".wave")
        n = await waves.count()
        if not idx:
            for i in range(n):
                alt = await waves.nth(i).evaluate("e => { const s = e.querySelector('svg'); return s ? s.getAttribute('aria-label') : ''; }")
                print(i, (alt or "")[:80])
        for i in idx:
            el = waves.nth(i)
            await el.scroll_into_view_if_needed()
            await el.screenshot(path=os.path.join(HERE, "out", f"w_{i}.png"))
            print("shot", i)
        await b.close()
asyncio.run(main())
