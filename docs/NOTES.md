# Notes, decisions and traps

This page carries the knowledge that used to live in the Phase-1 plans: the decisions that govern
the whole wrapper layer, the PenguScript traps the wrappers were written around, and the measured
behaviour of raylib that no header documents. The reference pages next to it are generated from
the source by `pengu doc`; this page is maintained by hand.

- [The two layers](#the-two-layers)
- [Decisions that govern the layer](#decisions-that-govern-the-layer)
- [PenguScript traps](#penguscript-traps)
- [Measured raylib traps](#measured-raylib-traps)
- [Toolchain commands worth knowing](#toolchain-commands-worth-knowing)

---

## The two layers

| Layer | Files | Written by | Contains |
|---|---|---|---|
| **1 — bindings** | `pengu/<name>.d.pengu` | `pengu bind` from the C headers in `include/` | `declare`, `rune`, `omen`, `const`, `alias`: a 1:1 C surface. Never edited by hand. |
| **2 — wrappers** | `pengu/<name>.pengu`, `pengu/raylibx/*.pengu` | hand-written | `weave` and `enchanting` only: the surface a Pengunic program calls. |

A layer-2 file **never** contains `include`, `link`, `declare`, `insignia` or `antiquus`. The one
piece of C in the project is `c/raygui_impl.c`, which exists because raygui is a single-header
library that needs `RAYGUI_IMPLEMENTATION` in exactly one translation unit; the build compiles
`c/*.c` of every installed binding into the bundle.

Nothing is re-exported: PenguScript's `@export` names a **C symbol**, not a module member, so the
`raylibx` facade does not make its families reachable as `raylibx.text.foo`. The call form is an
import alias:

```pengu
import raylibx.text as text

weave main into int:
    var parts as list of string is calling text.split_text with "a,b", ","
    return 0
```

---

## Decisions that govern the layer

Numbered as they were when the plans still existed, so citations elsewhere in the source keep
resolving.

| # | Decision | Why |
|---|---|---|
| D4 / D16 | **Families live in a subpackage**: `pengu/raylibx/<family>.pengu`, module name `raylibx.<family>`, next to the facade `pengu/raylibx.pengu`. | An earlier note claimed the subpackage did not resolve; it was wrong, and the cause of the error it blamed was `pengu expand` resolving against the current directory. Verified: the subpackage checks clean and builds. |
| D5 | **Method names are global per type.** `enchanting` methods carry no module prefix, so one method name may exist once per receiver type across the whole layer. | Two families cannot both define `Vector2.draw`. The facade is the integration check: running it in one process is what catches a collision and the order dependence that a per-family run hides. The precedent that same-name methods on *different* types are fine is `raylibx.audio`, where four receiver types share `is_valid`, `play` and `stop`. |
| D9 | **The subjecthood rule decides a function's shape.** A function whose first argument really is the subject becomes a method on it; the rest stay module-level. raylib marks many of these with a `V` suffix (`DrawCircleV` → `center.draw_circle`), and a function whose first argument is a `Rectangle` becomes a `Rectangle` method (`rec.draw`). | It is the mechanical form of the contract's "natural receiver" criterion, and it keeps the split predictable instead of a matter of taste. |
| D19 | **No balanced-helper wrappers.** `BeginDrawing`/`EndDrawing`, `rlBegin`/`rlEnd` and `rlPushMatrix`/`rlPopMatrix` stay binding calls or symmetric module functions. | PenguScript lambdas have **no closures**, so a helper that runs a caller's body between two C calls cannot be written; and an immediate-mode body needs the caller's state anyway. |
| D20 | **A qualified type is legal in a declaration but broken as a cast or `transmute` target.** `let first as ref to raylib.Matrix is sigil of (items at 0)` compiles; `transmute raw to raylib.Matrix` does not. | Measured. Route through an unqualified pointer (`ref to void`) or declare a typed local and take its address. |
| D22 | **Enum parameters are not checked.** A parameter typed as an `omen` accepts any integer, including a different enum's constant. | Measured on `pengu 2.4.0`. Consequence for the layer: a wrapper is justified by a boundary it crosses or by a shorter, self-documenting call — **never** by "type safety", because there is none to add. The omen in a signature is documentation. |
| D23 | **A `let` inside a block declares a *new* binding; it does not assign the outer one.** A pointer computed inside an `if` guard must be declared `var` outside and set with `set x is …` inside. | Found by a crash: `let raw … null_void` followed by `let raw … transmute …` inside a guard emitted **two** C variables, so the outer one stayed null and every non-empty slice was passed as a NULL pointer. The compiler is silent about it. |
| — | **One module per binding, one family per subject.** The 14 `raylibx` families split the single `raylib.d.pengu` binding; `raymathx`, `rcamerax`, `rlglx` and `rayguix` wrap their own bindings and live at `pengu/`. | `raylib.d.pengu` alone is over 2000 lines; a monolithic wrapper would be unreviewable. |

---

## PenguScript traps

Everything here was measured on `pengu 2.4.0` while writing the wrappers.

| Trap | Detail |
|---|---|
| **Reserved words** | `size`, `bytes`, `some`, `identity` cannot be identifiers. `size` belongs to `size of`, and as a parameter name it fails with `E0000 Syntax error: unexpected ','` at the *comma after it* — which is why the billboard methods spell it `quad_size`. Bindings get away with `size` because `declare` lines are parsed differently. |
| **No closures** | A lambda body cannot reference an enclosing local (`E0004`); `pengu check` can miss it through name shadowing while `expand` rejects it. |
| **No pointer arithmetic** | `ref to char + int` is `E0005 Arithmetic operator 'add' requires numeric type`. |
| **Slices are read-only views** | `set (view at i) is v` is a syntax error. To write into foreign memory, take a slice from `ffi.slice_of_bytes_from_ptr` and assign one byte at a time: `set essence of (sigil of (buffer at i)) is value`. `(slice at i)` already yields the element value, so it takes no `essence of` on the right. |
| **No `memcpy`** | `memcpy_raw` and `memset_raw` are documented in the language guide but **do not exist** in `std.ffi`. `ffi.list_*_from_ptr` **copies**, which is what makes it safe to free the source immediately. |
| **Raw strings** | `r"""…"""` is required for GLSL: `{` interpolates inside ordinary strings, and `\n` inside a *raw* string is a literal backslash-n, so newlines must be real. |
| **`maybe T` from an alias** | A binding call returning a type alias cannot initialise a `maybe` of that type directly (`E0005`); bind a plain nominal value first. |
| **Dotted import resolution** | `import components.player` resolves against the manifest's `src_dir` (`src_dir = "pengu"` here), **not** against the importing file's directory. |
| **`pengu expand` resolves against the current directory** | `pengu expand pengu/raylibx/x.pengu` fails from the repository root while `pengu check --entry pengu/raylibx/x.pengu` is clean. Use `check`/`build`/`test`, or run `expand` from inside `pengu/`. |
| **Omen qualification** | Omens declared in `rlgl.d.pengu` are `rlgl.*` (`rlgl.RL_BLEND_ALPHA`); qualifying them with `raylib.` is `E0022`. |

---

## Measured raylib traps

None of these is in a header. Each one is asserted or documented where it bites, and the wrapper
tests are written around them.

| Trap | Measurement |
|---|---|
| **The random generator starts from a fixed seed** | Two runs of the same unseeded program print the same sequence (`6 3 6 1 4 3`). Call `raylib.SetRandomSeed` or every run repeats. |
| **`GetRandomValue` is inclusive and swaps silently** | `GetRandomValue(10, 1)` answers inside `[1, 10]`. |
| **`LoadRandomSequence` does not swap** | `LoadRandomSequence(3, 5, 1)` returns `9 8 7` — values **outside both bounds**. It also returns a **null pointer** when asked for more values than the range holds, or for a negative count. `raylibx.random.sequence` turns all of that into `none`. |
| **raygui keeps its GUI font in a process global, initialised once** | After a window is destroyed and another created, `GuiGetTextWidth` returns `0` and every widget draws text with a dead texture, until `GuiSetFont(GetFontDefault())`. `GuiLoadStyleDefault` does **not** rebind it. |
| **`GuiLoadStyleFromMemory` does not validate its buffer** | Eight bytes beginning with the valid `.rgs` magic `rGS ` segfault the process; the same eight bytes of arbitrary junk survive, which is what makes it easy to miss. A wrapper cannot validate a style file, so this one is deliberately not wrapped. |
| **`GuiIconText` returns a static buffer** | Two consecutive calls both report the second call's text; the wrapper copies immediately, which is why its result is an owned `string`. |
| **`rlgl` is not pure CPU** | `rlGetVersion` and `rlGetPixelFormatName` work with no window, but `rlPushMatrix` **crashes** without one: rlgl's state is initialised by `rlglInit` inside `InitWindow`. |
| **3D projection needs a window to have existed** | `GetWorldToScreen` and `GetScreenToWorldRay` return `NaN` components — silently — before any window exists, because they divide by a screen size of `0`. The `_ex` forms take the viewport explicitly and work headless; they are also what a render-to-texture pass needs. The screen size survives `CloseWindow`, so this only shows in a program that never opens one. |
| **The 2D camera and the view matrices are pure maths** | `GetWorldToScreen2D`, `GetScreenToWorld2D`, `GetCameraMatrix2D`, `GetCameraMatrix`, `GetWorldToScreenEx` and `GetScreenToWorldRayEx` are correct with no window, and `GetWorldToScreen2D`/`GetScreenToWorld2D` are an exact round trip. |
| **Shared process state makes test order matter** | `InitWindow` initialises GLFW, which enumerates a gamepad (`IsGamepadAvailable` is false before a window and true after) and loads the default font, which calls `SetShapesTexture` (a shape's texture rectangle is `1×1` before a window and the font's `2×8` after). The families' tests branch on the state instead of assuming a virgin process. |
| **`GetCameraMatrix` is `Camera3D.view_matrix`** | The binding function is superseded by the wrapper method (the same value by a shorter name), which is why the projection helpers are documented as camera methods. |

---

## Toolchain commands worth knowing

| Command | Use |
|---|---|
| `pengu check --entry pengu/<file>.pengu` | type-check one module; the fastest loop |
| `pengu test --entry pengu/<file>.pengu` | compile and run that module's integrated tests |
| `pengu build --entry pengu/raylibx.pengu` | build the whole layer into one bundle, which is what catches symbol and state collisions |
| `pengu doc --entry <file> --output <dir>` | regenerate the reference pages in this directory from the `##` doc comments |
| `python3 tools/check_bindings.py --repo .` | verify every binding still covers the C header it came from |
| `python3 tools/check_binding_symbols.py` | find declares the installed `libraylib` does not export (the repository header is 6.1-dev; the installed library is 6.0.0) |
