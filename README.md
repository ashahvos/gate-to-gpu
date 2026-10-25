# Gate to GPU

An interactive study guide to digital hardware, from how a voltage becomes a bit to how a GPU runs thousands of threads. It is written for students and for engineers preparing for hardware, embedded and chip-design interviews.

**Read it online:** https://ashahvos.github.io/gate-to-gpu/

## What is inside

- **28 modules in 7 parts:** number systems and arithmetic, Boolean algebra and minimization, circuits and analog building blocks, CMOS, latches and flip-flops, state machines, timing and clock domains, processor datapaths, pipelining, caches and memory, GPUs and parallel programming, microcontroller I/O, interrupts and serial buses, Verilog, and the chip design flow.
- **403 practice problems** at four levels (intro, easy, medium, hard), each with a worked solution.
- **121 interview-style problems** grouped by topic, with explanations and links back to the modules that teach them.
- **16 interactive tools**, including a K-map solver, a floating-point explorer, a cache simulator, a pipeline hazard visualizer, a setup and hold calculator and an AVR timer calculator.
- **123 diagrams and 18 timing diagrams**, a formula and fact sheet, and a searchable glossary.

Progress you mark ("Got it") is saved in your own browser only.

## Using it

The whole guide is one self-contained file, `docs/index.html`. Open it in any browser, or visit the GitHub Pages site above. It needs an internet connection only for its web fonts; without one it falls back to system fonts.

## Building from source

The page is generated from the sources in `src/` by a build script that needs only Python 3.8 or later (no packages):

```sh
python3 build.py
```

This writes `docs/index.html`. It also writes a fragment without the document skeleton to `out/` (ignored by git), which is the form used when the page is hosted inside an app that supplies its own skeleton.

## Repository layout

```
build.py            build script: converts the module sources into one page
src/modules/        one file per module, in the authoring format described below
src/d1.py … d7.py   diagram and timing-diagram generators (SVG), registered by name
src/dlib.py         drawing helpers used by the generators (gates, flip-flops, muxes, axes, …)
src/js/             page behavior (problem filters, progress, search) and the interactive tools
src/style.css       styles; light and dark themes are defined as tokens at the top
src/shell_top.html  page header, contents panel and toolbar
docs/               the built page served by GitHub Pages
dev/                optional checking tools (see below)
```

## Writing and editing content

Each file in `src/modules/` is one module wrapped in a `<module>` tag. Ordinary HTML (`<p>`, `<h3>`, `<ul>`, `<b>`, `<sub>` …) works as usual, plus these tags:

| Tag | Purpose |
| --- | --- |
| `<module id num title short blurb part pre>` | Module wrapper. `num` orders and numbers it, `part` places it in a part, `pre` lists prerequisite module ids. |
| `<def term="…">`, `<key>`, `<warn>`, `<ex title="…">`, `<prac>`, `<analogy>` | Callouts: definition (also collected into the glossary), key idea, common mistake, worked example, in practice, analogy. |
| `<deeper title="…">` | Collapsible "going deeper" panel. |
| `<diagram name="…" args='{…}'>caption</diagram>` | An SVG diagram from a generator in `src/d*.py`. Labels accept `_x` or `_{…}` for subscripts and `^{…}` for superscripts. |
| `<wavegen name="…" args='{…}'>caption</wavegen>`, `<wave>{json}</wave>` | Timing diagrams, generated or written directly as JSON. |
| `<truth h="A B \| F">rows</truth>` | Truth table; rows separated by `;`. |
| `<grid cls="mono">` | Table: one row per line, the first line is the header, and cells are separated by vertical bars. |
| `<pre lang="c">` | Code block with highlighting for `c`, `cpp`, `cuda`, `v`, `sv`, `asm` (AVR) and `riscv`. |
| `<eq>` / `<eq c>` | Displayed equation (centered with `c`). |
| `<tool name="…"/>` | Embeds an interactive tool from `src/js/`. |
| `<practice title="…">` with `<prob level="easy" tags="…">`, `<ask>`, `<hint>`, `<sol>` | Practice problems. Levels: `intro`, `easy`, `medium`, `hard`. |
| `<ref to="id" t="text"/>` | Cross-reference to a module or any element id. |
| `<gterm t="…" to="module-id">definition</gterm>`, `<glossary/>` | Glossary-only terms, and where the glossary is placed. |

Inside `<grid>`, write a literal vertical bar in a cell as `\|`. Inline: backticks make `code`, and Unicode superscripts and subscripts (2¹⁰, log₂) are converted to `<sup>`/`<sub>` automatically. The build prints a warning for unknown diagrams, tools or references and for unbalanced tags; fix those before committing.

## Checking changes (optional)

The scripts in `dev/` render the page with Playwright to catch layout problems:

```sh
pip install playwright && python3 -m playwright install chromium
python3 dev/shot.py --check                 # screenshot plus overflow and console-error check
python3 dev/shot.py --check --phone --dark  # the same at phone width in dark mode
python3 dev/gallery.py kmap roofline        # render selected diagrams to out/
```

`dev/boolmin.py` is an exact two-level logic minimizer used to verify K-map and Boolean-algebra answers.

## Contributing

Found an error? Open an issue that names the module and problem number (for example "17.3") and explains what is wrong. To fix it yourself, edit the module in `src/modules/`, run `python3 build.py`, and open a pull request that includes the rebuilt `docs/index.html`.

## License

See [LICENSE](LICENSE).
