# raylib-pengu

PenguScript bindings for [raylib](https://www.raylib.com) — core, raymath, rlgl,
rcamera, rgestures and raygui — generated with `pengu bind` from the headers in
[`include/`](include).

The committed headers are raylib **6.1-dev**; `pengu/*.d.pengu` was generated
from exactly those files, so the library you link must be built from a matching
raylib (see [Native library](#native-library)).

**Reference and notes live in [`docs/`](docs/README.md)**: a generated page per
binding and per wrapper module, plus [`docs/NOTES.md`](docs/NOTES.md) for the
design decisions and the measured traps. Start at
[`docs/README.md`](docs/README.md).

## Modules

| `import`       | header        | surface                                                            | implemented by              |
| -------------- | ------------- | ------------------------------------------------------------------ | --------------------------- |
| `raylib`       | `raylib.h`    | window, input, shapes, textures, text, models, audio, files, colors | `libraylib`                 |
| `raymath`      | `raymath.h`   | Vector2/3/4, Quaternion and Matrix maths (146 functions)            | `libraylib`                 |
| `rcamera`      | `rcamera.h`   | the `Camera3D` helper system                                        | `libraylib`                 |
| `rgestures`    | `rgestures.h` | touch/gesture detection (`UpdateGestures`, `ProcessGestureEvent`)   | `libraylib`                 |
| `rlgl`         | `rlgl.h`      | the OpenGL abstraction layer raylib is built on                     | `libraylib`                 |
| `raygui`       | `raygui.h`    | immediate-mode GUI (`GuiButton`, `GuiWindowBox`, …)                 | `c/raygui_impl.c`           |
| `raylib-pengu` | —             | facade: re-exports every module above in one import                 | —                           |

`raymath`, `rcamera` and `rgestures` are header-only upstream, but raylib's
`rcore.c` defines `RAYMATH_IMPLEMENTATION`/`RCAMERA_IMPLEMENTATION`/
`RGESTURES_IMPLEMENTATION` before including them, so their functions are real
exported symbols of `libraylib` — the bindings only declare them.
`raygui` is **not** part of a default raylib build (`RAYLIB_MODULE_RAYGUI=FALSE`),
so this repository ships its implementation as glue code, which the consumer's
build compiles into the bundle.

## Install

From any PenguScript project:

```bash
pengu add <this-repo-url> --trust
```

`--trust` is required the first time because `build.py` builds the native part.
Then import what you need:

```pengu
import raylib
import raymath
import std.ffi

weave main into int:
    calling raylib.InitWindow with 800, 600, "Hello, raylib"
    calling raylib.SetTargetFPS with 60
    var a as Vector2 is with x is 1.0, y is 2.0
    var b as Vector2 is with x is 3.0, y is 4.0
    while not calling raylib.WindowShouldClose:
        calling raylib.BeginDrawing
        calling raylib.ClearBackground with RAYWHITE
        var sum as Vector2 is calling raymath.Vector2Add with a, b
        var text as string is "{(sum.x to string)}"
        calling raylib.DrawText with (calling ffi.cstr_from_string with text), 10, 10, 20, DARKGRAY
        calling raylib.EndDrawing
    calling raylib.CloseWindow
    return 0
```

Notes that trip people up:

- A C `const char *` is `ref to frozen char`, not `string`: a literal converts
  automatically, a `string` value needs `ffi.cstr_from_string`.
- `declare`s do not emit C prototypes; the `include "…"` line makes the C
  compiler check every call against the real header, so a signature mismatch is
  a compile error, not silent corruption.
- raylib's `Color` constants (`RAYWHITE`, `DARKGRAY`, …) are PenguScript `const`s
  but the C value comes from the header's own macro.

## Native library

`link "raylib"` in [`pengu/raylib.d.pengu`](pengu/raylib.d.pengu) propagates to
the consumer's link line, so a raylib installed system-wide (`-lraylib`) is
enough. Otherwise `build.py` provides one:

```bash
python3 build.py                 # build vendor/raylib (cloned) into lib/libraylib.a
RAYLIB_SRC=/path/to/raylib python3 build.py --force
```

`build.py` looks for a source tree in `$RAYLIB_SRC`, `vendor/raylib` and
`extern/raylib-*`, clones `raysan5/raylib` if there is none, builds with
`make PLATFORM=PLATFORM_DESKTOP`, and installs `lib/libraylib.a`. It never
overwrites the committed `include/*.h` (the bindings were generated from those)
and warns when the source tree's headers differ from them.

## Regenerating the declarations

Every `.d.pengu` under [`pengu/`](pengu) is the output of `pengu bind` plus the
hand fixes listed below. From the repository root:

```bash
# 1. Core binding (auto-import is disabled: modules here are top-level, not std.*)
pengu bind include/raylib.h    --output pengu/raylib.d.pengu    --auto-import ""
pengu bind include/rgestures.h --output pengu/rgestures.d.pengu --auto-import ""
pengu bind include/rlgl.h      --output pengu/rlgl.d.pengu      --auto-import ""

# 2. rcamera.h expects raylib.h to be included first, so preload it
pengu bind include/rcamera.h --output pengu/rcamera.d.pengu --auto-import "" \
    --include-paths include --cpp-flags "-include raylib.h"

# 3. raygui.h `#include "raylib.h"` (unless RAYGUI_STANDALONE), so give the
#    preprocessor the local include directory
pengu bind include/raygui.h --output pengu/raygui.d.pengu --auto-import "" \
    --include-paths include

# 4. raymath.h is header-only: `pengu bind` drops function *definitions*, so
#    bind a prototype-only copy of the same file name instead
python3 tools/gen_raymath_protos.py include/raymath.h build/raymath_decls/raymath.h
pengu bind build/raymath_decls/raymath.h --output pengu/raymath.d.pengu --auto-import ""
```

Then re-apply the hand fixes (they are commented in place in each file); they
exist because the generator either cannot express the construct or picks the
wrong `#ifdef` branch:

| File              | Hand fix                                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `raylib`          | `link "…"` block; the 26 `Color` constants (`LIGHTGRAY`…`RAYWHITE`); the `DEG2RAD`/`RAD2DEG` folds; the `MOUSE_*`, `MATERIAL_MAP_*` and `SHADER_LOC_MAP_*` compatibility aliases |
| `raymath`         | `import raylib` + delete the duplicated `Vector2`/`Vector3`/`Vector4`/`Quaternion`/`Matrix`; `link "m"`                          |
| `rcamera`         | `import raylib` + delete the `alias Camera/Matrix/Vector3` companion block; drop the implementation-only `CAMERA_*` constants    |
| `rgestures`       | `import raylib` + delete the duplicated `Vector2`; drop the `RGESTURES_IMPLEMENTATION`-only constants                            |
| `rlgl`            | `import raylib` + delete the duplicated `Matrix`; add `RLGL_VERSION` and the `RL_SHADER_LOC_MAP_*` aliases; drop the OpenGL/implementation-only constants |
| `raygui`          | `import raylib`; add `RAYGUI_VERSION_MAJOR`; delete the `alias Color/Font/Rectangle/Vector2/Vector3 as opaque` block; drop every `RAYGUI_IMPLEMENTATION`-only constant |

## Examples

`examples/` ports the upstream raylib examples one file at a time, keeping each
original's documentation in the comments. Every port lives next to its `.c`
source and uses the layer-2 wrappers (`raylibx.*`, `raymathx`, `rcamerax`)
wherever one exists; `InitWindow`/`CloseWindow` and other functions the
wrappers deliberately skip stay on the binding.

| Example | Run |
| --- | --- |
| `core_2d_camera` | `pengu run examples/core/core_2d_camera.pengu` |
| `core_2d_camera_mouse_zoom` | `pengu run examples/core/core_2d_camera_mouse_zoom.pengu` |
| `core_2d_camera_platformer` | `pengu run examples/core/core_2d_camera_platformer.pengu` |
| `core_2d_camera_split_screen` | `pengu run examples/core/core_2d_camera_split_screen.pengu` |
| `core_3d_camera_first_person` | `pengu run examples/core/core_3d_camera_first_person.pengu` |
| `core_3d_camera_fps` | `pengu run examples/core/core_3d_camera_fps.pengu` |
| `core_3d_camera_free` | `pengu run examples/core/core_3d_camera_free.pengu` |

The `raylibx.text` family is imported as `txt`, not `text`: with `pengu 2.9.0`
an alias identical to the module name makes the C backend emit
`text.draw_text(...)` instead of `text_draw_text(...)`, which does not compile.

### Why `src -> pengu` exists

Module resolution looks for an import in, in order: the importing file's own
directory, the project's `src_dir`, the `lib/` dependency directory, and the
project root. The LSP additionally has to *find* the project root, and until
PenguScript 2.2 it only recognised `pengu.yaml` or a directory literally named
`src/` as markers — so a project whose manifest is `pengu.toml` (the default)
had every `import` resolved relative to the document's own directory.

Two toolchain fixes make the natural layout work (both in the PenguScript
checkout, see *Toolchain fixes* below): the LSP now recognises every manifest
the CLI does, and module resolution honours the manifest's `src_dir`
(`src_dir = "pengu"` here). A `pengu` binary that predates those fixes needs a
one-entry compatibility shim (`src -> pengu`), which doubled as the `src/`
project-root marker the old LSP looked for and as the directory the old
resolver searched, so that `import raylib` worked from anywhere in the tree
without a rebuild.

**That shim has been deleted from this repository**: it is inert on a fixed
toolchain, and the `pengu` this project is built against has both fixes.

## Verifying the bindings

```bash
python3 tools/check_bindings.py     # needs gcc and pengu on PATH
pengu check                         # type-checks the project entry
```

`tools/check_bindings.py` re-derives what a consumer translation unit can see
(with `gcc -E -dM` and constant-expression probes) and reports, per module:

- **MISSING** — a macro that is visible and constant but is not declared here
  (nor in a binding this one imports), or a type/function that a fresh
  `pengu bind` run produces but the committed file lost;
- **WRONG** — a declared scalar constant whose macro is not a constant
  expression (e.g. binding picked the `0` from an `#else` branch of a
  function-like macro);
- **STALE** — a declared constant whose macro exists only inside a
  `*_IMPLEMENTATION` block and therefore does not exist in a consumer TU.

Current status: `OK: 6 bindings cover every visible constant, type and function`.

## Structure

```
raylib-pengu/
├── pengu.toml                  # entry = pengu/raylib.d.pengu, src_dir = "pengu"
├── build.py                    # builds raylib into lib/
├── pengu/
│   ├── raylib.d.pengu          # raylib.h        (+ colors, links)
│   ├── raymath.d.pengu         # raymath.h       (146 prototype-only declares)
│   ├── rcamera.d.pengu         # rcamera.h
│   ├── rgestures.d.pengu       # rgestures.h
│   ├── rlgl.d.pengu            # rlgl.h
│   ├── raygui.d.pengu          # raygui.h
│   ├── raylib_pengu.d.pengu    # facade: imports all of the above
│   ├── raymathx.pengu          # layer 2: 138 raymath wrappers, 416 tests
│   ├── rcamerax.pengu          # layer 2: 12 Camera3D methods
│   ├── rlglx.pengu             # layer 2: 18 rlgl wrappers (the boundary crossings only)
│   ├── rayguix.pengu           # layer 2: 38 raygui widgets (strings and text fields)
│   ├── raylibx.pengu           # layer 2 facade: imports the fourteen families below
│   └── raylibx/                # layer 2: one module per raylib family
│       ├── colors.pengu        #   raylibx.colors
│       ├── files.pengu         #   raylibx.files
│       ├── shapes.pengu        #   raylibx.shapes      (20 Vector2 + 7 Rectangle methods)
│       ├── shapes3d.pengu      #   raylibx.shapes3d    (4 Vector3 methods)
│       ├── text.pengu          #   raylibx.text        (5 Font methods)
│       ├── input.pengu         #   raylibx.input
│       ├── images.pengu        #   raylibx.images      (52 Image methods)
│       ├── textures.pengu      #   raylibx.textures
│       ├── drawing.pengu       #   raylibx.drawing     (the Begin/End pairs)
│       ├── window.pengu        #   raylibx.window
│       ├── shaders.pengu       #   raylibx.shaders
│       ├── models.pengu        #   raylibx.models
│       ├── audio.pengu         #   raylibx.audio
│       └── random.pengu        #   raylibx.random      (the azar appendix)
├── include/                    # the real C headers the bindings were made from
├── c/
│   └── raygui_impl.c           # RAYGUI_IMPLEMENTATION, compiled into the consumer's bundle
├── lib/                        # libraylib.a produced by build.py
├── tools/
│   ├── check_bindings.py       # completeness audit
│   ├── gen_docs.py             # regenerates docs/bindings + docs/wrappers
│   └── gen_raymath_protos.py   # raymath.h -> prototype-only header
├── docs/                       # the reference: start at docs/README.md
│   ├── README.md               # index: the two layers, the module map, how to cite
│   ├── NOTES.md                # decisions, PenguScript traps, measured raylib traps
│   ├── bindings/               # layer 1: one generated page per binding
│   ├── wrappers/               # layer 2: one generated page per wrapper module
│   └── WRAPPER_CONVENTIONS.md  # the design contract for new wrappers
└── examples/                   # the upstream .c examples and their .pengu translations
    └── core/
        ├── core_basic_window.c      # original
        └── core_basic_window.pengu  # translation (`pengu run`-able)
```

The facade module is `raylib_pengu` (underscore): an import path cannot contain
a hyphen, so `import raylib-pengu` would be a syntax error even though the
repository is called `raylib-pengu`.

The same holds for the wrapper layer: each family is a module under `pengu/raylibx/`
(`raylibx.colors`, `raylibx.text`, ...), and `pengu/raylibx.pengu` is their facade.
PenguScript has **no re-export**, so `import raylibx` does not expose the families --
import the ones you need with an alias (`import raylibx.text as text`) and call through
it. What the facade is for is compiling, linking and testing the whole layer at once:

```sh
pengu check --entry pengu/raylibx.pengu    # all fourteen families, one compilation
pengu build --entry pengu/raylibx.pengu    # one bundle that links
pengu test  --entry pengu/raylibx.pengu    # the layer's 261 tests in one run
```

That last one matters: the families share process-global state (a window initialises GLFW,
which enumerates a gamepad; `InitWindow` loads the default font, which calls
`SetShapesTexture`), so running them together is what catches tests that assumed a virgin
process.

## Toolchain fixes

Found while wiring the examples up; both live in the PenguScript checkout, not
here. A `pengu` binary without them needs the `src -> pengu` shim described
above; that shim has been deleted from this repository.

| File | Fix |
| ---- | --- |
| `pengu_lsp/server.py` | `_project_root_for_path` recognised only `pengu.yaml` and a literal `src/`, so a `pengu.toml` project resolved every import relative to the document's own directory and reported, as a cascade, that the binding exported no members. It now accepts the CLI's whole marker set. |
| `pengu_parser/pengu_symbols.py`, `pengu_checker.py`, `pengu_project.py`, `pengu_doc.py`, `pengu_lsp/server.py` | Module resolution hardcoded `src/` and ignored the manifest's `src_dir` (and `PenguChecker` stored `lib_dir` without ever using it). `find_module_path`/`resolve_imports`/`PenguChecker` now take `src_dir`, and script mode reads `src_dir`/`lib_dir`/`include_dir` from the manifest it already walked up to. |

The `link "…"` statements in `pengu/raylib.d.pengu` propagate to the consumer's
link line automatically; see the PenguScript `docs/BINDINGS.md` for the full
contract.
