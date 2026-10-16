# Plan: rayguix.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raygui.d.pengu` (61 `declare`, raygui **5.1-dev**)
- Wrapper target: `pengu/rayguix.pengu` — root level, next to the other layer-2 modules
- Owner in the master plan: recorded in `docs/plans/raylibx.md` (v0.1.3), which had left it as "planned separately"
- Dependencies: `import raygui` (which imports `raylib`), `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### ✅ The question that was asked first, answered

The concern was that raygui needs `#define RAYGUI_IMPLEMENTATION` before it can be used, and that this might need C blocks, a bridge `.c` file, or a change to the compiler.

**It needs none of them: the bridge already exists in this repository and works.**

| Option | Verdict |
|---|---|
| `antiquus` C blocks in the wrapper | **Forbidden by the contract**, twice: §1 and §9.6 — "Prohibidos `include`, `link`, `insignia`, `declare` y `antiquus` en la capa 2". |
| A `.c` bridge | **Already there.** `c/raygui_impl.c` defines `RAYGUI_IMPLEMENTATION` and includes `raygui.h`; the build compiles `c/*.c` of every installed binding into the bundle. |
| Change the compiler | **Unnecessary**, and nothing in this plan needs it. |

Measured, rather than assumed:

- **The bridge is load-bearing**: `nm -D /usr/lib/libraylib.so | grep -c Gui` is **0**. raylib only compiles raygui when built with `RAYLIB_MODULE_RAYGUI=TRUE`, which is not the default, so the `Gui*` symbols come from `c/raygui_impl.c` and nowhere else.
- **It links and runs end to end**: a probe with a window passes, exercising `GuiButton`, `GuiLabel`, `GuiGetTextWidth`, a `GuiSetStyle`/`GuiGetStyle` round trip (writes `7`, reads `7`), `GuiLoadStyleDefault` and `GuiGetState`.
- **The binding is complete**: `python3 tools/check_bindings.py --repo .` reports "OK: 6 bindings cover every visible constant, type and function".

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: the binding declares **61** functions. **38 are wrapped** (all module-level; raygui has no receiver type) and **23 are skipped**. | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`-style counting; every call's argument count is verified against the binding by script. |
| D2 | **The 34 string-boundary widgets are the family's justification.** raygui takes a `const char*` in almost every entry, so the binding costs one `ffi.cstr_from_string` plus one `ffi.cstr_free` **per string per call site**: `GuiMessageBox` alone takes three. | Contract §9 criterion 1: the wrapper shortens a real call. Per master plan D22 this is **token count and readability, never type safety** — a parameter typed as an `omen` accepts any integer. |
| D3 | **The out-parameter shape stays faithful**: 22 widgets read and write a caller-owned value, and the wrapper keeps `ref to T` with `sigil of value` at the call site instead of inventing a return value. | The widget's own return is raygui's drawing state (measured: `0` idle, `1` press or change), which is a different piece of information from the edited value. Folding both into one return would need a tuple the contract forbids; keeping the reference gives the caller both with no ambiguity. |
| D4 | **The three text fields are the design centre, and they take a `ref to string`.** `text_box`, `value_box_float` and `text_input_box` edit a caller-owned C buffer in place, and PenguScript strings are immutable; the wrapper allocates the buffer sized by `capacity`, seeds it, calls raygui, and copies the edited text back. | raygui's signature is `(bounds, text, textSize, editMode)` with `text` a mutable `char*`, which has no PenguScript equivalent. The `ref to string` shape was **proved in a live test before the plan was written**: it seeds, calls, reads back and leaves the caller's string intact when nothing is typed. |
| D5 | The copy is **byte by byte**, in three private helpers (`_clear_buffer`, `_seed_buffer`, `_read_buffer`), and the helpers are module-private (`_` prefix) because layer 2 cannot declare C bindings. | Measured: PenguScript has **no `memcpy`** (`memcpy_raw`/`memset_raw` are documented in the language guide but do not exist in `std.ffi`), **no pointer arithmetic** (`ref to char + int` is `E0005`), and **no assignable slice view** (`set (view at i) is v` is a syntax error). Writing one byte at a time through `set essence of (sigil of (buffer at i)) is v` is the only expressible route. |
| D6 | `GuiLoadStyleFromMemory` is **skipped even though it takes a slice**, and it is the only skip that is not a rename. | Measured: raygui reads a `.rgs` buffer **without validating its length**. Eight bytes beginning with the valid magic `rGS ` **segfault the process**; the same eight bytes of arbitrary junk survive, which is what makes the failure so easy to miss. A wrapper cannot validate a style file, so this one stays at the binding, where the caller passes `ref to frozen byte, dataSize` knowingly. `load_style`, from a file, **is** wrapped: measured safe on a missing path. |
| D7 | `GuiIconText` returns an owned `string`, not the binding's `ref to frozen char`. | Measured: raygui builds the label in a **static internal buffer**, so a second call overwrites the first; two consecutive calls both printed `#001#Save` in a C probe. `ffi.string_from_cstr` copies immediately, which is exactly the right lifetime, and the test asserts that two labels stay distinct. |
| D8 | The 19 no-string functions are **not** wrapped: `GuiEnable`, `GuiDisable`, `GuiLock`, `GuiUnlock`, `GuiIsLocked`, `GuiSetAlpha`, `GuiSetState`, `GuiGetState`, `GuiSetFont`, `GuiGetFont`, `GuiSetStyle`, `GuiGetStyle`, `GuiLoadStyleDefault`, `GuiEnableTooltip`, `GuiDisableTooltip`, `GuiSetIconScale`, `GuiGetIcons`, `GuiDrawIcon`, `GuiLoadStyleFromMemory`. | §9 row 1: the binding call is already a clear call and a Pengunic rename buys nothing. The two exception candidates are decided by measurement: `GuiSetStyle`/`GuiGetStyle` take two flattened enums each, and D22 says an enum parameter enforces nothing, so the wrapper would be a pure rename that *looks* safer; `GuiGetIcons` returns a `ref to u32` the user never dereferences (§9 row 7). |
| D9 | The 4 `char**` functions are **not** wrapped: `GuiListViewEx`, `GuiTabBarEx`, `GuiLoadIcons`, `GuiLoadIconsFromMemory`. | A `list of string` is an array of `PenguString` structs, not a `char**`, and without pointer arithmetic the wrapper cannot build an array of pointers. Reaching them would need a C helper, and calling one needs a `declare`, which layer 2 forbids — so it would have to enter through the binding's source header, the way `tools/gen_raymath_protos.py` feeds raymath's prototype-only header to `pengu bind`. Recorded as the route not taken, with its cost. |
| D10 | **Measured trap, documented on `text_width`:** raygui keeps its font in a process-global and initialises it lazily, **once**. | A program that closes a window and opens another must rebind it with `GuiSetFont(GetFontDefault())`, or `text_width` returns **`0`** and every widget draws its text with a dead texture. Found by a failing test: the measure returned `0` after the suite's first window was destroyed, and `GuiSetFont` fixed it. `GuiLoadStyleDefault` does **not** rebind it. |
| D11 | The tests open a window each and rebind the font after `InitWindow`. | Same class of process-global state as the `gamepad` and `SetShapesTexture` findings in the `window` and `shapes` families: the wrapper cannot fix it, so the docstring and the tests carry it. |
| D12 | No `insignia`, no enchantings, and the module is `pengu/rayguix.pengu` at the root. | raygui has no type that could serve as a receiver; every entry takes a `Rectangle` and returns an `int`, which is why this family is module-level like `drawing` and `rlglx`. It wraps a different binding, so it does not belong under `pengu/raylibx/`. |

### 🔧 Module-level functions (38)

| Function | Signature |
|---|---|
| `load_style` | `with path as string into void` |
| `set_tooltip` | `with text as string into void` |
| `text_width` | `with text as string into int` |
| `icon_text` | `with icon_id as int, text as string into string` |
| `window_box` | `with bounds as raylib.Rectangle, title as string into int` |
| `group_box` | `with bounds as raylib.Rectangle, text as string into int` |
| `line` | `with bounds as raylib.Rectangle, text as string into int` |
| `panel` | `with bounds as raylib.Rectangle, text as string into int` |
| `label` | `with bounds as raylib.Rectangle, text as string into int` |
| `button` | `with bounds as raylib.Rectangle, text as string into int` |
| `label_button` | `with bounds as raylib.Rectangle, text as string into int` |
| `status_bar` | `with bounds as raylib.Rectangle, text as string into int` |
| `dummy_rec` | `with bounds as raylib.Rectangle, text as string into int` |
| `toggle` | `with bounds as raylib.Rectangle, text as string, active as ref to bool into int` |
| `toggle_group` | `with bounds as raylib.Rectangle, text as string, active as ref to int into int` |
| `toggle_slider` | `with bounds as raylib.Rectangle, text as string, active as ref to int into int` |
| `check_box` | `with bounds as raylib.Rectangle, text as string, checked as ref to bool into int` |
| `combo_box` | `with bounds as raylib.Rectangle, text as string, active as ref to int into int` |
| `dropdown_box` | `with bounds as raylib.Rectangle, text as string, active as ref to int, edit_mode as bool into int` |
| `spinner` | `with bounds as raylib.Rectangle, text as string, value as ref to int, min_value as int, max_value as int, edit_mode as bool into int` |
| `value_box` | `with bounds as raylib.Rectangle, text as string, value as ref to int, min_value as int, max_value as int, edit_mode as bool into int` |
| `slider` | `with bounds as raylib.Rectangle, text_left as string, text_right as string, value as ref to f32, min_value as f32, max_value as f32 into int` |
| `slider_bar` | `with bounds as raylib.Rectangle, text_left as string, text_right as string, value as ref to f32, min_value as f32, max_value as f32 into int` |
| `progress_bar` | `with bounds as raylib.Rectangle, text_left as string, text_right as string, value as ref to f32, min_value as f32, max_value as f32 into int` |
| `grid` | `with bounds as raylib.Rectangle, text as string, spacing as f32, subdivs as int, mouse_cell as ref to raylib.Vector2 into int` |
| `list_view` | `with bounds as raylib.Rectangle, text as string, scroll_index as ref to int, active as ref to int into int` |
| `tab_bar` | `with bounds as raylib.Rectangle, text as string, h_scroll as ref to int, active as ref to int into int` |
| `scroll_panel` | `with bounds as raylib.Rectangle, text as string, content as raylib.Rectangle, scroll as ref to raylib.Vector2, view as ref to raylib.Rectangle into int` |
| `color_picker` | `with bounds as raylib.Rectangle, text as string, color as ref to raylib.Color into int` |
| `color_panel` | `with bounds as raylib.Rectangle, text as string, color as ref to raylib.Color into int` |
| `color_bar_alpha` | `with bounds as raylib.Rectangle, text as string, alpha as ref to f32 into int` |
| `color_bar_hue` | `with bounds as raylib.Rectangle, text as string, value as ref to f32 into int` |
| `color_picker_hsv` | `with bounds as raylib.Rectangle, text as string, color_hsv as ref to raylib.Vector3 into int` |
| `color_panel_hsv` | `with bounds as raylib.Rectangle, text as string, color_hsv as ref to raylib.Vector3 into int` |
| `message_box` | `with bounds as raylib.Rectangle, title as string, message as string, button_text as string, button_active as ref to int into int` |
| `text_box` | `with bounds as raylib.Rectangle, text as ref to string, capacity as int, edit_mode as bool into int` |
| `value_box_float` | `with bounds as raylib.Rectangle, label as string, text as ref to string, value as ref to f32, capacity as int, edit_mode as bool into int` |
| `text_input_box` | `with bounds as raylib.Rectangle, title as string, message as string, text as ref to string, capacity as int, button_text as string, button_active as ref to int, secret as ref to bool into int` |

Three private helpers back the text fields: `_clear_buffer`, `_seed_buffer` and `_read_buffer`. They are `_`-prefixed so the module stays encapsulated.

### 🎁 `maybe T` wrappers

**None apply.** raygui has no failure sentinel anywhere: every widget returns a drawing state, the two style loaders return `void` and report nothing, and `GuiIconText` never returns null. The one function whose failure is a crash is skipped (D6).

### ✂️ `slice` wrappers

**None survive.** A single `slice` parameter existed (`GuiLoadStyleFromMemory`) and D6 removed it, so this is the only layer-2 module with a slice-free public surface — and the module's most interesting code is precisely the *absence* of one, since the text fields need byte-level access the language gives only through `sigil of`.

### 📦 Multiple returns `(T, U)`

**None apply**, and the reason is D3: the 22 out-parameter widgets return a state *and* mutate a value, which a tuple cannot express under the contract's rules, so the reference stays.

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` + `ffi.cstr_free` | every string parameter, 34 functions |
| `const char*` → owned `string` | `ffi.string_from_cstr` | `icon_text`, `_read_buffer` |
| pointer → writable byte view | `ffi.slice_of_bytes_from_ptr` | the three text fields |
| null pointer | `ffi.null_void` | the initial value of the one buffer pointer |

### 💡 Compilable examples

```pengu
# Example 1 — the shortest complete raygui program
import raylib
import rayguix

weave main into int:
    calling raylib.InitWindow with 400, 200, "rayguix"
    defer calling raylib.CloseWindow
    var bounds as raylib.Rectangle is with x is 20.0, y is 20.0, width is 120.0, height is 24.0
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    var state as int is calling rayguix.button with bounds, "Save"
    calling raylib.EndDrawing
    return state
```

```pengu
# Example 2 — a slider that writes the caller's value
import raylib
import rayguix

weave main into int:
    calling raylib.InitWindow with 400, 200, "rayguix"
    defer calling raylib.CloseWindow
    var volume as f32 is 0.5
    var bounds as raylib.Rectangle is with x is 20.0, y is 20.0, width is 240.0, height is 24.0
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    var state as int is calling rayguix.slider with bounds, "0", "100", (sigil of volume), 0.0, 100.0
    calling raylib.EndDrawing
    return 0
```

```pengu
# Example 3 — a text field whose text comes back through the reference
import raylib
import rayguix

weave main into int:
    calling raylib.InitWindow with 400, 200, "rayguix"
    defer calling raylib.CloseWindow
    var name as string is "Pengunic"
    var bounds as raylib.Rectangle is with x is 20.0, y is 20.0, width is 200.0, height is 24.0
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    var state as int is calling rayguix.text_box with bounds, (sigil of name), 64, true
    calling raylib.EndDrawing
    return state
```

### 🧪 Test plan

**Four tests, all against a live window**, because every widget draws and raygui's state is global.

- **The nine string-only widgets** are drawn in one frame and each state is asserted non-negative: `window_box`, `group_box`, `line`, `panel`, `label`, `button`, `label_button`, `status_bar`, `dummy_rec`.
- **The out-parameter widgets, with the values checked afterwards**: all 22 are called, and then the test asserts that with no mouse input raygui left every caller value untouched (`enabled` still false, `checked` still true, `count` still 7, `volume` still 0.5, `tint` still red). That is the assertion that proves the references point where they should.
- **The three text fields** seed, draw and hand the text back: with no input the text must survive the round trip exactly, which is only true if seeding and reading are both correct.
- **The utilities**: `text_width` measures a non-zero width, `icon_text` builds a non-empty label and two consecutive labels stay distinct (the static-buffer property, D7), `set_tooltip` is callable, and `load_style` on a missing path is a survivable no-op.

Every test rebinds raygui's font with `GuiSetFont(GetFontDefault())` right after `InitWindow`, which is the fix for D10 and part of what the tests document.

### 🚫 Not wrapped (with reason)

| Rule | Symbols | Reason |
|---|---|---|
| §9 row 1 — already idiomatic | `GuiEnable`, `GuiDisable`, `GuiLock`, `GuiUnlock`, `GuiIsLocked`, `GuiSetAlpha`, `GuiSetState`, `GuiGetState`, `GuiSetFont`, `GuiGetFont`, `GuiSetStyle`, `GuiGetStyle`, `GuiLoadStyleDefault`, `GuiEnableTooltip`, `GuiDisableTooltip`, `GuiSetIconScale`, `GuiGetIcons`, `GuiDrawIcon` | no string, no slice, no ownership: the binding call is the clear call (D8) |
| §9 row 7 — opaque pointer | `GuiGetIcons` | returns a `ref to u32` the user never dereferences |
| measured unsafe | `GuiLoadStyleFromMemory` | raygui does not validate the buffer's length and a short one with valid magic segfaults (D6) |
| not expressible | `GuiListViewEx`, `GuiTabBarEx`, `GuiLoadIcons`, `GuiLoadIconsFromMemory` | they need a `char**`, which the value model cannot build (D9) |

Coverage audit: **61 C functions, 38 wrapped, 23 skipped, no leftovers and no duplicates.** The module adds 38 module-level names and three private helpers; it enchants nothing, so the method registry is untouched.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raygui.d.pengu` (61 `declare`, raygui **5.1-dev**)
- Wrapper destino: `pengu/rayguix.pengu` — en la raíz, junto a los demás módulos de capa 2
- Dueña en el plan maestro: registrada en `docs/plans/raylibx.md` (v0.1.3), que la había dejado como "planificada aparte"
- Dependencias: `import raygui` (que importa `raylib`), `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### ✅ La pregunta que se hizo primero, respondida

La preocupación era que raygui necesita `#define RAYGUI_IMPLEMENTATION` antes de poder usarse, y que eso podría exigir bloques C, un puente `.c` o cambiar el compilador.

**No hace falta ninguna de las tres cosas: el puente ya existe en este repositorio y funciona.**

| Opción | Veredicto |
|---|---|
| Bloques C con `antiquus` en el wrapper | **Prohibido por el contrato**, dos veces: §1 y §9.6 — "Prohibidos `include`, `link`, `insignia`, `declare` y `antiquus` en la capa 2". |
| Un puente `.c` | **Ya está.** `c/raygui_impl.c` define `RAYGUI_IMPLEMENTATION` e incluye `raygui.h`; el build compila `c/*.c` de cada binding instalado dentro del bundle. |
| Modificar el compilador | **Innecesario**, y nada de este plan lo necesita. |

Medido, en vez de asumido:

- **El puente es portante**: `nm -D /usr/lib/libraylib.so | grep -c Gui` da **0**. raylib solo compila raygui cuando se construye con `RAYLIB_MODULE_RAYGUI=TRUE`, que no es lo por defecto, así que los símbolos `Gui*` vienen de `c/raygui_impl.c` y de ningún otro sitio.
- **Enlaza y corre de extremo a extremo**: una sonda con ventana pasa, ejercitando `GuiButton`, `GuiLabel`, `GuiGetTextWidth`, una ida y vuelta de `GuiSetStyle`/`GuiGetStyle` (escribe `7`, lee `7`), `GuiLoadStyleDefault` y `GuiGetState`.
- **El binding está completo**: `python3 tools/check_bindings.py --repo .` informa "OK: 6 bindings cover every visible constant, type and function".

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: el binding declara **61** funciones. **38 se envuelven** (todas de módulo; raygui no tiene tipo receptor) y **23 se omiten**. | Enumerado desde el binding y cruzado a estilo `tools/check_binding_symbols.py`; el recuento de argumentos de cada llamada se verifica contra el binding por script. |
| D2 | **Las 34 envolturas de frontera de cadena son la justificación de la familia.** raygui recibe un `const char*` en casi todas sus entradas, así que el binding cuesta un `ffi.cstr_from_string` más un `ffi.cstr_free` **por cadena y por sitio de llamada**: `GuiMessageBox` sola recibe tres. | Criterio 1 del contrato §9: el wrapper acorta una llamada real. Según el D22 del plan maestro esto es **recuento de tokens y legibilidad, nunca seguridad de tipos** — un parámetro tipado como `omen` acepta cualquier entero. |
| D3 | **La forma de los parámetros de salida se mantiene fiel**: 22 widgets leen y escriben un valor que posee el llamador, y el wrapper conserva `ref to T` con `sigil of value` en el sitio de llamada en vez de inventar un valor de retorno. | El retorno propio del widget es el estado de dibujo de raygui (medido: `0` inactivo, `1` pulsación o cambio), que es información distinta del valor editado. Plegar los dos en un solo retorno exigiría una tupla que el contrato prohíbe; conservar la referencia da al llamador ambos sin ambigüedad. |
| D4 | **Los tres campos de texto son el centro de diseño, y reciben un `ref to string`.** `text_box`, `value_box_float` y `text_input_box` editan un búfer C del llamador en su sitio, y las cadenas de PenguScript son inmutables; el wrapper reserva el búfer dimensionado por `capacity`, lo siembra, llama a raygui y copia el texto editado de vuelta. | La firma de raygui es `(bounds, text, textSize, editMode)` con `text` un `char*` mutable, que no tiene equivalente en PenguScript. La forma `ref to string` se **demostró en un test vivo antes de escribir el plan**: siembra, llama, relee y deja intacta la cadena del llamador cuando no se teclea nada. |
| D5 | La copia es **byte a byte**, en tres ayudantes privados (`_clear_buffer`, `_seed_buffer`, `_read_buffer`), y los ayudantes son privados del módulo (prefijo `_`) porque la capa 2 no puede declarar enlaces C. | Medido: PenguScript **no tiene `memcpy`** (`memcpy_raw`/`memset_raw` están documentados en la guía pero no existen en `std.ffi`), **no tiene aritmética de punteros** (`ref to char + int` es `E0005`) y **no tiene vistas de slice asignables** (`set (view at i) is v` es un error de sintaxis). Escribir byte a byte con `set essence of (sigil of (buffer at i)) is v` es la única vía expresable. |
| D6 | `GuiLoadStyleFromMemory` se **omite aunque reciba un slice**, y es la única omisión que no es un renombrado. | Medido: raygui lee un búfer `.rgs` **sin validar su longitud**. Ocho bytes que empiecen por el magic válido `rGS ` **hacen reventar el proceso**; los mismos ocho bytes de basura arbitraria sobreviven, que es lo que hace el fallo tan fácil de no ver. Un wrapper no puede validar un fichero de estilo, así que este se queda en el binding, donde el llamador pasa `ref to frozen byte, dataSize` a sabiendas. `load_style`, desde fichero, **sí** se envuelve: medido seguro con una ruta ausente. |
| D7 | `GuiIconText` devuelve un `string` con posesión, no el `ref to frozen char` del binding. | Medido: raygui construye la etiqueta en un **búfer estático interno**, así que la segunda llamada sobrescribe la primera; dos llamadas consecutivas imprimieron ambas `#001#Save` en una sonda de C. `ffi.string_from_cstr` copia al momento, que es exactamente el tiempo de vida correcto, y el test asegura que dos etiquetas siguen siendo distintas. |
| D8 | Las 19 funciones sin cadena **no** se envuelven: `GuiEnable`, `GuiDisable`, `GuiLock`, `GuiUnlock`, `GuiIsLocked`, `GuiSetAlpha`, `GuiSetState`, `GuiGetState`, `GuiSetFont`, `GuiGetFont`, `GuiSetStyle`, `GuiGetStyle`, `GuiLoadStyleDefault`, `GuiEnableTooltip`, `GuiDisableTooltip`, `GuiSetIconScale`, `GuiGetIcons`, `GuiDrawIcon`, `GuiLoadStyleFromMemory`. | §9 fila 1: la llamada al binding ya es una llamada clara y un renombrado Pengunic no compra nada. Los dos candidatos con excepción los decide la medición: `GuiSetStyle`/`GuiGetStyle` reciben dos enums aplanados cada una, y el D22 dice que un parámetro de enum no impone nada, así que el wrapper sería un renombrado puro que *parece* más seguro; `GuiGetIcons` devuelve un `ref to u32` que el usuario nunca desreferencia (§9 fila 7). |
| D9 | Las 4 funciones de `char**` **no** se envuelven: `GuiListViewEx`, `GuiTabBarEx`, `GuiLoadIcons`, `GuiLoadIconsFromMemory`. | Una `list of string` es un array de structs `PenguString`, no un `char**`, y sin aritmética de punteros el wrapper no puede construir un array de punteros. Alcanzarlas exigiría un helper C, y llamarlo necesita un `declare`, que la capa 2 prohíbe; tendría que entrar por la cabecera fuente del binding, como `tools/gen_raymath_protos.py` alimenta a `pengu bind` con la cabecera solo-prototipos de raymath. Se registra como la ruta no tomada, con su coste. |
| D10 | **Trampa medida, documentada en `text_width`:** raygui guarda su fuente en un global de proceso y la inicializa de forma perezosa, **una sola vez**. | Un programa que cierra una ventana y abre otra debe reenlazarla con `GuiSetFont(GetFontDefault())`, o `text_width` devuelve **`0`** y cada widget dibuja su texto con una textura muerta. Lo encontró un test que fallaba: la medición devolvía `0` después de que se destruyera la primera ventana de la suite, y `GuiSetFont` lo arregló. `GuiLoadStyleDefault` **no** la reenlaza. |
| D11 | Los tests abren una ventana cada uno y reenlazan la fuente tras `InitWindow`. | La misma clase de estado global de proceso que los hallazgos del mando y de `SetShapesTexture` en las familias `window` y `shapes`: el wrapper no puede arreglarlo, así que lo cargan el docstring y los tests. |
| D12 | Sin `insignia`, sin enchantings, y el módulo es `pengu/rayguix.pengu` en la raíz. | raygui no tiene ningún tipo que pueda servir de receptor; cada entrada recibe un `Rectangle` y devuelve un `int`, y por eso esta familia es de módulo como `drawing` y `rlglx`. Envuelve otro binding, así que no pertenece a `pengu/raylibx/`. |

### 🔧 Funciones a nivel de módulo (38)

| Función | Firma |
|---|---|
| `load_style` | `with path as string into void` |
| `set_tooltip` | `with text as string into void` |
| `text_width` | `with text as string into int` |
| `icon_text` | `with icon_id as int, text as string into string` |
| `window_box` | `with bounds as raylib.Rectangle, title as string into int` |
| `group_box` | `with bounds as raylib.Rectangle, text as string into int` |
| `line` | `with bounds as raylib.Rectangle, text as string into int` |
| `panel` | `with bounds as raylib.Rectangle, text as string into int` |
| `label` | `with bounds as raylib.Rectangle, text as string into int` |
| `button` | `with bounds as raylib.Rectangle, text as string into int` |
| `label_button` | `with bounds as raylib.Rectangle, text as string into int` |
| `status_bar` | `with bounds as raylib.Rectangle, text as string into int` |
| `dummy_rec` | `with bounds as raylib.Rectangle, text as string into int` |
| `toggle` | `with bounds as raylib.Rectangle, text as string, active as ref to bool into int` |
| `toggle_group` | `with bounds as raylib.Rectangle, text as string, active as ref to int into int` |
| `toggle_slider` | `with bounds as raylib.Rectangle, text as string, active as ref to int into int` |
| `check_box` | `with bounds as raylib.Rectangle, text as string, checked as ref to bool into int` |
| `combo_box` | `with bounds as raylib.Rectangle, text as string, active as ref to int into int` |
| `dropdown_box` | `with bounds as raylib.Rectangle, text as string, active as ref to int, edit_mode as bool into int` |
| `spinner` | `with bounds as raylib.Rectangle, text as string, value as ref to int, min_value as int, max_value as int, edit_mode as bool into int` |
| `value_box` | `with bounds as raylib.Rectangle, text as string, value as ref to int, min_value as int, max_value as int, edit_mode as bool into int` |
| `slider` | `with bounds as raylib.Rectangle, text_left as string, text_right as string, value as ref to f32, min_value as f32, max_value as f32 into int` |
| `slider_bar` | `with bounds as raylib.Rectangle, text_left as string, text_right as string, value as ref to f32, min_value as f32, max_value as f32 into int` |
| `progress_bar` | `with bounds as raylib.Rectangle, text_left as string, text_right as string, value as ref to f32, min_value as f32, max_value as f32 into int` |
| `grid` | `with bounds as raylib.Rectangle, text as string, spacing as f32, subdivs as int, mouse_cell as ref to raylib.Vector2 into int` |
| `list_view` | `with bounds as raylib.Rectangle, text as string, scroll_index as ref to int, active as ref to int into int` |
| `tab_bar` | `with bounds as raylib.Rectangle, text as string, h_scroll as ref to int, active as ref to int into int` |
| `scroll_panel` | `with bounds as raylib.Rectangle, text as string, content as raylib.Rectangle, scroll as ref to raylib.Vector2, view as ref to raylib.Rectangle into int` |
| `color_picker` | `with bounds as raylib.Rectangle, text as string, color as ref to raylib.Color into int` |
| `color_panel` | `with bounds as raylib.Rectangle, text as string, color as ref to raylib.Color into int` |
| `color_bar_alpha` | `with bounds as raylib.Rectangle, text as string, alpha as ref to f32 into int` |
| `color_bar_hue` | `with bounds as raylib.Rectangle, text as string, value as ref to f32 into int` |
| `color_picker_hsv` | `with bounds as raylib.Rectangle, text as string, color_hsv as ref to raylib.Vector3 into int` |
| `color_panel_hsv` | `with bounds as raylib.Rectangle, text as string, color_hsv as ref to raylib.Vector3 into int` |
| `message_box` | `with bounds as raylib.Rectangle, title as string, message as string, button_text as string, button_active as ref to int into int` |
| `text_box` | `with bounds as raylib.Rectangle, text as ref to string, capacity as int, edit_mode as bool into int` |
| `value_box_float` | `with bounds as raylib.Rectangle, label as string, text as ref to string, value as ref to f32, capacity as int, edit_mode as bool into int` |
| `text_input_box` | `with bounds as raylib.Rectangle, title as string, message as string, text as ref to string, capacity as int, button_text as string, button_active as ref to int, secret as ref to bool into int` |

Tres ayudantes privados sostienen los campos de texto: `_clear_buffer`, `_seed_buffer` y `_read_buffer`, con prefijo `_` para que el módulo quede encapsulado.

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** raygui no tiene centinela de fallo en ningún sitio: cada widget devuelve un estado de dibujo, los dos cargadores de estilo devuelven `void` y no informan de nada, y `GuiIconText` nunca devuelve nulo. La única función cuyo fallo es un crash se omite (D6).

### ✂️ Wrappers de `slice`

**Ninguno sobrevive.** Existía un único parámetro de slice (`GuiLoadStyleFromMemory`) y el D6 lo eliminó, así que este es el único módulo de capa 2 con una superficie pública sin slices — y el código más interesante del módulo es precisamente la *ausencia* de uno, porque los campos de texto necesitan acceso a nivel de byte que el lenguaje solo da mediante `sigil of`.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica**, y el motivo es el D3: los 22 widgets con parámetro de salida devuelven un estado *y* mutan un valor, cosa que una tupla no puede expresar bajo las reglas del contrato, así que la referencia se queda.

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` + `ffi.cstr_free` | cada parámetro de cadena, 34 funciones |
| `const char*` → `string` con posesión | `ffi.string_from_cstr` | `icon_text`, `_read_buffer` |
| puntero → vista de bytes escribible | `ffi.slice_of_bytes_from_ptr` | los tres campos de texto |
| puntero nulo | `ffi.null_void` | el valor inicial del único puntero a búfer |

### 💡 Ejemplos compilables

Los tres ejemplos ingleses de arriba son la versión canónica; el tercero es el que muestra la forma `ref to string`:

```pengu
# Ejemplo 3 — un campo de texto cuyo texto vuelve por la referencia
import raylib
import rayguix

weave main into int:
    calling raylib.InitWindow with 400, 200, "rayguix"
    defer calling raylib.CloseWindow
    var name as string is "Pengunic"
    var bounds as raylib.Rectangle is with x is 20.0, y is 20.0, width is 200.0, height is 24.0
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    var state as int is calling rayguix.text_box with bounds, (sigil of name), 64, true
    calling raylib.EndDrawing
    return state
```

### 🧪 Plan de tests

**Cuatro tests, todos contra una ventana viva**, porque cada widget dibuja y el estado de raygui es global.

- **Los nueve widgets de solo cadena** se dibujan en un fotograma y se asegura que cada estado no es negativo: `window_box`, `group_box`, `line`, `panel`, `label`, `button`, `label_button`, `status_bar`, `dummy_rec`.
- **Los widgets con parámetro de salida, con los valores comprobados después**: se llaman los 22, y luego el test asegura que sin ratón raygui dejó intacto cada valor del llamador (`enabled` sigue falso, `checked` sigue verdadero, `count` sigue 7, `volume` sigue 0.5, `tint` sigue rojo). Esa es la aserción que demuestra que las referencias apuntan donde deben.
- **Los tres campos de texto** siembran, dibujan y devuelven el texto: sin entrada, el texto debe sobrevivir la ida y vuelta exactamente, lo que solo es cierto si sembrar y releer son correctos.
- **Las utilidades**: `text_width` mide un ancho distinto de cero, `icon_text` construye una etiqueta no vacía y dos etiquetas consecutivas siguen siendo distintas (la propiedad del búfer estático, D7), `set_tooltip` se puede llamar y `load_style` sobre una ruta ausente es un no-op que sobrevive.

Cada test reenlaza la fuente de raygui con `GuiSetFont(GetFontDefault())` justo después de `InitWindow`, que es el arreglo del D10 y parte de lo que los tests documentan.

### 🚫 NO se envuelve (con motivo)

| Regla | Símbolos | Motivo |
|---|---|---|
| §9 fila 1 — ya es idiomático | `GuiEnable`, `GuiDisable`, `GuiLock`, `GuiUnlock`, `GuiIsLocked`, `GuiSetAlpha`, `GuiSetState`, `GuiGetState`, `GuiSetFont`, `GuiGetFont`, `GuiSetStyle`, `GuiGetStyle`, `GuiLoadStyleDefault`, `GuiEnableTooltip`, `GuiDisableTooltip`, `GuiSetIconScale`, `GuiGetIcons`, `GuiDrawIcon` | sin cadena, sin slice y sin propiedad: la llamada al binding es la llamada clara (D8) |
| §9 fila 7 — puntero opaco | `GuiGetIcons` | devuelve un `ref to u32` que el usuario nunca desreferencia |
| medido inseguro | `GuiLoadStyleFromMemory` | raygui no valida la longitud del búfer y uno corto con magic válido revienta (D6) |
| no expresable | `GuiListViewEx`, `GuiTabBarEx`, `GuiLoadIcons`, `GuiLoadIconsFromMemory` | necesitan un `char**`, que el modelo de valores no puede construir (D9) |

Auditoría de cobertura: **61 funciones C, 38 envueltas, 23 omitidas, sin restos y sin duplicados.** El módulo añade 38 nombres de nivel de módulo y tres ayudantes privados; no encanta nada, así que el registro de métodos queda intacto.
