# Plan: drawing.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/drawing.pengu`
- Owner in the master plan: family `drawing` of `docs/plans/raylibx.md` (v0.1.2), twelfth in its order of implementation (brought forward because it resolves two pending registry rows)
- Dependencies: `import raylib` only (no strings, no slices, no allocation)
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: the drawing bucket holds **15** functions — **7 `Begin`/`End` pairs and `ClearBackground`** — and all 15 are exported by the installed library. `BeginVrStereoMode`/`EndVrStereoMode` are a separate VR group and are excluded (D5), and `DrawFPS` already belongs to `text`. | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`. The master plan's family table estimated "~11"; the real count is 15, and the plan records the recount. |
| D2 | **All 15 are module-level functions, and the pairs are named symmetrically** (`begin_drawing`/`end_drawing`, `begin_mode_2d`/`end_mode_2d`, …). | This is the family's design question and it got two evidence-based answers, D3 and D4. Symmetry matters because the pairs *must* be balanced and a reader should see the partner at a glance. |
| D3 | **The balanced "with-frame" helper built on a lambda is not offered, and the reason is measured.** `weave frame with body as weave into void` plus `calling drawing.frame with (lambda into …)` would be the ideal API, but PenguScript lambdas **do not capture locals** (`LANGUAGE_Spanish.md` §`lambda`: "Las lambdas no capturan variables locales del entorno"), and a drawing body always needs the caller's camera, render target and scene state. | Verified: a lambda body referencing an enclosing local fails with `E0004 Undefined identifier 'x'`. Worse, `pengu check` **does not always report it**: when the local's name coincides with a parameter name used elsewhere at module scope, `check` accepts the file (a name-shadowing false positive) while `pengu expand` rejects it with "All identifiers must be defined before use". A helper that passes `check` and fails at build time — or silently resolves to the wrong variable — is a trap, so it is not shipped. |
| D4 | The idiomatic balance mechanism is **`defer`**, and the docstrings teach it: `calling drawing.begin_drawing` then `defer calling drawing.end_drawing`. | `defer` runs at scope exit and scopes are delimited by indentation (`LANGUAGE_Spanish.md` §scopes), so a `defer`ed `end_*` is balanced with its `begin_*` as long as both live in the same scope. That is a real, safe discipline — unlike D3, which would have *looked* safer while being unable to compile. |
| D5 | `BeginVrStereoMode`/`EndVrStereoMode` are **not wrapped**. | Master plan D14: VR is outside the 20 % that matters, and `VrStereoConfig` is a struct the wrapper would have to hand the user to build. Recorded here rather than silently dropped. |
| D6 | No enchantings, and the master plan's registry rows for `Camera2D`, `Camera3D` and `RenderTexture` that listed `begin`/`end` as planned methods are **corrected to leave those names unassigned**. | Every `End*` function takes **no receiver** (`EndMode2D`, `EndTextureMode`, …), so it cannot be a method without an unused `self`; and splitting the pair — `camera.begin_mode_3d` next to `end_mode_3d` — would be worse than the symmetric module functions of D2. The `begin_*` functions do take a receiver, but symmetry wins: `calling target.begin_texture_mode` … `defer calling end_texture_mode`. |
| D7 | `begin_mode_2d` takes `raylib.Camera2D`, `begin_mode_3d` takes `raylib.Camera3D`, `begin_texture_mode` takes `raylib.RenderTexture2D`, `begin_shader_mode` takes `raylib.Shader`. Those are the binding's own types, so nothing is converted. | The family's parameters are all real types already, so its value is not type restoration (as in `input`) but **structure**: it is the only family that names the frame's state machine. |
| D8 | `begin_blend_mode` takes the real `raylib.BlendMode`, which the binding flattens to `int`. | The one enum the binding loses, restored. `begin_scissor_mode` takes four loose `int`s, as the binding does: a `Rectangle` would read better but `EndScissorMode` has no rectangle to pair with, and the binding's own `Rectangle` is not what raylib stores. |
| D9 | **The pairs ARE testable — corrected.** This plan first concluded that the family had no testable behaviour, from a measurement of what happens with **no graphics context**: `BeginDrawing`, `EndDrawing`, `ClearBackground`, `BeginScissorMode` and `EndScissorMode` crash, and `BeginBlendMode`/`EndBlendMode` survive one call and crash on the second. Planning `window` then measured that **this machine has a display** (`DISPLAY=:0`), so a test can open a real window through the binding — and with one open, **every pair works**. Both the shader pair and a full frame (clear, scissor, blend, 2D mode, 3D mode, drawing) are now asserted against a live window. | The original measurement was right and its conclusion was wrong: it described a headless process, not the family. Recorded rather than quietly overwritten, because the same trap applies to any family that concludes "not testable" from a headless measurement. The window lifecycle comes from `raylib.InitWindow`/`CloseWindow` because this wrapper deliberately does not wrap them (contract §9 row 8). |
| D10 | No `maybe`, no `slice`, no `banish`, no `std.ffi` — this is the only family of the module with **no boundary of any kind**. | Every parameter is a `raylib` value type or an `int`/`f32`; nothing can fail, nothing is allocated and nothing is released. The module imports `raylib`, `std.ward` (for the tests) and nothing else. |
| D11 | The docstrings state the balance requirement and the matching call explicitly, and each pair's two halves are adjacent in the file. | The wrapper cannot enforce the pairing (D3/D4), so the documentation is the safety net: each `end_*` docstring names the `begin_*` it closes and says what happens if the pairing is broken. |

### ✨ Enchantings

**None.** See D6, which also corrects the master plan's registry.

### 🔧 Module-level functions (15)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `begin_drawing` | `into void` | `BeginDrawing` | opens the frame; pair with `end_drawing` |
| `end_drawing` | `into void` | `EndDrawing` | closes the frame and presents it |
| `begin_mode_2d` | `with camera as raylib.Camera2D into void` | `BeginMode2D` | switches to 2D camera space |
| `end_mode_2d` | `into void` | `EndMode2D` | |
| `begin_mode_3d` | `with camera as raylib.Camera3D into void` | `BeginMode3D` | switches to 3D camera space |
| `end_mode_3d` | `into void` | `EndMode3D` | |
| `begin_texture_mode` | `with target as raylib.RenderTexture2D into void` | `BeginTextureMode` | redirects drawing into a render target |
| `end_texture_mode` | `into void` | `EndTextureMode` | |
| `begin_shader_mode` | `with shader as raylib.Shader into void` | `BeginShaderMode` | applies a shader to everything drawn until the matching end |
| `end_shader_mode` | `into void` | `EndShaderMode` | |
| `begin_blend_mode` | `with mode as raylib.BlendMode into void` | `BeginBlendMode` | |
| `end_blend_mode` | `into void` | `EndBlendMode` | |
| `begin_scissor_mode` | `with x as int, y as int, width as int, height as int into void` | `BeginScissorMode` | clips drawing to a rectangle |
| `end_scissor_mode` | `into void` | `EndScissorMode` | |
| `clear_background` | `with color as raylib.Color into void` | `ClearBackground` | fills the current target; needs an open frame |

The pairs are adjacent in the file, and the `Begin`/`End` naming makes the partner obvious without reading the docstring.

### 🎁 `maybe T` wrappers

**None apply.** That is the striking property of this family: **none of its 15 functions can fail**. Every one of them either sets frame state or, in the case of `ClearBackground`, paints. There is no resource to acquire, no pointer to check and no sentinel to fold.

### ✂️ `slice` wrappers

**None apply.** No function takes `(T*, count)`.

### 📦 Multiple returns `(T, U)`

**None apply.** All 15 return `void`.

### 🌉 `std.ffi` usage

**None apply, and this is the only family of the module that can say so.** There is no string, no array, no foreign pointer and no ownership: the module's imports are `raylib` and (for the test file) `std.ward`.

### 💡 Compilable examples

```pengu
# Example 1 — a frame with a 2D camera, balanced with defer
import raylib
import raylibx.drawing as drawing

weave main into int:
    var camera as raylib.Camera2D is with offset is (with x is 0.0, y is 0.0), target is (with x is 0.0, y is 0.0), rotation is 0.0, zoom is 1.0
    calling drawing.begin_drawing
    defer calling drawing.end_drawing
    calling drawing.clear_background with raylib.RAYWHITE
    calling drawing.begin_mode_2d with camera
    defer calling drawing.end_mode_2d
    return 0
```

```pengu
# Example 2 — the state modes, nested
import raylib
import raylibx.drawing as drawing

weave main into int:
    var camera as raylib.Camera3D is with position is (with x is 0.0, y is 10.0, z is 10.0), target is (with x is 0.0, y is 0.0, z is 0.0), up is (with x is 0.0, y is 1.0, z is 0.0), fovy is 45.0, projection is 0
    calling drawing.begin_drawing
    defer calling drawing.end_drawing
    calling drawing.begin_scissor_mode with 0, 0, 128, 128
    calling drawing.end_scissor_mode
    calling drawing.begin_blend_mode with raylib.BLEND_ALPHA
    calling drawing.end_blend_mode
    calling drawing.begin_mode_3d with camera
    calling drawing.end_mode_3d
    return 0
```

### 🧪 Test plan

**Two assertions, both against a live window.** This family is pure frame state, so it needs a window to mean anything: the plan first measured that without one most of it crashes (D9), then measured that this machine has a display and corrected its conclusion.

- **A full frame balances on a live window**: `begin_drawing`, `clear_background`, a scissor pair, a blend pair, a 2D camera pair, a 3D camera pair and `end_drawing`, all inside one open window. This is the test that supersedes the family's original "not testable" conclusion (D9), and it exercises six of the seven pairs.
- **The `begin_shader_mode`/`end_shader_mode` pair is called twice** — it is the one pair that was already measured safe without a window, and asserting it twice keeps that measurement pinned as well.
- **`drawing_api_probe`** references all 15 functions with the values they need, including the two the tests do not call (`begin_texture_mode`/`end_texture_mode`, which need a render target), so the whole public surface is type-checked at build time.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `BeginVrStereoMode`, `EndVrStereoMode` | VR, outside the master plan's scope (D5, master plan D14) |
| `DrawFPS` | already wrapped by `raylibx_text` (master plan I2) |
| `SwapScreenBuffer`, `PollInputEvents`, `WaitTime`, `EnableEventWaiting`, `DisableEventWaiting` | **not this family**: they are the custom frame-control group and belong to `window` |
| `SetTargetFPS`, `GetFPS`, `GetFrameTime`, `GetTime` | **not this family**: timing belongs to `window` |

Coverage audit: of the 15 drawing-bucket functions, **15 are wrapped**, all as module-level functions. **No enchantings**, so the method registry is unchanged — and the rows it had reserved for `begin`/`end` on three types are released (D6).

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/drawing.pengu`
- Dueña en el plan maestro: familia `drawing` de `docs/plans/raylibx.md` (v0.1.2), duodécima en su orden de implementación (adelantada porque resuelve dos filas pendientes del registro)
- Dependencias: solo `import raylib` (sin cadenas, sin slices, sin alojamiento)
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: el grupo de dibujo tiene **15** funciones — **7 pares `Begin`/`End` y `ClearBackground`** — y las 15 las exporta la biblioteca instalada. `BeginVrStereoMode`/`EndVrStereoMode` son un grupo de VR aparte y quedan excluidas (D5), y `DrawFPS` ya pertenece a `text`. | Enumerado desde el binding y cruzado con `tools/check_binding_symbols.py`. La tabla de familias del plan maestro estimaba "~11"; el recuento real es 15, y el plan lo registra. |
| D2 | **Las 15 son funciones de módulo, y los pares se nombran de forma simétrica** (`begin_drawing`/`end_drawing`, `begin_mode_2d`/`end_mode_2d`, …). | Esta es la pregunta de diseño de la familia y recibió dos respuestas basadas en evidencia, D3 y D4. La simetría importa porque los pares *deben* equilibrarse y el lector debería ver el compañero de un vistazo. |
| D3 | **El helper equilibrado "with-frame" construido con un lambda no se ofrece, y el motivo está medido.** `weave frame with body as weave into void` más `calling drawing.frame with (lambda into …)` sería la API ideal, pero los lambdas de PenguScript **no capturan locales** (`LANGUAGE_Spanish.md` §`lambda`: "Las lambdas no capturan variables locales del entorno"), y un cuerpo de dibujo siempre necesita la cámara, el objetivo de render y el estado de la escena del llamador. | Verificado: un cuerpo lambda que referencia un local del entorno falla con `E0004 Undefined identifier 'x'`. Peor aún, `pengu check` **no siempre lo reporta**: cuando el nombre del local coincide con el de un parámetro usado en otro sitio del módulo, `check` acepta el fichero (un falso positivo por ensombrecimiento de nombres) mientras `pengu expand` lo rechaza con "All identifiers must be defined before use". Un helper que pasa `check` y falla al construir — o que resuelve en silencio a la variable equivocada — es una trampa, así que no se envía. |
| D4 | El mecanismo idiomático de equilibrio es **`defer`**, y los docstrings lo enseñan: `calling drawing.begin_drawing` y luego `defer calling drawing.end_drawing`. | `defer` corre al salir del ámbito y los ámbitos están delimitados por la indentación (`LANGUAGE_Spanish.md` §ámbitos), así que un `end_*` diferido queda equilibrado con su `begin_*` siempre que ambos vivan en el mismo ámbito. Es una disciplina real y segura — a diferencia de D3, que *parecía* más segura siendo imposible de compilar. |
| D5 | `BeginVrStereoMode`/`EndVrStereoMode` **no se envuelven**. | Plan maestro D14: la VR queda fuera del 20 % que importa, y `VrStereoConfig` es un struct que el wrapper tendría que darle al usuario para construir. Se registra aquí en vez de omitirse en silencio. |
| D6 | Sin enchantings, y las filas del registro del plan maestro para `Camera2D`, `Camera3D` y `RenderTexture` que listaban `begin`/`end` como métodos previstos **se corrigen para dejar esos nombres sin asignar**. | Toda función `End*` **no recibe receptor** (`EndMode2D`, `EndTextureMode`, …), así que no puede ser método sin un `self` sin usar; y partir el par — `camera.begin_mode_3d` junto a `end_mode_3d` — sería peor que las funciones de módulo simétricas de D2. Las funciones `begin_*` sí reciben receptor, pero gana la simetría: `calling target.begin_texture_mode` … `defer calling end_texture_mode`. |
| D7 | `begin_mode_2d` recibe `raylib.Camera2D`, `begin_mode_3d` recibe `raylib.Camera3D`, `begin_texture_mode` recibe `raylib.RenderTexture2D` y `begin_shader_mode` recibe `raylib.Shader`. Son los tipos del propio binding, así que no se convierte nada. | Los parámetros de esta familia ya son tipos reales, así que su valor no es la restauración de tipos (como en `input`) sino la **estructura**: es la única familia que le pone nombre a la máquina de estados del fotograma. |
| D8 | `begin_blend_mode` recibe el `raylib.BlendMode` real, que el binding aplana a `int`. | El único enum que el binding pierde, restaurado. `begin_scissor_mode` recibe cuatro `int` sueltos, como el binding: un `Rectangle` se leería mejor, pero `EndScissorMode` no tiene rectángulo con el que emparejar, y el `Rectangle` del binding no es lo que raylib almacena. |
| D9 | **Los pares SÍ son testeables — corregido.** Este plan concluyó primero que la familia no tenía comportamiento testeable, a partir de una medición de lo que pasa **sin contexto gráfico**: `BeginDrawing`, `EndDrawing`, `ClearBackground`, `BeginScissorMode` y `EndScissorMode` revientan, y `BeginBlendMode`/`EndBlendMode` sobreviven a una llamada y revientan en la segunda. Al planificar `window` se midió después que **esta máquina tiene display** (`DISPLAY=:0`), así que un test puede abrir una ventana real desde el binding — y con una abierta, **todos los pares funcionan**. Ahora se aseguran tanto el par de shader como un fotograma completo (clear, scissor, blend, modo 2D, modo 3D, dibujo) contra una ventana viva. | La medición original era correcta y su conclusión era falsa: describía un proceso sin ventana, no la familia. Se registra en vez de sobrescribirse en silencio, porque la misma trampa vale para cualquier familia que concluya "no testeable" a partir de una medición sin ventana. El ciclo de vida de la ventana viene de `raylib.InitWindow`/`CloseWindow` porque este wrapper deliberadamente no las envuelve (contrato §9 fila 8). |
| D10 | Sin `maybe`, sin `slice`, sin `banish`, sin `std.ffi`: es la única familia del módulo **sin ninguna frontera**. | Todo parámetro es un tipo de valor de `raylib` o un `int`/`f32`; nada puede fallar, no se aloja nada y no se libera nada. El módulo importa `raylib` y `std.ward` (para los tests), y nada más. |
| D11 | Los docstrings declaran el requisito de equilibrio y la llamada que empareja, y las dos mitades de cada par están adyacentes en el fichero. | El wrapper no puede imponer el emparejamiento (D3/D4), así que la documentación es la red de seguridad: el docstring de cada `end_*` nombra el `begin_*` que cierra y dice qué pasa si el emparejamiento se rompe. |

### ✨ Enchantings

**Ninguno.** Ver D6, que además corrige el registro del plan maestro.

### 🔧 Funciones a nivel de módulo (15)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `begin_drawing` | `into void` | `BeginDrawing` | abre el fotograma; se empareja con `end_drawing` |
| `end_drawing` | `into void` | `EndDrawing` | cierra el fotograma y lo presenta |
| `begin_mode_2d` | `with camera as raylib.Camera2D into void` | `BeginMode2D` | cambia al espacio de cámara 2D |
| `end_mode_2d` | `into void` | `EndMode2D` | |
| `begin_mode_3d` | `with camera as raylib.Camera3D into void` | `BeginMode3D` | cambia al espacio de cámara 3D |
| `end_mode_3d` | `into void` | `EndMode3D` | |
| `begin_texture_mode` | `with target as raylib.RenderTexture2D into void` | `BeginTextureMode` | redirige el dibujo a un objetivo de render |
| `end_texture_mode` | `into void` | `EndTextureMode` | |
| `begin_shader_mode` | `with shader as raylib.Shader into void` | `BeginShaderMode` | aplica un shader a todo lo que se dibuje hasta el end correspondiente |
| `end_shader_mode` | `into void` | `EndShaderMode` | |
| `begin_blend_mode` | `with mode as raylib.BlendMode into void` | `BeginBlendMode` | |
| `end_blend_mode` | `into void` | `EndBlendMode` | |
| `begin_scissor_mode` | `with x as int, y as int, width as int, height as int into void` | `BeginScissorMode` | recorta el dibujo a un rectángulo |
| `end_scissor_mode` | `into void` | `EndScissorMode` | |
| `clear_background` | `with color as raylib.Color into void` | `ClearBackground` | rellena el objetivo actual; necesita un fotograma abierto |

Los pares están adyacentes en el fichero, y el nombre `Begin`/`End` hace obvio el compañero sin leer el docstring.

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** Es la propiedad llamativa de esta familia: **ninguna de sus 15 funciones puede fallar**. Todas o ajustan el estado del fotograma o, en el caso de `ClearBackground`, pintan. No hay recurso que adquirir, ni puntero que comprobar, ni centinela que plegar.

### ✂️ Wrappers de `slice`

**Ninguno aplica.** Ninguna función recibe `(T*, count)`.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Las 15 devuelven `void`.

### 🌉 Uso de `std.ffi`

**Ninguno aplica, y es la única familia del módulo que puede decirlo.** No hay cadenas, ni arrays, ni punteros ajenos, ni propiedad: los imports del módulo son `raylib` y (para el fichero de tests) `std.ward`.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — un fotograma con cámara 2D, equilibrado con defer
import raylib
import raylibx.drawing as drawing

weave main into int:
    var camera as raylib.Camera2D is with offset is (with x is 0.0, y is 0.0), target is (with x is 0.0, y is 0.0), rotation is 0.0, zoom is 1.0
    calling drawing.begin_drawing
    defer calling drawing.end_drawing
    calling drawing.clear_background with raylib.RAYWHITE
    calling drawing.begin_mode_2d with camera
    defer calling drawing.end_mode_2d
    return 0
```

```pengu
# Ejemplo 2 — los modos de estado, anidados
import raylib
import raylibx.drawing as drawing

weave main into int:
    var camera as raylib.Camera3D is with position is (with x is 0.0, y is 10.0, z is 10.0), target is (with x is 0.0, y is 0.0, z is 0.0), up is (with x is 0.0, y is 1.0, z is 0.0), fovy is 45.0, projection is 0
    calling drawing.begin_drawing
    defer calling drawing.end_drawing
    calling drawing.begin_scissor_mode with 0, 0, 128, 128
    calling drawing.end_scissor_mode
    calling drawing.begin_blend_mode with raylib.BLEND_ALPHA
    calling drawing.end_blend_mode
    calling drawing.begin_mode_3d with camera
    calling drawing.end_mode_3d
    return 0
```

### 🧪 Plan de tests

**Dos aserciones, ambas contra una ventana viva.** Esta familia es puro estado de fotograma, así que necesita una ventana para significar algo: el plan midió primero que sin ella la mayor parte revienta (D9), y después midió que esta máquina tiene display y corrigió su conclusión.

- **Un fotograma completo se equilibra en una ventana viva**: `begin_drawing`, `clear_background`, un par de scissor, uno de blend, uno de cámara 2D, uno de cámara 3D y `end_drawing`, todo dentro de una ventana abierta. Este es el test que deja obsoleta la conclusión original de "no testeable" (D9), y ejercita seis de los siete pares.
- **El par `begin_shader_mode`/`end_shader_mode` se llama dos veces** — es el único par que ya estaba medido como seguro sin ventana, y asegurarlo dos veces mantiene también esa medición fijada.
- **`drawing_api_probe`** referencia las 15 funciones con los valores que necesitan, incluidas las dos que los tests no llaman (`begin_texture_mode`/`end_texture_mode`, que necesitan un objetivo de render), así que toda la superficie pública se comprueba de tipos al construir.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `BeginVrStereoMode`, `EndVrStereoMode` | VR, fuera del alcance del plan maestro (D5, plan maestro D14) |
| `DrawFPS` | ya la envuelve `raylibx_text` (plan maestro I2) |
| `SwapScreenBuffer`, `PollInputEvents`, `WaitTime`, `EnableEventWaiting`, `DisableEventWaiting` | **no son de esta familia**: son el grupo de control de fotograma personalizado y pertenecen a `window` |
| `SetTargetFPS`, `GetFPS`, `GetFrameTime`, `GetTime` | **no son de esta familia**: el timing pertenece a `window` |

Auditoría de cobertura: de las 15 funciones del grupo de dibujo, **15 se envuelven**, todas como funciones de módulo. **Sin enchantings**, así que el registro de métodos no cambia — y las filas que tenía reservadas para `begin`/`end` en tres tipos quedan liberadas (D6).
