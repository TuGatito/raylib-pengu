# Plan: rcamerax.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/rcamera.d.pengu`
- Wrapper target: `pengu/rcamerax.pengu`
- Dependencies: `import raylib`, `import rcamera`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete**. 12 `declare`, all 12 corresponding to exported symbols of `libraylib.so` (`nm -D` check: every one shows as `T`). Nothing missing, nothing stale. | Cross-checked each name against the installed library. The rest of `rcamera.h` lives inside `#if defined(RCAMERA_IMPLEMENTATION)` and is not consumer API. |
| D2 | **Wrapping is worth it**, with a narrower payoff than `raymathx`. Decision: build `rcamerax`. The payoff is not chaining (7 of 12 methods return `void` and cannot chain) but removing the `(sigil of cam)` boilerplate from every call site: `cam.move_forward with d, true` instead of `rcamera.CameraMoveForward with (sigil of cam), d, true`. | What buys the wrapper: 12 real functions become methods on the camera (`cam.move_forward with d, true` instead of `rcamera.CameraMoveForward with (sigil of cam), d, true`), the receiver is a `rune` that the language already passes by reference, and every method is a single direct C call. What limits it: `UpdateCamera`/`UpdateCameraPro` — the entry points that cover the ordinary raylib camera workflows — are **already declared in `raylib.d.pengu`** (`:1177`, `:1179`), so they are not part of this module, and `rcamera.h` supports **only `Camera3D`**: there is no `Camera2D` helper at all. |
| D3 | Enchanting target is `raylib.Camera3D`; the file needs both `import raylib` and `import rcamera`. Types live in `raylib.d.pengu`. | Contract §1 and §4. `enchanting rcamera.Camera3D:` is `E0004`; `Camera` is an alias of `Camera3D`, and the nominal name is the safe target (same reasoning as `raymathx` D2/D4). |
| D4 | All 12 entries are **methods on the camera**; no module-level functions. | Unlike `rgesturesx`, every function here takes the camera as its first parameter, so the receiver is obvious. Module-level functions: none apply. |
| D5 | The 7 C functions that return `void` and write through `camera as ref to Camera` become `weave … into void` **without** `@mutates`: `move_forward`, `move_up`, `move_right`, `move_to_target`, `yaw`, `pitch`, `roll`. | Contract §4 and `raymathx` D7: `@mutates` requires the receiver's own type as the return type (`E0067` otherwise). `self` is already `ref to Camera3D`, so it is passed unchanged and the C routine mutates it in place. |
| D6 | The 5 getters are pure methods: `forward`, `up`, `right`, `view_matrix`, `projection_matrix`. | They return a value derived from the camera and leave it untouched, so no `@mutates` and no `get_*` form (contract §4). |
| D7 | The boolean parameters are **kept 1:1** and documented, not split into named variants. | Splitting `CameraPitch` into one method per flag combination would turn 1 function into up to 8 methods and would bury which C call runs (`lockView` prevents somersaults, `rotateAroundTarget` picks the pivot, `rotateUp` also rotates the camera's up — `include/rcamera.h:352-407`). A transparent 1:1 mapping keeps the wrapper's value where it actually is: the receiver and the argument plumbing. The docstrings spell out the combinations. `(revisable in Fase 2 if a named convenience variant proves necessary.)` |
| D8 | `up` as a method name coexists with the `Camera3D.up` field. | Verified with `pengu 2.4.0`: a method named `up` generates `Camera3D_up`, which cannot collide with the struct field. The distinction is documented: `cam.up` is the raw field, `cam.up` called as a method is the normalised direction. |
| D9 | `CameraMoveToTarget` keeps the C semantics, corrected after reading the implementation: `delta` is an **offset added to the current camera-to-target distance**, not a new distance and not a lerp fraction. `0.0` changes nothing, a negative value pulls the camera closer, a positive value pushes it away, and the result is clamped to a small positive minimum. | `include/rcamera.h:310-326`: `distance = Vector3Distance(position, target); distance += delta; if (distance <= 0) distance = 0.001f; position = target + forward * -distance`. Measured in C from a 14.142136 distance: `delta -10` gives 4.142136, `delta +10` gives 24.142138, `delta -1000` clamps to 0.001. The docstring states this plainly, because the name invites the wrong guess. |
| D10 | `projection_matrix` takes `aspect` explicitly; no default is invented. | The C signature is `with camera as ref to Camera, aspect as f32 into Matrix`. A default would have to guess a window size, which the wrapper does not know. |
| D11 | `UpdateCamera` and `UpdateCameraPro` are **not** wrapped, and not re-exported. | They are already reachable as `raylib.UpdateCamera` / `raylib.UpdateCameraPro` from the binding the wrapper imports (D2). Re-wrapping them would add a second name for the same call (contract §9 criterion 1). |
| D12 | `CameraMoveUp` is exposed without an `in_plane` flag because the C function has none. | Asymmetry with `move_forward`/`move_right` is inherited from the header, not chosen here; it is documented rather than papered over. |
| D13 | **The appendix exists because two other plans reassigned work here**, and it is **ten wrappers**: `docs/plans/raylibx_shaders.md` D13 reassigned eight projection helpers on the receiver test of §9 criterion 2, and `docs/plans/raylibx_models.md` D12 reassigned the three billboards because the camera is their first parameter. One of the eight, `GetCameraMatrix`, was already `Camera3D.view_matrix` (§9 row 2, superseded), so seven are new methods on `Camera3D` and three open a second enchanting block for `Camera2D`. | The reassignments were promises made by the plans that could not keep them; this is where they land. |
| D14 | The projection methods are named **`to_screen`** and **`to_world_ray`** (plus their `_ex` forms), and `Camera2D` reuses `to_screen`, `to_world` and `view_matrix`. | `raylibx_shaders` D13 named the call form `camera.to_screen with position`, so the name was already decided. Reusing the same names on the two camera types is safe and deliberate: the receiver type disambiguates them, and the precedent is `raylibx.audio`, where four receiver types share `is_valid`, `play` and `stop` in one module. |
| D15 | The `_ex` forms stay separate methods with an explicit `width`/`height`, rather than folding the viewport into a `Vector2`. | They are not a convenience: measured, they are the **only** projection forms that work before a window exists, and they are what a render-to-texture pass needs, since its viewport is not the window's. Folding a pixel size into a float vector would also make the two forms harder to tell apart. |
| D16 | **A registry row in the master plan was wrong and is corrected there.** The `raylib.Camera2D` row claimed `to_world`/`to_screen` "are not wrapped: they are two-argument getters that already read well from the binding", and it assigned the type's methods to `drawing`. | The reservation was never executed — the `drawing` family has no `enchanting` block at all — and the reasoning does not survive §9 criterion 1: as a method the camera **drops out** of the argument list, so `camera.to_screen with position` is shorter than `GetWorldToScreen2D(position, camera)`, not merely clearer. The master's `Camera2D` and `Camera3D` rows now record the reassignment. |
| D17 | The methods pass the receiver as **`essence of self`**, not `self`. | Measured while writing it: the raylib projection functions and the billboards take the camera **by value** (`camera as Camera` / `Camera2D`), while every `rcamera` function this module already wrapped takes `ref to Camera`. The two shapes look alike and compile differently, and the compiler catches it — `E0005 Argument 'camera' expects 'Camera2D', got 'ref to Camera2D'`. |
| D18 | The billboard size parameter is named **`quad_size`**, not `size`. | `size` is a reserved word in PenguScript: it belongs to `size of`, and as a real identifier the parser reports `E0000 Syntax error: unexpected ','` at the comma after it. The bindings get away with `size` only because a `declare` line is parsed differently, which is exactly the kind of trap worth writing down. |

### ✨ Enchantings

No `@mutates` in this module: the 7 mutators return `void` (D5) and the 5 getters are pure (D6), so the compiler generates no `get_*` form anywhere.

#### `enchanting raylib.Camera3D`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `forward` | pure | `into raylib.Vector3` | `rcamera.GetCameraForward` | normalised view direction |
| `up` | pure | `into raylib.Vector3` | `rcamera.GetCameraUp` | normalised up; distinct from the `up` field (D8). **Docstring must state: `cam.up` (no `calling`) reads the field; `calling cam.up` invokes this method.** |
| `right` | pure | `into raylib.Vector3` | `rcamera.GetCameraRight` | normalised right |
| `view_matrix` | pure | `into raylib.Matrix` | `rcamera.GetCameraViewMatrix` | |
| `projection_matrix` | pure | `with aspect as f32 into raylib.Matrix` | `rcamera.GetCameraProjectionMatrix` | `aspect` = width / height (D10) |
| `move_forward` | mutator | `with distance as f32, in_plane as bool into void` | `rcamera.CameraMoveForward` | `in_plane` = move on the world XZ plane |
| `move_up` | mutator | `with distance as f32 into void` | `rcamera.CameraMoveUp` | no `in_plane` in the header (D12) |
| `move_right` | mutator | `with distance as f32, in_plane as bool into void` | `rcamera.CameraMoveRight` | |
| `move_to_target` | mutator | `with delta as f32 into void` | `rcamera.CameraMoveToTarget` | `delta` is an offset added to the current camera-to-target distance; negative approaches, positive retreats (D9) |
| `yaw` | mutator | `with angle as f32, around_target as bool into void` | `rcamera.CameraYaw` | `around_target` false pivots on the camera position |
| `pitch` | mutator | `with angle as f32, lock_view as bool, around_target as bool, rotate_up as bool into void` | `rcamera.CameraPitch` | `lock_view` clamps to straight up/down; `rotate_up` also turns the up vector (D7) |
| `roll` | mutator | `with angle as f32 into void` | `rcamera.CameraRoll` | radians, around the forward axis |

### ➕ Appendix: the ten reassigned wrappers

| Method | Signature | C backing |
|---|---|---|
| `Camera3D.to_screen` | `with position as raylib.Vector3 into raylib.Vector2` | `GetWorldToScreen` |
| `Camera3D.to_screen_ex` | `with position as raylib.Vector3, width as int, height as int into raylib.Vector2` | `GetWorldToScreenEx` |
| `Camera3D.to_world_ray` | `with position as raylib.Vector2 into raylib.Ray` | `GetScreenToWorldRay` |
| `Camera3D.to_world_ray_ex` | `with position as raylib.Vector2, width as int, height as int into raylib.Ray` | `GetScreenToWorldRayEx` |
| `Camera3D.draw_billboard` | `with texture as raylib.Texture, position as raylib.Vector3, scale as f32, tint as raylib.Color into void` | `DrawBillboard` |
| `Camera3D.draw_billboard_rec` | `with texture as raylib.Texture, source as raylib.Rectangle, position as raylib.Vector3, quad_size as raylib.Vector2, tint as raylib.Color into void` | `DrawBillboardRec` |
| `Camera3D.draw_billboard_pro` | `with texture as raylib.Texture, source as raylib.Rectangle, position as raylib.Vector3, up as raylib.Vector3, quad_size as raylib.Vector2, origin as raylib.Vector2, rotation as f32, tint as raylib.Color into void` | `DrawBillboardPro` |
| `Camera2D.to_screen` | `with position as raylib.Vector2 into raylib.Vector2` | `GetWorldToScreen2D` |
| `Camera2D.to_world` | `with position as raylib.Vector2 into raylib.Vector2` | `GetScreenToWorld2D` |
| `Camera2D.view_matrix` | `into raylib.Matrix` | `GetCameraMatrix2D` |

Six of the ten draw nothing and touch no screen size, which is what makes most of them testable without a window. The measured facts the appendix rests on:

| # | Measurement | Result |
|---|---|---|
| M1 | `GetWorldToScreen` and `GetScreenToWorldRay` in a program that **never created a window** | `NaN` components, silently: the screen size is zero and the functions divide by it. No error, no crash. |
| M2 | The same two **with** a window | Correct, and equal to their `_ex` forms to the pixel. |
| M3 | `GetWorldToScreenEx`, `GetScreenToWorldRayEx`, `GetCameraMatrix` and all three `Camera2D` entries with no window | Correct, which is why the `_ex` forms are the escape hatch and not a duplicate. |
| M4 | The screen size after `CloseWindow` | Still the last window's size, so the `NaN` of M1 only ever shows in a program that never opens a window at all. |
| M5 | `GetCameraMatrix2D` for `target (100, 100)`, `offset (0, 0)`, `zoom 1`, `rotation 0` | `m0 = 1`, `m5 = 1`, `m12 = -100`, `m13 = -100`: the translation by `-target`. |
| M6 | `GetWorldToScreen2D` of the camera's own target, even with `zoom 2` and a non-zero offset | Exactly the camera's `offset`, which is what that field means. |
| M7 | `GetWorldToScreen2D` then `GetScreenToWorld2D` on the same point | An exact round trip. |

### 🔧 Module-level functions

**None apply.** All 12 source functions take the camera as their first parameter, so every one of them is a method (D4). There is no free-function gesture (unlike `rgesturesx`) and no scalar helper (unlike `raymathx`).

### 🎁 `maybe T` wrappers

**None apply.** No camera function can fail: each one is arithmetic over the camera struct plus raymath helpers, with no file, GPU, audio device or pointer that can be null. `CameraMoveToTarget` on a camera whose position equals its target yields `NaN` inside the matrix rather than an error, and `projection_matrix` with `aspect == 0` divides by zero; both are *wrong values*, not *absent values*, so they are documented in the docstrings and deliberately not modelled as `maybe` (contract §3).

### ✂️ `slice` wrappers

**None apply.** No function takes `(T* ptr, int count)`; the only pointer parameter is the receiver itself.

### 📦 Multiple returns `(T, U)`

**None apply.** Every function returns one `Vector3`/`Matrix` or nothing. A camera pose is two `Vector3` fields of a `rune` (`Camera3D.position` / `.target`) that the caller reads directly, so no tuple is needed.

### 🌉 `std.ffi` usage

**None apply, reason: the only pointer in play is the receiver, and it is already the right shape.** The C signatures take `Camera *`, which the binding declares as `ref to Camera`; inside an `enchanting` block `self` **is** `ref to Camera3D`, so it is passed as-is. There is no `char*`, no `void*`, no slice and no `transmute`. `import std.ffi` is not in the dependency list.

### 💡 Compilable examples

Verified with `pengu expand` against a draft of the wrapper.

```pengu
# Example 1 — orienting a camera with the pure getters
import raylib
import raymathx
import rcamerax

weave make_camera into raylib.Camera3D:
    return with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0

weave main into int:
    var cam as raylib.Camera3D is calling make_camera
    var forward as raylib.Vector3 is calling cam.forward
    var up as raylib.Vector3 is calling cam.up
    var right as raylib.Vector3 is calling cam.right
    var view as raylib.Matrix is calling cam.view_matrix
    var projection as raylib.Matrix is calling cam.projection_matrix with 1.7777778
    return 0
```

```pengu
# Example 2 — driving a custom camera controller
import raylib
import raymathx
import rcamerax

weave main into int:
    var cam as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    calling cam.move_forward with 0.1, true
    calling cam.move_right with 0.1, true
    calling cam.move_up with 0.05
    calling cam.yaw with 0.01, true
    calling cam.pitch with 0.01, true, true, false
    calling cam.roll with 0.01
    calling cam.move_to_target with 0.05
    return 0
```

```pengu
# Example 3 — feeding camera getters into raymathx methods
import raylib
import raymathx
import rcamerax

weave main into int:
    var cam as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    var forward as raylib.Vector3 is calling cam.forward
    var cam_up as raylib.Vector3 is calling cam.up
    var view as raylib.Matrix is calling cam.view_matrix
    var forward_len as f32 is calling forward.length
    var half_up as raylib.Vector3 is calling cam_up.get_scale with 0.5
    var forward_added as raylib.Vector3 is calling forward.get_add with half_up
    var inv_view as raylib.Matrix is calling view.get_invert
    return 0
```

**Compiler constraint (verified on `pengu 2.4.0`):** a method call **result** cannot be chained directly — `calling cam.forward.length` is rejected with `Type 'Camera3D' does not define method 'length'`, and `calling a.get_add with b.length` is a parse error. Chaining works only when each link starts from a binding or a field (`calling a.get_add with b` then `calling (local).get_add with c`), so cross-wrapper composition needs one local per link. This is why chaining is **not** the argument for this wrapper (D2); the argument is removing `(sigil of cam)`.

### 🧪 Test plan

All 12 methods are pure arithmetic over a camera struct, so every test runs in **CI with no window, GPU or input** (verified with `pengu test` on a headless run). Three tests per method, using a locally built camera:

- **`forward`**: unit length; points from `position` towards `target`; a camera looking down `-Z` gives approximately `(0, 0, -1)`.
- **`up`**: unit length; orthogonal to `forward`; a default camera yields approximately `(0, 1, 0)`.
- **`right`**: unit length; orthogonal to both `forward` and `up`; the right-handed cross product `forward × up` agrees in sign.
- **`view_matrix`**: finite components; the identity camera (position `(0,0,1)`, target at origin) maps the origin to the origin; translation lands in `m12..m14`.
- **`projection_matrix`**: finite with a normal aspect; `m11` non-zero (the perspective term); a wider field of view shrinks `m0` monotonically.
- **`move_forward`**: positive distance moves the camera along `forward`; `in_plane` true leaves `position.y` unchanged; zero distance is a no-op.
- **`move_up`**: positive distance raises `position.y`; negative lowers it; zero is a no-op.
- **`move_right`**: positive distance moves along `right`; `in_plane` true keeps `position.y`; zero is a no-op.
- **`move_to_target`**: `delta = 1` puts the position on the target; `delta = 0` is a no-op; the result stays finite for a degenerate camera whose position equals its target (documented `NaN` case).
- **`yaw`**: `around_target` true keeps `position` fixed and moves `target`; false does the opposite; a full turn returns the camera to its starting orientation within epsilon.
- **`pitch`**: `lock_view` true clamps the angle instead of over-rotating; `rotate_up` true changes the `up` field and false leaves it; `around_target` picks which endpoint moves.
- **`roll`**: a non-zero angle changes the `up` field; a full turn restores it within epsilon; zero is a no-op.

The appendix adds six more tests. **Five of them open no window at all**, which is new for this module's drawing side:

- **`Camera2D.to_screen` lands the target on the offset** — pins M6 with a zoom of 2 and a non-zero offset.
- **`Camera2D.to_screen` and `to_world` are an exact round trip** — pins M7, with the measured intermediate value `(50, 20)` asserted as well.
- **`Camera2D.view_matrix` is a translation by the target** — pins M5 field by field.
- **`Camera3D.to_screen_ex` centres the target with no window** — the escape hatch of M3, asserted to be exactly the viewport's centre.
- **`Camera3D.to_world_ray_ex` points from the camera through the target** — the ray's direction is asserted component by component, and its origin at the camera.
- **With a window the base projections agree with the `_ex` forms and the billboards draw** — the base forms are only meaningful once a window exists (M1, M4), so they are asserted *against* their `_ex` twins, and the three billboards are drawn on a real texture, which is the only way to exercise them.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `UpdateCamera`, `UpdateCameraPro` | Already declared in `raylib.d.pengu` (`:1177`, `:1179`) and reachable as `raylib.UpdateCamera` / `raylib.UpdateCameraPro`; wrapping them here would add a second name for the same call (D11, contract §9 criterion 1). |
| Everything else in `rcamera.h` | Not consumer API: the remaining definitions sit inside `#if defined(RCAMERA_IMPLEMENTATION)` (`include/rcamera.h:171-562`). `pengu bind` correctly did not declare them. |
| `CAMERA_CULL_DISTANCE_NEAR`, `CAMERA_CULL_DISTANCE_FAR`, `CAMERA_MOVE_SPEED` and the other tuning macros | Expand to `RL_CULL_DISTANCE_*` (undefined unless `rlgl.h` is included) or live inside `RCAMERA_IMPLEMENTATION`; the binding does not export them and the wrapper cannot invent them. Tuning them means recompiling raylib. |
| `Camera2D` and any 2D camera helper | Does not exist in `rcamera.h`. 2D cameras are plain field arithmetic on `raylib.Camera2D` and stay in user code; this module is `Camera3D` only (D2). |

Coverage audit: of the 12 functions declared in `rcamera.d.pengu`, **12 are wrapped** — 5 pure methods and 7 mutating methods, all on `raylib.Camera3D`. Nothing is skipped, and no module-level function is needed (D4).

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/rcamera.d.pengu`
- Wrapper destino: `pengu/rcamerax.pengu`
- Dependencias: `import raylib`, `import rcamera`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo**. 12 `declare`, y las 12 corresponden a símbolos exportados por `libraylib.so` (comprobación con `nm -D`: todas aparecen como `T`). No falta ninguna ni sobra ninguna. | Verificado nombre a nombre contra la biblioteca instalada. El resto de `rcamera.h` vive dentro de `#if defined(RCAMERA_IMPLEMENTATION)` y no es API de consumidor. |
| D2 | **Vale la pena envolverlo**, con un beneficio más estrecho que `raymathx`. Decisión: hacer `rcamerax`. El beneficio no es el encadenamiento (7 de 12 métodos devuelven `void` y no encadenan) sino eliminar el ruido de `(sigil of cam)` en cada sitio de llamada: `cam.move_forward with d, true` en lugar de `rcamera.CameraMoveForward with (sigil of cam), d, true`. | Lo que aporta: 12 funciones reales pasan a ser métodos de la cámara (`cam.move_forward with d, true` en lugar de `rcamera.CameraMoveForward with (sigil of cam), d, true`), el receptor es un `rune` que el lenguaje ya pasa por referencia, y cada método es una sola llamada C directa. Lo que lo limita: `UpdateCamera`/`UpdateCameraPro` — los puntos de entrada que cubren los flujos de cámara habituales de raylib — **ya están declarados en `raylib.d.pengu`** (`:1177`, `:1179`), así que no forman parte de este módulo, y `rcamera.h` solo soporta **`Camera3D`**: no hay ningún helper de `Camera2D`. |
| D3 | El objetivo de `enchanting` es `raylib.Camera3D`; el archivo necesita `import raylib` y `import rcamera`. Los tipos viven en `raylib.d.pengu`. | Contrato §1 y §4. `enchanting rcamera.Camera3D:` es `E0004`; `Camera` es alias de `Camera3D`, y el nombre nominal es el objetivo seguro (mismo razonamiento que `raymathx` D2/D4). |
| D4 | Las 12 entradas son **métodos de la cámara**; ninguna función de módulo. | A diferencia de `rgesturesx`, aquí todas las funciones reciben la cámara como primer parámetro, así que el receptor es obvio. Funciones de módulo: ninguna aplica. |
| D5 | Las 7 funciones C que devuelven `void` y escriben por `camera as ref to Camera` pasan a `weave … into void` **sin** `@mutates`: `move_forward`, `move_up`, `move_right`, `move_to_target`, `yaw`, `pitch`, `roll`. | Contrato §4 y `raymathx` D7: `@mutates` exige el tipo del propio receptor como retorno (`E0067` en otro caso). `self` ya es `ref to Camera3D`, así que se pasa tal cual y la rutina C lo muta en su sitio. |
| D6 | Los 5 getters son métodos puros: `forward`, `up`, `right`, `view_matrix`, `projection_matrix`. | Devuelven un valor derivado de la cámara y no la tocan, así que no llevan `@mutates` ni forma `get_*` (contrato §4). |
| D7 | Los parámetros booleanos se mantienen **1:1** y documentados, no se parten en variantes con nombre. | Partir `CameraPitch` en un método por combinación de flags convertiría 1 función en hasta 8 métodos y escondería qué llamada C se ejecuta (`lockView` evita las piruetas, `rotateAroundTarget` elige el pivote, `rotateUp` rota además el vector up — `include/rcamera.h:352-407`). Un mapeo 1:1 transparente deja el valor del wrapper donde realmente está: el receptor y el paso de argumentos. Los docstrings explican las combinaciones. `(revisable en Fase 2 si una variante con nombre resulta necesaria.)` |
| D8 | El nombre de método `up` convive con el campo `Camera3D.up`. | Verificado con `pengu 2.4.0`: un método llamado `up` genera `Camera3D_up`, que no puede colisionar con el campo del struct. La distinción queda documentada: `cam.up` es el campo crudo, `cam.up` invocado como método es la dirección normalizada. |
| D9 | `CameraMoveToTarget` conserva la semántica C, corregida tras leer la implementación: `delta` es un **desplazamiento que se suma a la distancia actual** entre cámara y objetivo, no una distancia nueva ni una fracción de interpolación. `0.0` no cambia nada, un valor negativo acerca la cámara, uno positivo la aleja, y el resultado se acota a un mínimo positivo pequeño. | `include/rcamera.h:310-326`: `distance = Vector3Distance(position, target); distance += delta; if (distance <= 0) distance = 0.001f; position = target + forward * -distance`. Medido en C desde una distancia de 14.142136: `delta -10` da 4.142136, `delta +10` da 24.142138, `delta -1000` se acota a 0.001. El docstring lo dice sin rodeos, porque el nombre invita a la conjetura equivocada. |
| D10 | `projection_matrix` recibe `aspect` explícito; no se inventa un valor por defecto. | La firma C es `with camera as ref to Camera, aspect as f32 into Matrix`. Un valor por defecto tendría que adivinar un tamaño de ventana, que el wrapper no conoce. |
| D11 | `UpdateCamera` y `UpdateCameraPro` **no** se envuelven ni se reexportan. | Ya son alcanzables como `raylib.UpdateCamera` / `raylib.UpdateCameraPro` desde el binding que el wrapper importa (D2). Reenvolverlos añadiría un segundo nombre para la misma llamada (contrato §9, criterio 1). |
| D12 | `CameraMoveUp` se expone sin flag `in_plane` porque la función C no lo tiene. | La asimetría con `move_forward`/`move_right` viene del header, no se elige aquí; se documenta en vez de disimularla. |
| D13 | **El apéndice existe porque otros dos planes reasignaron trabajo aquí**, y son **diez envolturas**: el D13 de `docs/plans/raylibx_shaders.md` reasignó ocho helpers de proyección por el criterio del receptor del §9 criterio 2, y el D12 de `docs/plans/raylibx_models.md` reasignó los tres billboards porque la cámara es su primer parámetro. Uno de los ocho, `GetCameraMatrix`, ya era `Camera3D.view_matrix` (§9 fila 2, superseded), así que siete son métodos nuevos en `Camera3D` y tres abren un segundo bloque de `enchanting` para `Camera2D`. | Las reasignaciones eran promesas hechas por los planes que no podían cumplirlas; aquí es donde aterrizan. |
| D14 | Los métodos de proyección se llaman **`to_screen`** y **`to_world_ray`** (más sus formas `_ex`), y `Camera2D` reutiliza `to_screen`, `to_world` y `view_matrix`. | El D13 de `raylibx_shaders` ya nombró la forma de llamada `camera.to_screen with position`, así que el nombre estaba decidido. Reutilizar los mismos nombres en los dos tipos de cámara es seguro y deliberado: el tipo del receptor los desambigua, y el precedente es `raylibx.audio`, donde cuatro tipos receptores comparten `is_valid`, `play` y `stop` en un mismo módulo. |
| D15 | Las formas `_ex` se quedan como métodos aparte con `width`/`height` explícitos, en vez de plegar el viewport en un `Vector2`. | No son una comodidad: medido, son las **únicas** formas de proyección que funcionan antes de que exista una ventana, y son lo que necesita una pasada de render a textura, porque su viewport no es el de la ventana. Plegar un tamaño en píxeles dentro de un vector de flotantes también haría más difícil distinguir las dos formas. |
| D16 | **Una fila del registro del plan maestro estaba equivocada y se corrige allí.** La fila de `raylib.Camera2D` afirmaba que `to_world`/`to_screen` "no se envuelven: son getters de dos argumentos que ya se leen bien desde el binding", y asignaba los métodos del tipo a `drawing`. | La reserva nunca se ejecutó — la familia `drawing` no tiene ni un bloque `enchanting` — y el razonamiento no sobrevive al criterio 1 del §9: como método, la cámara **sale** de la lista de argumentos, así que `camera.to_screen with position` es más corto que `GetWorldToScreen2D(position, camera)`, no solo más claro. Las filas de `Camera2D` y `Camera3D` del maestro ahora registran la reasignación. |
| D17 | Los métodos pasan el receptor como **`essence of self`**, no `self`. | Medido al escribirlo: las funciones de proyección de raylib y los billboards reciben la cámara **por valor** (`camera as Camera` / `Camera2D`), mientras que todas las funciones de `rcamera` que este módulo ya envolvía reciben `ref to Camera`. Las dos formas se parecen y compilan distinto, y el compilador lo caza — `E0005 Argument 'camera' expects 'Camera2D', got 'ref to Camera2D'`. |
| D18 | El parámetro de tamaño de los billboards se llama **`quad_size`**, no `size`. | `size` es palabra reservada en PenguScript: pertenece a `size of`, y como identificador real el parser informa `E0000 Syntax error: unexpected ','` en la coma que le sigue. Los bindings se salvan con `size` solo porque una línea `declare` se parsea de otra forma, que es justo el tipo de trampa que merece quedar escrita. |

### ✨ Enchantings

En este módulo no hay `@mutates`: los 7 mutadores devuelven `void` (D5) y los 5 getters son puros (D6), así que el compilador no genera ninguna forma `get_*`.

#### `enchanting raylib.Camera3D`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `forward` | puro | `into raylib.Vector3` | `rcamera.GetCameraForward` | dirección de vista normalizada |
| `up` | puro | `into raylib.Vector3` | `rcamera.GetCameraUp` | up normalizado; distinto del campo `up` (D8). **El docstring debe decir: `cam.up` (sin `calling`) lee el campo; `calling cam.up` invoca este método.** |
| `right` | puro | `into raylib.Vector3` | `rcamera.GetCameraRight` | derecha normalizada |
| `view_matrix` | puro | `into raylib.Matrix` | `rcamera.GetCameraViewMatrix` | |
| `projection_matrix` | puro | `with aspect as f32 into raylib.Matrix` | `rcamera.GetCameraProjectionMatrix` | `aspect` = ancho / alto (D10) |
| `move_forward` | mutador | `with distance as f32, in_plane as bool into void` | `rcamera.CameraMoveForward` | `in_plane` = moverse en el plano XZ del mundo |
| `move_up` | mutador | `with distance as f32 into void` | `rcamera.CameraMoveUp` | sin `in_plane` en el header (D12) |
| `move_right` | mutador | `with distance as f32, in_plane as bool into void` | `rcamera.CameraMoveRight` | |
| `move_to_target` | mutador | `with delta as f32 into void` | `rcamera.CameraMoveToTarget` | `delta` es un desplazamiento que se suma a la distancia actual cámara-objetivo; negativo acerca, positivo aleja (D9) |
| `yaw` | mutador | `with angle as f32, around_target as bool into void` | `rcamera.CameraYaw` | con `around_target` en falso pivota sobre la posición de la cámara |
| `pitch` | mutador | `with angle as f32, lock_view as bool, around_target as bool, rotate_up as bool into void` | `rcamera.CameraPitch` | `lock_view` acota a mirar recto arriba/abajo; `rotate_up` gira también el vector up (D7) |
| `roll` | mutador | `with angle as f32 into void` | `rcamera.CameraRoll` | radianes, alrededor del eje forward |

### ➕ Apéndice: las diez envolturas reasignadas

| Método | Firma | C backing |
|---|---|---|
| `Camera3D.to_screen` | `with position as raylib.Vector3 into raylib.Vector2` | `GetWorldToScreen` |
| `Camera3D.to_screen_ex` | `with position as raylib.Vector3, width as int, height as int into raylib.Vector2` | `GetWorldToScreenEx` |
| `Camera3D.to_world_ray` | `with position as raylib.Vector2 into raylib.Ray` | `GetScreenToWorldRay` |
| `Camera3D.to_world_ray_ex` | `with position as raylib.Vector2, width as int, height as int into raylib.Ray` | `GetScreenToWorldRayEx` |
| `Camera3D.draw_billboard` | `with texture as raylib.Texture, position as raylib.Vector3, scale as f32, tint as raylib.Color into void` | `DrawBillboard` |
| `Camera3D.draw_billboard_rec` | `with texture as raylib.Texture, source as raylib.Rectangle, position as raylib.Vector3, quad_size as raylib.Vector2, tint as raylib.Color into void` | `DrawBillboardRec` |
| `Camera3D.draw_billboard_pro` | `with texture as raylib.Texture, source as raylib.Rectangle, position as raylib.Vector3, up as raylib.Vector3, quad_size as raylib.Vector2, origin as raylib.Vector2, rotation as f32, tint as raylib.Color into void` | `DrawBillboardPro` |
| `Camera2D.to_screen` | `with position as raylib.Vector2 into raylib.Vector2` | `GetWorldToScreen2D` |
| `Camera2D.to_world` | `with position as raylib.Vector2 into raylib.Vector2` | `GetScreenToWorld2D` |
| `Camera2D.view_matrix` | `into raylib.Matrix` | `GetCameraMatrix2D` |

Seis de las diez no dibujan nada ni tocan el tamaño de pantalla, que es lo que hace que la mayoría sean testeables sin ventana. Los hechos medidos en los que se apoya el apéndice:

| # | Medición | Resultado |
|---|---|---|
| M1 | `GetWorldToScreen` y `GetScreenToWorldRay` en un programa que **nunca creó una ventana** | Componentes `NaN`, en silencio: el tamaño de pantalla es cero y las funciones dividen por él. Sin error y sin crash. |
| M2 | Esas mismas dos **con** ventana | Correctas, e iguales a sus formas `_ex` al píxel. |
| M3 | `GetWorldToScreenEx`, `GetScreenToWorldRayEx`, `GetCameraMatrix` y las tres entradas de `Camera2D` sin ventana | Correctas, que es por lo que las formas `_ex` son la salida de emergencia y no un duplicado. |
| M4 | El tamaño de pantalla tras `CloseWindow` | Sigue siendo el de la última ventana, así que el `NaN` de M1 solo aparece en un programa que no abre ninguna ventana. |
| M5 | `GetCameraMatrix2D` para `target (100, 100)`, `offset (0, 0)`, `zoom 1`, `rotation 0` | `m0 = 1`, `m5 = 1`, `m12 = -100`, `m13 = -100`: la traslación por `-target`. |
| M6 | `GetWorldToScreen2D` del propio objetivo de la cámara, incluso con `zoom 2` y offset distinto de cero | Exactamente el `offset` de la cámara, que es lo que significa ese campo. |
| M7 | `GetWorldToScreen2D` y luego `GetScreenToWorld2D` sobre el mismo punto | Una ida y vuelta exacta. |

### 🔧 Funciones a nivel de módulo

**Ninguna aplica.** Las 12 funciones de origen reciben la cámara como primer parámetro, así que todas son métodos (D4). No hay función libre (a diferencia de `rgesturesx`) ni helper escalar (a diferencia de `raymathx`).

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** Ninguna función de cámara puede fallar: todas son aritmética sobre el struct de cámara más helpers de raymath, sin fichero, GPU, dispositivo de audio ni puntero que pueda ser nulo. `CameraMoveToTarget` sobre una cámara cuya posición coincide con su objetivo produce `NaN` dentro de la matriz en vez de un error, y `projection_matrix` con `aspect == 0` divide entre cero; ambos son *valores incorrectos*, no *valores ausentes*, así que se documentan en los docstrings y deliberadamente no se modelan como `maybe` (contrato §3).

### ✂️ Wrappers de `slice`

**Ninguno aplica.** Ninguna función recibe `(T* ptr, int count)`; el único parámetro puntero es el propio receptor.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Cada función devuelve un `Vector3`/`Matrix` o nada. La pose de una cámara son dos campos `Vector3` de un `rune` (`Camera3D.position` / `.target`) que el llamador lee directamente, así que no hace falta tupla.

### 🌉 Uso de `std.ffi`

**Ninguno aplica, motivo: el único puntero en juego es el receptor, y ya tiene la forma correcta.** Las firmas C reciben `Camera *`, que el binding declara como `ref to Camera`; dentro de un bloque `enchanting`, `self` **es** `ref to Camera3D`, así que se pasa tal cual. No hay `char*`, ni `void*`, ni slice, ni `transmute`. `import std.ffi` no figura en las dependencias.

### 💡 Ejemplos compilables

Verificados con `pengu expand` contra un borrador del wrapper.

```pengu
# Ejemplo 1 — orientar una cámara con los getters puros
import raylib
import raymathx
import rcamerax

weave make_camera into raylib.Camera3D:
    return with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0

weave main into int:
    var cam as raylib.Camera3D is calling make_camera
    var forward as raylib.Vector3 is calling cam.forward
    var up as raylib.Vector3 is calling cam.up
    var right as raylib.Vector3 is calling cam.right
    var view as raylib.Matrix is calling cam.view_matrix
    var projection as raylib.Matrix is calling cam.projection_matrix with 1.7777778
    return 0
```

```pengu
# Ejemplo 2 — controlador de cámara propio
import raylib
import raymathx
import rcamerax

weave main into int:
    var cam as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    calling cam.move_forward with 0.1, true
    calling cam.move_right with 0.1, true
    calling cam.move_up with 0.05
    calling cam.yaw with 0.01, true
    calling cam.pitch with 0.01, true, true, false
    calling cam.roll with 0.01
    calling cam.move_to_target with 0.05
    return 0
```

```pengu
# Ejemplo 3 — alimentar los getters de cámara hacia métodos de raymathx
import raylib
import raymathx
import rcamerax

weave main into int:
    var cam as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    var forward as raylib.Vector3 is calling cam.forward
    var cam_up as raylib.Vector3 is calling cam.up
    var view as raylib.Matrix is calling cam.view_matrix
    var forward_len as f32 is calling forward.length
    var half_up as raylib.Vector3 is calling cam_up.get_scale with 0.5
    var forward_added as raylib.Vector3 is calling forward.get_add with half_up
    var inv_view as raylib.Matrix is calling view.get_invert
    return 0
```

**Restricción del compilador (verificada en `pengu 2.4.0`):** el **resultado** de una llamada a método no se puede encadenar directamente — `calling cam.forward.length` se rechaza con `Type 'Camera3D' does not define method 'length'`, y `calling a.get_add with b.length` es un error de parseo. El encadenamiento solo funciona cuando cada eslabón parte de un binding o de un campo (`calling a.get_add with b` y luego `calling (local).get_add with c`), así que la composición entre wrappers necesita un local por eslabón. Por eso el encadenamiento **no** es el argumento de este wrapper (D2); el argumento es eliminar `(sigil of cam)`.

### 🧪 Plan de tests

Los 12 métodos son aritmética pura sobre un struct de cámara, así que todos los tests se ejecutan en **CI sin ventana, GPU ni entrada** (verificado con `pengu test` en una ejecución sin display). Tres tests por método, con una cámara construida localmente:

- **`forward`**: longitud unitaria; apunta de `position` hacia `target`; una cámara mirando por `-Z` da aproximadamente `(0, 0, -1)`.
- **`up`**: longitud unitaria; ortogonal a `forward`; una cámara por defecto da aproximadamente `(0, 1, 0)`.
- **`right`**: longitud unitaria; ortogonal a `forward` y a `up`; el producto vectorial diestro `forward × up` coincide en signo.
- **`view_matrix`**: componentes finitos; la cámara identidad (posición `(0,0,1)`, objetivo en el origen) lleva el origen al origen; la traslación cae en `m12..m14`.
- **`projection_matrix`**: finita con un aspect normal; `m11` distinto de cero (el término de perspectiva); un campo de visión más amplio reduce `m0` de forma monótona.
- **`move_forward`**: una distancia positiva mueve la cámara a lo largo de `forward`; con `in_plane` verdadero `position.y` no cambia; distancia cero no hace nada.
- **`move_up`**: una distancia positiva sube `position.y`; una negativa la baja; cero no hace nada.
- **`move_right`**: una distancia positiva mueve a lo largo de `right`; con `in_plane` verdadero `position.y` no cambia; cero no hace nada.
- **`move_to_target`**: `delta = 1` lleva la posición al objetivo; `delta = 0` no hace nada; el resultado sigue siendo finito para una cámara degenerada cuya posición coincide con su objetivo (caso `NaN` documentado).
- **`yaw`**: con `around_target` verdadero `position` no se mueve y `target` sí; con falso ocurre lo contrario; una vuelta completa devuelve la cámara a su orientación inicial dentro del epsilon.
- **`pitch`**: con `lock_view` verdadero se acota el ángulo en vez de sobre-rotar; con `rotate_up` verdadero cambia el campo `up` y con falso no; `around_target` decide qué extremo se mueve.
- **`roll`**: un ángulo distinto de cero cambia el campo `up`; una vuelta completa lo restaura dentro del epsilon; cero no hace nada.

El apéndice añade seis tests más. **Cinco de ellos no abren ventana alguna**, lo que es nuevo en el lado de dibujo de este módulo:

- **`Camera2D.to_screen` deja el objetivo en el offset** — fija M6 con un zoom de 2 y un offset distinto de cero.
- **`Camera2D.to_screen` y `to_world` son una ida y vuelta exacta** — fija M7, asegurando también el valor intermedio medido `(50, 20)`.
- **`Camera2D.view_matrix` es una traslación por el objetivo** — fija M5 campo a campo.
- **`Camera3D.to_screen_ex` centra el objetivo sin ventana** — la salida de emergencia de M3, asegurada como exactamente el centro del viewport.
- **`Camera3D.to_world_ray_ex` apunta desde la cámara a través del objetivo** — la dirección del rayo se asegura componente a componente, y su origen en la cámara.
- **Con ventana, las proyecciones base coinciden con las formas `_ex` y los billboards dibujan** — las formas base solo tienen sentido una vez existe una ventana (M1, M4), así que se aseguran *contra* sus gemelas `_ex`, y los tres billboards se dibujan sobre una textura real, que es la única forma de ejercitarlos.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `UpdateCamera`, `UpdateCameraPro` | Ya están declarados en `raylib.d.pengu` (`:1177`, `:1179`) y son alcanzables como `raylib.UpdateCamera` / `raylib.UpdateCameraPro`; envolverlos aquí añadiría un segundo nombre para la misma llamada (D11, contrato §9 criterio 1). |
| Todo lo demás de `rcamera.h` | No es API de consumidor: las definiciones restantes están dentro de `#if defined(RCAMERA_IMPLEMENTATION)` (`include/rcamera.h:171-562`). `pengu bind` hizo bien en no declararlas. |
| `CAMERA_CULL_DISTANCE_NEAR`, `CAMERA_CULL_DISTANCE_FAR`, `CAMERA_MOVE_SPEED` y el resto de macros de ajuste | Expanden a `RL_CULL_DISTANCE_*` (indefinidas salvo que se incluya `rlgl.h`) o viven dentro de `RCAMERA_IMPLEMENTATION`; el binding no las exporta y el wrapper no puede inventarlas. Ajustarlas implica recompilar raylib. |
| `Camera2D` y cualquier helper de cámara 2D | No existen en `rcamera.h`. Las cámaras 2D son aritmética de campos sobre `raylib.Camera2D` y se quedan en el código de usuario; este módulo es solo `Camera3D` (D2). |

Auditoría de cobertura: de las 12 funciones declaradas en `rcamera.d.pengu`, **12 se envuelven** — 5 métodos puros y 7 métodos mutadores, todos sobre `raylib.Camera3D`. No se omite ninguna y no hace falta ninguna función de módulo (D4).
