# Plan: rlglx.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/rlgl.d.pengu` (163 `declare`, 3 `rune`, 11 `omen`, 87 `const`, 621 lines)
- Wrapper target: `pengu/rlglx.pengu` — **root level, not under `raylibx/`**: it wraps a different binding
- Owner in the master plan: family `rlglx` of `docs/plans/raylibx.md` (v0.1.2), last in its order of implementation
- Dependencies: `import rlgl` (which itself imports `raylib`), `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### ✅ Verdict, first

**`rlglx` is feasible and it works — and the module should be as small as the contract predicted, but not empty.**

| Question | Measured answer |
|---|---|
| Can PenguScript call `rlgl` at all? | **Yes.** A three-test probe compiles, links and runs through the binding: the queries, the matrix stack, immediate mode, `rlLoadVertexBuffer` with a slice and `rlLoadShaderProgram` with two strings all pass. |
| Does it need a window? | **Yes, almost everything.** `rlGetVersion()` and `rlGetPixelFormatName()` work with no context; `rlPushMatrix()` **segfaults** without one (measured: `RLGL.State` is only initialised by `rlglInit` inside `InitWindow`). This is the whole layer, so the tests open a window. |
| Is there a 6.1/6.0 gap? | **No.** All 163 declares are exported by the installed library (0 missing) — the best case in the project. |
| How much should be wrapped? | **18 of 163 (11 %)**; 145 skipped. That is the highest skip rate in the module, exactly what §9 row 9 anticipated: *"rlglx puede concluir 'no envolver casi nada; usar el binding directo'"*. |

The alternative — **no module at all** — was seriously considered and rejected, for a specific reason: **five of the eighteen are string crossings and nine are slice folds.** Without a wrapper, every call site needs `ffi.cstr_from_string` or `ffi.string_from_cstr` plus a `transmute`, or a hand-computed byte count. Those are precisely the calls the contract exists to fix. Everything else in `rlgl` reads perfectly well through the binding and is skipped.

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: the binding declares **163** functions, **all exported**. **18 are wrapped** (16 module functions and 2 methods) and **145 are skipped** with a rule each. | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`; a script asserts that all 163 land in exactly one bucket. |
| D2 | **`rlgl` is not pure CPU, and the matrix stack is the proof.** `rlPushMatrix()`/`rlTranslatef()`/`rlPopMatrix()`/`rlLoadIdentity()` **crash without a context**; only `rlGetVersion()` and `rlGetPixelFormatName()` were measured safe with no window. | Measured twice: first in the PenguScript probe (test 1 segfaulted), then isolated in C (`version = 3` and `R8G8B8A8` printed, then `rlPushMatrix` crashed). It is the reason every test opens a window, and it is worth recording because "matrix maths is CPU work" is the natural wrong assumption. |
| D3 | **Omen-typed parameters are documentation, not enforcement, so no function is wrapped for its enum alone.** Measured on `pengu 2.4.0`: a parameter typed `rlgl.rlBlendMode` accepts `rlgl.RL_TRIANGLES` (a `const`), `raylib.BLEND_ADDITIVE` (the raylib duplicate enum) and a raw `5`. | This corrects a claim in `raylibx_input` D2 and is recorded project-wide as master plan D22. It is the reason `rlSetBlendMode` and `rlSetCullFace` are **skipped** — a wrapper would be a pure rename — while `load_texture` keeps the omen in its signature because that function crosses a slice boundary anyway. |
| D4 | The 145 skips are grouped by rule: **raw GL state and drawing (≈120)** are "already idiomatic" (§9 row 1) — `rlEnableDepthTest()`, `rlClearColor(…)`, `rlBegin`/`rlVertex2f`/`rlEnd` read perfectly as binding calls; **opaque pointers (4)** are §9 row 7 (`rlLoadExtensions`, `rlGetProcAddress`, `rlEnableStatePointer`, `rlGetShaderLocsDefault`); **enum-only renames (≈21)** fail criterion 1 and D3. | The mechanical application of the contract. The module docstring says plainly that the rest is used through the binding, so a partial module cannot be mistaken for full coverage. |
| D5 | **The `Begin`/`End`-shaped pairs are not wrapped** (`rlBegin`/`rlEnd`, `rlPushMatrix`/`rlPopMatrix`). | The balanced helper that would justify a wrapper is impossible: PenguScript lambdas have no closures (master plan D19), and a body driving immediate-mode GL always needs the caller's state. A rename would add a hop and nothing else — the same conclusion as `drawing` D3. |
| D6 | `rlSetUniform` is narrowed to **`set_uniform_floats`**, and the general case is skipped. | raylib's `count` means the number of *elements*, whose size depends on `uniformType`, so the same call reads `count` or `count * 2` floats. Exposing only the unambiguous case (`RL_FLOAT`, where `count` is the slice's length) is the same decision as `raylibx_shaders` D7. |
| D7 | Three functions are skipped for **structural** reasons rather than by rule: `rlGetGlTextureFormats` (three out-parameters would need the tuple the contract forbids), `rlGenTextureMipmaps` (its `ref to int` is both an input and an output), and `rlReadTexturePixels`/`rlCopyFramebuffer` (caller-owned out-buffers whose size raylib never reports, and whose allocation `rlReadTexturePixels` expects `MemFree`d). | Contract §4 and §5. They are recorded individually because each is a near miss: they cross a boundary but cannot express their result in PenguScript's value model. |
| D8 | The string crossings keep the shape the rest of the project uses: `load_shader`/`load_shader_program` take `string`, `uniform_location`/`attrib_location` return `maybe int` (`-1` is raylib's "not found"), and `pixel_format_name` returns a plain `string`. | Measured in the probe: the two-`string` shader program compiles and links. `-1` is folded because that is the contract's sentinel rule, and it matches `raylibx_shaders`' `location`. |
| D9 | The slice folds take `slice of byte` for byte buffers and `slice of raylib.Matrix`/`slice of u32` where the element type is known, and the byte count is **derived from the slice** wherever the binding has a redundant size parameter. | `rlLoadVertexBuffer(buffer, size, dynamic)` becomes `load_vertex_buffer with data, dynamic`; `rlUpdateVertexBuffer(id, data, dataSize, offset)` becomes `update_vertex_buffer with id, data, offset`. This is the one place where folding a parameter is unambiguous, because raylib's size is exactly the slice's length. |
| D10 | `rlLoadTexture` takes an **empty slice as a null pointer**, which is how raylib creates an uninitialised texture. The docstring says so. | raylib's own contract allows `data == NULL`; a guarded "no-op on empty" would have silently changed the meaning. This is the opposite of the other families' empty-slice guards, and it is deliberate. |
| D11 | `rlRenderBatch` gets **two methods** (`draw`, `set_active`) and two module functions (`load_render_batch`, `unload_render_batch`). | It is the only rlgl type with a natural receiver: the three functions that act on a batch take it as their subject. `rlDrawRenderBatchActive` is not a method — it acts on whichever batch is current, so it has no receiver and is skipped. |
| D12 | The module is `pengu/rlglx.pengu` at the **root**, next to the other layer-2 modules, and imports `rlgl` directly rather than through the `raylibx` facade. | It wraps a different binding, so it does not belong under `pengu/raylibx/`; and `rlgl.d.pengu` already imports `raylib`, so a single `import rlgl` brings both surfaces. |
| D13 | No `insignia`, no enchantings beyond the two `rlRenderBatch` methods, and every omen in a signature is written with the **`rlgl.`** qualifier (`rlgl.rlBlendMode`, `rlgl.RL_BLEND_ALPHA`). | The bindings have no `insignia`, so the module name is the qualifier: `rlgl.*`. Measured: qualifying with `raylib.` fails (`E0022`), and the correct qualifier compiles. |
| D14 | The verdict above is part of the deliverable. | Contract §9 row 9 and the master plan both make "wrap almost nothing" a valid Phase 1 outcome; this plan states which of the two outcomes it chose and why, with the numbers. |

### ✨ Enchantings

#### `enchanting rlgl.rlRenderBatch` — 2 methods

| Method | Signature | C backing |
|---|---|---|
| `draw` | `with batch as rlgl.rlRenderBatch into void` | `rlDrawRenderBatch` |
| `set_active` | `with batch as rlgl.rlRenderBatch into void` | `rlSetRenderBatchActive` |

### 🔧 Module-level functions (16)

| Function | Signature | C backing | Boundary |
|---|---|---|---|
| `load_shader` | `with code as string, shader_type as int into u32` | `rlLoadShader` | string in |
| `load_shader_program` | `with vs_code as string, fs_code as string into u32` | `rlLoadShaderProgram` | two strings in |
| `uniform_location` | `with program as u32, name as string into maybe int` | `rlGetLocationUniform` | string in, `-1` sentinel |
| `attrib_location` | `with program as u32, name as string into maybe int` | `rlGetLocationAttrib` | string in, `-1` sentinel |
| `pixel_format_name` | `with format as rlgl.rlPixelFormat into string` | `rlGetPixelFormatName` | `const char*` out |
| `load_vertex_buffer` | `with data as slice of byte, dynamic as bool into u32` | `rlLoadVertexBuffer` | slice + size fold |
| `load_vertex_buffer_element` | `with data as slice of byte, dynamic as bool into u32` | `rlLoadVertexBufferElement` | slice + size fold |
| `update_vertex_buffer` | `with id as u32, data as slice of byte, offset as int into void` | `rlUpdateVertexBuffer` | slice + size fold |
| `update_vertex_buffer_elements` | `with id as u32, data as slice of byte, offset as int into void` | `rlUpdateVertexBufferElements` | slice + size fold |
| `set_uniform_floats` | `with location as int, values as slice of f32 into void` | `rlSetUniform` | slice + `void*` |
| `set_uniform_matrices` | `with location as int, matrices as slice of raylib.Matrix into void` | `rlSetUniformMatrices` | slice + count fold |
| `load_texture` | `with pixels as slice of byte, width as int, height as int, format as rlgl.rlPixelFormat, mipmap_count as int into u32` | `rlLoadTexture` | slice + omen |
| `update_texture` | `with id as u32, x as int, y as int, width as int, height as int, format as rlgl.rlPixelFormat, pixels as slice of byte into void` | `rlUpdateTexture` | slice + omen |
| `draw_vertex_array_elements` | `with offset as int, indices as slice of u32 into void` | `rlDrawVertexArrayElements` | typed slice + count fold |
| `load_render_batch` | `with num_buffers as int, buffer_elements as int into rlgl.rlRenderBatch` | `rlLoadRenderBatch` | rlRenderBatch |
| `unload_render_batch` | `with batch as rlgl.rlRenderBatch into void` | `rlUnloadRenderBatch` | rlRenderBatch |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `uniform_location` | `maybe int` | `-1` for a name the program does not declare |
| `attrib_location` | `maybe int` | `-1` |

### ✂️ `slice` wrappers

Nine of them, all **inputs** (the caller owns the memory): the four vertex-buffer functions, `set_uniform_floats`, `set_uniform_matrices`, `load_texture`, `update_texture` and `draw_vertex_array_elements`. The count or byte size is folded from the slice wherever the binding's parameter is exactly that, and the empty slice means "no data" — which for `load_texture` is a **valid input** meaning "allocate without uploading" (D10).

### 📦 Multiple returns `(T, U)`

**None apply**, and one near miss is recorded: `rlGetGlTextureFormats` has three out-parameters, which the contract's tuple rule cannot express (D7).

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | the four string inputs |
| `const char*` → owned `string` | `ffi.string_from_cstr` | `pixel_format_name` |
| value → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | the nine slice folds |

### 💡 Compilable examples

```pengu
# Example 1 — the raw-GL surface through the binding, which is where 145 of the 163 live
import raylib
import rlgl

weave main into int:
    calling raylib.InitWindow with 800, 600, "rlgl"
    defer calling raylib.CloseWindow
    calling raylib.BeginDrawing
    calling rlgl.rlEnableDepthTest
    calling rlgl.rlClearColor with 0.1, 0.1, 0.1, 1.0
    calling rlgl.rlClearScreenBuffers
    calling rlgl.rlBegin with (rlgl.RL_TRIANGLES to int)
    calling rlgl.rlColor4f with 1.0, 0.0, 0.0, 1.0
    calling rlgl.rlVertex2f with 10.0, 10.0
    calling rlgl.rlVertex2f with 60.0, 10.0
    calling rlgl.rlVertex2f with 35.0, 50.0
    calling rlgl.rlEnd
    calling raylib.EndDrawing
    return 0
```

```pengu
# Example 2 — the strings and the omen, which is what rlglx exists for
import raylib
import rlgl
import rlglx
import std.ffi

weave main with vs as string, fs as string into int:
    calling raylib.InitWindow with 320, 240, "rlglx"
    defer calling raylib.CloseWindow
    var program as u32 is calling rlglx.load_shader_program with vs, fs
    var location as maybe int is calling rlglx.uniform_location with program, "u_time"
    if location is present:
        var values as list of f32 is [1.5]
        defer banish values
        calling rlglx.set_uniform_floats with (calling location.unwrap), (values at 0 to (values.length))
    var format_name as string is calling rlglx.pixel_format_name with rlgl.RL_PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
    return 0
```

```pengu
# Example 3 — an index buffer and a batch
import raylib
import rlgl
import rlglx

weave main into int:
    calling raylib.InitWindow with 320, 240, "rlglx buffers"
    defer calling raylib.CloseWindow
    var indices as list of u32 is [0, 1, 2]
    defer banish indices
    calling rlglx.draw_vertex_array_elements with 0, (indices at 0 to (indices.length))
    var batch as rlgl.rlRenderBatch is calling rlglx.load_render_batch with 1, 8192
    defer calling rlglx.unload_render_batch with batch
    calling batch.draw
    calling batch.set_active
    return 0
```

### 🧪 Test plan

**Four tests, all against a live window**, because D2 measured that the layer has no usable CPU-only surface.

- **The only wrapper that needs no window works with none** — `pixel_format_name` returns a non-empty string, and the binding's `rlGetVersion` is asserted in the same test as the contrast (it is skipped by D3 as a bare rename, so the test calls it through `rlgl`). This is the only test that does not open a window.
- **The matrix stack and the state calls need a window and work with one** — `push`/`translate`/`pop`/`load_identity` plus a blend-mode call.
- **The string crossings compile a real GLSL program** — `load_shader_program` with two raw triple-quoted sources returns a non-zero id, which is the test that proves the `ffi` conversions are right. (Measured the hard way while probing: `\n` inside a **raw** string is a literal backslash-n, so GLSL must be written with real newlines or the compile silently returns `0`.)
- **The slice folds work on real data** — `load_vertex_buffer` with a `slice of byte` returns a non-zero buffer id.
- **`uniform_location` is `maybe`** — a declared uniform is `some` and a missing one is `none`.

### 🚫 Not wrapped (with reason)

Grouped by the rule that excludes them; the module docstring repeats the message so a reader cannot mistake the module for full coverage.

| Rule | Symbols | Reason |
|---|---|---|
| §9 row 1 — already idiomatic | the ~120 raw GL state, matrix, immediate-mode and query functions: `rlMatrixMode`, `rlPushMatrix`, `rlPopMatrix`, `rlLoadIdentity`, `rlTranslatef`, `rlRotatef`, `rlScalef`, `rlMultMatrixf`, `rlFrustum`, `rlOrtho`, `rlViewport`, `rlBegin`, `rlEnd`, `rlVertex2i`, `rlVertex2f`, `rlVertex3f`, `rlTexCoord2f`, `rlNormal3f`, `rlColor4ub`, `rlColor3f`, `rlColor4f`, `rlEnable*`, `rlDisable*`, `rlClearColor`, `rlClearScreenBuffers`, `rlScissor`, `rlTextureParameters`, `rlSetTexture`, `rlGetTextureIdDefault`, `rlGetShaderIdDefault`, `rlGetVersion`, `rlUnload*`, `rlLoadVertexArray`, `rlDrawVertexArray`, `rlGetMatrix*`, `rlSetMatrix*`, … | `rlEnableDepthTest()` and `rlClearColor(…)` are already clear calls; the matrix and immediate-mode APIs are the OpenGL idiom itself. A Pengunic rename buys nothing (§9 row 9). |
| §9 row 1 + D3 — enum-only rename | `rlSetBlendMode`, `rlSetCullFace`, `rlBindImageTexture`, `rlFramebufferAttach`, `rlSetVertexAttribute`, `rlSetVertexAttributeDefault`, `rlEnableStatePointer`, `rlDisableStatePointer`, `rlTextureParameters`, `rlCubemapParameters`, `rlLoadShaderProgramEx`, `rlLoadShaderProgramCompute`, `rlSetBlendFactors`, `rlSetBlendFactorsSeparate`, `rlLoadTextureDepth`, `rlReadScreenPixels`, `rlResizeFramebuffer`, `rlComputeShaderDispatch`, `rlLoadShaderBuffer`, `rlUnloadShaderBuffer`, `rlUpdateShaderBuffer`, `rlBindShaderBuffer`, `rlReadShaderBuffer`, `rlCopyShaderBuffer`, `rlGetShaderBufferSize`, `rlLoadDrawCube`, `rlLoadDrawQuad` | their only difference from the binding is an enum parameter, and D3 measured that an enum parameter enforces nothing. |
| §9 row 7 — opaque pointers | `rlLoadExtensions`, `rlGetProcAddress`, `rlEnableStatePointer`, `rlGetShaderLocsDefault` | pointers the user never dereferences. |
| D7 — structural near misses | `rlGetGlTextureFormats`, `rlGenTextureMipmaps`, `rlReadTexturePixels`, `rlCopyFramebuffer` | three out-parameters, an in/out `ref to int`, and caller-owned out-buffers with unreported sizes. |
| D5 — pairs without closures | `rlBegin`/`rlEnd`, `rlPushMatrix`/`rlPopMatrix` | a balanced helper is impossible and a rename buys nothing. |
| D6 — ambiguous count | `rlSetUniform` in its general form | the element count depends on the uniform type; only the float case is exposed. |
| structural — `rlgl` lifecycle | `rlglInit`, `rlglClose` | raylib owns them; calling them by hand fights `InitWindow`/`CloseWindow`. |

Coverage audit: **163 C functions, 18 wrapped, 145 skipped, no leftovers and no duplicates.** The method registry gains the two `rlRenderBatch` names. **No other family may add an `rlRenderBatch` method**, and nothing here touches the `raylibx` types.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/rlgl.d.pengu` (163 `declare`, 3 `rune`, 11 `omen`, 87 `const`, 621 líneas)
- Wrapper destino: `pengu/rlglx.pengu` — **en la raíz, no bajo `raylibx/`**: envuelve otro binding
- Dueña en el plan maestro: familia `rlglx` de `docs/plans/raylibx.md` (v0.1.2), última en su orden de implementación
- Dependencias: `import rlgl` (que a su vez importa `raylib`), `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### ✅ Veredicto, lo primero

**`rlglx` es factible y funciona — y el módulo debe ser tan pequeño como el contrato predijo, pero no vacío.**

| Pregunta | Respuesta medida |
|---|---|
| ¿Puede PenguScript llamar a `rlgl`? | **Sí.** Una sonda de tres tests compila, enlaza y corre a través del binding: las consultas, la pila de matrices, el modo inmediato, `rlLoadVertexBuffer` con un slice y `rlLoadShaderProgram` con dos cadenas pasan todos. |
| ¿Necesita ventana? | **Sí, casi todo.** `rlGetVersion()` y `rlGetPixelFormatName()` funcionan sin contexto; `rlPushMatrix()` **revienta** sin uno (medido: `RLGL.State` solo lo inicializa `rlglInit` dentro de `InitWindow`). Es toda la capa, así que los tests abren ventana. |
| ¿Hay hueco 6.1/6.0? | **No.** Los 163 declares los exporta la biblioteca instalada (0 ausentes): el mejor caso del proyecto. |
| ¿Cuánto hay que envolver? | **18 de 163 (11 %)**; 145 omitidas. Es la mayor tasa de descarte del módulo, exactamente lo que la §9 fila 9 anticipaba: *"rlglx puede concluir 'no envolver casi nada; usar el binding directo'"*. |

La alternativa — **ningún módulo** — se consideró en serio y se descartó por un motivo concreto: **cinco de los dieciocho son cruces de cadena y nueve son pliegues de slice.** Sin wrapper, cada sitio de llamada necesita `ffi.cstr_from_string` o `ffi.string_from_cstr` más un `transmute`, o un recuento de bytes calculado a mano. Esos son precisamente los sitios que el contrato existe para arreglar. Todo lo demás de `rlgl` se lee perfectamente por el binding y se omite.

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: el binding declara **163** funciones, **todas exportadas**. **18 se envuelven** (16 funciones de módulo y 2 métodos) y **145 se omiten** con su regla. | Enumerado desde el binding y cruzado con `tools/check_binding_symbols.py`; un script comprueba que las 163 caen exactamente en un grupo. |
| D2 | **`rlgl` no es CPU pura, y la pila de matrices es la prueba.** `rlPushMatrix()`/`rlTranslatef()`/`rlPopMatrix()`/`rlLoadIdentity()` **revientan sin contexto**; solo `rlGetVersion()` y `rlGetPixelFormatName()` se midieron seguras sin ventana. | Medido dos veces: primero en la sonda de PenguScript (el test 1 reventó), después aislado en C (`version = 3` y `R8G8B8A8` impresos, y luego `rlPushMatrix` reventó). Es la razón de que cada test abra ventana, y merece registrarse porque "la matemática de matrices es trabajo de CPU" es la suposición natural equivocada. |
| D3 | **Los parámetros tipados como omen son documentación, no comprobación, así que ninguna función se envuelve solo por su enum.** Medido en `pengu 2.4.0`: un parámetro tipado `rlgl.rlBlendMode` acepta `rlgl.RL_TRIANGLES` (un `const`), `raylib.BLEND_ADDITIVE` (el enum duplicado de raylib) y un `5` crudo. | Esto corrige una afirmación del D2 de `raylibx_input` y queda registrado para todo el proyecto como D22 del plan maestro. Es la razón de que `rlSetBlendMode` y `rlSetCullFace` se **omitan** — un wrapper sería un renombrado puro — mientras que `load_texture` conserva el omen en su firma porque esa función cruza una frontera de slice de todos modos. |
| D4 | Las 145 omisiones se agrupan por regla: **estado y dibujo crudos de GL (≈120)** son "ya idiomáticos" (§9 fila 1) — `rlEnableDepthTest()`, `rlClearColor(…)`, `rlBegin`/`rlVertex2f`/`rlEnd` se leen perfectamente como llamadas al binding; **punteros opacos (4)** son la §9 fila 7 (`rlLoadExtensions`, `rlGetProcAddress`, `rlEnableStatePointer`, `rlGetShaderLocsDefault`); **renombrados solo de enum (≈21)** fallan el criterio 1 y el D3. | La aplicación mecánica del contrato. El docstring del módulo dice claramente que el resto se usa por el binding, para que un módulo parcial no se confunda con cobertura total. |
| D5 | **Los pares con forma `Begin`/`End` no se envuelven** (`rlBegin`/`rlEnd`, `rlPushMatrix`/`rlPopMatrix`). | El helper equilibrado que justificaría un wrapper es imposible: los lambdas de PenguScript no tienen closures (plan maestro D19), y un cuerpo que maneja GL en modo inmediato siempre necesita el estado del llamador. Un renombrado añadiría un salto y nada más: la misma conclusión que el D3 de `drawing`. |
| D6 | `rlSetUniform` se estrecha a **`set_uniform_floats`**, y el caso general se omite. | El `count` de raylib significa el número de *elementos*, cuyo tamaño depende de `uniformType`, así que la misma llamada lee `count` o `count * 2` floats. Exponer solo el caso inequívoco (`RL_FLOAT`, donde `count` es la longitud del slice) es la misma decisión que el D7 de `raylibx_shaders`. |
| D7 | Tres funciones se omiten por motivos **estructurales** y no por regla: `rlGetGlTextureFormats` (tres parámetros de salida necesitarían la tupla que el contrato prohíbe), `rlGenTextureMipmaps` (su `ref to int` es a la vez entrada y salida) y `rlReadTexturePixels`/`rlCopyFramebuffer` (búferes de salida que posee el llamador, cuyo tamaño raylib nunca informa y cuya reserva `rlReadTexturePixels` espera que se libere con `MemFree`). | Contrato §4 y §5. Se registran una por una porque cada una es un casi: cruzan una frontera pero no pueden expresar su resultado en el modelo de valores de PenguScript. |
| D8 | Los cruces de cadena conservan la forma que usa el resto del proyecto: `load_shader`/`load_shader_program` reciben `string`, `uniform_location`/`attrib_location` devuelven `maybe int` (`-1` es el "no encontrado" de raylib) y `pixel_format_name` devuelve un `string` simple. | Medido en la sonda: el programa de shader con dos `string` compila y enlaza. El `-1` se pliega porque es la regla del centinela del contrato, y coincide con el `location` de `raylibx_shaders`. |
| D9 | Los pliegues de slice reciben `slice of byte` para búferes de bytes y `slice of raylib.Matrix`/`slice of u32` donde el tipo de elemento se conoce, y el recuento de bytes se **deriva del slice** allí donde el binding tiene un parámetro de tamaño redundante. | `rlLoadVertexBuffer(buffer, size, dynamic)` pasa a `load_vertex_buffer with data, dynamic`; `rlUpdateVertexBuffer(id, data, dataSize, offset)` pasa a `update_vertex_buffer with id, data, offset`. Es el único sitio donde plegar un parámetro es inequívoco, porque el tamaño de raylib es exactamente la longitud del slice. |
| D10 | `rlLoadTexture` recibe un **slice vacío como puntero nulo**, que es como raylib crea una textura sin inicializar. El docstring lo dice. | El propio contrato de raylib admite `data == NULL`; una guarda de "no-op si está vacío" habría cambiado el significado en silencio. Es lo contrario de las guardas de slice vacío de las demás familias, y es deliberado. |
| D11 | `rlRenderBatch` gana **dos métodos** (`draw`, `set_active`) y dos funciones de módulo (`load_render_batch`, `unload_render_batch`). | Es el único tipo de rlgl con receptor natural: las tres funciones que actúan sobre un batch lo reciben como sujeto. `rlDrawRenderBatchActive` no es método — actúa sobre el batch que esté activo, así que no tiene receptor y se omite. |
| D12 | El módulo es `pengu/rlglx.pengu` en la **raíz**, junto a los demás módulos de capa 2, e importa `rlgl` directamente en vez de por la fachada `raylibx`. | Envuelve otro binding, así que no pertenece a `pengu/raylibx/`; y `rlgl.d.pengu` ya importa `raylib`, así que un solo `import rlgl` trae las dos superficies. |
| D13 | Sin `insignia`, sin enchantings más allá de los dos métodos de `rlRenderBatch`, y cada omen en una firma se escribe con el calificador **`rlgl.`** (`rlgl.rlBlendMode`, `rlgl.RL_BLEND_ALPHA`). | Los bindings no llevan `insignia`, así que el nombre del módulo es el calificador: `rlgl.*`. Medido: calificar con `raylib.` falla (`E0022`), y el calificador correcto compila. |
| D14 | El veredicto de arriba es parte del entregable. | La §9 fila 9 del contrato y el plan maestro hacen de "no envolver casi nada" un resultado válido de Fase 1; este plan declara cuál de los dos resultados eligió y por qué, con los números. |

### ✨ Enchantings

#### `enchanting rlgl.rlRenderBatch` — 2 métodos

| Método | Firma | C backing |
|---|---|---|
| `draw` | `with batch as rlgl.rlRenderBatch into void` | `rlDrawRenderBatch` |
| `set_active` | `with batch as rlgl.rlRenderBatch into void` | `rlSetRenderBatchActive` |

### 🔧 Funciones a nivel de módulo (16)

| Función | Firma | C backing | Frontera |
|---|---|---|---|
| `load_shader` | `with code as string, shader_type as int into u32` | `rlLoadShader` | cadena de entrada |
| `load_shader_program` | `with vs_code as string, fs_code as string into u32` | `rlLoadShaderProgram` | dos cadenas de entrada |
| `uniform_location` | `with program as u32, name as string into maybe int` | `rlGetLocationUniform` | cadena de entrada, centinela `-1` |
| `attrib_location` | `with program as u32, name as string into maybe int` | `rlGetLocationAttrib` | cadena de entrada, centinela `-1` |
| `pixel_format_name` | `with format as rlgl.rlPixelFormat into string` | `rlGetPixelFormatName` | `const char*` de salida |
| `load_vertex_buffer` | `with data as slice of byte, dynamic as bool into u32` | `rlLoadVertexBuffer` | slice + pliegue de tamaño |
| `load_vertex_buffer_element` | `with data as slice of byte, dynamic as bool into u32` | `rlLoadVertexBufferElement` | slice + pliegue de tamaño |
| `update_vertex_buffer` | `with id as u32, data as slice of byte, offset as int into void` | `rlUpdateVertexBuffer` | slice + pliegue de tamaño |
| `update_vertex_buffer_elements` | `with id as u32, data as slice of byte, offset as int into void` | `rlUpdateVertexBufferElements` | slice + pliegue de tamaño |
| `set_uniform_floats` | `with location as int, values as slice of f32 into void` | `rlSetUniform` | slice + `void*` |
| `set_uniform_matrices` | `with location as int, matrices as slice of raylib.Matrix into void` | `rlSetUniformMatrices` | slice + pliegue de recuento |
| `load_texture` | `with pixels as slice of byte, width as int, height as int, format as rlgl.rlPixelFormat, mipmap_count as int into u32` | `rlLoadTexture` | slice + omen |
| `update_texture` | `with id as u32, x as int, y as int, width as int, height as int, format as rlgl.rlPixelFormat, pixels as slice of byte into void` | `rlUpdateTexture` | slice + omen |
| `draw_vertex_array_elements` | `with offset as int, indices as slice of u32 into void` | `rlDrawVertexArrayElements` | slice tipado + pliegue de recuento |
| `load_render_batch` | `with num_buffers as int, buffer_elements as int into rlgl.rlRenderBatch` | `rlLoadRenderBatch` | `rlRenderBatch` |
| `unload_render_batch` | `with batch as rlgl.rlRenderBatch into void` | `rlUnloadRenderBatch` | `rlRenderBatch` |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `uniform_location` | `maybe int` | `-1` para un nombre que el programa no declara |
| `attrib_location` | `maybe int` | `-1` |

### ✂️ Wrappers de `slice`

Nueve, todos de **entrada** (la memoria la posee el llamador): las cuatro funciones de búfer de vértices, `set_uniform_floats`, `set_uniform_matrices`, `load_texture`, `update_texture` y `draw_vertex_array_elements`. El recuento o el tamaño en bytes se pliega del slice allí donde el parámetro del binding es exactamente eso, y el slice vacío significa "sin datos" — que para `load_texture` es una **entrada válida** que significa "reserva sin subir" (D10).

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica**, y se registra un casi: `rlGetGlTextureFormats` tiene tres parámetros de salida, que la regla de tuplas del contrato no puede expresar (D7).

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | las cuatro entradas de cadena |
| `const char*` → `string` con posesión | `ffi.string_from_cstr` | `pixel_format_name` |
| valor → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | los nueve pliegues de slice |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — la superficie cruda de GL por el binding, que es donde viven 145 de las 163
import raylib
import rlgl

weave main into int:
    calling raylib.InitWindow with 800, 600, "rlgl"
    defer calling raylib.CloseWindow
    calling raylib.BeginDrawing
    calling rlgl.rlEnableDepthTest
    calling rlgl.rlClearColor with 0.1, 0.1, 0.1, 1.0
    calling rlgl.rlClearScreenBuffers
    calling rlgl.rlBegin with (rlgl.RL_TRIANGLES to int)
    calling rlgl.rlColor4f with 1.0, 0.0, 0.0, 1.0
    calling rlgl.rlVertex2f with 10.0, 10.0
    calling rlgl.rlVertex2f with 60.0, 10.0
    calling rlgl.rlVertex2f with 35.0, 50.0
    calling rlgl.rlEnd
    calling raylib.EndDrawing
    return 0
```

```pengu
# Ejemplo 2 — las cadenas y el omen, que es para lo que existe rlglx
import raylib
import rlgl
import rlglx
import std.ffi

weave main with vs as string, fs as string into int:
    calling raylib.InitWindow with 320, 240, "rlglx"
    defer calling raylib.CloseWindow
    var program as u32 is calling rlglx.load_shader_program with vs, fs
    var location as maybe int is calling rlglx.uniform_location with program, "u_time"
    if location is present:
        var values as list of f32 is [1.5]
        defer banish values
        calling rlglx.set_uniform_floats with (calling location.unwrap), (values at 0 to (values.length))
    var format_name as string is calling rlglx.pixel_format_name with rlgl.RL_PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
    return 0
```

```pengu
# Ejemplo 3 — un búfer de índices y un batch
import raylib
import rlgl
import rlglx

weave main into int:
    calling raylib.InitWindow with 320, 240, "rlglx buffers"
    defer calling raylib.CloseWindow
    var indices as list of u32 is [0, 1, 2]
    defer banish indices
    calling rlglx.draw_vertex_array_elements with 0, (indices at 0 to (indices.length))
    var batch as rlgl.rlRenderBatch is calling rlglx.load_render_batch with 1, 8192
    defer calling rlglx.unload_render_batch with batch
    calling batch.draw
    calling batch.set_active
    return 0
```

### 🧪 Plan de tests

**Cuatro tests, todos contra una ventana viva**, porque el D2 midió que la capa no tiene superficie usable solo de CPU.

- **El único wrapper que no necesita ventana funciona sin ninguna** — `pixel_format_name` devuelve una cadena no vacía, y el `rlGetVersion` del binding se asegura en el mismo test como contraste (lo omite el D3 por ser un renombrado puro, así que el test lo llama por `rlgl`). Es el único test que no abre ventana.
- **La pila de matrices y las llamadas de estado necesitan ventana y funcionan con ella** — `push`/`translate`/`pop`/`load_identity` más una llamada de modo de mezcla.
- **Los cruces de cadena compilan un programa GLSL real** — `load_shader_program` con dos fuentes raw entre comillas triples devuelve un id distinto de cero, que es el test que demuestra que las conversiones de `ffi` son correctas. (Medido a las malas durante el sondeo: `\n` dentro de una cadena **raw** es un backslash-n literal, así que el GLSL hay que escribirlo con saltos de línea reales o la compilación devuelve `0` en silencio.)
- **Los pliegues de slice funcionan con datos reales** — `load_vertex_buffer` con un `slice of byte` devuelve un id de búfer distinto de cero.
- **`uniform_location` es `maybe`** — un uniform declarado es `some` y uno ausente es `none`.

### 🚫 NO se envuelve (con motivo)

Agrupadas por la regla que las excluye; el docstring del módulo repite el mensaje para que un lector no confunda el módulo con cobertura total.

| Regla | Símbolos | Motivo |
|---|---|---|
| §9 fila 1 — ya es idiomático | las ~120 funciones crudas de estado, matrices, modo inmediato y consultas de GL: `rlMatrixMode`, `rlPushMatrix`, `rlPopMatrix`, `rlLoadIdentity`, `rlTranslatef`, `rlRotatef`, `rlScalef`, `rlMultMatrixf`, `rlFrustum`, `rlOrtho`, `rlViewport`, `rlBegin`, `rlEnd`, `rlVertex2i`, `rlVertex2f`, `rlVertex3f`, `rlTexCoord2f`, `rlNormal3f`, `rlColor4ub`, `rlColor3f`, `rlColor4f`, `rlEnable*`, `rlDisable*`, `rlClearColor`, `rlClearScreenBuffers`, `rlScissor`, `rlTextureParameters`, `rlSetTexture`, `rlGetTextureIdDefault`, `rlGetShaderIdDefault`, `rlGetVersion`, `rlUnload*`, `rlLoadVertexArray`, `rlDrawVertexArray`, `rlGetMatrix*`, `rlSetMatrix*`, … | `rlEnableDepthTest()` y `rlClearColor(…)` ya son llamadas claras; las APIs de matrices y de modo inmediato son el propio idioma de OpenGL. Un renombrado Pengunic no compra nada (§9 fila 9). |
| §9 fila 1 + D3 — renombrado solo de enum | `rlSetBlendMode`, `rlSetCullFace`, `rlBindImageTexture`, `rlFramebufferAttach`, `rlSetVertexAttribute`, `rlSetVertexAttributeDefault`, `rlEnableStatePointer`, `rlDisableStatePointer`, `rlTextureParameters`, `rlCubemapParameters`, `rlLoadShaderProgramEx`, `rlLoadShaderProgramCompute`, `rlSetBlendFactors`, `rlSetBlendFactorsSeparate`, `rlLoadTextureDepth`, `rlReadScreenPixels`, `rlResizeFramebuffer`, `rlComputeShaderDispatch`, `rlLoadShaderBuffer`, `rlUnloadShaderBuffer`, `rlUpdateShaderBuffer`, `rlBindShaderBuffer`, `rlReadShaderBuffer`, `rlCopyShaderBuffer`, `rlGetShaderBufferSize`, `rlLoadDrawCube`, `rlLoadDrawQuad` | su única diferencia con el binding es un parámetro de enum, y el D3 midió que un parámetro de enum no impone nada. |
| §9 fila 7 — punteros opacos | `rlLoadExtensions`, `rlGetProcAddress`, `rlEnableStatePointer`, `rlGetShaderLocsDefault` | punteros que el usuario nunca desreferencia. |
| D7 — casi estructurales | `rlGetGlTextureFormats`, `rlGenTextureMipmaps`, `rlReadTexturePixels`, `rlCopyFramebuffer` | tres parámetros de salida, un `ref to int` de entrada y salida, y búferes de salida que posee el llamador con tamaños no informados. |
| D5 — pares sin closures | `rlBegin`/`rlEnd`, `rlPushMatrix`/`rlPopMatrix` | un helper equilibrado es imposible y un renombrado no compra nada. |
| D6 — recuento ambiguo | `rlSetUniform` en su forma general | el recuento de elementos depende del tipo del uniform; solo se expone el caso float. |
| estructural — ciclo de vida de `rlgl` | `rlglInit`, `rlglClose` | los posee raylib; llamarlos a mano pelea con `InitWindow`/`CloseWindow`. |

Auditoría de cobertura: **163 funciones C, 18 envueltas, 145 omitidas, sin restos y sin duplicados.** El registro de métodos gana los dos nombres de `rlRenderBatch`. **Ninguna otra familia puede añadir un método a `rlRenderBatch`**, y nada de aquí toca los tipos de `raylibx`.
