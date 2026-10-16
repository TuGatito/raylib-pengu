# Plan: window.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/window.pengu`
- Owner in the master plan: family `window` of `docs/plans/raylibx.md` (v0.1.2), third in its order of implementation (brought forward: it is the family that makes everything else runnable)
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: the family's scope is **67** functions — the 55 of the header's window section plus the 12 the master plan assigns to it from the timing, custom-frame-control and logging sections. All 67 are exported by the installed library. **11 are wrapped and 56 are not.** | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`; a script asserts that all 67 land in exactly one bucket. The master plan estimated 61; the plan records the recount. |
| D2 | **`InitWindow` and `CloseWindow` are not wrapped, and this is the contract's explicit instruction, not an oversight.** Contract §9 row 8 names them: "configuración global de un solo uso … se llama una vez; envolver no reduce tokens". The same row takes `SetConfigFlags` and `SetTraceLogLevel`. | They are the most surprising omission in the whole module, so they get their own decision. A wrapper would add a hop to two calls that a program makes once each, and criterion 1 (fewer tokens) fails by definition. **The consequence is deliberate and documented: a window is opened with `raylib.InitWindow` directly, and the test suite does exactly that for setup.** `defer calling raylib.CloseWindow` pairs with it. |
| D3 | **This family wraps only boundary crossings: 11 functions.** Three take or return a bitmask of `raylib.ConfigFlags` (`is_window_state`, `set_window_state`, `clear_window_state`), two take an `Image` (`set_window_icon`, `set_window_icons`), four cross the C string boundary (`set_window_title`, `set_clipboard_text`, `get_clipboard_text`, `take_screenshot`), one returns a string that raylib owns (`get_monitor_name`) and one returns an `Image` (`get_clipboard_image`). | The mechanical application of contract §9's three conditions. Everything else in the family is a zero-argument getter, a zero-argument void mutator, or an `int`/`f32` setter: criterion 1 fails (no token reduction) and criterion 2 fails (**raylib has no window type, so there is no natural receiver**, and none of them renames a `Get*`/`Check*`). This is the same conclusion contract §9 row 9 anticipates for `rlglx`: "envolver casi nada … es un entregable válido". |
| D4 | `is_window_state` takes **one** flag (`raylib.ConfigFlags`), while `set_window_state` and `clear_window_state` take a **slice** of them. | Measured from raylib's own semantics: `IsWindowState(flags)` returns `(current & flags) != 0`, i.e. **"any of these bits is set"**, so a slice there would silently mean "any" and a reader would assume "all". A single flag has no such ambiguity. For setting and clearing, the union is exactly what the caller means, so the slice is right and `|`-combination is the point (the `input` family's `enable_gestures` pattern). |
| D5 | `get_monitor_name` returns a plain `string`, **not** `maybe string`. | Measured: `GetMonitorName(99)` returns an **empty string**, not `NULL`, so there is no failure sentinel to fold. This is the same shape as `GetGamepadName` in `input`. (The `const char*` is still a boundary, which is why the function is wrapped at all.) |
| D6 | `get_clipboard_text` returns `maybe string`; `set_clipboard_text` takes `string`. | Measured: a fresh clipboard returns `NULL` (`GetClipboardText fresh = (null)`), and after `SetClipboardText("pengunic rocks")` the round trip returns that exact string. So the sentinel is real and folds into `maybe`. |
| D7 | `get_clipboard_image` is wrapped as `maybe raylib.Image` **with a prominent warning**, and it is the one function in the module measured to **hang** rather than fail. | Measured: it blocks indefinitely in this environment, because an X11 clipboard image requires a selection owner that pumps events. The wrapper is still worth having — `maybe raylib.Image` is a real improvement over a raw `Image` — but its docstring says the call can block and the test suite never calls it. Recorded rather than hidden: a footgun that is documented is a smaller footgun. |
| D8 | `take_screenshot` returns `void`, not `bool`, and its docstring carries **three measured warnings**: raylib **prepends the working directory** to the path, the write is **deferred**, and it **reports no failure**. It is the one function in this family that no test calls. | Measured in plain C: a *relative* path works and an **absolute path fails** — `"/tmp/x.png"` becomes `"/cwd//tmp/x.png"` and raylib logs "Screenshot could not be saved"; the write is deferred, so the file appears a frame later (517 bytes for a 120x80 frame); and inside a **PenguScript test binary the call crashes with SIGFPE (signal 8) and writes no file**, reproducibly — the identical test with the `TakeScreenshot` line removed passes. The wrapper is a single string conversion, so the instability is raylib's and the driver's, not the wrapper's; the function ships, its docstring warns, and `window_api_probe` type-checks it instead. |
| D9 | `set_window_icons` takes `slice of raylib.Image`. | The binding takes `(Image *images, int count)`; the slice is the pair folded, with the empty case guarded (raylib would read past a null pointer). |
| D10 | **No enchantings**, and the master plan's registry needs no new rows for this family. | There is no window type in raylib to serve as a receiver (D3). This is a genuine structural property of the C API, not a choice. |
| D11 | **This family has real, window-backed tests, and that changes the project's testing story.** Measured: a window **can** be created in this environment (`DISPLAY=:0`), a frame drawn and the window closed, and repeated `InitWindow`/`CloseWindow` cycles work. | Every family planned so far had to skip its window-bound surface. From here on, a test may open a window through the binding for setup; this family does, and asserts on a live window. **The finding also supersedes `raylibx_drawing`'s D9**, which concluded that its pairs could not be tested: they can, once a window is open. That plan is being corrected rather than left standing. |
| D12 | The tests bind the window's own lifecycle with `defer calling raylib.CloseWindow`, and each test that needs a window opens its own. | There is no setup/teardown hook in the test runner, and repeated cycles are measured to work (D11), so per-test windows are both necessary and safe. |

### ✨ Enchantings

**None.** See D10.

### 🔧 Module-level functions (11)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `is_window_state` | `with flag as raylib.ConfigFlags into bool` | `IsWindowState` | `true` when **any** of the flag's bits is set |
| `set_window_state` | `with states as slice of raylib.ConfigFlags into void` | `SetWindowState` | adds the given flags to the window's state |
| `clear_window_state` | `with states as slice of raylib.ConfigFlags into void` | `ClearWindowState` | removes them |
| `set_window_title` | `with title as string into void` | `SetWindowTitle` | passes through `ffi.cstr_from_string` |
| `set_window_icon` | `with icon as raylib.Image into void` | `SetWindowIcon` | the image is read, not consumed |
| `set_window_icons` | `with icons as slice of raylib.Image into void` | `SetWindowIcons` | empty slice is a no-op |
| `get_monitor_name` | `with monitor as int into string` | `GetMonitorName` | empty string for an out-of-range index |
| `set_clipboard_text` | `with text as string into void` | `SetClipboardText` | |
| `get_clipboard_text` | `into maybe string` | `GetClipboardText` | `maybe none` when the clipboard is empty |
| `get_clipboard_image` | `into maybe raylib.Image` | `GetClipboardImage` | **can block**; `maybe none` for an invalid image |
| `take_screenshot` | `with path as string into void` | `TakeScreenshot` | the file lands on the next frame |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `get_clipboard_text` | `maybe string` | `NULL` on an empty clipboard (measured) |
| `get_clipboard_image` | `maybe raylib.Image` | `IsImageValid` |

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `set_window_state`, `clear_window_state` | `states as slice of raylib.ConfigFlags` (combined with `|`) |
| `set_window_icons` | `icons as slice of raylib.Image` |

Both guard the empty case. `|` is used for the flag union, never `or`, which is boolean-only and rejects `u32` (`E0005`).

### 📦 Multiple returns `(T, U)`

**None apply.** `SetWindowIcons`' `(Image*, count)` folds into a slice (D9); the rest return a single value or nothing.

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | `set_window_title`, `set_clipboard_text`, `take_screenshot` |
| `const char*` → owned `string` | `ffi.string_from_cstr` | `get_monitor_name`, `get_clipboard_text` |
| null check | `ffi.is_null` | `get_clipboard_text`, `get_clipboard_image` |
| `Image*` → `void*` for the slice | `transmute` via `sigil of` | `set_window_icons` |

### 💡 Compilable examples

```pengu
# Example 1 — a window, its state and its title, using the binding for the lifecycle (D2)
import raylib
import raylibx.window as window

weave main into int:
    calling raylib.InitWindow with 800, 600, "Pengunic"
    defer calling raylib.CloseWindow
    var states as list of raylib.ConfigFlags is list of raylib.ConfigFlags
    defer banish states
    calling states.push with raylib.FLAG_WINDOW_ALWAYS_RUN
    calling window.set_window_state with (states at 0 to (states.length))
    calling window.set_window_title with "Pengunic - level 1"
    if calling window.is_window_state with raylib.FLAG_WINDOW_ALWAYS_RUN:
        calling window.clear_window_state with (states at 0 to (states.length))
    return 0
```

```pengu
# Example 2 — the clipboard and the monitor name
import raylib
import raylibx.window as window

weave main into int:
    calling raylib.InitWindow with 320, 240, "clipboard"
    defer calling raylib.CloseWindow
    calling window.set_clipboard_text with "copied from Pengunic"
    var pasted as maybe string is calling window.get_clipboard_text
    var monitor as string is calling window.get_monitor_name with 0
    return 0
```

```pengu
# Example 3 — a screenshot, and when the file actually appears (D8)
import raylib
import raylibx.window as window

weave main into int:
    calling raylib.InitWindow with 320, 240, "shot"
    defer calling raylib.CloseWindow
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    calling raylib.EndDrawing
    calling window.take_screenshot with "/tmp/pengunic.png"
    # the file does not exist yet: raylib writes it when the frame advances
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    calling raylib.EndDrawing
    return 0
```

### 🧪 Test plan

**Seven tests, all against a live window, and a probe for the four that cannot be called.** This is the first family in the project whose tests exercise real behaviour rather than compile-only types, and the reason is D11: the environment has a display, so `raylib.InitWindow` from the binding opens a real window. Each test opens its own and closes it with `defer`.

- **`is_window_state` / `set_window_state` / `clear_window_state` round-trip on a real flag** — set `FLAG_WINDOW_ALWAYS_RUN`, assert `true`, clear it, assert `false`. Measured exactly this sequence in C.
- **`set_window_state` takes several flags at once** — two flags in one slice, both asserted set.
- **the empty slice is a no-op** for both state setters.
- **`set_window_title`** is callable on a live window.
- **`get_monitor_name` returns a string, and an out-of-range index returns an empty string** — the deterministic half of the assertion is the out-of-range case, which is measured to be `""` and does not depend on the monitor layout.
- **the clipboard round-trips**: `set_clipboard_text` then `get_clipboard_text` is `some` with the exact text. The `maybe none` path is **not** asserted, because an empty clipboard depends on the session rather than on the wrapper.
- **`set_window_icon` and `set_window_icons`** accept a generated image (built with `raylib.GenImageColor` from the binding, since a family file never imports another family).
- **`take_screenshot` and `get_clipboard_image` are not called anywhere**, and the file carries a comment block explaining both with their measurements (SIGFPE in the test binary and the path-prepending bug for the first, an indefinite block for the second). Both are referenced by `window_api_probe`, so their signatures are still checked at build time. **This is the honest boundary of the family: 7 of its 11 functions are asserted, 4 are type-checked.**

### 🚫 Not wrapped (with reason)

Grouped by the contract §9 rule that excludes them; every one of the 56 is listed.

| Rule | Symbols | Reason |
|---|---|---|
| §9 row 8 — one-shot global configuration | `InitWindow`, `CloseWindow`, `SetConfigFlags`, `SetTraceLogLevel` | named by the contract itself; called once, so a wrapper adds a hop (D2) |
| §9 row 5 — raw C variadics | `TraceLog` | PenguScript cannot build the variadic list |
| §9 row 6 — C callbacks | `SetTraceLogCallback` | no closures in PenguScript; the binding is already the right interface |
| §9 row 7 — opaque pointers | `GetWindowHandle` | a `void*` the user never dereferences |
| §9 row 1 — already idiomatic | `WindowShouldClose`, `IsWindowReady`, `IsWindowFullscreen`, `IsWindowHidden`, `IsWindowMinimized`, `IsWindowMaximized`, `IsWindowFocused`, `IsWindowResized`, `IsCursorHidden`, `IsCursorOnScreen`, `GetScreenWidth`, `GetScreenHeight`, `GetRenderWidth`, `GetRenderHeight`, `GetMonitorCount`, `GetCurrentMonitor`, `GetMonitorPosition`, `GetMonitorWidth`, `GetMonitorHeight`, `GetMonitorPhysicalWidth`, `GetMonitorPhysicalHeight`, `GetMonitorRefreshRate`, `GetWindowPosition`, `GetWindowScaleDPI`, `GetFPS`, `GetFrameTime`, `GetTime` | zero-argument getters and `bool` predicates: the binding call is already clear, and criterion 2 fails because **raylib has no window type** to serve as a receiver |
| §9 criterion 2 fails — no receiver, no rename, no boundary | `ToggleFullscreen`, `ToggleBorderlessWindowed`, `MaximizeWindow`, `MinimizeWindow`, `RestoreWindow`, `SetWindowPosition`, `SetWindowMonitor`, `SetWindowMinSize`, `SetWindowMaxSize`, `SetWindowSize`, `SetWindowOpacity`, `SetWindowFocused`, `ShowCursor`, `HideCursor`, `EnableCursor`, `DisableCursor`, `EnableEventWaiting`, `DisableEventWaiting`, `SwapScreenBuffer`, `PollInputEvents`, `WaitTime`, `SetTargetFPS` | zero-argument void mutators and `int`/`f32` setters: a wrapper would rename without shortening (`raylib.SetWindowSize with 800, 600` is already a clear call) |

Coverage audit: **67 candidates, 11 wrapped, 56 not wrapped, no leftovers and no duplicates.** No enchantings, so the method registry is unchanged.

### ⚠️ Gap found while planning: the random functions belong to no family

`SetRandomSeed`, `GetRandomValue`, `LoadRandomSequence` and `UnloadRandomSequence` are in the header's timing and custom-frame-control sections, but **the master plan's family table assigns them to no family** — the `window` row lists `SetTargetFPS`/`GetFPS`/`GetTime`/`GetFrameTime` and stops there, and `raymathx` (the math family) is already delivered and closed without them. They are therefore **out of this family's scope by the plan of record**, and they are recorded here as an open gap rather than quietly adopted. `GetRandomValue` is genuinely useful — the `files` family's tests already call `raylib.GetRandomValue` from the binding — so the recommendation is a small addendum: either a `random` addendum to `raymathx` or an explicit row in the master plan.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/window.pengu`
- Dueña en el plan maestro: familia `window` de `docs/plans/raylibx.md` (v0.1.2), tercera en su orden de implementación (adelantada: es la familia que hace ejecutable todo lo demás)
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: el alcance de la familia son **67** funciones — las 55 de la sección de ventana del header más las 12 que el plan maestro le asigna de las secciones de timing, control de fotograma personalizado y logging. Las 67 las exporta la biblioteca instalada. **11 se envuelven y 56 no.** | Enumerado desde el binding y cruzado con `tools/check_binding_symbols.py`; un script comprueba que las 67 caen exactamente en un grupo. El plan maestro estimaba 61; el plan registra el recuento. |
| D2 | **`InitWindow` y `CloseWindow` no se envuelven, y esto es una instrucción explícita del contrato, no un descuido.** La fila 8 del contrato §9 las nombra: "configuración global de un solo uso … se llama una vez; envolver no reduce tokens". La misma fila se lleva `SetConfigFlags` y `SetTraceLogLevel`. | Son la omisión más sorprendente de todo el módulo, así que tienen su propia decisión. Un wrapper añadiría un salto a dos llamadas que un programa hace una vez cada una, y el criterio 1 (menos tokens) falla por definición. **La consecuencia es deliberada y está documentada: una ventana se abre con `raylib.InitWindow` directamente, y la suite de tests hace exactamente eso para preparar el entorno.** `defer calling raylib.CloseWindow` lo empareja. |
| D3 | **Esta familia envuelve solo cruces de frontera: 11 funciones.** Tres reciben o devuelven una máscara de bits de `raylib.ConfigFlags` (`is_window_state`, `set_window_state`, `clear_window_state`), dos reciben una `Image` (`set_window_icon`, `set_window_icons`), cuatro cruzan la frontera de cadenas de C (`set_window_title`, `set_clipboard_text`, `get_clipboard_text`, `take_screenshot`), una devuelve una cadena que posee raylib (`get_monitor_name`) y una devuelve una `Image` (`get_clipboard_image`). | La aplicación mecánica de las tres condiciones del contrato §9. Todo lo demás de la familia es un getter sin argumentos, un mutador void sin argumentos o un setter de `int`/`f32`: el criterio 1 falla (no reduce tokens) y el criterio 2 falla (**raylib no tiene un tipo ventana, así que no hay receptor natural**, y ninguno renombra un `Get*`/`Check*`). Es la misma conclusión que el contrato §9 fila 9 anticipa para `rlglx`: "envolver casi nada … es un entregable válido". |
| D4 | `is_window_state` recibe **una** bandera (`raylib.ConfigFlags`), mientras que `set_window_state` y `clear_window_state` reciben un **slice** de ellas. | Medido a partir de la semántica del propio raylib: `IsWindowState(flags)` devuelve `(current & flags) != 0`, es decir **"alguno de estos bits está puesto"**, así que un slice ahí significaría "alguno" en silencio y el lector asumiría "todos". Una sola bandera no tiene esa ambigüedad. Para poner y quitar, la unión es exactamente lo que quiere el llamador, así que el slice es lo correcto y la combinación con `|` es el objetivo (el patrón `enable_gestures` de la familia `input`). |
| D5 | `get_monitor_name` devuelve un `string` simple, **no** `maybe string`. | Medido: `GetMonitorName(99)` devuelve una **cadena vacía**, no `NULL`, así que no hay centinela de fallo que plegar. Es la misma forma que `GetGamepadName` en `input`. (El `const char*` sigue siendo una frontera, y por eso la función se envuelve.) |
| D6 | `get_clipboard_text` devuelve `maybe string`; `set_clipboard_text` recibe `string`. | Medido: un portapapeles recién arrancado devuelve `NULL` (`GetClipboardText fresh = (null)`), y tras `SetClipboardText("pengunic rocks")` el viaje de ida y vuelta devuelve esa cadena exacta. Así que el centinela es real y se pliega en `maybe`. |
| D7 | `get_clipboard_image` se envuelve como `maybe raylib.Image` **con un aviso destacado**, y es la única función del módulo medida que **se cuelga** en vez de fallar. | Medido: bloquea indefinidamente en este entorno, porque una imagen del portapapeles de X11 necesita un dueño de la selección que procese eventos. El wrapper sigue mereciendo la pena — `maybe raylib.Image` es una mejora real sobre una `Image` cruda — pero su docstring dice que la llamada puede bloquear y la suite de tests no la llama nunca. Se registra en vez de esconderse: una trampa documentada es una trampa más pequeña. |
| D8 | `take_screenshot` devuelve `void`, no `bool`, y su docstring lleva **tres avisos medidos**: raylib **antepone el directorio de trabajo** a la ruta, la escritura está **diferida** y **no informa de fallos**. Es la única función de esta familia que ningún test llama. | Medido en C puro: una ruta *relativa* funciona y una **ruta absoluta falla** — `"/tmp/x.png"` se convierte en `"/cwd//tmp/x.png"` y raylib registra "Screenshot could not be saved"; la escritura está diferida, así que el fichero aparece un fotograma después (517 bytes para un fotograma 120x80); y dentro de un **binario de test de PenguScript la llamada revienta con SIGFPE (señal 8) y no escribe ningún fichero**, de forma reproducible — el test idéntico sin la línea de `TakeScreenshot` pasa. El wrapper es una sola conversión de cadena, así que la inestabilidad es de raylib y del driver, no del wrapper; la función se envía, su docstring avisa, y `window_api_probe` la comprueba de tipos en vez de llamarla. |
| D9 | `set_window_icons` recibe `slice of raylib.Image`. | El binding recibe `(Image *images, int count)`; el slice es el par plegado, con el caso vacío guardado (raylib leería más allá de un puntero nulo). |
| D10 | **Sin enchantings**, y el registro del plan maestro no necesita filas nuevas para esta familia. | No hay ningún tipo ventana en raylib que sirva de receptor (D3). Es una propiedad estructural real de la API de C, no una elección. |
| D11 | **Esta familia tiene tests reales con ventana, y eso cambia la historia de pruebas del proyecto.** Medido: en este entorno **sí** se puede crear una ventana (`DISPLAY=:0`), dibujar un fotograma y cerrarla, y los ciclos repetidos de `InitWindow`/`CloseWindow` funcionan. | Todas las familias planificadas hasta ahora tuvieron que saltarse su superficie ligada a ventana. A partir de aquí, un test puede abrir una ventana desde el binding para preparar el entorno; esta familia lo hace y asegura sobre una ventana viva. **El hallazgo además deja obsoleto el D9 de `raylibx_drawing`**, que concluía que sus pares no se podían testear: sí se pueden, una vez hay una ventana abierta. Ese plan se corrige en vez de dejarlo en pie. |
| D12 | Los tests emparejan el ciclo de vida de la ventana con `defer calling raylib.CloseWindow`, y cada test que necesita ventana abre la suya. | El ejecutor de tests no tiene ganchos de preparación/limpieza, y los ciclos repetidos están medidos como seguros (D11), así que una ventana por test es a la vez necesario y seguro. |

### ✨ Enchantings

**Ninguno.** Ver D10.

### 🔧 Funciones a nivel de módulo (11)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `is_window_state` | `with flag as raylib.ConfigFlags into bool` | `IsWindowState` | `true` cuando **alguno** de los bits de la bandera está puesto |
| `set_window_state` | `with states as slice of raylib.ConfigFlags into void` | `SetWindowState` | añade las banderas dadas al estado de la ventana |
| `clear_window_state` | `with states as slice of raylib.ConfigFlags into void` | `ClearWindowState` | las quita |
| `set_window_title` | `with title as string into void` | `SetWindowTitle` | pasa por `ffi.cstr_from_string` |
| `set_window_icon` | `with icon as raylib.Image into void` | `SetWindowIcon` | la imagen se lee, no se consume |
| `set_window_icons` | `with icons as slice of raylib.Image into void` | `SetWindowIcons` | un slice vacío es un no-op |
| `get_monitor_name` | `with monitor as int into string` | `GetMonitorName` | cadena vacía para un índice fuera de rango |
| `set_clipboard_text` | `with text as string into void` | `SetClipboardText` | |
| `get_clipboard_text` | `into maybe string` | `GetClipboardText` | `maybe none` cuando el portapapeles está vacío |
| `get_clipboard_image` | `into maybe raylib.Image` | `GetClipboardImage` | **puede bloquear**; `maybe none` para una imagen inválida |
| `take_screenshot` | `with path as string into void` | `TakeScreenshot` | el fichero aparece en el siguiente fotograma |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `get_clipboard_text` | `maybe string` | `NULL` con el portapapeles vacío (medido) |
| `get_clipboard_image` | `maybe raylib.Image` | `IsImageValid` |

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `set_window_state`, `clear_window_state` | `states as slice of raylib.ConfigFlags` (combinado con `|`) |
| `set_window_icons` | `icons as slice of raylib.Image` |

Ambas guardan el caso vacío. Se usa `|` para la unión de banderas, nunca `or`, que es solo booleano y rechaza `u32` (`E0005`).

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** El `(Image*, count)` de `SetWindowIcons` se pliega en un slice (D9); el resto devuelven un solo valor o nada.

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | `set_window_title`, `set_clipboard_text`, `take_screenshot` |
| `const char*` → `string` con posesión | `ffi.string_from_cstr` | `get_monitor_name`, `get_clipboard_text` |
| comprobación de nulo | `ffi.is_null` | `get_clipboard_text`, `get_clipboard_image` |
| `Image*` → `void*` para el slice | `transmute` vía `sigil of` | `set_window_icons` |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — una ventana, su estado y su título, usando el binding para el ciclo de vida (D2)
import raylib
import raylibx.window as window

weave main into int:
    calling raylib.InitWindow with 800, 600, "Pengunic"
    defer calling raylib.CloseWindow
    var states as list of raylib.ConfigFlags is list of raylib.ConfigFlags
    defer banish states
    calling states.push with raylib.FLAG_WINDOW_RESIZABLE
    calling window.set_window_state with (states at 0 to (states.length))
    calling window.set_window_title with "Pengunic - nivel 1"
    if calling window.is_window_state with raylib.FLAG_WINDOW_RESIZABLE:
        calling window.clear_window_state with (states at 0 to (states.length))
    return 0
```

```pengu
# Ejemplo 2 — el portapapeles y el nombre del monitor
import raylib
import raylibx.window as window

weave main into int:
    calling raylib.InitWindow with 320, 240, "portapapeles"
    defer calling raylib.CloseWindow
    calling window.set_clipboard_text with "copiado desde Pengunic"
    var pegado as maybe string is calling window.get_clipboard_text
    var monitor as string is calling window.get_monitor_name with 0
    return 0
```

```pengu
# Ejemplo 3 — una captura, y cuándo aparece de verdad el fichero (D8)
import raylib
import raylibx.window as window

weave main into int:
    calling raylib.InitWindow with 320, 240, "captura"
    defer calling raylib.CloseWindow
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    calling raylib.EndDrawing
    calling window.take_screenshot with "/tmp/pengunic.png"
    # el fichero todavía no existe: raylib lo escribe cuando avanza el fotograma
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    calling raylib.EndDrawing
    return 0
```

### 🧪 Plan de tests

**Siete tests, todos contra una ventana viva, y una sonda para las cuatro que no se pueden llamar.** Es la primera familia del proyecto cuyos tests ejercitan comportamiento real en vez de solo tipos de compilación, y el motivo es D11: el entorno tiene display, así que `raylib.InitWindow` desde el binding abre una ventana de verdad. Cada test abre la suya y la cierra con `defer`.

- **`is_window_state` / `set_window_state` / `clear_window_state` hacen ida y vuelta sobre una bandera real** — poner `FLAG_WINDOW_ALWAYS_RUN`, asegurar `true`, quitarla, asegurar `false`. Esta secuencia exacta está medida en C.
- **`set_window_state` acepta varias banderas a la vez** — dos banderas en un slice, ambas aseguradas como puestas.
- **el slice vacío es un no-op** para los dos setters de estado.
- **`set_window_title`** se puede llamar sobre una ventana viva.
- **`get_monitor_name` devuelve una cadena, y un índice fuera de rango devuelve cadena vacía** — la mitad determinista de la aserción es el caso fuera de rango, medido como `""` e independiente de la disposición de monitores.
- **el portapapeles hace ida y vuelta**: `set_clipboard_text` y luego `get_clipboard_text` es `some` con el texto exacto. La ruta `maybe none` **no** se asegura, porque un portapapeles vacío depende de la sesión y no del wrapper.
- **`set_window_icon` y `set_window_icons`** aceptan una imagen generada (construida con `raylib.GenImageColor` del binding, ya que un fichero de familia nunca importa otra familia).
- **`take_screenshot` y `get_clipboard_image` no se llaman en ningún sitio**, y el fichero lleva un bloque de comentarios que explica las dos con sus mediciones (SIGFPE en el binario de test y el bug de anteposición de ruta para la primera, bloqueo indefinido para la segunda). Ambas las referencia `window_api_probe`, así que sus firmas se siguen comprobando al construir. **Es la frontera honesta de la familia: 7 de sus 11 funciones se aseguran, 4 se comprueban de tipos.**

### 🚫 NO se envuelve (con motivo)

Agrupadas por la regla del contrato §9 que las excluye; están las 56.

| Regla | Símbolos | Motivo |
|---|---|---|
| §9 fila 8 — configuración global de un solo uso | `InitWindow`, `CloseWindow`, `SetConfigFlags`, `SetTraceLogLevel` | las nombra el propio contrato; se llaman una vez, así que un wrapper añade un salto (D2) |
| §9 fila 5 — variádicos crudos de C | `TraceLog` | PenguScript no puede construir la lista variádica |
| §9 fila 6 — callbacks de C | `SetTraceLogCallback` | no hay closures en PenguScript; el binding ya es la interfaz correcta |
| §9 fila 7 — punteros opacos | `GetWindowHandle` | un `void*` que el usuario nunca desreferencia |
| §9 fila 1 — ya es idiomático | `WindowShouldClose`, `IsWindowReady`, `IsWindowFullscreen`, `IsWindowHidden`, `IsWindowMinimized`, `IsWindowMaximized`, `IsWindowFocused`, `IsWindowResized`, `IsCursorHidden`, `IsCursorOnScreen`, `GetScreenWidth`, `GetScreenHeight`, `GetRenderWidth`, `GetRenderHeight`, `GetMonitorCount`, `GetCurrentMonitor`, `GetMonitorPosition`, `GetMonitorWidth`, `GetMonitorHeight`, `GetMonitorPhysicalWidth`, `GetMonitorPhysicalHeight`, `GetMonitorRefreshRate`, `GetWindowPosition`, `GetWindowScaleDPI`, `GetFPS`, `GetFrameTime`, `GetTime` | getters sin argumentos y predicados `bool`: la llamada al binding ya es clara, y el criterio 2 falla porque **raylib no tiene un tipo ventana** que sirva de receptor |
| §9 criterio 2 falla — sin receptor, sin renombrado, sin frontera | `ToggleFullscreen`, `ToggleBorderlessWindowed`, `MaximizeWindow`, `MinimizeWindow`, `RestoreWindow`, `SetWindowPosition`, `SetWindowMonitor`, `SetWindowMinSize`, `SetWindowMaxSize`, `SetWindowSize`, `SetWindowOpacity`, `SetWindowFocused`, `ShowCursor`, `HideCursor`, `EnableCursor`, `DisableCursor`, `EnableEventWaiting`, `DisableEventWaiting`, `SwapScreenBuffer`, `PollInputEvents`, `WaitTime`, `SetTargetFPS` | mutadores void sin argumentos y setters de `int`/`f32`: un wrapper renombraría sin acortar (`raylib.SetWindowSize with 800, 600` ya es una llamada clara) |

Auditoría de cobertura: **67 candidatas, 11 envueltas, 56 sin envolver, sin restos y sin duplicados.** Sin enchantings, así que el registro de métodos no cambia.

### ⚠️ Hueco encontrado al planificar: las funciones de azar no son de ninguna familia

`SetRandomSeed`, `GetRandomValue`, `LoadRandomSequence` y `UnloadRandomSequence` están en las secciones de timing y control de fotograma personalizado del header, pero **la tabla de familias del plan maestro no las asigna a ninguna** — la fila de `window` lista `SetTargetFPS`/`GetFPS`/`GetTime`/`GetFrameTime` y ahí se queda, y `raymathx` (la familia matemática) ya está entregada y cerrada sin ellas. Por tanto quedan **fuera del alcance de esta familia según el plan vigente**, y se registran aquí como un hueco abierto en vez de adoptarlas en silencio. `GetRandomValue` es genuinamente útil — los tests de la familia `files` ya llaman a `raylib.GetRandomValue` desde el binding — así que la recomendación es un añadido pequeño: o un apéndice `random` en `raymathx`, o una fila explícita en el plan maestro.
