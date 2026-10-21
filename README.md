<div align="center">

# 🐧 raylib-pengu

### Raylib 6.x bindings and idiomatic wrappers for PenguScript

[![PenguScript](https://img.shields.io/badge/PenguScript-2.14%2B-blueviolet)](https://github.com/pengus-lang/penguscript)
[![raylib](https://img.shields.io/badge/raylib-6.x-black)](https://www.raylib.com/)
[![Examples](https://img.shields.io/badge/examples-226-brightgreen)](examples/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](#platform-notes)

**Write raylib games in PenguScript — from 1:1 C calls to a Pengunic wrapper layer.**

[Quick start](#quick-start) · [Add to your project](#add-the-binding-to-your-project) · [Examples](#examples) · [Assets](#assets-and-paths) · [One executable](#one-executable-with-arca)

</div>

---

`raylib-pengu` is the bridge between [raylib](https://www.raylib.com/) and
[PenguScript](https://github.com/pengus-lang/penguscript). It gives you the complete raylib C API
**and** a hand-written wrapper layer on top, so you can choose the style that fits each line of
code: raw and exact where you need it, short and Pengunic everywhere else.

> **No interpreter. No separate runtime.** PenguScript compiles your program to C99, links
> `libraylib`, and calls the real C functions directly.

**Jump to:** [Why](#why) · [How it works](#how-it-works) · [Quick start](#quick-start) ·
[Add to your project](#add-the-binding-to-your-project) · [Two styles](#two-styles) ·
[Module map](#module-map) · [Examples](#examples) · [Assets](#assets-and-paths) ·
[One executable](#one-executable-with-arca) · [Platform notes](#platform-notes) ·
[Troubleshooting](#troubleshooting) · [Development](#development) · [Documentation](#documentation)

---

## <a id="why"></a>🚀 Why raylib + PenguScript?

| | What you get |
|---|---|
| 🧱 **1:1 C binding** | The raylib C surface — types, constants and functions — generated from the headers in [`include/`](include/), callable through `import raylib`. |
| 🪄 **Idiomatic wrappers** | `raylibx.*` turns raw calls into `snake_case` functions, methods on `Vector2`/`Rectangle`/`Texture`/`Image`, `maybe` return values, slices and safe cleanup patterns. |
| 🧩 **raygui + reasings** | Immediate-mode GUI and easing functions are included: `import raygui`, `import rayguix`, `import reasings`. |
| 📦 **226 examples** | A complete translated corpus in [`examples/`](examples/), from a basic window to PBR, skinning, shaders, audio and `raygui` tools. |
| 🔗 **Static raylib** | [`build.pengu`](build.pengu) builds `lib/libraylib.a` from source (or uses your system raylib), so your game links one archive. |
| 🛠️ **Zero glue for you** | `pengu run` compiles the generated bundle **and** the C files in [`c/`](c/) automatically — including `raygui` and `msf_gif` implementations. |
| 📚 **Documented API** | Generated binding pages in [`docs/bindings/`](docs/bindings/) and wrapper pages in [`docs/wrappers/`](docs/wrappers/). |

---

## <a id="how-it-works"></a>🧠 How PenguScript works with raylib

PenguScript is a compiled language. `pengu` turns every imported `.pengu` module into one C99
translation unit (`bundle.c`) and invokes your C compiler. A binding therefore needs only three
things:

1. **Headers** — [`include/raylib.h`](include/raylib.h), `raymath.h`, `rlgl.h`, `rcamera.h`,
   `rgestures.h`, `raygui.h`.
2. **Declarations** — [`pengu/raylib.d.pengu`](pengu/raylib.d.pengu) declares the C functions,
   structs (`rune`), enums (`omen`) and constants, and contains `include "raylib.h"` +
   `link "raylib"`.
3. **Glue C when a header needs a translation unit** — raygui is header-only, so
   [`c/raygui_impl.c`](c/raygui_impl.c) defines `RAYGUI_IMPLEMENTATION`. The screen-recording
   example needs the same for `msf_gif.h`, supplied by [`c/msf_gif_impl.c`](c/msf_gif_impl.c).

```text
┌──────────────────────────────────────────────────────────────────┐
│  your .pengu program                                             │
│    import raylib                       import raylibx.drawing   │
│    import raylibx.text                 import raylibx.images    │
├──────────────────────────────────────────────────────────────────┤
│  layer 2 — raylibx / raymathx / rcamerax / rayguix / rlglx       │
│    hand-written PenguScript wrappers, methods and maybe values   │
├──────────────────────────────────────────────────────────────────┤
│  layer 1 — raylib.d.pengu, raymath.d.pengu, raygui.d.pengu, …    │
│    generated 1:1 declarations from the C headers                 │
├──────────────────────────────────────────────────────────────────┤
│  bundle.c  +  c/*.c  +  lib/libraylib.a  +  OpenGL / X11 / …     │
└──────────────────────────────────────────────────────────────────┘
```

The important consequence: **what you call is what C sees**. A `raylib.Vector2` is the raylib
`Vector2` struct passed by value; a `raylib.Texture` is the same handle; an `antiquus` block is C
embedded directly in the bundle. There is no marshalling layer and no reflection at runtime.

---

## <a id="quick-start"></a>⚡ Quick start

### Requirements

| Tool | Version | Notes |
|---|---|---|
| **PenguScript** | 2.14+ | `pengu` must be on `PATH`; newer releases auto-discover `build.pengu`. |
| **C compiler** | GCC, Clang or MSVC | C99; GCC/Clang are the tested paths. |
| **raylib** | 6.x | `build.pengu` builds a static `libraylib.a`, or links a system raylib. |
| **Native tools** | `git`, `make`, a C compiler | Needed only when `build.pengu` builds raylib from source. |
| **Graphics** | OpenGL 3.3+ | raylib's default desktop backend. |
| **Linux** | X11 + OpenGL development packages | `libGL`, `libX11`, headers. |
| **macOS** | Xcode Command Line Tools | Add the raylib frameworks to `ldflags` (see [platform notes](#platform-notes)). |
| **Windows** | MinGW-w64 or MSVC | The binding links `opengl32` and `gdi32` for you. |

> [!NOTE]
> The committed headers are raylib **6.1-dev**. Link against a compatible raylib 6.x build. If you
> need an older raylib major version, regenerate the raw bindings from that version's headers.

### Run an example from this repository

```bash
git clone https://github.com/TuGatito/raylib-pengu.git
cd raylib-pengu

# 1) Build raylib into lib/libraylib.a if it is not there yet.
#    The script reuses $RAYLIB_SRC, vendor/raylib or a system raylib when it can.
pengu run build.pengu

# 2) Run any example from the repository root.
pengu run examples/core/core_basic_window.pengu
pengu run examples/textures/textures_bunnymark.pengu
pengu run examples/shaders/shaders_basic_pbr.pengu
```

To rebuild raylib from scratch:

```bash
pengu run build.pengu -- --force
```

To build from a specific raylib checkout:

```bash
RAYLIB_SRC=/path/to/raylib pengu run build.pengu -- --force
```

> [!TIP]
> If your `pengu` release does not discover `build.pengu` automatically, run it explicitly with
> the command above.

---

## <a id="add-the-binding-to-your-project"></a>📥 Add the binding to your project

From the root of an existing PenguScript project:

```bash
cd my-game

pengu add https://github.com/TuGatito/raylib-pengu.git --trust
```

During development, a local checkout works the same way:

```bash
pengu add ../raylib-pengu --trust
```

`pengu add` installs the binding under `lib/raylib-pengu/`, registers it as a dependency in
`pengu.toml`, and makes its modules importable:

```pengu
import raylib
import raylibx.drawing as drawing
import raylibx.text as txt
```

> [!NOTE]
> `--trust` runs the binding's native build script, which may clone and compile raylib. Review the
> script first if the source is not yours. Update later with `pengu update`.

> [!IMPORTANT]
> The import path is **`raylib`**, not `raylib-pengu`. PenguScript modules live in
> `pengu/`, so the package name and the module name are intentionally different.

### Your first window

```pengu
import raylib
import raylibx.drawing as drawing
import raylibx.text as txt

weave main into int:
    calling raylib.InitWindow with 800, 450, "My first raylib-pengu game"
    defer calling raylib.CloseWindow
    calling raylib.SetTargetFPS with 60

    while not calling raylib.WindowShouldClose:
        calling drawing.begin_drawing
        calling drawing.clear_background with raylib.RAYWHITE
        calling txt.draw_text with "Hello, PenguScript!", 300, 210, 20, raylib.DARKGRAY
        calling drawing.end_drawing

    return 0
```

```bash
pengu run
```

### If `pengu add` did not build the native library

Some PenguScript releases do not run a dependency's build script automatically. If
`lib/libraylib.a` is missing, build it inside the installed binding:

```bash
cd lib/raylib-pengu
pengu run build.pengu
```

Or simply use a system raylib: the binding declares `link "raylib"`, so the linker will find
`-lraylib` if it is installed in a standard location.

---

## <a id="two-styles"></a>🎨 Two ways to write the same window

### Style 1 — C style (`import raylib`)

Use the raw layer when you want the exact raylib API, a function that has no wrapper, or full
control over C types.

```pengu
import raylib

weave main into int:
    calling raylib.InitWindow with 800, 450, "raylib C style"
    defer calling raylib.CloseWindow
    calling raylib.SetTargetFPS with 60

    while not calling raylib.WindowShouldClose:
        calling raylib.BeginDrawing
        calling raylib.ClearBackground with raylib.RAYWHITE
        calling raylib.DrawText with "Hello from the C binding", 190, 200, 20, raylib.LIGHTGRAY
        calling raylib.EndDrawing

    return 0
```

### Style 2 — Pengu style (`import raylibx.*`)

Use the wrapper layer for everyday game code: `snake_case` names, methods on raylib structs,
`maybe` instead of silent failure, and explicit memory helpers.

```pengu
import raylib
import raylibx.drawing as drawing
import raylibx.shapes as shapes
import raylibx.text as txt

weave main into int:
    calling raylib.InitWindow with 800, 450, "Pengu style"
    defer calling raylib.CloseWindow
    calling raylib.SetTargetFPS with 60

    let center as raylib.Vector2 is with x is 400.0, y is 225.0
    while not calling raylib.WindowShouldClose:
        calling drawing.begin_drawing
        calling drawing.clear_background with raylib.RAYWHITE
        calling txt.draw_text with "Hello, wrappers!", 320, 200, 20, raylib.DARKGRAY
        calling center.draw_circle with 8.0, raylib.RED
        calling drawing.end_drawing

    return 0
```

### Which one should I use?

| | C style | Pengu style |
|---|---|---|
| Header mirror | **1:1** with `raylib.h` | Designed for PenguScript |
| Naming | `InitWindow`, `DrawText` | `begin_drawing`, `draw_text` |
| Failures | Raw raylib return values | `maybe`, empty slices, `none` |
| Resource cleanup | You call `Unload*` / `Close*` | Same, but `defer` keeps it scoped |
| Best for | Porting C, using unwrapped functions, exact ABI | New game code, UI, tools, prototypes |

You can mix both styles in the same file. The wrapper layer is built **on top of** the raw binding,
not next to it.

---

## <a id="module-map"></a>🗺️ Module map

### Layer 1 — raw C bindings

| Import | Header | What it gives you |
|---|---|---|
| `raylib` | `raylib.h` | Window, input, shapes, textures, text, models, audio |
| `raymath` | `raymath.h` | Vector, quaternion and matrix maths |
| `rcamera` | `rcamera.h` | The `Camera3D` helper system |
| `rgestures` | `rgestures.h` | Touch and gesture detection |
| `rlgl` | `rlgl.h` | The OpenGL abstraction raylib builds on |
| `raygui` | `raygui.h` | Immediate-mode GUI (implementation in `c/raygui_impl.c`) |
| `reasings` | `reasings.h` | Robert Penner easing functions, pure PenguScript |
| `raylib_pengu` | — | Facade that imports the core raw modules at once |

### Layer 2 — PenguScript wrappers

| Import | What it wraps |
|---|---|
| `raylibx.drawing` | The `Begin`/`End` frame-state pairs |
| `raylibx.shapes` | 2D shapes, plus `Vector2` and `Rectangle` methods |
| `raylibx.shapes3d` | 3D primitives, plus `Vector3` methods |
| `raylibx.text` | Fonts and text, plus `Font` methods |
| `raylibx.textures` | `Texture` and `RenderTexture`, plus draw methods |
| `raylibx.images` | The image pipeline, plus `Image` methods |
| `raylibx.models` | Meshes, materials, models, animations and 3D collision |
| `raylibx.audio` | Waves, sounds, music and audio streams |
| `raylibx.shaders` | Shader loading, memory shaders and typed uniforms |
| `raylibx.input` | Keyboard, mouse, gamepad, touch and gestures |
| `raylibx.files` | Files, directories, paths and clipboard-of-files |
| `raylibx.window` | Window state, monitors and the system clipboard |
| `raylibx.colors` | `Color` methods and colour helpers |
| `raylibx.random` | `between`, `sequence`, and the measured raylib traps |

Companion wrappers: `raymathx`, `rcamerax`, `rayguix`, `rlglx`, and the facade `raylibx`.

Each family has its own reference page in [`docs/wrappers/`](docs/wrappers/). The raw surface is
documented in [`docs/bindings/`](docs/bindings/).

---

## <a id="examples"></a>🎮 Examples

The repository ships **226 standalone examples**, translated from raylib's own examples and
extended with PenguScript-specific demos.

| Category | Count | Start here |
|---|---:|---|
| [`core`](examples/core/) | 48 | `core_basic_window.pengu`, `core_input_keys.pengu` |
| [`shapes`](examples/shapes/) | 45 | `shapes_basic_shapes.pengu`, `shapes_ball_physics.pengu` |
| [`shaders`](examples/shaders/) | 36 | `shaders_basic_lighting.pengu`, `shaders_basic_pbr.pengu` |
| [`textures`](examples/textures/) | 33 | `textures_bunnymark.pengu`, `textures_sprite_animation.pengu` |
| [`models`](examples/models/) | 32 | `models_loading_gltf.pengu`, `models_animation_gpu_skinning.pengu` |
| [`text`](examples/text/) | 17 | `text_font_loading.pengu`, `text_format_text.pengu` |
| [`audio`](examples/audio/) | 11 | `audio_sound_loading.pengu`, `audio_music_stream.pengu` |
| [`others`](examples/others/) | 4 | `rlgl_standalone.pengu`, `embedded_files_loading.pengu` |

Run any example **from the repository root**:

```bash
pengu run examples/core/core_basic_window.pengu
pengu run examples/textures/textures_bunnymark.pengu
pengu run examples/shaders/shaders_deferred_rendering.pengu
```

Every example is a normal PenguScript script with `weave main into int`, so you can copy it into
your own project, adapt the resources and keep going.

---

## <a id="assets-and-paths"></a>📁 Assets and paths

### The rule: paths are relative to the project root

`pengu run` executes your program with the **project root as its working directory** — the
directory that contains `pengu.toml`, not necessarily the directory that contains the `.pengu`
file. raylib resolves paths at runtime with the OS, so any file path you pass is relative to that
root.

For this repository:

```pengu
# ✅ Correct: relative to the repository root
calling textures.load_texture with "examples/models/resources/raylib_logo.png"

# ❌ Wrong: looks for <root>/resources/... — the file is not there
calling textures.load_texture with "resources/raylib_logo.png"
```

For your own project:

```text
my-game/
├── pengu.toml
├── src/
│   └── main.pengu
└── assets/
    └── textures/
        └── logo.png
```

```pengu
# Inside a weave, with:
#   import raylib
#   import raylibx.textures as textures
# Resolves to my-game/assets/textures/logo.png
var logo_opt as maybe raylib.Texture is calling textures.load_texture with "assets/textures/logo.png"
```

> [!WARNING]
> Do not build asset paths from the `.pengu` file's location unless you also compute the project
> root yourself. A path like `"resources/logo.png"` is **not** automatically relative to
> `src/main.pengu`; it is relative to the process working directory.

### Path cheatsheet

| You want… | Use |
|---|---|
| A file that stays on disk | `"assets/logo.png"` (relative to project root) |
| An example asset in this repo | `"examples/<category>/resources/..."` |
| A file embedded in the executable | `"logo.png"` with `arca` (relative to `assets/`) |

---

## <a id="one-executable-with-arca"></a>📦 One executable with arca

PenguScript can embed files into the executable with its **assets** feature (`arca`). The bytes are
stored in a read-only data section (`.rodata`), so the final binary does not need an `assets/`
folder next to it.

### 1. Configure assets in your project

```toml
# pengu.toml
[assets]
dir = "assets"          # directory relative to the project root
module = "arca"         # generates src/arca.pengu
embed = true            # true = .rodata, false = read from disk at runtime
exclude = ["*.psd", "*.tmp"]
```

### 2. Generate the asset module

```bash
pengu assets                 # writes src/arca.pengu + build/arca_assets.c
pengu assets --list          # list tracked files, sizes and constants
```

The generated module gives you a small, typed API:

| API | Returns | Ownership |
|---|---|---|
| `arca.count` | `int` | — |
| `arca.name` / `arca.name_at` | `string` | Borrowed view |
| `arca.has` / `arca.exists` | `bool` | — |
| `arca.size` | `usize` | — |
| `arca.ptr` | `ref to frozen void` | Borrowed |
| `arca.bytes` | `slice of byte` | Borrowed view |
| `arca.string` | `string` | **Owned copy** — safe to `banish` |

Asset names are **relative to the `assets/` directory**: `"logo.png"`, `"shaders/fade.fs"`,
`"audio/theme.ogg"`. `pengu assets` also emits constants such as
`arca.ASSET_LOGO_PNG_<HASH>`; either the constant or the literal name works.

### 3. Decode an embedded texture with raylib

`raylibx.images` and `raylibx.textures` accept slices, so the embedded bytes go straight into
raylib's memory loaders:

```pengu
import arca
import raylib
import raylibx.drawing as drawing
import raylibx.images as images
import raylibx.textures as textures

weave main into int:
    calling raylib.InitWindow with 800, 450, "Embedded logo"
    defer calling raylib.CloseWindow

    # arca.bytes is a borrowed view over .rodata: do not banish it.
    var image_opt as maybe raylib.Image is calling images.load_image_from_memory with ".png", calling arca.bytes with "logo.png"
    if image_opt is present:
        var image as raylib.Image is image_opt.value
        var texture_opt as maybe raylib.Texture is calling textures.load_texture_from_image with image
        calling images.unload_image with image

        if texture_opt is present:
            var tex as raylib.Texture is texture_opt.value
            defer calling textures.unload_texture with tex

            while not calling raylib.WindowShouldClose:
                calling drawing.begin_drawing
                calling drawing.clear_background with raylib.RAYWHITE
                calling tex.draw with 0, 0, raylib.WHITE
                calling drawing.end_drawing

    return 0
```

The same pattern works for other asset kinds:

- **Shaders:** `arca.string("shaders/fade.vs")` + `raylibx.shaders.load_shader_from_memory`.
- **Fonts:** `arca.bytes("fonts/game.ttf")` + `raylibx.text.load_font_from_memory`.
- **Audio:** `arca.bytes("audio/theme.ogg")` + `raylibx.audio.load_music_stream_from_memory`.
- **Raw data:** `arca.ptr` + `arca.size` for C APIs that take `(pointer, length)`.

### 4. Build the single executable

```bash
pengu build --profile release
```

In a game project this produces `build/<output_name>` with the assets embedded. No asset folder is
needed at runtime.

> [!NOTE]
> “Single executable” means **no extra game data files**. The binary still dynamically links the
> operating system's graphics stack (on Linux: OpenGL, X11, and friends), exactly like a normal
> raylib build. Use `embed = false` while iterating on assets if you prefer loading them from disk
> and replacing them without recompiling.

---

## <a id="platform-notes"></a>🖥️ Platform notes

### Linux

- Install X11 and OpenGL development packages; the binding links `GL`, `dl`, `rt` and `X11`.
- A static `lib/libraylib.a` is preferred. If you use a system raylib, make sure `-lraylib` and
  the headers are discoverable.
- If the executable cannot find `libraylib.so` at runtime, either use the static archive or add
  the library directory to `LD_LIBRARY_PATH`.

### macOS

The binding links only `raylib`; add the frameworks yourself in `pengu.toml`:

```toml
[build]
ldflags = [
  "-framework", "Cocoa",
  "-framework", "OpenGL",
  "-framework", "IOKit",
  "-framework", "CoreVideo",
]
```

### Windows

The raw binding already declares `raylib`, `opengl32` and `gdi32` for you. Use a raylib build that
matches your compiler (MinGW with GCC, or the MSVC library with MSVC). If you use the raylib DLL,
ship it next to the `.exe`.

---

## <a id="troubleshooting"></a>🩺 Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Failed to open file: [resources/...]` | Path is relative to the process cwd, which is the project root | Prefix it with `examples/<category>/` in this repo, or `assets/` in your game; or embed it with `arca`. |
| `Cannot resolve imported module 'raylib'` | Dependency not installed, or running outside the project root | `pengu add … --trust` and run `pengu` from the directory containing `pengu.toml`. |
| `undefined reference to 'GuiLabel'` / `GuiSetStyle` | `c/raygui_impl.c` is missing from the installed binding | Update the binding, or re-add it with `--trust`. |
| `undefined reference to 'msf_gif_begin'` | `c/msf_gif_impl.c` is missing | Same as above; this glue is required by `core_screen_recording`. |
| `E0014: 'with:' block construction…` when passing a builder to a call | A multi-line `with:` block is not valid as an argument | Assign it to a typed variable first, or use the one-line form `with x is 1, y is 2`. |
| `error: expected expression before ';'` with an empty list | On PenguScript 2.14, `is []` can generate invalid C for an empty list | Write the element type: `var xs as list of T is list of T`. |
| `weave main` not found by `pengu run` | The example uses an `entry` weave | Use `weave main into int:` for a standalone script. |
| Linker cannot find `raylib` | `lib/libraylib.a` missing and no system raylib | `pengu run build.pengu` inside the binding, or set `RAYLIB_SRC`. |

> [!TIP]
> The fastest way to diagnose a bad asset path is to run the program from the project root and
> look at raylib's `FILEIO` warning. It prints the exact path it tried to open.

---

## <a id="development"></a>🛠️ Development

Useful commands while working on the binding itself:

```bash
# Type-check the project entry
pengu check

# Type-check the whole wrapper layer as one unit
pengu check --entry pengu/raylibx.pengu

# Compile and run a known-good example (smoke check)
pengu run examples/core/core_basic_window.pengu

# Regenerate the API reference pages
python3 tools/gen_docs.py

# Report pages that would change, without writing
python3 tools/gen_docs.py --check
```

The generated raw bindings come from the headers in [`include/`](include/) via `pengu bind`. Do not
hand-edit `pengu/*.d.pengu`; change the header, regenerate, and keep the wrapper layer in sync.

Wrapper design rules live in [`docs/WRAPPER_CONVENTIONS.md`](docs/WRAPPER_CONVENTIONS.md). Measured
raylib behaviour and the traps the wrappers work around live in
[`docs/NOTES.md`](docs/NOTES.md).

> [!TIP]
> Found a broken example? Run it from the repository root and include the full command plus the
> `pengu run` output in the issue — the `FILEIO`/`SHADER` lines usually identify the problem.

### Project layout

```text
raylib-pengu/
├── pengu/
│   ├── raylib.d.pengu          # 1:1 raylib declarations
│   ├── raymath.d.pengu         # 1:1 raymath declarations
│   ├── raygui.d.pengu          # 1:1 raygui declarations
│   ├── raylib_pengu.d.pengu    # raw facade
│   ├── raylibx/                # wrapper families
│   ├── raylibx.pengu           # wrapper facade
│   └── raymathx.pengu, rcamerax.pengu, rayguix.pengu, rlglx.pengu
├── include/                    # C headers used by the bindings
├── c/                          # glue C compiled into the consumer bundle
├── lib/                        # libraylib.a (built by build.pengu)
├── examples/                   # 226 standalone example programs
├── docs/                       # generated bindings + wrapper reference
├── build.pengu                 # native raylib build script
└── pengu.toml                  # project configuration
```

---

## <a id="documentation"></a>📚 Documentation

| Page | What is inside |
|---|---|
| [`docs/README.md`](docs/README.md) | The two-layer map and how to navigate the reference |
| [`docs/bindings/`](docs/bindings/) | Every raw C symbol, generated from the headers |
| [`docs/wrappers/`](docs/wrappers/) | The PenguScript API: functions, methods, `maybe` contracts |
| [`docs/NOTES.md`](docs/NOTES.md) | Measured raylib behaviour, decisions and traps |
| [`docs/WRAPPER_CONVENTIONS.md`](docs/WRAPPER_CONVENTIONS.md) | The design contract for new wrappers |
| [raylib cheatsheet](https://www.raylib.com/cheatsheet/cheatsheet.html) | The C API this binding mirrors |
| [PenguScript](https://github.com/pengus-lang/penguscript) | The language, toolchain and standard library |

---

## <a id="license"></a>📜 License and credits

The binding and wrapper code in this repository are **MIT licensed** — see [`LICENSE`](LICENSE).

It stands on the shoulders of:

- **[raylib](https://www.raylib.com/)** by Ramon Santamaria and contributors (zlib/libpng).
- **[raygui](https://github.com/raysan5/raygui)**, **[reasings](https://github.com/raysan5/raylib/blob/master/examples/shapes/reasings.h)** and the upstream raylib examples.
- **[msf_gif](https://github.com/notnullnotvoid/msf_gif)** for the GIF encoder used by the screen-recording example.
- **[PenguScript](https://github.com/pengus-lang/penguscript)** for the language and toolchain.

The translated examples keep the license and attribution notes from their upstream raylib versions.

---

<div align="center">

**Happy hacking — and have fun rendering penguins in raylib! 🐧🎨**

</div>
