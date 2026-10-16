# Plan: textures.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/textures.pengu`
- Owner in the master plan: family `textures` of `docs/plans/raylibx.md` (v0.1.2), sixth in its order of implementation
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: the textures bucket holds **20** functions. **19 are available** and all 19 are wrapped; `LoadRenderTextureEx` is a raylib 6.1 addition that the installed 6.0.0 library does not export (master plan D17). | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`. |
| D2 | **The enchanting target is the nominal type, not the alias**: `enchanting raylib.Texture:` and `enchanting raylib.RenderTexture:`. | `Texture2D` is `alias Texture2D as Texture` and `RenderTexture2D` is `alias RenderTexture2D as RenderTexture`, so both names resolve to the same type and would emit the same C symbols. Master plan D3 and the `raymathx` lesson (where enchanting an alias pair produced duplicate symbols) say to name the nominal type. Callers still write `raylib.Texture2D`; the alias resolves. |
| D3 | 12 methods on `raylib.Texture`: `draw`, `draw_at`, `draw_ex`, `draw_rec`, `draw_pro`, `draw_npatch`, `update`, `update_rec`, `generate_mipmaps`, `set_filter`, `set_wrap`, `is_valid`. | The texture is the subject of every one of them, and the master plan's registry already reserved `draw`, `draw_at`, `draw_ex`, `draw_rec`, `draw_pro` and `update` for this family. The `Draw*` members are the reason the family earns its place: `tex.draw_pro with src, dst, origin, rotation, tint` is seven positional arguments in the binding, and the method form keeps the receiver visible. |
| D4 | 1 method on `raylib.RenderTexture`: `is_valid`. | `IsRenderTextureValid` is the only C function whose first argument is a render texture. |
| D5 | `RenderTexture.begin` / `RenderTexture.end` are **not** added here, and this corrects the master plan's registry row for that type, which listed them as planned. `BeginTextureMode` and `EndTextureMode` belong to the **`drawing`** family (its row in the family table owns them), and master plan D6 says the family that owns the C function wraps it. | One owner per symbol. The registry row's intent was right — a render target *should* know how to activate itself — so the plan records that `drawing` should expose them as `RenderTexture` methods (`target.begin`), which is why the names are left free here. `RenderTexture.draw` is likewise unnecessary: the `texture` field is already a `Texture` with the full draw surface. |
| D6 | The six resource entries stay module-level: `load_texture`, `load_texture_from_image`, `load_texture_cubemap`, `load_render_texture`, `unload_texture`, `unload_render_texture`. | They are constructors and destructors: the texture does not exist yet when the loader runs, and `unload_*` matches the convention already used by `raylibx_files` (`unload_font`, `unload_image`). Keeping the destructors module-level across families is deliberate. |
| D7 | The four loaders return `maybe`, checked with the type's own predicate: `load_texture`, `load_texture_from_image`, `load_texture_cubemap` → `maybe raylib.Texture` via `IsTextureValid`; `load_render_texture` → `maybe raylib.RenderTexture` via `IsRenderTextureValid`. | Contract §3 with the library's own predicate, exactly as `raylibx_images` does with `IsImageValid`. |
| D8 | `update` and `update_rec` take `pixels as slice of byte`, and the pointer conversion goes through `void*`. | The binding takes `ref to frozen void` with no length, because raylib reads the texture's dimensions. An empty slice is passed as an empty view rather than being guarded away, because raylib would read zero bytes; the docstring states that the caller must supply a full texture worth of pixels. |
| D9 | `set_filter` and `set_wrap` take the real enums (`raylib.TextureFilter`, `raylib.TextureWrap`), which the binding flattens to `int`. | The type-restoration argument of the `input` family: `tex.set_filter with raylib.TEXTURE_FILTER_BILINEAR` instead of `with (raylib.TEXTURE_FILTER_BILINEAR to int)`. |
| D10 | **This family is mostly window-bound, and it is the first one where the failure paths are the whole CI surface.** Measured headless: `IsTextureValid`, `IsRenderTextureValid`, `UnloadTexture`, `UnloadRenderTexture` and `GenTextureMipmaps` are safe; `SetTextureFilter`, `SetTextureWrap` and `UpdateTexture` **segfault**; and the four loaders fail *gracefully*, returning an invalid zeroed texture rather than crashing. | Measured in C, one process per function. The consequence for the tests is in the test plan: the loaders' `maybe none` path and the two predicates are asserted, everything that touches GL is type-checked by a probe and never called. |
| D11 | No `maybe` on `is_valid`, and no `@mutates` anywhere. | `is_valid` returns a `bool` that cannot fail. The mutators return `void`, so `@mutates` does not apply (contract §4). |
| D12 | `NPatchInfo` is passed by value to `draw_npatch`, as `raylib.NPatchInfo`. | It is a small `rune` the caller builds once to describe a nine-slice layout; the binding takes it by value and so does the wrapper. |

### ✨ Enchantings

#### `enchanting raylib.Texture` — 12 methods

| Method | Signature | C backing | Notes |
|---|---|---|---|
| `draw` | `with x as int, y as int, tint as raylib.Color into void` | `DrawTexture` | needs an active drawing frame |
| `draw_at` | `with position as raylib.Vector2, tint as raylib.Color into void` | `DrawTextureV` | |
| `draw_ex` | `with position as raylib.Vector2, rotation as f32, scale as f32, tint as raylib.Color into void` | `DrawTextureEx` | |
| `draw_rec` | `with rec as raylib.Rectangle, position as raylib.Vector2, tint as raylib.Color into void` | `DrawTextureRec` | draws a sub-rectangle of the texture |
| `draw_pro` | `with src_rec as raylib.Rectangle, dst_rec as raylib.Rectangle, origin as raylib.Vector2, rotation as f32, tint as raylib.Color into void` | `DrawTexturePro` | the full-control form: source and destination rectangles |
| `draw_npatch` | `with patch as raylib.NPatchInfo, dst_rec as raylib.Rectangle, origin as raylib.Vector2, rotation as f32, tint as raylib.Color into void` | `DrawTextureNPatch` | nine-slice scaling |
| `update` | `with pixels as slice of byte into void` | `UpdateTexture` | uploads a whole texture worth of pixels |
| `update_rec` | `with rec as raylib.Rectangle, pixels as slice of byte into void` | `UpdateTextureRec` | uploads only the rectangle |
| `generate_mipmaps` | `into void` | `GenTextureMipmaps` | mutates the receiver through `self`; raylib rebuilds the texture with its mipmap chain |
| `set_filter` | `with filter as raylib.TextureFilter into void` | `SetTextureFilter` | |
| `set_wrap` | `with wrap as raylib.TextureWrap into void` | `SetTextureWrap` | |
| `is_valid` | `into bool` | `IsTextureValid` | |

#### `enchanting raylib.RenderTexture` — 1 method

| Method | Signature | C backing |
|---|---|---|
| `is_valid` | `into bool` | `IsRenderTextureValid` |

### 🔧 Module-level functions (6)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `load_texture` | `with path as string into maybe raylib.Texture` | `LoadTexture` | `maybe none` for a missing file |
| `load_texture_from_image` | `with image as raylib.Image into maybe raylib.Texture` | `LoadTextureFromImage` | the image is read, not consumed |
| `load_texture_cubemap` | `with image as raylib.Image, layout as int into maybe raylib.Texture` | `LoadTextureCubemap` | `layout` describes how the six faces are arranged; raylib reports a failure for a layout it cannot detect |
| `load_render_texture` | `with width as int, height as int into maybe raylib.RenderTexture` | `LoadRenderTexture` | the render target owns two textures and a framebuffer |
| `unload_texture` | `with texture as raylib.Texture into void` | `UnloadTexture` | safe on an invalid texture |
| `unload_render_texture` | `with target as raylib.RenderTexture into void` | `UnloadRenderTexture` | releases both textures and the framebuffer |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `load_texture` | `maybe raylib.Texture` | `IsTextureValid` |
| `load_texture_from_image` | `maybe raylib.Texture` | `IsTextureValid` |
| `load_texture_cubemap` | `maybe raylib.Texture` | `IsTextureValid` |
| `load_render_texture` | `maybe raylib.RenderTexture` | `IsRenderTextureValid` |

> The four are the family's only failure channel, and headless they all report `maybe none`, which is exactly what the tests assert (D10).

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `Texture.update`, `Texture.update_rec` | `pixels as slice of byte` |

Neither guards the empty case: raylib reads the texture's own dimensions, so an empty slice would upload zero bytes, and the docstring tells the caller how much data is expected. The pointer is routed through `void*` (master plan D19).

### 📦 Multiple returns `(T, U)`

**None apply.** Four functions return `void`, one returns `bool`, and the rest return a single `Texture`/`RenderTexture` wrapped in `maybe`.

### 🌉 `std.ffi` usage

Only two things: `ffi.cstr_from_string` for `load_texture`'s path, and the `sigil of (pixels at 0)` → `void*` conversion for the two uploads. There is no ownership to manage — a texture is a GPU handle, not a heap buffer, so nothing is copied and nothing is freed with `MemFree`; the releases are `unload_texture` and `unload_render_texture`.

### 💡 Compilable examples

```pengu
# Example 1 — the drawing surface
import raylib
import raylibx.textures as textures

weave main into int:
    var tex as maybe raylib.Texture2D is calling textures.load_texture with "sprite.png"
    if tex is present:
        var img as raylib.Texture2D is calling tex.unwrap
        calling img.draw with 10, 10, raylib.WHITE
        calling img.draw_at with (with x is 10.0, y is 40.0), raylib.WHITE
        calling img.draw_ex with (with x is 10.0, y is 80.0), 45.0, 2.0, raylib.WHITE
        calling img.draw_rec with (with x is 0.0, y is 0.0, width is 16.0, height is 16.0), (with x is 10.0, y is 120.0), raylib.WHITE
        calling img.draw_pro with (with x is 0.0, y is 0.0, width is 16.0, height is 16.0), (with x is 10.0, y is 160.0, width is 32.0, height is 32.0), (with x is 0.0, y is 0.0), 0.0, raylib.WHITE
    return 0
```

```pengu
# Example 2 — filters, wrapping and pixel uploads
import raylib
import raylibx.textures as textures

weave main into int:
    var tex as maybe raylib.Texture2D is calling textures.load_texture with "tile.png"
    if tex is present:
        var img as raylib.Texture2D is calling tex.unwrap
        calling img.set_filter with raylib.TEXTURE_FILTER_BILINEAR
        calling img.set_wrap with raylib.TEXTURE_WRAP_REPEAT
        calling img.generate_mipmaps
        var patch as raylib.NPatchInfo is with source is (with x is 0.0, y is 0.0, width is 48.0, height is 48.0), left is 16, top is 16, right is 16, bottom is 16, layout is 0
        calling img.draw_npatch with patch, (with x is 0.0, y is 0.0, width is 128.0, height is 128.0), (with x is 0.0, y is 0.0), 0.0, raylib.WHITE
        var valid as bool is calling img.is_valid
    return 0
```

```pengu
# Example 3 — a render target
import raylib
import raylibx.textures as textures

weave main into int:
    var target as maybe raylib.RenderTexture2D is calling textures.load_render_texture with 256, 256
    if target is present:
        var rt as raylib.RenderTexture2D is calling target.unwrap
        defer calling textures.unload_render_texture with rt
        var valid as bool is calling rt.is_valid
        var inner as raylib.Texture2D is rt.texture
    return 0
```

### 🧪 Test plan

**The honest shape of this family: it is the first where the CI surface is small and made of failure paths.** Measured before promising anything (D10): a texture is a GPU handle, so anything that talks to OpenGL needs a window, and three functions even segfault when handed an invalid texture.

**CI-testable (8 assertions):**

- **`is_valid` on an invalid texture is `false`** — a zeroed `Texture2D` and a zeroed `RenderTexture2D`, built as struct literals. This is the predicate every loader's `maybe` rests on, so asserting it is asserting the family's failure model.
- **`load_texture` is `maybe none` for a missing file.**
- **`load_texture_from_image` is `maybe none` headless** — the image is valid (it comes from a pure generator) but the GPU upload yields an invalid texture, which is exactly the case the predicate exists for.
- **`load_texture_cubemap` is `maybe none`** — measured: raylib warns that it cannot detect the layout and returns an invalid texture.
- **`load_render_texture` is `maybe none` headless.**
- **`unload_texture` / `unload_render_texture` / `generate_mipmaps` are callable on an invalid texture without crashing** — measured safe, and they prove the `self` conversion for the one mutator.
- **The empty-slice no-op for `update` and `update_rec` is *not* asserted**: raylib would read zero bytes, but only after dereferencing the pointer, and the measured behaviour with an invalid texture is a segfault, so the probe references them for type checking and no test calls them.

**Window-bound (compile-only probe):** the six `draw_*` methods and `set_filter`, `set_wrap`, `update`, `update_rec`.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `LoadRenderTextureEx` | raylib 6.1 only; the installed 6.0.0 library does not export it (D1) |
| `BeginTextureMode`, `EndTextureMode` | **not this family**: `drawing` owns them, and D5 records that it should expose them as `RenderTexture` methods |
| `SetShapesTexture`, `GetShapesTexture`, `GetShapesTextureRectangle` | already wrapped by `raylibx_shapes` |
| `GetPixelDataSize` | already wrapped by `raylibx_images`, where it belongs next to the pixel formats |

Coverage audit: of the 20 textures-bucket functions, **19 are wrapped** (13 methods and 6 module functions) and **1 is unavailable**. The method registry gains the 13 `raylib.Texture`/`raylib.RenderTexture` names; **no other family may add a method to either type**, and the `begin`/`end` names are deliberately left unassigned for `drawing`.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/textures.pengu`
- Dueña en el plan maestro: familia `textures` de `docs/plans/raylibx.md` (v0.1.2), sexta en su orden de implementación
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: el grupo de texturas tiene **20** funciones. **19 están disponibles** y las 19 se envuelven; `LoadRenderTextureEx` es un añadido de raylib 6.1 que la biblioteca 6.0.0 instalada no exporta (plan maestro D17). | Enumerado desde el binding y cruzado con `tools/check_binding_symbols.py`. |
| D2 | **El objetivo de `enchanting` es el tipo nominal, no el alias**: `enchanting raylib.Texture:` y `enchanting raylib.RenderTexture:`. | `Texture2D` es `alias Texture2D as Texture` y `RenderTexture2D` es `alias RenderTexture2D as RenderTexture`, así que ambos nombres resuelven al mismo tipo y emitirían los mismos símbolos C. El plan maestro D3 y la lección de `raymathx` (donde encantar un par de alias produjo símbolos duplicados) dicen que hay que nombrar el tipo nominal. El llamador sigue escribiendo `raylib.Texture2D`; el alias resuelve. |
| D3 | 12 métodos sobre `raylib.Texture`: `draw`, `draw_at`, `draw_ex`, `draw_rec`, `draw_pro`, `draw_npatch`, `update`, `update_rec`, `generate_mipmaps`, `set_filter`, `set_wrap`, `is_valid`. | La textura es el sujeto de todos ellos, y el registro del plan maestro ya reservaba `draw`, `draw_at`, `draw_ex`, `draw_rec`, `draw_pro` y `update` para esta familia. Los miembros `Draw*` son la razón de que la familia se gane su sitio: `tex.draw_pro with src, dst, origin, rotation, tint` son siete argumentos posicionales en el binding, y la forma de método mantiene visible el receptor. |
| D4 | 1 método sobre `raylib.RenderTexture`: `is_valid`. | `IsRenderTextureValid` es la única función C cuyo primer argumento es una textura de render. |
| D5 | `RenderTexture.begin` / `RenderTexture.end` **no** se añaden aquí, y esto corrige la fila del registro del plan maestro para ese tipo, que las listaba como previstas. `BeginTextureMode` y `EndTextureMode` pertenecen a la familia **`drawing`** (su fila en la tabla de familias las posee), y el D6 del plan maestro dice que la familia dueña de la función C la envuelve. | Un dueño por símbolo. La intención de la fila del registro era correcta — un objetivo de render *debería* saber activarse — así que el plan registra que `drawing` debería exponerlas como métodos de `RenderTexture` (`target.begin`), y por eso los nombres se dejan libres aquí. `RenderTexture.draw` tampoco hace falta: el campo `texture` ya es una `Texture` con toda la superficie de dibujo. |
| D6 | Las seis entradas de recurso se quedan de módulo: `load_texture`, `load_texture_from_image`, `load_texture_cubemap`, `load_render_texture`, `unload_texture`, `unload_render_texture`. | Son constructores y destructores: la textura todavía no existe cuando corre el cargador, y `unload_*` coincide con la convención que ya usan `raylibx_files` (`unload_font`, `unload_image`). Mantener los destructores de módulo en todas las familias es deliberado. |
| D7 | Los cuatro cargadores devuelven `maybe`, comprobado con el predicado del propio tipo: `load_texture`, `load_texture_from_image`, `load_texture_cubemap` → `maybe raylib.Texture` con `IsTextureValid`; `load_render_texture` → `maybe raylib.RenderTexture` con `IsRenderTextureValid`. | Contrato §3 con el predicado de la propia biblioteca, exactamente como hace `raylibx_images` con `IsImageValid`. |
| D8 | `update` y `update_rec` reciben `pixels as slice of byte`, y la conversión a puntero pasa por `void*`. | El binding recibe `ref to frozen void` sin longitud, porque raylib lee las dimensiones de la textura. Un slice vacío se pasa como vista vacía en vez de guardarse, porque raylib leería cero bytes; el docstring dice que el llamador debe aportar los píxeles de una textura completa. |
| D9 | `set_filter` y `set_wrap` reciben los enums reales (`raylib.TextureFilter`, `raylib.TextureWrap`), que el binding aplana a `int`. | El argumento de restauración de tipos de la familia `input`: `tex.set_filter with raylib.TEXTURE_FILTER_BILINEAR` en vez de `with (raylib.TEXTURE_FILTER_BILINEAR to int)`. |
| D10 | **Esta familia está mayormente ligada a ventana, y es la primera donde las rutas de fallo son toda la superficie de CI.** Medido sin ventana: `IsTextureValid`, `IsRenderTextureValid`, `UnloadTexture`, `UnloadRenderTexture` y `GenTextureMipmaps` son seguras; `SetTextureFilter`, `SetTextureWrap` y `UpdateTexture` **revientan**; y los cuatro cargadores fallan *con elegancia*, devolviendo una textura inválida a ceros en vez de reventar. | Medido en C, un proceso por función. La consecuencia para los tests está en el plan de tests: la ruta `maybe none` de los cargadores y los dos predicados se aseguran, y todo lo que toca GL se comprueba de tipos con una sonda y no se llama. |
| D11 | Sin `maybe` en `is_valid`, y sin `@mutates` en ningún sitio. | `is_valid` devuelve un `bool` que no puede fallar. Los mutadores devuelven `void`, así que `@mutates` no aplica (contrato §4). |
| D12 | `NPatchInfo` se pasa por valor a `draw_npatch`, como `raylib.NPatchInfo`. | Es un `rune` pequeño que el llamador construye una vez para describir un diseño de nueve piezas; el binding lo recibe por valor y el wrapper también. |

### ✨ Enchantings

#### `enchanting raylib.Texture` — 12 métodos

| Método | Firma | C backing | Notas |
|---|---|---|---|
| `draw` | `with x as int, y as int, tint as raylib.Color into void` | `DrawTexture` | necesita marco de dibujo activo |
| `draw_at` | `with position as raylib.Vector2, tint as raylib.Color into void` | `DrawTextureV` | |
| `draw_ex` | `with position as raylib.Vector2, rotation as f32, scale as f32, tint as raylib.Color into void` | `DrawTextureEx` | |
| `draw_rec` | `with rec as raylib.Rectangle, position as raylib.Vector2, tint as raylib.Color into void` | `DrawTextureRec` | dibuja un subrectángulo de la textura |
| `draw_pro` | `with src_rec as raylib.Rectangle, dst_rec as raylib.Rectangle, origin as raylib.Vector2, rotation as f32, tint as raylib.Color into void` | `DrawTexturePro` | la forma de control total: rectángulos de origen y destino |
| `draw_npatch` | `with patch as raylib.NPatchInfo, dst_rec as raylib.Rectangle, origin as raylib.Vector2, rotation as f32, tint as raylib.Color into void` | `DrawTextureNPatch` | escalado de nueve piezas |
| `update` | `with pixels as slice of byte into void` | `UpdateTexture` | sube una textura entera de píxeles |
| `update_rec` | `with rec as raylib.Rectangle, pixels as slice of byte into void` | `UpdateTextureRec` | sube solo el rectángulo |
| `generate_mipmaps` | `into void` | `GenTextureMipmaps` | muta el receptor vía `self`; raylib reconstruye la textura con su cadena de mipmaps |
| `set_filter` | `with filter as raylib.TextureFilter into void` | `SetTextureFilter` | |
| `set_wrap` | `with wrap as raylib.TextureWrap into void` | `SetTextureWrap` | |
| `is_valid` | `into bool` | `IsTextureValid` | |

#### `enchanting raylib.RenderTexture` — 1 método

| Método | Firma | C backing |
|---|---|---|
| `is_valid` | `into bool` | `IsRenderTextureValid` |

### 🔧 Funciones a nivel de módulo (6)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `load_texture` | `with path as string into maybe raylib.Texture` | `LoadTexture` | `maybe none` para un fichero ausente |
| `load_texture_from_image` | `with image as raylib.Image into maybe raylib.Texture` | `LoadTextureFromImage` | la imagen se lee, no se consume |
| `load_texture_cubemap` | `with image as raylib.Image, layout as int into maybe raylib.Texture` | `LoadTextureCubemap` | `layout` describe cómo están colocadas las seis caras; raylib informa un fallo cuando no puede detectar el diseño |
| `load_render_texture` | `with width as int, height as int into maybe raylib.RenderTexture` | `LoadRenderTexture` | el objetivo de render posee dos texturas y un framebuffer |
| `unload_texture` | `with texture as raylib.Texture into void` | `UnloadTexture` | seguro sobre una textura inválida |
| `unload_render_texture` | `with target as raylib.RenderTexture into void` | `UnloadRenderTexture` | libera las dos texturas y el framebuffer |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `load_texture` | `maybe raylib.Texture` | `IsTextureValid` |
| `load_texture_from_image` | `maybe raylib.Texture` | `IsTextureValid` |
| `load_texture_cubemap` | `maybe raylib.Texture` | `IsTextureValid` |
| `load_render_texture` | `maybe raylib.RenderTexture` | `IsRenderTextureValid` |

> Los cuatro son el único canal de fallo de la familia, y sin ventana todos informan `maybe none`, que es exactamente lo que aseguran los tests (D10).

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `Texture.update`, `Texture.update_rec` | `pixels as slice of byte` |

Ninguna guarda el caso vacío: raylib lee las dimensiones de la propia textura, así que un slice vacío subiría cero bytes, y el docstring dice al llamador cuántos datos se esperan. El puntero pasa por `void*` (plan maestro D19).

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Cuatro funciones devuelven `void`, una devuelve `bool` y el resto devuelven una sola `Texture`/`RenderTexture` envuelta en `maybe`.

### 🌉 Uso de `std.ffi`

Solo dos cosas: `ffi.cstr_from_string` para la ruta de `load_texture`, y la conversión `sigil of (pixels at 0)` → `void*` de las dos subidas. No hay propiedad que gestionar: una textura es un handle de GPU, no un búfer del montón, así que no se copia nada ni se libera nada con `MemFree`; las liberaciones son `unload_texture` y `unload_render_texture`.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — la superficie de dibujo
import raylib
import raylibx.textures as textures

weave main into int:
    var tex as maybe raylib.Texture2D is calling textures.load_texture with "sprite.png"
    if tex is present:
        var img as raylib.Texture2D is calling tex.unwrap
        calling img.draw with 10, 10, raylib.WHITE
        calling img.draw_at with (with x is 10.0, y is 40.0), raylib.WHITE
        calling img.draw_ex with (with x is 10.0, y is 80.0), 45.0, 2.0, raylib.WHITE
        calling img.draw_rec with (with x is 0.0, y is 0.0, width is 16.0, height is 16.0), (with x is 10.0, y is 120.0), raylib.WHITE
        calling img.draw_pro with (with x is 0.0, y is 0.0, width is 16.0, height is 16.0), (with x is 10.0, y is 160.0, width is 32.0, height is 32.0), (with x is 0.0, y is 0.0), 0.0, raylib.WHITE
    return 0
```

```pengu
# Ejemplo 2 — filtros, wrapping y subidas de píxeles
import raylib
import raylibx.textures as textures

weave main into int:
    var tex as maybe raylib.Texture2D is calling textures.load_texture with "tile.png"
    if tex is present:
        var img as raylib.Texture2D is calling tex.unwrap
        calling img.set_filter with raylib.TEXTURE_FILTER_BILINEAR
        calling img.set_wrap with raylib.TEXTURE_WRAP_REPEAT
        calling img.generate_mipmaps
        var patch as raylib.NPatchInfo is with source is (with x is 0.0, y is 0.0, width is 48.0, height is 48.0), left is 16, top is 16, right is 16, bottom is 16, layout is 0
        calling img.draw_npatch with patch, (with x is 0.0, y is 0.0, width is 128.0, height is 128.0), (with x is 0.0, y is 0.0), 0.0, raylib.WHITE
        var valid as bool is calling img.is_valid
    return 0
```

```pengu
# Ejemplo 3 — un objetivo de render
import raylib
import raylibx.textures as textures

weave main into int:
    var target as maybe raylib.RenderTexture2D is calling textures.load_render_texture with 256, 256
    if target is present:
        var rt as raylib.RenderTexture2D is calling target.unwrap
        defer calling textures.unload_render_texture with rt
        var valid as bool is calling rt.is_valid
        var inner as raylib.Texture2D is rt.texture
    return 0
```

### 🧪 Plan de tests

**La forma honesta de esta familia: es la primera donde la superficie de CI es pequeña y está hecha de rutas de fallo.** Medido antes de prometer nada (D10): una textura es un handle de GPU, así que todo lo que habla con OpenGL necesita ventana, y tres funciones incluso revientan cuando reciben una textura inválida.

**Testeable en CI (8 aserciones):**

- **`is_valid` sobre una textura inválida es `false`** — una `Texture2D` a ceros y una `RenderTexture2D` a ceros, construidas como literales de struct. Es el predicado sobre el que descansa el `maybe` de todos los cargadores, así que asegurarlo es asegurar el modelo de fallo de la familia.
- **`load_texture` es `maybe none` para un fichero ausente.**
- **`load_texture_from_image` es `maybe none` sin ventana** — la imagen es válida (viene de un generador puro) pero la subida a GPU da una textura inválida, que es exactamente el caso para el que existe el predicado.
- **`load_texture_cubemap` es `maybe none`** — medido: raylib avisa de que no puede detectar el diseño y devuelve una textura inválida.
- **`load_render_texture` es `maybe none` sin ventana.**
- **`unload_texture` / `unload_render_texture` / `generate_mipmaps` se pueden llamar sobre una textura inválida sin reventar** — medido seguro, y demuestran la conversión de `self` para el único mutador.
- **El no-op de slice vacío de `update` y `update_rec` *no* se asegura**: raylib leería cero bytes, pero solo después de desreferenciar el puntero, y el comportamiento medido con una textura inválida es un fallo de segmentación, así que la sonda las referencia para la comprobación de tipos y ningún test las llama.

**Ligado a ventana (sonda de solo compilación):** los seis métodos `draw_*` y `set_filter`, `set_wrap`, `update`, `update_rec`.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `LoadRenderTextureEx` | solo raylib 6.1; la biblioteca 6.0.0 instalada no lo exporta (D1) |
| `BeginTextureMode`, `EndTextureMode` | **no son de esta familia**: las posee `drawing`, y D5 registra que debería exponerlas como métodos de `RenderTexture` |
| `SetShapesTexture`, `GetShapesTexture`, `GetShapesTextureRectangle` | ya las envuelve `raylibx_shapes` |
| `GetPixelDataSize` | ya la envuelve `raylibx_images`, que es donde corresponde junto a los formatos de píxel |

Auditoría de cobertura: de las 20 funciones del grupo de texturas, **19 se envuelven** (13 métodos y 6 funciones de módulo) y **1 no está disponible**. El registro de métodos gana los 13 nombres de `raylib.Texture`/`raylib.RenderTexture`; **ninguna otra familia puede añadir un método a ninguno de los dos tipos**, y los nombres `begin`/`end` se dejan deliberadamente sin asignar para `drawing`.
