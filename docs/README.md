# raylib-pengu — reference

Two layers, and a page for each of them:

| Layer | Pages | What it is |
|---|---|---|
| **1 — bindings** | [`docs/bindings/`](bindings/README.md) | the 1:1 C surface, generated from the headers by `pengu bind`. Seven pages. |
| **2 — wrappers** | [`docs/wrappers/`](wrappers/README.md) | the Pengunic surface a program calls, hand-written. Nineteen pages. |

Two hand-written pages sit alongside them:

- **[Notes, decisions and traps](NOTES.md)** — the decisions that govern the layer, the
  PenguScript traps the wrappers are written around, and the measured raylib behaviour no header
  documents. **Read this before writing code against the wrapper**, and cite it in the wiki when a
  reader needs to know *why* a call looks the way it does.
- **[WRAPPER_CONVENTIONS.md](WRAPPER_CONVENTIONS.md)** — the design contract: what belongs in a
  wrapper, what never does, naming, memory and testing rules.

Every page in `bindings/` and `wrappers/` is generated from the `##` doc comments in the source by
`pengu doc`; the index files, `NOTES.md` and the contract are maintained by hand.

---

## Which page do I want?

| I want to… | Go to |
|---|---|
| call raylib the easy way | [`wrappers/raylibx.md`](wrappers/raylibx.md) — the facade, with the fourteen families below it |
| do maths | [`wrappers/raymathx.md`](wrappers/raymathx.md) |
| drive a camera | [`wrappers/rcamerax.md`](wrappers/rcamerax.md) |
| draw a GUI | [`wrappers/rayguix.md`](wrappers/rayguix.md) |
| use raw OpenGL | [`wrappers/rlglx.md`](wrappers/rlglx.md) |
| see every raw C function and constant | [`bindings/raylib.md`](bindings/raylib.md) and its siblings |
| know why something is wrapped the way it is | [`NOTES.md`](NOTES.md) |
| write a new wrapper | [`WRAPPER_CONVENTIONS.md`](WRAPPER_CONVENTIONS.md) |

---

## The module map

```
pengu/
├── raylib.d.pengu          layer 1  →  docs/bindings/raylib.md
├── raymath.d.pengu                    docs/bindings/raymath.md
├── rcamera.d.pengu                    docs/bindings/rcamera.md
├── rgestures.d.pengu                  docs/bindings/rgestures.md
├── rlgl.d.pengu                       docs/bindings/rlgl.md
├── raygui.d.pengu                     docs/bindings/raygui.md
├── raylib_pengu.d.pengu               docs/bindings/raylib-pengu.md
│
├── raylibx.pengu           layer 2  →  docs/wrappers/raylibx.md       the facade
├── raylibx/                           docs/wrappers/raylibx-<family>.md
│   ├── audio, colors, drawing, files, images, input, models, random,
│   └── shaders, shapes, shapes3d, text, textures, window                fourteen families
├── raymathx.pengu                     docs/wrappers/raymathx.md
├── rcamerax.pengu                     docs/wrappers/rcamerax.md
├── rlglx.pengu                        docs/wrappers/rlglx.md
└── rayguix.pengu                      docs/wrappers/rayguix.md
```

`pengu/raylibx.pengu` is a facade: it imports the fourteen families so that one `pengu build` (or
`pengu test`) compiles the whole layer in a single process, which is what catches method-name
collisions and order-dependent tests. It re-exports nothing — PenguScript has no re-export, so a
family is reached through an import alias:

```pengu
import raylibx.text as text

weave main into int:
    var parts as list of string is calling text.split_text with "a,b", ","
    return 0
```

---

## Citing these pages in the wiki

The pages are plain Markdown and every one of them states its source path in the second line, so a
wiki article can link or transclude them directly:

```
[docs/wrappers/raylibx-shapes.md](wrappers/raylibx-shapes.md)
```

Conventions that keep citations stable:

- **Wrapper pages are named after the module**, with the family after a hyphen:
  `raylibx-shapes.md` documents `raylibx.shapes`.
- **Binding pages are named after the binding file**: `rlgl.md` documents `pengu/rlgl.d.pengu`.
- **One symbol, one page.** Each page lists its symbols as `###` headings, so a deep link can point
  at a single function.
- The generated pages carry a breadcrumb back here; the two hand-written pages do not need one.

## Regenerating the reference

```sh
python3 tools/gen_docs.py            # rewrite every generated page
python3 tools/gen_docs.py --check    # report drift without writing
```

The script runs `pengu doc` once per top-level entry, keeps the pages that belong to this project,
drops the `std.*` modules PenguScript ships (it documents those itself), files the rest under the
names above and adds the breadcrumb line. It never touches the hand-written pages.

**`pengu doc` skips a module whose doc-time check reports any problem, even when `pengu check` is
clean** — so a module with a warning silently loses its page. `tools/gen_docs.py` fails loudly
instead, naming the module that produced no page; see [`NOTES.md`](NOTES.md) for the measured
example.
