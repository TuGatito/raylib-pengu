# Plan: raylibx — master plan and index

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu` (619 `declare`, 35 `rune`, 21 `omen`, 14 `alias`, 40 `const`; 2019 lines)
- Wrapper target: `pengu/raylibx.pengu` (façade) **plus** `pengu/raylibx_<family>.pengu` (one flat file per family, siblings of the binding)
- Dependencies: `import raylib`, `import raymath` (where a family measures or builds vectors), `import std.ffi` (families that cross the string boundary)
- Sub-plans: `docs/plans/raylibx_<family>.md`, one per row of the family tables below
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

This master plan fixes what the eleven family plans must share. It is deliberately **not** an enumeration of the 619 symbols: that is what each `docs/plans/raylibx_<family>.md` is for (contract §2, "la enumeración por símbolo es Fase 1"). What follows is the architecture, the naming and skip policy specific to raylib, the cross-family collision registry, and the verified cross-cutting patterns.

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete**. `include/raylib.h` declares exactly 619 `RLAPI` functions and the binding declares exactly 619; the counts match and the name sets are the same shape as the header's own sections. | Counted both sides. `raymath`-style gating does not apply here: everything in `raylib.h` is consumer API, and the camera/gesture helpers that `rcamera.h`/`rgestures.h` gate behind a macro are declared in *this* binding (which is why `rgesturesx` was archived and its functions land here). |
| D2 | **`raylibx` is a façade plus family modules**, not one file: `pengu/raylibx.pengu` contains only a module docstring and the `import` lines; every symbol lives in a **flat** sibling file `pengu/raylibx_<family>.pengu`. | `raylib.d.pengu` is 2019 lines for *declarations only*; a single wrapper over 619 functions with docstrings and tests is far past the manageable module size of `PenguScriptGuideSpanish.md` §3.2. Verified on `pengu 2.4.0`: the façade `import raylibx_window` + `import raylibx_input` makes both families reachable as `raylibx.<fn>` from `import raylibx` alone. |
| D3 | The user writes `import raylib` **and** `import raylibx`; the binding is imported explicitly, not assumed transitive. | Contract §1. The family files themselves import `raylib` (and `raymath`/`std.ffi` when they need it). |
| D4 | **Flat file naming** `raylibx_<family>.pengu`. **No `insignia` is used**: `pengu 2.4.0` already mangles module-level functions with the module name, so two sibling families with the *same* function name emit `raylibx_window_screen_width` and `raylibx_input_screen_width` and coexist. Enchanting methods are emitted as `<Type>_<method>` with **no** module prefix, which is why the method registry (D5) exists. | Verified on `pengu 2.4.0` with two sibling modules declaring both `screen_width` and `is_key_down`: the emitted symbols are `raylibx_window_screen_width` and `raylibx_input_screen_width`. For enchantings the probe used *distinct* names on purpose (`Camera3D_window_probe_len` vs `Camera3D_input_probe_len`) and both survive, confirming that two modules can each enchant the same type. Using the *same* method name in both modules emits `Camera3D_probe_len` twice — the exact hazard D5 prevents. |
| D5 | **Global method-name registry, one name per type, across all family files.** While work on `raylibx` is in progress, `pengu/raylibx.pengu` imports only the family files already wrapped, and an empty façade is a valid intermediate state. | Verified on `pengu 2.4.0`: two modules *can* each add methods to the same type, but two methods with the same name emit the same C symbol twice and the C build fails with `redefinition of '<Type>_<method>'`, while `pengu check` does not catch it (this is the same hazard recorded in `WRAPPER_CONVENTIONS.md` §1 for the `Quaternion`/`Vector4` alias). A `Draw*` function is the natural place for an accidental duplicate, so the rule is: **one name, one module, assigned here**. |
| D6 | Module-level functions are wrapped in the **family that owns the C function**, even when their natural home looks like another family. | `SetGesturesEnabled`/`IsGestureDetected`/`GetGesture*` live in `raylib.d.pengu` and belong to the `input` family, not to a `gestures` family that wraps nothing (D10). Same for `GetClipboardText` (window), `GetColor` (textures/colors) and the file helpers (files). |
| D7 | The `Color` value API (`Color*`, `Fade`, `GetColor`, `SetPixelColor`, `GetPixelColor`) is wrapped as **methods on `raylib.Color`** and module functions in the `colors` family, not duplicated into every drawing family. **A drawing *family file* does not import or call `colors`**: if it needs a colour transform it either calls `raylib.Fade` directly (the binding) or takes the already-transformed `Color` as an argument. `colors` exists for the *user's* convenience, and D2 forbids family-to-family imports. | One owner per symbol (D5/D6), and the wrapper layer is not a library the families consume. |
| D8 | The `raylib.Color` constants (`RAYWHITE`, `LIGHTGRAY`, … the 26 hand-maintained `const`s) are **never wrapped or re-exported**; code uses `raylib.<NAME>`. | Contract §2: they are part of raylib's contract and keep their C spelling. `import raylib` already makes them available. |
| D9 | Every `Draw*` function is a module-level function reading as an **instruction** (`draw_rectangle_rec`, `draw_text_ex`, `draw_cube`), **except** when the C name is `<Shape>V` and the first argument *is* the shape's anchor — then it becomes a method on that type (`DrawCircleV` → `v.draw_circle`, `DrawPixelV` → `v.draw_pixel`, `DrawLineV` → `v.draw_line_to`). | Contract §6.1 with an explicit rule so family plans do not re-litigate it per symbol: `DrawCube(Vector3 position, …)` creates a cube *at* a point, so the point is an argument, not the subject; `DrawCircleV(Vector2 center, …)` draws a circle *whose centre is* the vector. The `<Shape>V` suffix is the mechanical test. |
| D10 | There is **no `gestures` family file**. The eight gesture functions are wrapped inside `input`. | They are input state; a separate file would be a file with eight functions and no theme (the archived `rgesturesx` lesson: the wrapper must wrap its own binding, and these live in `raylib.d.pengu`). |
| D11 | The `Load*` + `Is*Valid` + `Unload*` contract is wrapped as **`maybe T` for the loader and nothing for the unloader**, and every family plan must state the unload call for each resource it loads. | Contract §3 and §8. `LoadFileText` returning `char*` is wrapped as `maybe string` with the owned copy taken *before* `UnloadFileText` (verified: `ffi_string_from_cstr` copies, then `UnloadFileText(text)`). |
| D12 | The `(T* ptr, int count)` families (`DrawLineStrip`, `DrawTriangleFan`, the five `DrawSpline*`, `DrawTextCodepoints`, `LoadFontEx`, `ImageKernelConvolution`, `DrawMeshInstanced`, `TextJoin`, …) take `slice of T`. | Contract §5. Each one needs the empty-slice guard and the single `transmute (sigil of (pts at 0))`; verified to emit one direct C call with no copy. |
| D13 | **String boundaries are uniform**: `string` → `ffi.cstr_from_string`; C `char*` → `maybe string`/`string` via `ffi.string_from_cstr` with the library's own free; C `const char*` returns that raylib owns (`GetClipboardText`, `GetMonitorName`, `GetKeyName`, `GetDirectoryPath`, …) are copied and **not** freed; `TextFormat` (variadic) is not wrapped. | Contract §7 and §8. Verified end to end on `LoadFileText`. The distinction between "raylib owns it" and "the caller frees it" is read from each header comment and recorded per function in the family plans. |
| D14 | `TraceLog` (variadic), the callback setters (`SetTraceLogCallback`, `SetLoadFileDataCallback`, …), `@noreturn`-style aborts, `MemAlloc`/`MemRealloc`/`MemFree`, and the VR/automation entry points are **not wrapped**. | Contract §9 rows 4–8: variadic C cannot be built from PenguScript, callbacks have no closures here, `MemFree` belongs with the unload policy, and VR/automation are outside the 20 % that matters. Each is listed with its reason in its family plan. |
| D15 | `raygui` and `raylib_pengu` stay out of scope. | `raygui.d.pengu` is a separate binding with its own wrapper story (`rayguix`), and `raylib_pengu.d.pengu` is a hand-written re-export facade, not a binding. Neither belongs to this plan. |
| D19 | **PenguScript lambdas have no closures, so no wrapper in this project may offer a callback-based *balanced* API.** Measured while planning `drawing`: a lambda body referencing an enclosing local fails with `E0004`, and `pengu check` does **not** always report it — when the local's name coincides with a parameter name used at module scope, `check` accepts the file while `pengu expand` rejects it. | A helper that takes the body as a lambda would pass `check` and fail at build time, or silently resolve to the wrong variable. Any future family tempted by a callback-shaped wrapper (a scoped resource, an iterator, an event handler) must first verify that the callback needs no caller state; otherwise it takes explicit begin/end plus `defer`. Recorded here so the experiment is not repeated family by family. |
| D20 | **A qualified type is fine in a declaration but broken as a `transmute`/cast target.** `let first as ref to raylib.Image is sigil of (icons at 0)` emits valid C (`SetWindowIcons(first, icons.len)`), while `transmute x to ref to raylib.Image` emits a cast that names a type the C compiler does not know. | Found while wrapping `SetWindowIcons` in `window`. It refines D19: the `void*` detour of `shapes`/`images` is still the right fix when a cast is unavoidable, but **a typed local removes the need for the cast entirely** and reads better. Any wrapper that needs `ref to T` from a slice should declare the local rather than transmute. |
| D21 | **The project is no longer compile-only: this machine has a display (`DISPLAY=:0`), so a test can open a real window** with `raylib.InitWindow` from the binding and assert against live behaviour. Measured: `InitWindow` succeeds, frames can be drawn and presented, and repeated `InitWindow`/`CloseWindow` cycles in one process work. | Found while planning `window`. It **supersedes `raylibx_drawing`'s D9**, which had concluded "no CI-testable behaviour" from a headless measurement; that plan and its test suite are corrected. From here on, a family that skips a window-bound surface must say whether it checked this, and `InitWindow`/`CloseWindow` are called from the binding for setup because §9 row 8 keeps them out of the wrapper. |
| D22 | **PenguScript does not check enum parameters: an `omen`-typed parameter accepts any integer.** A minimal probe on `pengu 2.4.0` passes `raylib.MOUSE_BUTTON_LEFT` and even a raw `42` to a parameter typed `raylib.KeyboardKey` with no diagnostic. | Measured while evaluating `rlglx`, and it corrects a claim in `raylibx_input`'s D2. The consequence for the project is a rule: **a wrapper is justified by a boundary it crosses (string, slice, ownership, `maybe`) or by a shorter, self-documenting call -- never by "type safety", because there is none to add.** An enum in a wrapper signature is documentation that reads well at the call site; it does not enforce anything, and a family whose only argument is enum restoration must justify itself on token count instead. |
| D23 | **A `let` inside a block declares a *new* binding; it does not assign to the outer one.** A pointer computed inside a `if`-guard must be declared `var` outside and set with `set x is …` inside, or the outer variable keeps its initial value. | Found by a crash while testing `rlglx`: the pattern `let raw as ref to void is calling ffi.null_void` followed by `if (slice.length) > 0:` / `let raw as ref to void is transmute …` emitted **two** C variables, so the outer one stayed null and every non-empty slice was passed as a NULL pointer. The same latent bug was present in `raylibx.textures`' `update` and `update_rec`, where no test had ever exercised it. Both are fixed, and the rule is recorded because the compiler is silent about it. |
| D18 | **The `input` family was narrowed during Phase 1b.** Of its 47 functions only **28 are wrapped**; the 19 left out are the zero-argument getters that cannot fail (`GetMousePosition`, `GetMouseDelta`, the wheel getters, `GetTouchX/Y`, `GetTouchPosition`, `GetTouchPointCount`, the five gesture value getters), plus `IsGamepadAvailable`, `GetGamepadAxisCount`, `SetGamepadVibration` and `SetExitKey`. | Contract §9 rows 1 and 160, and its ordering row 417, which explicitly names `GetTouchPointCount` as a function not to wrap. The input family's value turned out to be **type restoration** — the binding flattens every enum parameter to `int` — plus the `maybe` sentinels, and nothing else. This amends the family description in the table above, which listed `GetMouse*`/`GetTouch*`/`GetGesture*`; `docs/plans/raylibx_input.md` D3 has the full reasoning. |
| D17 | **A `declare` existing in the header does not mean the installed library exports it.** The repo header is raylib **6.1-dev**; `/usr/lib/libraylib.so` is **6.0.0**, and **22 declared functions are missing from the library** (3 `files`, 10 `images`, 1 `textures`, 7 `shapes`, 1 `text`). Every family plan must therefore run `python3 tools/check_binding_symbols.py pengu/<binding> <library>` before claiming case (a), and must list the functions it cannot wrap for this reason. | Discovered while implementing `raylibx_shapes`: `pengu check` and `pengu build` were both clean and the failure appeared only at link time (`referencia a 'GetSplinePointBezierQuadratic' sin definir`). The tool was added to the repo so the check is one command instead of a bug hunt. `raylibx_colors` and `raylibx_files` were re-audited and call no missing symbol. |
| D16 | **(Corrected in v0.1.3.) Family files live in the `pengu/raylibx/` subpackage** as modules `raylibx.<family>`, with `pengu/raylibx.pengu` as the facade. The earlier v0.1.2 version of this decision claimed the subpackage was rejected by the resolver; **that was wrong**, and it was corrected by re-measuring on the same `pengu 2.4.0`: all thirteen families in `pengu/raylibx/` resolve `import raylib`, `pengu check` is clean, `pengu build` links (218 KB, no undefined references), and the full 261-test suite runs through the facade. The likeliest cause of the original error is that the probe producing it lived in `src/`, which is **not** a configured root (`src_dir = "pengu"`), where `import raylib` cannot resolve by design. | Verified on `pengu 2.4.0`: a module one directory deeper cannot resolve `import raylib` — `Cannot resolve imported module 'raylib'` with `Ensure 'raylib.pengu' exists in source directory …`, because the binding lives in the `src_dir` root and the resolver does not walk back up. Adding the subdirectory to `src_dirs` in `pengu.toml` does **not** fix it either. The flat layout works. |

### 🏗️ Architecture

```
pengu/
├── raylib.d.pengu              ← binding (capa 1, no se toca)
├── raylibx.pengu               ← fachada: docstring + los imports de familia, cero símbolos
├── raylibx_window.pengu        ← window      (InitWindow, monitores, timing, portapapeles)
├── raylibx_input.pengu         ← input       (teclas, ratón, gamepad, táctil, las 8 funciones de gestos)
├── raylibx_drawing.pengu       ← drawing     (pares Begin/End de frame y modo, ClearBackground)
├── raylibx_shapes.pengu        ← shapes      (formas 2D y splines)
├── raylibx_shapes3d.pengu      ← shapes3d    (primitivas 3D)
├── raylibx_text.pengu          ← text        (fuentes, DrawText*, MeasureText*, helpers Text*)
├── raylibx_textures.pengu      ← textures    (Texture, RenderTexture)
├── raylibx_images.pengu        ← images      (Image y sus 49 mutadores, GenImage*, LoadImage*)
├── raylibx_colors.pengu        ← colors      (valores Color, Fade, GetColor)
├── raylibx_models.pengu        ← models      (Model, Mesh, Material, Animation, colisiones 3D)
├── raylibx_audio.pengu         ← audio       (Wave, Sound, Music, AudioStream)
├── raylibx_files.pengu         ← files       (sistema de ficheros, compresión, hashes)
└── raylibx_shaders.pengu       ← shaders     (Shader, uniforms, pantalla↔mundo)
```

Rules that follow from D2, D4 and D16:

- `raylibx.pengu` has **no `enchanting`, no `weave`, no `const`**. Its docstring states the module relationship (`raylib` binding + `raylibx` wrapper) and lists the families.
- Each family file is self-contained: its own `import raylib` (plus `import raymath` / `import std.ffi` if it needs them), its own docstring, its own `enchanting` blocks, its own inline tests.
- A family file **never** imports another family file. Shared helpers that two families need go in the family that owns the underlying C function (D6/D7).
- Adding a family means adding one `import` line to the façade; nothing else changes.

### 📛 Global method registry (collision control)

This is the table D5 exists for. Fase 1b fills the per-family method lists, and every name is checked against this registry before it is committed. The rows below are the **planned owners**; a family plan may add rows but may not reuse a name already owned for the same type.

| Type | Owner family | Methods already assigned | Notes |
|---|---|---|---|
| `raylib.Color` | `colors` ✅ **closed** | `is_equal`, `to_int`, `to_normalized`, `to_hsv`, `with_alpha`, `tint_with`, `brighten_by`, `contrast_with`, `blend_over`, `lerp_to` + rituals `from_hex`, `from_int`, `from_hsv`, `from_normalized` | closed by `raylibx.colors`; **no other family may add a `Color` method** |
| `raylib.Image` | `images` ✅ **closed** | `to_format`, `to_power_of_two`, `crop`, `crop_to_alpha`, `clear_alpha`, `apply_alpha_mask`, `premultiply_alpha`, `blur_gaussian`, `convolve`, `resize`, `resize_nearest`, `resize_canvas`, `generate_mipmaps`, `dither`, `flip_vertical`, `flip_horizontal`, `rotate`, `rotate_cw`, `rotate_ccw`, `tint`, `invert`, `to_grayscale`, `adjust_contrast`, `adjust_brightness`, `replace_color`, `copy`, `region`, `channel`, `colors`, `palette`, `alpha_border`, `color_at`, `clear`, `draw_pixel`, `draw_pixel_at`, `draw_line`, `draw_line_between`, `draw_line_thick`, `draw_triangle`, `draw_triangle_outline`, `draw_triangle_fan`, `draw_triangle_strip`, `draw_rectangle`, `draw_rectangle_at`, `draw_rectangle_rec`, `draw_rectangle_outline`, `draw_circle`, `draw_circle_at`, `draw_circle_outline`, `draw_circle_outline_at`, `draw_text`, `draw_text_ex` | closed by `raylibx.images`: 52 methods (25 transforms, 20 draws, 7 readers/producers). **No other family may add an `Image` method** |
| `raylib.Texture2D` | `textures` ✅ **closed** | `draw`, `draw_at`, `draw_ex`, `draw_rec`, `draw_pro`, `draw_npatch`, `update`, `update_rec`, `generate_mipmaps`, `set_filter`, `set_wrap`, `is_valid` | closed by `raylibx.textures`; enchanted on the nominal `raylib.Texture` because `Texture2D` is its alias. **No other family may add a `Texture` method** |
| `raylib.RenderTexture2D` | `textures` ✅ **closed** | `is_valid` | closed by `raylibx.textures`. **`begin`/`end` are deliberately left unassigned**: `BeginTextureMode`/`EndTextureMode` belong to `drawing`, which should expose them as methods on this type. `draw` is unnecessary: the `texture` field already carries the full `Texture` surface |
| `raylib.Font` | `text` ✅ **closed** | `draw`, `draw_pro`, `draw_codepoint`, `draw_codepoints`, `measure` | closed by `raylibx.text`; the glyph queries (`font_glyph_index`, `font_glyph_info`, `font_glyph_atlas_rec`) are **module functions**, not methods. **No other family may add a `Font` method** |
| `raylib.Model` | `models` ✅ **closed** | `is_valid`, `bounding_box`, `draw`, `draw_ex`, `draw_wires`, `draw_wires_ex`, `set_mesh_material`, `update_animation`, `update_animation_ex`, `is_animation_valid` | closed by `raylibx.models`. **`load_model_from_mesh` does not return `maybe`**: measured, raylib does not validate the mesh and a zeroed-mesh model reports valid (D3). **No other family may add a `Model` method** |
| `raylib.Mesh` | `models` ✅ **closed** | `upload`, `update_buffer`, `draw`, `draw_instanced`, `bounding_box`, `generate_tangents`, `export`, `export_as_code` | closed by `raylibx.models`. The reserved name `tangents` becomes `generate_tangents`, because a `void` mutator named `tangents` reads like a getter. **No other family may add a `Mesh` method** |
| `raylib.Material` | `models` ✅ **closed** | `set_texture` | closed by `raylibx.models`. **No other family may add a `Material` method** |
| `raylib.ModelAnimation` | `models` ✅ **no methods** | — | every animation operation takes the **model** as its subject (`model.update_animation`, `model.is_animation_valid`), so the type gains no methods. `load_animations`/`unload_animations` are module-level because an animation exists before the model it is applied to (D4) |
| `raylib.Shader` | `shaders` ✅ **closed** | `is_valid`, `location`, `location_attrib`, `set_float`, `set_int`, `set_vec2`, `set_vec3`, `set_vec4`, `set_matrix`, `set_texture`, `set_floats`, `set_ints` | closed by `raylibx.shaders`: 12 methods. The reserved name `set_value` is **released** in favour of the typed family, because one generic method would keep the `void*` and the `SHADER_UNIFORM_*` enum at the call site. **No other family may add a `Shader` method** |
| `raylib.Wave` | `audio` ✅ **closed** | `is_valid`, `copy`, `crop`, `to_format`, `export`, `export_as_code`, `samples` | closed by `raylibx.audio`. `samples` returns a **view** released by `unload_wave_samples` (D8). **No other family may add a `Wave` method** |
| `raylib.Sound` | `audio` ✅ **closed** | `is_valid`, `update`, `play`, `stop`, `pause`, `resume`, `is_playing`, `set_volume`, `set_pitch`, `set_pan` | closed by `raylibx.audio`. **`load_sound_from_wave` resamples**: the sound's `frameCount` is the device's, never the wave's (D9). **No other family may add a `Sound` method** |
| `raylib.Music` | `audio` ✅ **closed** | `is_valid`, `play`, `stop`, `pause`, `resume`, `is_playing`, `update`, `seek`, `set_volume`, `set_pitch`, `set_pan`, `time_length`, `time_played` | closed by `raylibx.audio`. Looping is the `Music.looping` **field**, not a method, because raylib 6.0 has no setter for it (D11). **No other family may add a `Music` method** |
| `raylib.AudioStream` | `audio` ✅ **closed** | `is_valid`, `update`, `is_processed`, `play`, `pause`, `resume`, `is_playing`, `stop`, `set_volume`, `set_pitch`, `set_pan` | closed by `raylibx.audio`. Building one needs the audio device, so `load_audio_stream` returns a `maybe` (D7). **No other family may add an `AudioStream` method** |
| `raylib.Camera2D` | `rcamerax` ✅ **closed** | `view_matrix`, `to_screen`, `to_world` | **Corrected**: this row used to say `to_world`/`to_screen` "are not wrapped: they are two-argument getters that already read well from the binding", and it assigned the type's methods to `drawing`. The reservation was never executed — `drawing` has no `enchanting` block at all — and the receiver test decides it the other way: as a method the camera **leaves** the argument list, so `camera.to_screen with position` is shorter than the binding call, which is §9 criterion 1 satisfied rather than failed. Closed by `rcamerax`'s appendix (its D13–D16). **`begin`/`end` released**: `EndMode2D` takes no receiver, so the pair stays symmetric module functions in `raylibx_drawing` |
| `raylib.Camera3D` | `rcamerax` ✅ **closed** | `forward`, `up`, `right`, `view_matrix`, `projection_matrix`, `move_*`, `yaw`, `pitch`, `roll`, plus the appendix's `to_screen`, `to_screen_ex`, `to_world_ray`, `to_world_ray_ex`, `draw_billboard`, `draw_billboard_rec`, `draw_billboard_pro` | **`begin`/`end` released**: same reason as `Camera2D`. **`raymathx`/`rcamerax` own the whole camera surface** — `raylibx` must not re-add any of it. The three billboards are `rmodels` functions in the C headers, but the camera is their first parameter and therefore the receiver (§9 criterion 2), so they belong here; `raylibx.models` reassigned them by its D12 |
| `raylib.Vector3` | `shapes3d` ✅ **closed** | `draw_point`, `draw_cube`, `draw_cube_wires`, `draw_plane` (the `V`-anchored names plus the two non-`V` subject names) | closed by `raylibx.shapes3d`; the sphere and cylinder families stayed module-level because raylib has no `DrawSphereV`/`DrawCylinderV`. **No other family may add a `Vector3` draw method**, and `raymathx` keeps all the arithmetic |
| `raylib.Rectangle` | `shapes` ✅ **closed** | `draw`, `draw_pro`, `draw_gradient`, `draw_outline`, `draw_rounded`, `draw_rounded_outline`, `contains_point` | closed by `raylibx.shapes`; **no other family may add a `Rectangle` method** |
| `raylib.Vector2` | `shapes` ✅ **closed** | `draw_pixel`, `draw_line_to`, `draw_line_ex`, `draw_line_bezier`, `draw_line_dashed`, `draw_circle`, `draw_circle_gradient`, `draw_circle_lines`, `draw_circle_sector`, `draw_circle_sector_lines`, `draw_ellipse`, `draw_ellipse_lines`, `draw_ring`, `draw_ring_lines`, `draw_poly`, `draw_poly_lines`, `draw_poly_lines_ex`, `draw_rectangle`, `draw_triangle`, `draw_triangle_lines` | closed by `raylibx.shapes` (the `<Shape>V` rule of D9). **`raymathx` owns every arithmetic method and no other family may add a `Vector2` method** |

| `raylib.Vector4` | (none) | — | **`raymathx` owns every 4D arithmetic method and `identity`; `raylibx` adds none** |
| `raylib.Quaternion` | (none) | — | **`raymathx` owns every quaternion method (`mul`, `slerp_to`, `to_matrix`, …) and its factories are module-level; `raylibx` adds none** |
| `raylib.Color` (again) | — | — | listed once; the second mention is a warning that `Color` is the easiest accidental duplicate |

**Verification procedure for every family plan** (mechanical, from `WRAPPER_CONVENTIONS.md` §1):

1. Declare the family's methods in its `.md`.
2. Diff the resulting `<Type>_<method>` symbol set against every other family file already written.
3. Only then write the `.pengu`; `pengu check` will not catch a duplicate, so the diff is the gate.

### 🔧 Cross-family policies

| Policy | Rule |
|---|---|
| Strings in | `let c_x as ref to frozen char is calling ffi.cstr_from_string with x` (contract §7) |
| Strings out, caller frees | copy with `ffi.string_from_cstr`, then the raylib free (`UnloadFileText`, `UnloadUTF8`, `MemFree`), then return the owned copy — **copy before free** (D11) |
| Strings out, raylib owns | copy with `ffi.string_from_cstr` and **do not** free (`GetClipboardText`, `GetMonitorName`, `GetKeyName`, `GetDirectoryPath`, `TextFormat`) |
| Arrays in | `slice of T`, guard the empty case, one `transmute (sigil of (pts at 0))` (D12) |
| Arrays out | `ffi.list_from_ptr of T` (owned, `banish` it) or `slice` from `ffi.slice_from_ptr` only when the pointer outlives the call — the family plan must say which and why |
| Resources | `maybe T` at load, `defer calling raylib.UnloadX with res` at the call site (D11) |
| Lifetime of `ref to T` returns | `Font.recs`, `Font.glyphs`, `Model.meshes`, `Image.data` and friends point **into** the resource; never `banish` them, and never use them after the owner is unloaded (contract §8) |
| Never wrapped | `TraceLog`, `TextFormat`, the callback setters, `MemAlloc`/`MemRealloc`/`MemFree`, VR/automation, `MemFree`-style raw allocation (D14) |

| Random (`SetRandomSeed`, `GetRandomValue`, `LoadRandomSequence`, `UnloadRandomSequence`) | **resolved**: neither of the two options this row proposed was taken — the functions became **family 14 (`random`)**, because they come from `raylib.d.pengu` and an addendum to `raymathx` would have wrapped a different binding. `GetRandomValue` and `LoadRandomSequence` are wrapped (`between`, `sequence`); `SetRandomSeed` is skipped by §9 row 8 and `UnloadRandomSequence` by §9 row 4, because `sequence` owns the array it allocates. Two measured traps are recorded there: the generator's **fixed default seed** (an unseeded program repeats on every run) and `LoadRandomSequence` answering an inverted range with **values outside both bounds** instead of a null pointer. See `docs/plans/raylibx_random.md` |
### 🎁 `maybe T` wrappers

This master plan assigns the **family**, not the per-symbol list. In Fase 1b each family plan must produce the table the contract asks for:

| Family | `maybe` loaders expected | Predicate |
|---|---|---|
| `textures` | `LoadTexture`, `LoadTextureFromImage`, `LoadTextureCubemap`, `LoadRenderTexture`, `LoadRenderTextureEx` | `IsTextureValid`, `IsRenderTextureValid` |
| `images` | `LoadImage`, `LoadImageRaw`, `LoadImageAnim*`, `LoadImageFromMemory`, `LoadImageFromTexture`, `LoadImageFromScreen`, `LoadImageColors`, `LoadImagePalette`, `LoadFontData`-adjacent | `IsImageValid`, or a null/zero-count check for the pointer-returning ones |
| `text` | `LoadFont`, `LoadFontEx`, `LoadFontFromMemory`, `LoadFontFromImage`, `LoadFontData`, `LoadUTF8`, `LoadTextLines` | `IsFontValid`, null or count check |
| `models` | `LoadModel`, `LoadModelFromMesh`, `LoadMaterials`, `LoadModelAnimations`, `LoadMesh`-adjacent | `IsModelValid`, `IsMaterialValid`, `IsModelAnimationValid` |
| `audio` | `LoadWave`, `LoadWaveFromMemory`, `LoadSound`, `LoadSoundFromWave`, `LoadSoundAlias`, `LoadMusicStream`, `LoadMusicStreamFromMemory`, `LoadAudioStream`, `LoadWaveSamples` | `IsWaveValid`, `IsSoundValid`, `IsMusicValid`, `IsAudioStreamValid` |
| `files` | `LoadFileData`, `LoadFileText`, `LoadDirectoryFiles`, `LoadDirectoryFilesEx`, `LoadDroppedFiles`, `LoadAutomationEventList` | null check, or `count > 0` for `FilePathList` |
| `window` | `GetClipboardImage`? (no predicate) | none; documented caveat instead |
| `shaders` | `LoadShader`, `LoadShaderFromMemory` | `IsShaderValid` |

`Gen*` constructors (`GenImageColor`, `GenMeshCube`, `GenTextureMipmaps`) are **not** `maybe`: they are computed values, not external resources (contract §3).

### ✂️ `slice` wrappers (families that need them)

| Family | Slice-shaped C signatures |
|---|---|
| `shapes` | `DrawLineStrip`, `DrawTriangleFan`, `DrawTriangleStrip`, `DrawSplineLinear`, `DrawSplineBasis`, `DrawSplineCatmullRom`, `DrawSplineBezierQuadratic`, `DrawSplineBezierCubic`, `CheckCollisionPointPoly` |
| `shapes3d` | `DrawTriangleStrip3D` |
| `text` | `LoadFontEx`, `LoadFontFromMemory`, `DrawTextCodepoints`, `MeasureTextCodepoints`, `LoadUTF8` |
| `images` | `ImageDrawLineStrip`, `ImageDrawTriangleFan`, `ImageDrawTriangleStrip`, `ImageKernelConvolution` |
| `models` | `DrawMeshInstanced`, `GenImageFontAtlas`-adjacent, `UnloadFontData`/`UnloadModelAnimations` out-params |
| `files` | `TextJoin`, `TextSplit`, `UnloadTextLines`, `LoadTextLines` |
| `textures` | none in the strict `(T*, int)` shape |

### 📦 Multiple returns `(T, U)`

**None apply**, and the reason is structural rather than a per-family judgement: raylib's "several values" always take one of the shapes the contract already resolves — a `rune` (`GetWindowPosition` → `Vector2`), an out-parameter count (`LoadFileData` → `.length`), or a success `bool` (`ExportImage` → `result`). The four out-parameter scalar APIs (`QuaternionToAxisAngle`-style) are in `raymathx`/`rcamerax`, not here. Where a family finds a genuine pair, it must come back to this plan before inventing a tuple.

### 🌉 `std.ffi` usage

Only the families that cross the string or array boundary import `std.ffi`: `window` (clipboard, window title), `text` (every text function), `textures` (file paths), `images` (paths, kernels, codepoint arrays), `files` (all of it), `shaders` (uniform names). `colors`, `shapes`, `shapes3d`, `drawing`, `models` (except path-taking loaders) and `audio` (except file loaders) work with numerics and handles only.

### 💡 Compilable examples

The façade form below is verified with `pengu expand` against a two-family draft (`window` + `input`) on `pengu 2.4.0`:

```pengu
# Example 1 — the façade surface
import raylib
import raymath
import raylibx

weave main into int:
    var w as int is calling raylibx.screen_width
    var down as bool is calling raylibx.is_key_down with raylib.KEY_A
    var camera as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    var forward as raylib.Vector3 is calling camera.forward
    return w
```

```pengu
# Example 2 — the string, maybe and slice policies together
import raylib
import raymathx
import std.ffi

weave load_file_text with path as string into maybe string:
    let c_path as ref to frozen char is calling ffi.cstr_from_string with path
    var text as ref to char is calling raylib.LoadFileText with c_path
    if calling ffi.is_null with (transmute text to ref to void):
        return maybe none
    var owned as string is calling ffi.string_from_cstr with text
    calling raylib.UnloadFileText with text
    return some owned

weave draw_fan with pts as slice of raylib.Vector2, color as raylib.Color into void:
    if (pts.length) == 0:
        return
    let raw as ref to frozen raylib.Vector2 is transmute (sigil of (pts at 0)) to ref to frozen raylib.Vector2
    calling raylib.DrawTriangleFan with raw, (pts.length), color

weave main into int:
    var text as maybe string is calling load_file_text with "notes.txt"
    var pts as list of raylib.Vector2 is list of raylib.Vector2
    defer banish pts
    calling pts.push with (calling Vector2.new with 0.0, 0.0)
    calling pts.push with (calling Vector2.new with 1.0, 0.0)
    calling draw_fan with (pts at 0 to 2), raylib.RAYWHITE
    return 0
```

### 🗺️ Family breakdown

Counts are `declare`s in `raylib.d.pengu` matched by C name family, and are the scope estimate for each sub-plan. The C names are grouped by the header's own module comments.

| # | Family | ~Functions | Headline C families | Sub-plan |
|---|---|---|---|---|
| 1 | `window` ✅ implemented (67 recounted) | the 55 of the window section plus timing, frame control and logging. **Only 11 are wrapped**: raylib has no window type to serve as a receiver, so §9 row 1 and criterion 2 exclude the 56 getters, void mutators and flat setters. `InitWindow`/`CloseWindow` are excluded explicitly by §9 row 8. See `docs/plans/raylibx_window.md` |
| 2 | `input` ✅ implemented | 47 (recounted) | `IsKey*`, `GetKey*`, `Is/GetMouse*`, `SetMouse*`, `GetTouch*`, `Is/Set/GetGamepad*`, `SetGesturesEnabled`, `IsGestureDetected`, `GetGesture*` | `docs/plans/raylibx_input.md` |
| 3 | `drawing` | ~11 | `Begin/EndDrawing`, `Begin/EndMode2D`, `Begin/EndMode3D`, `Begin/EndTextureMode`, `Begin/EndShaderMode`, `Begin/EndBlendMode`, `Begin/EndScissorMode`, `ClearBackground`. **`DrawFPS` is not here** (D6/I2): it belongs to `text` | `docs/plans/raylibx_drawing.md` |
| 4 | `shapes` ✅ implemented | 75 (recounted) | `DrawLine*`, `DrawCircle*`, `DrawRectangle*`, `DrawEllipse*`, `DrawRing*`, `DrawPoly*`, `DrawTriangle*`, `DrawPixel*`, splines, `SetShapesTexture` | `docs/plans/raylibx_shapes.md` |
| 5 | `shapes3d` ✅ implemented | 21 | `DrawCube*`, `DrawSphere*`, `DrawCylinder*`, `DrawCapsule*`, `DrawPlane`, `DrawRay`, `DrawGrid`, `DrawBoundingBox`, `DrawLine3D`, `DrawPoint3D`, `DrawTriangle3D`, `DrawTriangleStrip3D` | `docs/plans/raylibx_shapes3d.md` |
| 6 | `text` ✅ implemented | 59 (recounted) | `LoadFont*`, `IsFontValid`, `DrawText*`, `MeasureText*`, `Text*` (23 helpers), `GetGlyph*`, `SetTextLineSpacing`, `GetFontDefault`, `DrawFPS` (owns it, D6/I2) | `docs/plans/raylibx_text.md` |
| 7 | `textures` ✅ implemented | 20 (recounted) | `LoadTexture*`, `IsTextureValid`, `Load/UnloadRenderTexture`, `UpdateTexture*`, `DrawTexture*`, `SetTextureFilter/Wrap` | `docs/plans/raylibx_textures.md` |
| 8 | `images` ✅ implemented | 90 (recounted) | every `Image*` mutator, `LoadImage*`, `IsImageValid`, `GenImage*`, `ExportImage*`, `GetImage*`, `LoadImageColors/Palette` | `docs/plans/raylibx_images.md` |
| 9 | `colors` ✅ implemented | 12 | `Color*`, `Fade`, `GetColor`, `SetPixelColor`, `GetPixelColor` | `docs/plans/raylibx_colors.md` |
| 10 | `models` ✅ implemented (52 recounted) | the 52 functions of the models banner: 37 wrapped (19 methods and 18 module functions), 11 generators skipped by §9 row 11 and 3 billboards reassigned to `rcamerax` by receiver (D12). A **1:1 ratio**: no C function fans out into several wrappers |
| 11 | `audio` ✅ implemented (66 recounted) | the 66 functions of the section: 55 wrapped (**41 methods**, because there are **four receiver types**, and 14 module functions), 5 callbacks skipped by §9 row 6 and 6 one-shot configuration entries. **The audio device is measured to exist**, so the family has 8 real tests |
| 12 | `files` ✅ implemented | 40 (recounted) | `Load/Unload/SaveFile*`, `File*`, `Directory*`, `IsFile*`, `IsPath*`, `GetFile*`, `LoadDirectoryFiles*`, `LoadDroppedFiles`, `Compress/Decompress/Encode/Decode`, `ComputeCRC32/MD5/SHA1/SHA256` | `docs/plans/raylibx_files.md` |
| 13 | `shaders` ✅ implemented (10 + 8 reassigned) | the 10 shader-section functions, all wrapped in 15 wrappers. `SetShaderValue` becomes seven typed methods; both loaders check their precondition because raylib silently substitutes the default shader. The 8 projection functions this row used to list are reassigned to `rcamerax` (that plan's D13) |
| 14 | `random` ✅ implemented (4 recounted) | raylib's four random functions: **2 wrapped and 2 skipped**. `GetRandomValue` becomes `between`, a `Get*` renamed to a Pengunic noun, and the one place the inclusive-bounds and silent-swap facts are written down; `LoadRandomSequence` becomes `sequence`, which folds a NULL sentinel into `maybe list of int` and owns the C array so the caller cannot leak. `SetRandomSeed` is skipped by §9 row 8 and `UnloadRandomSequence` by §9 row 4. Two measured traps come with it: raylib's generator has a **fixed default seed**, so an unseeded program repeats itself on every run, and `LoadRandomSequence` answers an impossible request with a NULL pointer and an inverted range with **values outside both bounds**. See `docs/plans/raylibx_random.md` |

The bucket estimates sum to **~555**. The binding has **619** functions, so the difference (~64) is the `D14` exclusions (~20) plus the estimation error of the three families marked `~` (`drawing`, `textures`, `shaders`). `Total estimado: ~555 (recalcular en Fase 1b)` — **every family plan must recount its own bucket exactly, and these master-plan counts are scope estimates, not commitments.**

**Per-family plan requirements.** Each sub-plan follows the contract template and adds two things this master plan cannot:

1. The full method/function tables (the per-symbol enumeration the contract defers to Fase 1).
2. A "🚫 NO se envuelve" table with the reason for every symbol the family leaves out, including the `D14` set.

### 🚫 Not wrapped (whole module)

| Symbol group | Reason |
|---|---|
| `TraceLog` | variadic C; the wrapper cannot build the argument list (contract §9 row 5) |
| `TextFormat` | same: variadic, and it returns a `char*` the caller does not own |
| `SetTraceLogCallback`, `SetLoadFileDataCallback`, `SetSaveFileDataCallback`, `SetLoadFileTextCallback`, `SetSaveFileTextCallback`, `SetAudioStreamCallback` | no closures in PenguScript; the binding is already the correct interface (contract §9 row 6) |
| `MemAlloc`, `MemRealloc`, `MemFree` | raw allocation; `MemFree` is used *inside* wrappers that own a raylib buffer, never exposed as an API (contract §8/§9) |
| `SetConfigFlags`, `SetExitKey`, `SetTraceLogLevel` | one-shot global configuration; calling them once does not justify a wrapper (contract §9 row 8) |
| VR and automation (`LoadVrStereoConfig`, `SetVrStereoConfig`, `*AutomationEvent*`) | outside the 20 % that matters, and the window family plan must say so explicitly |
| `GetWindowHandle` | returns `void*` the user never manipulates (contract §9 row 7) |
| Callback `alias`es (`TraceLogCallback`, `LoadFileDataCallback`, `SaveFileDataCallback`, `LoadFileTextCallback`, `SaveFileTextCallback`, `AudioCallback`) | type declarations, not functions; the wrapper does not re-declare binding types |

### 🧪 Test plan

Per family, from the contract §12: three tests per public method, all inline, all in the family file. The split that matters here is what can run in CI:

| Family | CI-testable alone | Needs a window / GPU / audio device |
|---|---|---|
| `colors`, `shapes` (math parts), `shapes3d` (math parts), `files`, `models` (math parts), `text` (measurement) | yes, when the call does not draw | the `Draw*` calls themselves |
| `window`, `drawing`, `textures`, `images`, `audio` | the `maybe` failure path with a missing file, and the pure helpers | everything that creates a device or draws |

The rule the family plans must follow: a method that draws or needs a device gets a documented caveat test (a failure path, a pure helper, or a shape/measurement equivalent) and is marked as not asserted in CI. This is the same degradation already used in `raymathx` and `rcamerax`.

### 🗺️ Order of implementation

| Order | Family | Why here |
|---|---|---|
| 1 | `colors` | 12 pure functions, no device, no strings; the cheapest full pass and it settles the `Color` method ownership (D7) |
| 2 | `files` | pure I/O and hashes; exercises the whole string policy (D13) with no GPU |
| 3 | `shapes` | the first family with `Draw*` and with slice-shaped functions (D12) |
| 4 | `text` | the hub of the string policy; fonts make it the largest `maybe` family after textures |
| 5 | `images` | 61 mutators on one type; the `Image` method table is the module's biggest |
| 6 | `textures` | small and pairs with `images` and `text` |
| 7 | `shapes3d` | mirrors `shapes` in 3D |
| 8 | `models` | the second-largest surface, and it owns the 3D collision predicates |
| 9 | `audio` | large but mechanically uniform; needs a device for half its tests |
| 10 | `window` | global state and the window lifecycle; smallest useful surface once the device family lands |
| 11 | `input` | includes the eight gesture functions rescued from the archived `rgesturesx` |
| 12 | `drawing` ✅ implemented (15) | the `Begin/End` pairs. **The design question is answered: no lambda-based balanced helper**, because PenguScript lambdas do not capture locals and a drawing body always needs the caller's state; `defer` at scope exit is the idiomatic balance instead. See `docs/plans/raylibx_drawing.md` D3/D4 |
| 13 | `shaders` | uniforms need `void*` handling; do it last with the whole module as context |
| 14 | `random` | the azar appendix: two wrappers, no receiver and no window, so it is the cheapest family to add |

### 🧱 `rlglx` (recorded here, planned separately)

`pengu/rlgl.d.pengu` declares 163 functions across 621 lines: 126 raw OpenGL wrappers and 37 raylib-level helpers, with 22 slice-shaped signatures and no `insignia`. On the contract's own skip criteria (§9 row 9) the expected conclusion is **"wrap almost nothing; use the binding directly"**: the layer exists to be the OpenGL escape hatch, and a Pengunic rename buys nothing. Its plan belongs in `docs/plans/rlglx.md` (root-level module, `pengu/rlglx.pengu`), not under `raylibx/`. The only candidates worth weighing there are the raylib-level helpers (`rlLoadRenderBatch`, `rlSetMatrix*`, `rlGetTextureIdDefault`) and the slice-shaped state arrays (`rlSetUniformMatrices`). **The plan is written and the verdict is in** (`docs/plans/rlglx.md`): the layer is **feasible** — a probe compiles, links and runs rlgl from PenguScript, including a slice-driven vertex buffer and a two-string shader program — but **18 of the 163 functions are wrapped and 145 are skipped (89 %)**, the highest skip rate in the module. The wrapped set is exactly the boundary crossings: five string conversions, nine slice folds and the `rlRenderBatch` type's two methods. This master plan only recorded the expectation; the numbers are `rlglx`'s own.

### 🧱 `raygui` / `rayguix` (recorded here, planned separately)

`pengu/raygui.d.pengu` declares 61 functions over raygui **5.1-dev**, and it is the one binding whose usability was in doubt before any wrapper existed: raygui is a single-header library whose implementation only exists in a translation unit defining `RAYGUI_IMPLEMENTATION`. **The question is already answered by the repository, not by this plan**: `c/raygui_impl.c` carries the macro and the build compiles `c/*.c` of every installed binding into the bundle. Measured, `nm -D /usr/lib/libraylib.so | grep -c Gui` is **0**, so the bridge is load-bearing rather than decorative, and a probe links and runs the widgets end to end. Of the three routes that were considered — `antiquus` C blocks, a `.c` bridge, or changing the compiler — the first is **forbidden by the contract in layer 2** (§1, §9.6), the second is already in place, and the third is unnecessary. Its plan is `docs/plans/rayguix.md` and its verdict is **38 of the 61 functions wrapped and 23 skipped**: the 34 string-boundary widgets plus the three text fields, whose `ref to string` shape was proved in a live test before the plan was written. Two measured traps came out of it and are recorded project-wide: raygui's **font lives in a process-global initialised once**, so a program that recreates a window must call `GuiSetFont(GetFontDefault())` or `text_width` returns `0` (D10 of that plan); and **`GuiLoadStyleFromMemory` does not validate its buffer's length**, so eight bytes beginning with the valid magic `rGS ` segfault — which is why the only slice-shaped function in the family is deliberately *not* wrapped.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu` (619 `declare`, 35 `rune`, 21 `omen`, 14 `alias`, 40 `const`; 2019 líneas)
- Wrapper destino: `pengu/raylibx.pengu` (fachada) **más** `pengu/raylibx_<familia>.pengu` (un archivo plano por familia, hermano del binding)
- Dependencias: `import raylib`, `import raymath` (donde la familia mida o construya vectores), `import std.ffi` (familias que cruzan la frontera de cadenas)
- Sub-planes: `docs/plans/raylibx_<familia>.md`, uno por fila de las tablas de familia de abajo
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

Este plan maestro fija lo que los once planes de familia deben compartir. Deliberadamente **no** es una enumeración de los 619 símbolos: para eso está cada `docs/plans/raylibx_<familia>.md` (contrato §2, "la enumeración por símbolo es Fase 1"). Lo que sigue es la arquitectura, la política de nombres y de skip propia de raylib, el registro de colisiones entre familias y los patrones transversales ya verificados.

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo**. `include/raylib.h` declara exactamente 619 funciones `RLAPI` y el binding declara exactamente 619; los recuentos coinciden y el conjunto de nombres tiene la misma forma que las secciones del propio header. | Contados ambos lados. El condicionante estilo `raymath` no aplica aquí: todo `raylib.h` es API de consumidor, y los helpers de cámara y gestos que `rcamera.h`/`rgestures.h` encierran tras una macro están declarados en *este* binding (por eso `rgesturesx` se archivó y sus funciones aterrizan aquí). |
| D2 | **`raylibx` es una fachada más módulos de familia**, no un archivo: `pengu/raylibx.pengu` contiene solo el docstring de módulo y los `import`; cada símbolo vive en un archivo **plano** hermano `pengu/raylibx_<familia>.pengu`. | `raylib.d.pengu` ocupa 2019 líneas solo de *declaraciones*; un wrapper único sobre 619 funciones con docstrings y tests se pasa con mucho del tamaño manejable de `PenguScriptGuideSpanish.md` §3.2. Verificado en `pengu 2.4.0`: la fachada `import raylibx_window` + `import raylibx_input` hace ambas familias alcanzables como `raylibx.<fn>` con solo `import raylibx`. |
| D3 | El usuario escribe `import raylib` **y** `import raylibx`; el binding se importa explícitamente, no se asume transitivo. | Contrato §1. Los propios archivos de familia importan `raylib` (y `raymath`/`std.ffi` cuando lo necesitan). |
| D4 | **Nombres de archivo planos** `raylibx_<familia>.pengu`. **No se usa `insignia`**: `pengu 2.4.0` ya manglea las funciones de módulo con el nombre del módulo, así que dos familias hermanas con el *mismo* nombre de función emiten `raylibx_window_screen_width` y `raylibx_input_screen_width` y conviven. Los métodos de `enchanting` se emiten como `<Tipo>_<método>` **sin** prefijo de módulo, y por eso existe el registro de métodos (D5). | Verificado en `pengu 2.4.0` con dos módulos hermanos que declaran `screen_width` e `is_key_down`: los símbolos emitidos son `raylibx_window_screen_width` y `raylibx_input_screen_width`. Para los `enchanting` la sonda usó nombres *distintos* a propósito (`Camera3D_window_probe_len` frente a `Camera3D_input_probe_len`) y ambos sobreviven, lo que confirma que dos módulos pueden encantar el mismo tipo. Usar el *mismo* nombre de método en ambos módulos emite `Camera3D_probe_len` dos veces: exactamente el peligro que D5 evita. |
| D5 | **Registro global de nombres de método: un nombre por tipo, en todos los archivos de familia.** Mientras `raylibx` esté a medias, `pengu/raylibx.pengu` importa solo las familias ya envueltas, y una fachada vacía es un estado intermedio válido. | Verificado en `pengu 2.4.0`: dos módulos *pueden* añadir métodos al mismo tipo, pero dos métodos con el mismo nombre emiten el mismo símbolo C dos veces y el build de C falla con `redefinition of '<Tipo>_<método>'`, mientras que `pengu check` no lo detecta (es el mismo peligro registrado en `WRAPPER_CONVENTIONS.md` §1 para el alias `Quaternion`/`Vector4`). Una función `Draw*` es el sitio natural donde aparece un duplicado accidental, así que la regla es: **un nombre, un módulo, asignado aquí**. |
| D6 | Las funciones de módulo se envuelven en la **familia dueña de la función C**, aunque su sitio natural parezca otra familia. | `SetGesturesEnabled`/`IsGestureDetected`/`GetGesture*` viven en `raylib.d.pengu` y pertenecen a la familia `input`, no a una familia `gestures` que no envuelve nada (D10). Lo mismo `GetClipboardText` (window), `GetColor` (textures/colors) y los helpers de fichero (files). |
| D7 | La API de valores `Color` (`Color*`, `Fade`, `GetColor`, `SetPixelColor`, `GetPixelColor`) se envuelve como **métodos sobre `raylib.Color`** y funciones de módulo en la familia `colors`, y no se duplica en cada familia de dibujo. **Un *archivo de familia* de dibujo no importa ni llama a `colors`**: si necesita una transformación de color, llama directamente a `raylib.Fade` (el binding) o recibe el `Color` ya transformado como argumento. `colors` existe para comodidad del *usuario*, y D2 prohíbe los imports entre familias. | Un dueño por símbolo (D5/D6), y la capa wrapper no es una biblioteca que las familias consuman. |
| D8 | Las constantes de `raylib.Color` (`RAYWHITE`, `LIGHTGRAY`, … los 26 `const` mantenidos a mano) **nunca** se envuelven ni se reexportan; el código usa `raylib.<NOMBRE>`. | Contrato §2: son parte del contrato de raylib y conservan su grafía C. `import raylib` ya las pone a disposición. |
| D9 | Toda función `Draw*` es una función de módulo que se lee como **instrucción** (`draw_rectangle_rec`, `draw_text_ex`, `draw_cube`), **salvo** cuando el nombre C es `<Shape>V` y el primer argumento *es* el ancla de la figura — entonces pasa a método de ese tipo (`DrawCircleV` → `v.draw_circle`, `DrawPixelV` → `v.draw_pixel`, `DrawLineV` → `v.draw_line_to`). | Contrato §6.1 con una regla explícita para que los planes de familia no lo re-litiguen símbolo a símbolo: `DrawCube(Vector3 position, …)` crea un cubo *en* un punto, así que el punto es un argumento, no el sujeto; `DrawCircleV(Vector2 center, …)` dibuja un círculo *cuyo centro es* el vector. El sufijo `<Shape>V` es la prueba mecánica. |
| D10 | **No hay archivo de familia `gestures`**. Las ocho funciones de gestos se envuelven dentro de `input`. | Son estado de entrada; un archivo aparte sería un archivo con ocho funciones y sin tema (la lección de `rgesturesx` archivado: el wrapper debe envolver su propio binding, y éstas viven en `raylib.d.pengu`). |
| D11 | El contrato `Load*` + `Is*Valid` + `Unload*` se envuelve como **`maybe T` para el cargador y nada para el liberador**, y cada plan de familia debe declarar la llamada de liberación de cada recurso que carga. | Contrato §3 y §8. `LoadFileText`, que devuelve `char*`, se envuelve como `maybe string` tomando la copia con posesión **antes** de `UnloadFileText` (verificado: `ffi_string_from_cstr` copia y después `UnloadFileText(text)`). |
| D12 | Las familias `(T* ptr, int count)` (`DrawLineStrip`, `DrawTriangleFan`, los cinco `DrawSpline*`, `DrawTextCodepoints`, `LoadFontEx`, `ImageKernelConvolution`, `DrawMeshInstanced`, `TextJoin`, …) reciben `slice of T`. | Contrato §5. Cada una necesita la guarda de slice vacío y el único `transmute (sigil of (pts at 0))`; verificado que emite una llamada C directa sin copia. |
| D13 | **Las fronteras de cadena son uniformes**: `string` → `ffi.cstr_from_string`; `char*` de C → `maybe string`/`string` con `ffi.string_from_cstr` y la liberación propia de la biblioteca; los `const char*` que raylib posee (`GetClipboardText`, `GetMonitorName`, `GetKeyName`, `GetDirectoryPath`, …) se copian y **no** se liberan; `TextFormat` (variádica) no se envuelve. | Contrato §7 y §8. Verificado de extremo a extremo con `LoadFileText`. La distinción entre "lo posee raylib" y "lo libera el llamador" se lee del comentario de cada header y se registra por función en los planes de familia. |
| D14 | `TraceLog` (variádica), los setters de callbacks (`SetTraceLogCallback`, `SetLoadFileDataCallback`, …), los abortos estilo `@noreturn`, `MemAlloc`/`MemRealloc`/`MemFree` y los puntos de entrada de VR/automatización **no se envuelven**. | Contrato §9 filas 4–8: la C variádica no se puede construir desde PenguScript, los callbacks no tienen closures aquí, `MemFree` pertenece a la política de liberación, y VR/automatización quedan fuera del 20 % que importa. Cada uno se lista con su motivo en su plan de familia. |
| D15 | `raygui` y `raylib_pengu` quedan fuera de alcance. | `raygui.d.pengu` es otro binding con su propia historia de wrapper (`rayguix`), y `raylib_pengu.d.pengu` es una fachada de reexportación escrita a mano, no un binding. Ninguno pertenece a este plan. |
| D19 | **Los lambdas de PenguScript no tienen closures, así que ningún wrapper de este proyecto puede ofrecer una API *equilibrada* basada en callback.** Medido al planificar `drawing`: un cuerpo lambda que referencia un local del entorno falla con `E0004`, y `pengu check` **no siempre lo reporta** — cuando el nombre del local coincide con el de un parámetro usado en el módulo, `check` acepta el fichero mientras `pengu expand` lo rechaza. | Un helper que recibiera el cuerpo como lambda pasaría `check` y fallaría al construir, o resolvería en silencio a la variable equivocada. Cualquier familia futura tentada por un wrapper con forma de callback (un recurso con ámbito, un iterador, un manejador de eventos) debe verificar primero que el callback no necesita estado del llamador; si no, usa begin/end explícitos más `defer`. Se registra aquí para no repetir el experimento familia por familia. |
| D20 | **Un tipo cualificado está bien en una declaración pero roto como destino de `transmute`/cast.** `let first as ref to raylib.Image is sigil of (icons at 0)` emite C válido (`SetWindowIcons(first, icons.len)`), mientras que `transmute x to ref to raylib.Image` emite un cast que nombra un tipo que el compilador de C no conoce. | Encontrado al envolver `SetWindowIcons` en `window`. Refina el D19: el rodeo por `void*` de `shapes`/`images` sigue siendo el arreglo correcto cuando el cast es inevitable, pero **un local tipado elimina la necesidad del cast** y se lee mejor. Cualquier wrapper que necesite `ref to T` a partir de un slice debería declarar el local en vez de transmutar. |
| D21 | **El proyecto ya no es solo de compilación: esta máquina tiene display (`DISPLAY=:0`), así que un test puede abrir una ventana real** con `raylib.InitWindow` desde el binding y asegurar contra comportamiento vivo. Medido: `InitWindow` funciona, se pueden dibujar y presentar fotogramas, y los ciclos repetidos de `InitWindow`/`CloseWindow` en un proceso funcionan. | Encontrado al planificar `window`. **Deja obsoleto el D9 de `raylibx_drawing`**, que había concluido "sin comportamiento testeable en CI" a partir de una medición sin ventana; ese plan y su suite se corrigen. A partir de aquí, una familia que se salte una superficie ligada a ventana debe decir si comprobó esto, y `InitWindow`/`CloseWindow` se llaman desde el binding para preparar el entorno porque la §9 fila 8 las mantiene fuera del wrapper. |
| D22 | **PenguScript no comprueba los parámetros de enum: un parámetro tipado como `omen` acepta cualquier entero.** Una sonda mínima sobre `pengu 2.4.0` pasa `raylib.MOUSE_BUTTON_LEFT` y hasta un `42` crudo a un parámetro tipado `raylib.KeyboardKey` sin diagnóstico. | Medido al evaluar `rlglx`, y corrige una afirmación del D2 de `raylibx_input`. La consecuencia para el proyecto es una regla: **un wrapper se justifica por la frontera que cruza (cadena, slice, propiedad, `maybe`) o por una llamada más corta y autodocumentada — nunca por "seguridad de tipos", porque no hay ninguna que añadir.** Un enum en la firma de un wrapper es documentación que se lee bien en el sitio de llamada; no impone nada, y una familia cuyo único argumento sea restaurar enums debe justificarse por el recuento de tokens. |
| D23 | **Un `let` dentro de un bloque declara un enlace *nuevo*; no asigna al exterior.** Un puntero calculado dentro de una guarda `if` debe declararse `var` fuera y asignarse con `set x is …` dentro, o la variable exterior conserva su valor inicial. | Encontrado por un fallo al probar `rlglx`: el patrón `let raw as ref to void is calling ffi.null_void` seguido de `if (slice.length) > 0:` / `let raw as ref to void is transmute …` emitía **dos** variables C, así que la exterior seguía siendo nula y **cada slice no vacío se pasaba como puntero NULL**. El mismo bug latente estaba en `update` y `update_rec` de `raylibx.textures`, donde ningún test lo había ejercitado. Los dos están arreglados, y la regla queda registrada porque el compilador no dice nada. |
| D18 | **La familia `input` se estrechó durante la Fase 1b.** De sus 47 funciones solo **28 se envuelven**; las 19 que quedan fuera son los getters sin argumentos que no pueden fallar (`GetMousePosition`, `GetMouseDelta`, los getters de la rueda, `GetTouchX/Y`, `GetTouchPosition`, `GetTouchPointCount`, los cinco getters de valores de gestos), más `IsGamepadAvailable`, `GetGamepadAxisCount`, `SetGamepadVibration` y `SetExitKey`. | Contrato §9 filas 1 y 160, y su fila de orden 417, que nombra explícitamente `GetTouchPointCount` como función que no se envuelve. El valor de la familia resultó ser la **restauración de tipos** — el binding aplana todos los parámetros de enum a `int` — más los centinelas `maybe`, y nada más. Esto enmienda la descripción de familia de la tabla de arriba, que listaba `GetMouse*`/`GetTouch*`/`GetGesture*`; el D3 de `docs/plans/raylibx_input.md` tiene el razonamiento completo. |
| D17 | **Que un `declare` exista en el header no significa que la biblioteca instalada lo exporte.** El header del repo es raylib **6.1-dev**; `/usr/lib/libraylib.so` es **6.0.0**, y **faltan 22 funciones declaradas** (3 de `files`, 10 de `images`, 1 de `textures`, 7 de `shapes`, 1 de `text`). Cada plan de familia debe ejecutar `python3 tools/check_binding_symbols.py pengu/<binding> <biblioteca>` antes de declarar el caso (a), y listar las funciones que no puede envolver por este motivo. | Descubierto al implementar `raylibx_shapes`: `pengu check` y `pengu build` salían limpios y el fallo aparecía solo al enlazar (`referencia a 'GetSplinePointBezierQuadratic' sin definir`). La herramienta se añadió al repo para que la comprobación sea un comando en vez de una cacería. `raylibx_colors` y `raylibx_files` se reauditaron y no llaman a ningún símbolo ausente. |
| D16 | **(Corregido en v0.1.3.) Los archivos de familia viven en el subpaquete `pengu/raylibx/`** como módulos `raylibx.<familia>`, con `pengu/raylibx.pengu` como fachada. La versión v0.1.2 de esta decisión afirmaba que el resolutor rechazaba el subpaquete; **era falso**, y se corrigió volviendo a medir sobre el mismo `pengu 2.4.0`: las trece familias en `pengu/raylibx/` resuelven `import raylib`, `pengu check` sale limpio, `pengu build` enlaza (218 KB, sin referencias sin definir) y la suite completa de 261 tests corre a través de la fachada. La causa más probable del error original es que la sonda que lo produjo vivía en `src/`, que **no** es una raíz configurada (`src_dir = "pengu"`), donde `import raylib` no puede resolverse por diseño. el archivo de familia es `pengu/raylibx_<familia>.pengu`, junto al binding. | Verificado en `pengu 2.4.0`: un módulo un directorio más abajo no puede resolver `import raylib` — `Cannot resolve imported module 'raylib'`, porque el binding vive en la raíz de `src_dir` y el resolutor no sube. Añadir el subdirectorio a `src_dirs` en `pengu.toml` **tampoco** lo arregla. El diseño plano sí funciona. |

### 🏗️ Arquitectura

```
pengu/
├── raylib.d.pengu              ← binding (capa 1, no se toca)
├── raylibx.pengu               ← fachada: docstring + los imports de familia, cero símbolos
├── raylibx_window.pengu        ← window      (InitWindow, monitores, timing, portapapeles)
├── raylibx_input.pengu         ← input       (teclas, ratón, gamepad, táctil, las 8 funciones de gestos)
├── raylibx_drawing.pengu       ← drawing     (pares Begin/End de frame y modo, ClearBackground)
├── raylibx_shapes.pengu        ← shapes      (formas 2D y splines)
├── raylibx_shapes3d.pengu      ← shapes3d    (primitivas 3D)
├── raylibx_text.pengu          ← text        (fuentes, DrawText*, MeasureText*, helpers Text*)
├── raylibx_textures.pengu      ← textures    (Texture, RenderTexture)
├── raylibx_images.pengu        ← images      (Image y sus 49 mutadores, GenImage*, LoadImage*)
├── raylibx_colors.pengu        ← colors      (valores Color, Fade, GetColor)
├── raylibx_models.pengu        ← models      (Model, Mesh, Material, Animation, colisiones 3D)
├── raylibx_audio.pengu         ← audio       (Wave, Sound, Music, AudioStream)
├── raylibx_files.pengu         ← files       (sistema de ficheros, compresión, hashes)
└── raylibx_shaders.pengu       ← shaders     (Shader, uniforms, pantalla↔mundo)
```

Reglas que se derivan de D2, D4 y D16:

- `raylibx.pengu` **no tiene `enchanting`, ni `weave`, ni `const`**. Su docstring declara la relación entre módulos (binding `raylib` + wrapper `raylibx`) y lista las familias.
- Cada archivo de familia es autocontenido: su propio `import raylib` (más `import raymath` / `import std.ffi` si los necesita), su docstring, sus bloques `enchanting` y sus tests inline.
- Un archivo de familia **nunca** importa otro archivo de familia. Los helpers compartidos que dos familias necesiten van en la familia dueña de la función C subyacente (D6/D7).
- Añadir una familia significa añadir una línea `import` a la fachada; nada más cambia.

### 📛 Registro global de métodos (control de colisiones)

Esta es la tabla para la que existe D5. La Fase 1b rellena las listas de métodos por familia, y cada nombre se comprueba contra este registro antes de comprometerse. Las filas de abajo son los **dueños previstos**; un plan de familia puede añadir filas pero no puede reutilizar un nombre ya asignado al mismo tipo.

| Tipo | Familia dueña | Métodos ya asignados | Notas |
|---|---|---|---|
| `raylib.Color` | `colors` | se enumeran en `colors.md` | `to_int`, `fade`, `from_hex`, `from_hsv`, …; ninguna otra familia puede añadir métodos a `Color` |
| `raylib.Image` | `images` ✅ **cerrada** | `to_format`, `to_power_of_two`, `crop`, `crop_to_alpha`, `clear_alpha`, `apply_alpha_mask`, `premultiply_alpha`, `blur_gaussian`, `convolve`, `resize`, `resize_nearest`, `resize_canvas`, `generate_mipmaps`, `dither`, `flip_vertical`, `flip_horizontal`, `rotate`, `rotate_cw`, `rotate_ccw`, `tint`, `invert`, `to_grayscale`, `adjust_contrast`, `adjust_brightness`, `replace_color`, `copy`, `region`, `channel`, `colors`, `palette`, `alpha_border`, `color_at`, `clear`, `draw_pixel`, `draw_pixel_at`, `draw_line`, `draw_line_between`, `draw_line_thick`, `draw_triangle`, `draw_triangle_outline`, `draw_triangle_fan`, `draw_triangle_strip`, `draw_rectangle`, `draw_rectangle_at`, `draw_rectangle_rec`, `draw_rectangle_outline`, `draw_circle`, `draw_circle_at`, `draw_circle_outline`, `draw_circle_outline_at`, `draw_text`, `draw_text_ex` | cerrada por `raylibx.images`: 52 métodos (25 transformaciones, 20 dibujos, 7 lectores/productores). **Ninguna otra familia puede añadir un método a `Image`** |
| `raylib.Texture2D` | `textures` ✅ **cerrada** | `draw`, `draw_at`, `draw_ex`, `draw_rec`, `draw_pro`, `draw_npatch`, `update`, `update_rec`, `generate_mipmaps`, `set_filter`, `set_wrap`, `is_valid` | cerrada por `raylibx.textures`; se encanta sobre el nominal `raylib.Texture` porque `Texture2D` es su alias. **Ninguna otra familia puede añadir un método a `Texture`** |
| `raylib.RenderTexture2D` | `textures` ✅ **cerrada** | `is_valid` | cerrada por `raylibx.textures`. **`begin`/`end` se dejan sin asignar a propósito**: `BeginTextureMode`/`EndTextureMode` son de `drawing`, que debería exponerlas como métodos de este tipo. `draw` no hace falta: el campo `texture` ya lleva toda la superficie de `Texture` |
| `raylib.Font` | `text` ✅ **closed** | `draw`, `draw_pro`, `draw_codepoint`, `draw_codepoints`, `measure` | closed by `raylibx.text`; the glyph queries (`font_glyph_index`, `font_glyph_info`, `font_glyph_atlas_rec`) are **module functions**, not methods. **No other family may add a `Font` method** |
| `raylib.Model` | `models` ✅ **cerrada** | `is_valid`, `bounding_box`, `draw`, `draw_ex`, `draw_wires`, `draw_wires_ex`, `set_mesh_material`, `update_animation`, `update_animation_ex`, `is_animation_valid` | cerrada por `raylibx.models`. **`load_model_from_mesh` no devuelve `maybe`**: medido, raylib no valida la malla y un modelo de malla a ceros informa válido (D3). **Ninguna otra familia puede añadir un método a `Model`** |
| `raylib.Mesh` | `models` ✅ **cerrada** | `upload`, `update_buffer`, `draw`, `draw_instanced`, `bounding_box`, `generate_tangents`, `export`, `export_as_code` | cerrada por `raylibx.models`. El nombre reservado `tangents` pasa a `generate_tangents`, porque un mutador que devuelve `void` llamado `tangents` se lee como un getter. **Ninguna otra familia puede añadir un método a `Mesh`** |
| `raylib.Material` | `models` ✅ **cerrada** | `set_texture` | cerrada por `raylibx.models`. **Ninguna otra familia puede añadir un método a `Material`** |
| `raylib.ModelAnimation` | `models` ✅ **sin métodos** | — | toda operación de animación tiene el **modelo** como sujeto (`model.update_animation`, `model.is_animation_valid`), así que el tipo no gana métodos. `load_animations`/`unload_animations` son de módulo porque una animación existe antes que el modelo al que se aplica (D4) |
| `raylib.Shader` | `shaders` ✅ **cerrada** | `is_valid`, `location`, `location_attrib`, `set_float`, `set_int`, `set_vec2`, `set_vec3`, `set_vec4`, `set_matrix`, `set_texture`, `set_floats`, `set_ints` | cerrada por `raylibx.shaders`: 12 métodos. El nombre reservado `set_value` queda **liberado** en favor de la familia tipada, porque un método genérico único dejaría el `void*` y el enum `SHADER_UNIFORM_*` en el sitio de llamada. **Ninguna otra familia puede añadir un método a `Shader`** |
| `raylib.Wave` | `audio` ✅ **cerrada** | `is_valid`, `copy`, `crop`, `to_format`, `export`, `export_as_code`, `samples` | cerrada por `raylibx.audio`. `samples` devuelve una **vista** que libera `unload_wave_samples` (D8). **Ninguna otra familia puede añadir un método a `Wave`** |
| `raylib.Sound` | `audio` ✅ **cerrada** | `is_valid`, `update`, `play`, `stop`, `pause`, `resume`, `is_playing`, `set_volume`, `set_pitch`, `set_pan` | cerrada por `raylibx.audio`. **`load_sound_from_wave` remuestrea**: el `frameCount` del sonido es el del dispositivo, nunca el de la onda (D9). **Ninguna otra familia puede añadir un método a `Sound`** |
| `raylib.Music` | `audio` ✅ **cerrada** | `is_valid`, `play`, `stop`, `pause`, `resume`, `is_playing`, `update`, `seek`, `set_volume`, `set_pitch`, `set_pan`, `time_length`, `time_played` | cerrada por `raylibx.audio`. El bucle es el **campo** `Music.looping`, no un método, porque raylib 6.0 no tiene setter para ello (D11). **Ninguna otra familia puede añadir un método a `Music`** |
| `raylib.AudioStream` | `audio` ✅ **cerrada** | `is_valid`, `update`, `is_processed`, `play`, `pause`, `resume`, `is_playing`, `stop`, `set_volume`, `set_pitch`, `set_pan` | cerrada por `raylibx.audio`. Construir uno necesita el dispositivo de audio, así que `load_audio_stream` devuelve un `maybe` (D7). **Ninguna otra familia puede añadir un método a `AudioStream`** |
| `raylib.Camera2D` | `rcamerax` ✅ **cerrada** | `view_matrix`, `to_screen`, `to_world` | **Corregida**: esta fila decía que `to_world`/`to_screen` "no se envuelven: son getters de dos argumentos que ya se leen bien desde el binding", y asignaba los métodos del tipo a `drawing`. La reserva nunca se ejecutó — `drawing` no tiene ni un bloque `enchanting` — y el criterio del receptor decide lo contrario: como método, la cámara **sale** de la lista de argumentos, así que `camera.to_screen with position` es más corto que la llamada al binding, que es el criterio 1 del §9 cumplido en vez de fallado. Cerrada por el apéndice de `rcamerax` (sus D13–D16). **`begin`/`end` liberados**: `EndMode2D` no recibe receptor, así que el par se queda como funciones de módulo simétricas en `raylibx_drawing` |
| `raylib.Camera3D` | `rcamerax` ✅ **cerrada** | `forward`, `up`, `right`, `view_matrix`, `projection_matrix`, `move_*`, `yaw`, `pitch`, `roll`, más las del apéndice `to_screen`, `to_screen_ex`, `to_world_ray`, `to_world_ray_ex`, `draw_billboard`, `draw_billboard_rec`, `draw_billboard_pro` | **`begin`/`end` liberados**: el mismo motivo que en `Camera2D`. **`raymathx`/`rcamerax` poseen toda la superficie de cámara**; `raylibx` no debe volver a añadir nada de ella. Los tres billboards son funciones de `rmodels` en las cabeceras de C, pero la cámara es su primer parámetro y por tanto el receptor (§9 criterio 2), así que pertenecen aquí; `raylibx.models` los reasignó por su D12 |
| `raylib.Vector3` | `shapes3d` ✅ **cerrada** | `draw_point`, `draw_cube`, `draw_cube_wires`, `draw_plane` (los nombres anclados en la `V` más los dos nombres de sujeto sin `V`) | cerrada por `raylibx.shapes3d`; las familias de esfera y cilindro se quedaron de módulo porque raylib no tiene `DrawSphereV`/`DrawCylinderV`. **Ninguna otra familia puede añadir un método de dibujo a `Vector3`**, y `raymathx` conserva toda la aritmética |
| `raylib.Rectangle` | `shapes` ✅ **closed** | `draw`, `draw_pro`, `draw_gradient`, `draw_outline`, `draw_rounded`, `draw_rounded_outline`, `contains_point` | closed by `raylibx.shapes`; **no other family may add a `Rectangle` method** |
| `raylib.Vector2` | `shapes` ✅ **cerrada** | los 20 `draw_*` de las funciones `<Shape>V` (`draw_circle`, `draw_pixel`, `draw_line_to`, …) | cerrada por `raylibx.shapes` (regla `<Shape>V` de D9). **`raymathx` posee toda la aritmética y ninguna otra familia puede añadir un método a `Vector2`** |

| `raylib.Vector4` | (ninguna) | — | **`raymathx` posee toda la aritmética 4D y `identity`; `raylibx` no añade ninguno** |
| `raylib.Quaternion` | (ninguna) | — | **`raymathx` posee todos los métodos de quaternion (`mul`, `slerp_to`, `to_matrix`, …) y sus factorías son de módulo; `raylibx` no añade ninguno** |
| `raylib.Color` (otra vez) | — | — | se lista una vez; la segunda mención es el aviso de que `Color` es el duplicado accidental más fácil |

**Procedimiento de verificación para cada plan de familia** (mecánico, de `WRAPPER_CONVENTIONS.md` §1):

1. Declarar los métodos de la familia en su `.md`.
2. Diferenciar el conjunto resultante de símbolos `<Tipo>_<método>` contra todos los demás archivos de familia ya escritos.
3. Solo entonces escribir el `.pengu`; `pengu check` no detecta un duplicado, así que el diff es la puerta.

### 🔧 Políticas transversales

| Política | Regla |
|---|---|
| Cadenas de entrada | `let c_x as ref to frozen char is calling ffi.cstr_from_string with x` (contrato §7) |
| Cadenas de salida que libera el llamador | copiar con `ffi.string_from_cstr`, luego la liberación de raylib (`UnloadFileText`, `UnloadUTF8`, `MemFree`), luego devolver la copia con posesión — **copiar antes de liberar** (D11) |
| Cadenas de salida que posee raylib | copiar con `ffi.string_from_cstr` y **no** liberar (`GetClipboardText`, `GetMonitorName`, `GetKeyName`, `GetDirectoryPath`, `TextFormat`) |
| Arrays de entrada | `slice of T`, guardar el caso vacío, un solo `transmute (sigil of (pts at 0))` (D12) |
| Arrays de salida | `ffi.list_from_ptr of T` (con posesión, hay que `banish`) o `slice` desde `ffi.slice_from_ptr` solo si el puntero sobrevive a la llamada; el plan de familia debe decir cuál y por qué |
| Recursos | `maybe T` al cargar, `defer calling raylib.UnloadX with res` en el sitio de uso (D11) |
| Tiempo de vida de los `ref to T` devueltos | `Font.recs`, `Font.glyphs`, `Model.meshes`, `Image.data` y compañía apuntan **dentro** del recurso; nunca `banish`, y nunca usarlos después de liberar al dueño (contrato §8) |
| Nunca se envuelven | `TraceLog`, `TextFormat`, los setters de callbacks, `MemAlloc`/`MemRealloc`/`MemFree`, VR/automatización, la asignación cruda (D14) |

| Azar (`SetRandomSeed`, `GetRandomValue`, `LoadRandomSequence`, `UnloadRandomSequence`) | **resuelto**: no se tomó ninguna de las dos opciones que proponía esta fila — las funciones pasaron a ser la **familia 14 (`random`)**, porque vienen de `raylib.d.pengu` y un apéndice en `raymathx` habría envuelto otro binding. `GetRandomValue` y `LoadRandomSequence` se envuelven (`between`, `sequence`); `SetRandomSeed` se omite por la §9 fila 8 y `UnloadRandomSequence` por la fila 4, porque `sequence` posee el array que reserva. Allí quedan registradas dos trampas medidas: la **semilla por defecto fija** del generador (un programa sin sembrar se repite en cada ejecución) y que `LoadRandomSequence` responde a un rango invertido con **valores fuera de ambos límites** en vez de con un puntero nulo. Ver `docs/plans/raylibx_random.md` |
### 🎁 Wrappers `maybe T`

Este plan maestro asigna la **familia**, no la lista por símbolo. En Fase 1b cada plan de familia debe producir la tabla que pide el contrato:

| Familia | Cargadores `maybe` previstos | Predicado |
|---|---|---|
| `textures` | `LoadTexture`, `LoadTextureFromImage`, `LoadTextureCubemap`, `LoadRenderTexture`, `LoadRenderTextureEx` | `IsTextureValid`, `IsRenderTextureValid` |
| `images` | `LoadImage`, `LoadImageRaw`, `LoadImageAnim*`, `LoadImageFromMemory`, `LoadImageFromTexture`, `LoadImageFromScreen`, `LoadImageColors`, `LoadImagePalette`, los adyacentes a `LoadFontData` | `IsImageValid`, o comprobación de nulo/recuento cero en los que devuelven puntero |
| `text` | `LoadFont`, `LoadFontEx`, `LoadFontFromMemory`, `LoadFontFromImage`, `LoadFontData`, `LoadUTF8`, `LoadTextLines` | `IsFontValid`, nulo o recuento |
| `models` | `LoadModel`, `LoadModelFromMesh`, `LoadMaterials`, `LoadModelAnimations`, los adyacentes a `LoadMesh` | `IsModelValid`, `IsMaterialValid`, `IsModelAnimationValid` |
| `audio` | `LoadWave`, `LoadWaveFromMemory`, `LoadSound`, `LoadSoundFromWave`, `LoadSoundAlias`, `LoadMusicStream`, `LoadMusicStreamFromMemory`, `LoadAudioStream`, `LoadWaveSamples` | `IsWaveValid`, `IsSoundValid`, `IsMusicValid`, `IsAudioStreamValid` |
| `files` | `LoadFileData`, `LoadFileText`, `LoadDirectoryFiles`, `LoadDirectoryFilesEx`, `LoadDroppedFiles`, `LoadAutomationEventList` | nulo, o `count > 0` para `FilePathList` |
| `window` | `GetClipboardImage`? (sin predicado) | ninguno; advertencia documentada |
| `shaders` | `LoadShader`, `LoadShaderFromMemory` | `IsShaderValid` |

Los constructores `Gen*` (`GenImageColor`, `GenMeshCube`, `GenTextureMipmaps`) **no** son `maybe`: son valores calculados, no recursos externos (contrato §3).

### ✂️ Wrappers de `slice` (familias que los necesitan)

| Familia | Firmas C con forma de slice |
|---|---|
| `shapes` | `DrawLineStrip`, `DrawTriangleFan`, `DrawTriangleStrip`, `DrawSplineLinear`, `DrawSplineBasis`, `DrawSplineCatmullRom`, `DrawSplineBezierQuadratic`, `DrawSplineBezierCubic`, `CheckCollisionPointPoly` |
| `shapes3d` | `DrawTriangleStrip3D` |
| `text` | `LoadFontEx`, `LoadFontFromMemory`, `DrawTextCodepoints`, `MeasureTextCodepoints`, `LoadUTF8`, rutas de texto tipo `DrawMeshInstanced` |
| `images` | `ImageDrawLineStrip`, `ImageDrawTriangleFan`, `ImageDrawTriangleStrip`, `ImageKernelConvolution` |
| `models` | `DrawMeshInstanced`, adyacentes a `GenImageFontAtlas`, los out-params de `UnloadFontData`/`UnloadModelAnimations` |
| `files` | `TextJoin`, `TextSplit`, `UnloadTextLines`, `LoadTextLines` |
| `textures` | ninguna en la forma estricta `(T*, int)` |

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica**, y el motivo es estructural más que un juicio por familia: los "varios valores" de raylib toman siempre una de las formas que el contrato ya resuelve — un `rune` (`GetWindowPosition` → `Vector2`), un recuento por out-param (`LoadFileData` → `.length`) o un `bool` de éxito (`ExportImage` → `result`). Las cuatro APIs de out-param escalar (estilo `QuaternionToAxisAngle`) están en `raymathx`/`rcamerax`, no aquí. Si una familia encuentra un par genuino, debe volver a este plan antes de inventar una tupla.

### 🌉 Uso de `std.ffi`

Solo importan `std.ffi` las familias que cruzan la frontera de cadenas o de arrays: `window` (portapapeles, título de ventana), `text` (todas las funciones de texto), `textures` (rutas), `images` (rutas, kernels, arrays de codepoints), `files` (todo) y `shaders` (nombres de uniform). `colors`, `shapes`, `shapes3d`, `drawing`, `models` (salvo los cargadores con ruta) y `audio` (salvo los cargadores de fichero) trabajan solo con numéricos y handles.

### 💡 Ejemplos compilables

La forma de fachada de abajo está verificada con `pengu expand` contra un borrador de dos familias (`window` + `input`) en `pengu 2.4.0`:

```pengu
# Ejemplo 1 — la superficie de la fachada
import raylib
import raymath
import raylibx

weave main into int:
    var w as int is calling raylibx.screen_width
    var down as bool is calling raylibx.is_key_down with raylib.KEY_A
    var camera as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    var forward as raylib.Vector3 is calling camera.forward
    return w
```

```pengu
# Ejemplo 2 — las políticas de cadena, maybe y slice juntas
import raylib
import raymathx
import std.ffi

weave load_file_text with path as string into maybe string:
    let c_path as ref to frozen char is calling ffi.cstr_from_string with path
    var text as ref to char is calling raylib.LoadFileText with c_path
    if calling ffi.is_null with (transmute text to ref to void):
        return maybe none
    var owned as string is calling ffi.string_from_cstr with text
    calling raylib.UnloadFileText with text
    return some owned

weave draw_fan with pts as slice of raylib.Vector2, color as raylib.Color into void:
    if (pts.length) == 0:
        return
    let raw as ref to frozen raylib.Vector2 is transmute (sigil of (pts at 0)) to ref to frozen raylib.Vector2
    calling raylib.DrawTriangleFan with raw, (pts.length), color

weave main into int:
    var text as maybe string is calling load_file_text with "notes.txt"
    var pts as list of raylib.Vector2 is list of raylib.Vector2
    defer banish pts
    calling pts.push with (calling Vector2.new with 0.0, 0.0)
    calling pts.push with (calling Vector2.new with 1.0, 0.0)
    calling draw_fan with (pts at 0 to 2), raylib.RAYWHITE
    return 0
```

### 🗺️ Desglose por familia

Los recuentos son los `declare` de `raylib.d.pengu` agrupados por familia de nombre C, y son la estimación de alcance de cada sub-plan. Los nombres C están agrupados según los comentarios de módulo del propio header.

| # | Familia | ~Funciones | Familias C destacadas | Sub-plan |
|---|---|---|---|---|
| 1 | `window` ✅ implementada (67 recontadas) | las 55 de la sección de ventana más timing, control de fotograma y logging. **Solo 11 se envuelven**: raylib no tiene un tipo ventana que sirva de receptor, así que la §9 fila 1 y el criterio 2 dejan fuera los 56 getters, mutadores void y setters planos. `InitWindow`/`CloseWindow` los excluye explícitamente la §9 fila 8. Ver `docs/plans/raylibx_window.md` |
| 2 | `input` ✅ implemented | 47 (recontadas) | `IsKey*`, `GetKey*`, `Is/GetMouse*`, `SetMouse*`, `GetTouch*`, `Is/Set/GetGamepad*`, `SetGesturesEnabled`, `IsGestureDetected`, `GetGesture*` | `docs/plans/raylibx_input.md` |
| 3 | `drawing` | ~11 | `Begin/EndDrawing`, `Begin/EndMode2D`, `Begin/EndMode3D`, `Begin/EndTextureMode`, `Begin/EndShaderMode`, `Begin/EndBlendMode`, `Begin/EndScissorMode`, `ClearBackground`. **`DrawFPS` is not here** (D6/I2): it belongs to `text` | `docs/plans/raylibx_drawing.md` |
| 4 | `shapes` ✅ implemented | 75 (recounted) | `DrawLine*`, `DrawCircle*`, `DrawRectangle*`, `DrawEllipse*`, `DrawRing*`, `DrawPoly*`, `DrawTriangle*`, `DrawPixel*`, splines, `SetShapesTexture` | `docs/plans/raylibx_shapes.md` |
| 5 | `shapes3d` ✅ implemented | 21 | `DrawCube*`, `DrawSphere*`, `DrawCylinder*`, `DrawCapsule*`, `DrawPlane`, `DrawRay`, `DrawGrid`, `DrawBoundingBox`, `DrawLine3D`, `DrawPoint3D`, `DrawTriangle3D`, `DrawTriangleStrip3D` | `docs/plans/raylibx_shapes3d.md` |
| 6 | `text` ✅ implemented | 59 (recounted) | `LoadFont*`, `IsFontValid`, `DrawText*`, `MeasureText*`, los 23 helpers `Text*`, `GetGlyph*`, `SetTextLineSpacing`, `GetFontDefault`, `DrawFPS` (la posee, D6/I2) | `docs/plans/raylibx_text.md` |
| 7 | `textures` | ~40 (del grupo de texturas) | `LoadTexture*`, `IsTextureValid`, `Load/UnloadRenderTexture`, `UpdateTexture*`, `DrawTexture*`, `SetTextureFilter/Wrap` | `docs/plans/raylibx_textures.md` |
| 8 | `images` ✅ implemented | 90 (recounted) | cada mutador `Image*`, `LoadImage*`, `IsImageValid`, `GenImage*`, `ExportImage*`, `GetImage*`, `LoadImageColors/Palette` | `docs/plans/raylibx_images.md` |
| 9 | `colors` | 12 | `Color*`, `Fade`, `GetColor`, `SetPixelColor`, `GetPixelColor` | `docs/plans/raylibx_colors.md` |
| 10 | `models` ✅ implementada (52 recontadas) | las 52 funciones del banner de modelos: 37 envueltas (19 métodos y 18 de módulo), 11 generadores omitidos por la §9 fila 11 y 3 billboards reasignados a `rcamerax` por receptor (D12). **Una proporción 1:1**: ninguna función C da varios wrappers |
| 11 | `audio` ✅ implementada (66 recontadas) | las 66 funciones de la sección: 55 envueltas (**41 métodos**, porque hay **cuatro tipos receptores**, y 14 de módulo), 5 callbacks omitidos por la §9 fila 6 y 6 de configuración de un solo uso. **El dispositivo de audio existe medido**, así que la familia tiene 8 tests reales |
| 12 | `files` | 54 | `Load/Unload/SaveFile*`, `File*`, `Directory*`, `IsFile*`, `IsPath*`, `GetFile*`, `LoadDirectoryFiles*`, `LoadDroppedFiles`, `Compress/Decompress/Encode/Decode`, `ComputeCRC32/MD5/SHA1/SHA256` | `docs/plans/raylibx_files.md` |
| 13 | `shaders` ✅ implementada (10 + 8 reasignadas) | las 10 funciones de la sección de shaders, todas envueltas en 15 wrappers. `SetShaderValue` da siete métodos tipados; los dos cargadores comprueban su precondición porque raylib sustituye el shader por defecto en silencio. Las 8 funciones de proyección que esta fila listaba se reasignan a `rcamerax` (D13 de ese plan) |
| 14 | `random` ✅ implementada (4 recontadas) | las cuatro funciones de azar de raylib: **2 envueltas y 2 omitidas**. `GetRandomValue` pasa a `between`, un `Get*` renombrado a un sustantivo Pengunic, y el único sitio donde quedan escritos los hechos del rango inclusivo y del intercambio silencioso; `LoadRandomSequence` pasa a `sequence`, que pliega un centinela NULL en `maybe list of int` y posee el array de C para que el llamador no pueda filtrarlo. `SetRandomSeed` se omite por la §9 fila 8 y `UnloadRandomSequence` por la fila 4. Trae dos trampas medidas: el generador de raylib tiene una **semilla por defecto fija**, así que un programa sin sembrar se repite en cada ejecución, y `LoadRandomSequence` responde a una petición imposible con un puntero NULL y a un rango invertido con **valores fuera de ambos límites**. Ver `docs/plans/raylibx_random.md` |

Las estimaciones por grupo suman **~555**. El binding tiene **619** funciones, así que la diferencia (~64) son las exclusiones de `D14` (~20) más el error de estimación de las tres familias marcadas con `~` (`drawing`, `textures`, `shaders`). `Total estimado: ~555 (recalcular en Fase 1b)` — **cada plan de familia debe recontar su propio grupo con exactitud, y estos recuentos del plan maestro son estimaciones de alcance, no compromisos.**

**Requisitos de cada plan de familia.** Cada sub-plan sigue la plantilla del contrato y añade las dos cosas que este plan maestro no puede dar:

1. Las tablas completas de métodos/funciones (la enumeración por símbolo que el contrato difiere a Fase 1).
2. Una tabla "🚫 NO se envuelve" con el motivo de cada símbolo que la familia deja fuera, incluido el conjunto de D14.

### 🚫 NO se envuelve (todo el módulo)

| Grupo de símbolos | Motivo |
|---|---|
| `TraceLog` | C variádica; el wrapper no puede construir la lista de argumentos (contrato §9 fila 5) |
| `TextFormat` | igual: variádica, y devuelve un `char*` que el llamador no posee |
| `SetTraceLogCallback`, `SetLoadFileDataCallback`, `SetSaveFileDataCallback`, `SetLoadFileTextCallback`, `SetSaveFileTextCallback`, `SetAudioStreamCallback` | no hay closures en PenguScript; el binding ya es la interfaz correcta (contrato §9 fila 6) |
| `MemAlloc`, `MemRealloc`, `MemFree` | asignación cruda; `MemFree` se usa *dentro* de los wrappers que poseen un búfer de raylib, nunca como API expuesta (contrato §8/§9) |
| `SetConfigFlags`, `SetExitKey`, `SetTraceLogLevel` | configuración global de un solo uso; llamarlas una vez no justifica un wrapper (contrato §9 fila 8) |
| VR y automatización (`LoadVrStereoConfig`, `SetVrStereoConfig`, `*AutomationEvent*`) | fuera del 20 % que importa, y el plan de `window` debe decirlo explícitamente |
| `GetWindowHandle` | devuelve un `void*` que el usuario nunca manipula (contrato §9 fila 7) |
| Los `alias` de callback (`TraceLogCallback`, `LoadFileDataCallback`, `SaveFileDataCallback`, `LoadFileTextCallback`, `SaveFileTextCallback`, `AudioCallback`) | son declaraciones de tipo, no funciones; el wrapper no redeclara tipos del binding |

### 🧪 Plan de tests

Por familia, según el contrato §12: tres tests por método público, inline, en el archivo de la familia. La división que importa aquí es qué puede correr en CI:

| Familia | Testeable en CI por sí sola | Necesita ventana / GPU / dispositivo de audio |
|---|---|---|
| `colors`, `shapes` (parte matemática), `shapes3d` (parte matemática), `files`, `models` (parte matemática), `text` (medición) | sí, cuando la llamada no dibuja | las llamadas `Draw*` en sí |
| `window`, `drawing`, `textures`, `images`, `audio` | la rama de fallo `maybe` con un fichero ausente y los helpers puros | todo lo que crea un dispositivo o dibuja |

La regla que deben seguir los planes de familia: un método que dibuja o necesita dispositivo recibe un test de advertencia documentada (una ruta de fallo, un helper puro o un equivalente de forma/medición) y se marca como no asegurado en CI. Es la misma degradación ya usada en `raymathx` y `rcamerax`.

### 🗺️ Orden de implementación

| Orden | Familia | Por qué aquí |
|---|---|---|
| 1 | `colors` | 12 funciones puras, sin dispositivo y sin cadenas; la pasada completa más barata y fija la propiedad de los métodos de `Color` (D7) |
| 2 | `files` | E/S y hashes puros; ejercita toda la política de cadenas (D13) sin GPU |
| 3 | `shapes` | la primera familia con `Draw*` y con funciones de forma slice (D12) |
| 4 | `text` | el eje de la política de cadenas; las fuentes la convierten en la mayor familia `maybe` después de texturas |
| 5 | `images` | 61 mutadores sobre un tipo; la tabla de métodos de `Image` es la mayor del módulo |
| 6 | `textures` | pequeña y empareja con `images` y `text` |
| 7 | `shapes3d` | refleja `shapes` en 3D |
| 8 | `models` | la segunda superficie mayor, y posee los predicados de colisión 3D |
| 9 | `audio` | grande pero mecánicamente uniforme; necesita dispositivo para la mitad de sus tests |
| 10 | `window` | estado global y ciclo de vida de la ventana; superficie útil pequeña una vez aterrizada la familia de dispositivo |
| 11 | `input` | incluye las ocho funciones de gestos rescatadas del archivado `rgesturesx` |
| 12 | `drawing` ✅ implementada (15) | los pares `Begin/End`. **La pregunta de diseño está respondida: sin helper equilibrado basado en lambda**, porque los lambdas de PenguScript no capturan locales y un cuerpo de dibujo siempre necesita el estado del llamador; `defer` al salir del ámbito es el equilibrio idiomático. Ver D3/D4 de `docs/plans/raylibx_drawing.md` |
| 13 | `shaders` | los uniforms necesitan manejo de `void*`; hacerlo al final, con todo el módulo como contexto |
| 14 | `random` | el apéndice de azar: dos envolturas, sin receptor y sin ventana, así que es la familia más barata de añadir |

### 🧱 `rlglx` (registrado aquí, planificado aparte)

`pengu/rlgl.d.pengu` declara 163 funciones en 621 líneas: 126 envoltorios crudos de OpenGL y 37 helpers de nivel raylib, con 22 firmas de forma slice y sin `insignia`. Según los propios criterios de skip del contrato (§9 fila 9), la conclusión esperada es **"no envolver casi nada; usar el binding directo"**: la capa existe para ser la salida de emergencia a OpenGL, y un renombrado Pengunic no aporta nada. Su plan corresponde a `docs/plans/rlglx.md` (módulo de nivel raíz, `pengu/rlglx.pengu`), no bajo `raylibx/`. Los únicos candidatos que merecen sopesarse allí son los helpers de nivel raylib (`rlLoadRenderBatch`, `rlSetMatrix*`, `rlGetTextureIdDefault`) y los arrays de estado con forma slice (`rlSetUniformMatrices`). **El plan está escrito y el veredicto está dado** (`docs/plans/rlglx.md`): la capa es **factible** — una sonda compila, enlaza y ejecuta rlgl desde PenguScript, incluido un búfer de vértices alimentado por un slice y un programa de shader con dos cadenas — pero **se envuelven 18 de las 163 funciones y se omiten 145 (89 %)**, la mayor tasa de descarte del módulo. El conjunto envuelto son exactamente los cruces de frontera: cinco conversiones de cadena, nueve pliegues de slice y los dos métodos del tipo `rlRenderBatch`. Este plan maestro solo registraba la expectativa; los números son de `rlglx`.

### 🧱 `raygui` / `rayguix` (registrado aquí, planificado aparte)

`pengu/raygui.d.pengu` declara 61 funciones sobre raygui **5.1-dev**, y es el único binding cuya usabilidad estuvo en duda antes de que existiera wrapper alguno: raygui es una biblioteca de cabecera única cuya implementación solo existe en una unidad de traducción que define `RAYGUI_IMPLEMENTATION`. **La pregunta ya la responde el repositorio, no este plan**: `c/raygui_impl.c` lleva el macro y el build compila `c/*.c` de cada binding instalado dentro del bundle. Medido, `nm -D /usr/lib/libraylib.so | grep -c Gui` da **0**, así que el puente es portante y no decorativo, y una sonda enlaza y ejecuta los widgets de extremo a extremo. De las tres rutas que se consideraron — bloques C con `antiquus`, un puente `.c` o cambiar el compilador — la primera está **prohibida por el contrato en la capa 2** (§1, §9.6), la segunda ya está puesta y la tercera es innecesaria. Su plan es `docs/plans/rayguix.md` y su veredicto es **38 de las 61 funciones envueltas y 23 omitidas**: los 34 widgets de frontera de cadena más los tres campos de texto, cuya forma `ref to string` se demostró en un test vivo antes de escribir el plan. De ahí salieron dos trampas medidas, registradas para todo el proyecto: la **fuente de raygui vive en un global de proceso que se inicializa una sola vez**, así que un programa que recrea la ventana debe llamar a `GuiSetFont(GetFontDefault())` o `text_width` devuelve `0` (D10 de ese plan); y **`GuiLoadStyleFromMemory` no valida la longitud de su búfer**, así que ocho bytes que empiecen por el magic válido `rGS ` revientan el proceso — por eso la única función con forma de slice de la familia deliberadamente **no** se envuelve.
