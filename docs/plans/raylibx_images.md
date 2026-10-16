# Plan: images.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/images.pengu`
- Owner in the master plan: family `images` of `docs/plans/raylibx.md` (v0.1.2), fifth in its order of implementation
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: the image bucket holds **90** functions. Of those, **11 are not exported by the installed library** (they are raylib 6.1 additions, master plan D17), **one belongs to another family** (`GenImageFontAtlas`, already wrapped as `raylibx_text`'s `font_atlas_image`), and **two cannot be wrapped** (D6). That leaves **76 candidates: 74 public wrappers and 2 internal releases**. | Enumerated from `pengu/raylib.d.pengu` and cross-checked against `tools/check_binding_symbols.py`. There are no unwrapped leftovers: a script asserts that every candidate is assigned to exactly one of the three lists. |
| D2 | **The family is dominated by methods on `raylib.Image`**: 52 of the 74. Every mutator, every draw and every pixel reader takes the image as its subject, so `img.crop with rect` and `img.draw_circle with 8, 8, 4, raylib.RED` replace argument-order-sensitive calls into the binding. | Contract §6.1. The master plan's registry already reserved `raylib.Image` for this family; this plan fills it in. |
| D3 | The 25 transforms and the 20 draws return `**void**` and mutate in place, so they are **not** `@mutates`: `@mutates` requires returning the receiver's own type (contract §4), and these return nothing. The three producers (`copy`, `region`, `channel`) return a **new** image. | The same shape as `rcamerax`'s mutators. The distinction matters to the caller: the seven entries that return `raylib.Image` hand back a resource that must be released separately, and their docstrings say so. |
| D4 | The pixel readers fold into owned PenguScript values and release the raylib buffer inside: `colors` → `maybe (list of raylib.Color)` (raylib returns null for an invalid image, and the count is `width * height`), `palette` → `list of raylib.Color` (raylib reports the count through an out-parameter, so it folds into `.length`), `alpha_border` → `raylib.Rectangle`, `color_at` → `raylib.Color`. | Contract §3 and §5. `UnloadImageColors` and `UnloadImagePalette` are therefore **internal releases**, not public wrappers. |
| D5 | `ImageKernelConvolution` takes `slice of f32`, and the two slice-shaped draws take `slice of raylib.Vector2`; all three guard the empty slice and convert through `void*`. | Contract §5 for the slice shape, and master plan D19 / `shapes` D13 for the `void*` route: a typed `ref to frozen raylib.Vector2` makes the compiler emit an invalid C cast. An empty kernel is a no-op rather than a read of element zero. |
| D6 | **Two functions are skipped because their second result cannot be returned**: `LoadImageAnim` and `LoadImageAnimFromMemory`. Both report the frame count through an `int *` out-parameter, and contract §4 forbids a tuple when one component is an out-parameter. | The count is not recoverable from the image: raylib stores the frames stacked vertically, and without the count the caller cannot know how many there are, so wrapping the loader alone would hand back a resource nobody can use. Recorded rather than silently omitted. |
| D7 | **Eleven functions are skipped because the installed library does not export them**: `ImageDrawLineStrip`, `ImageDrawTriangleGradient`, `ImageDrawRectanglePro`, `ImageDrawRectangleLinesEx`, `ImageDrawRectangleGradientEx`, `ImageDrawCircleGradient`, `ImageDrawImage`, `ImageDrawImageEx`, `ImageDrawImageRec`, `ImageDrawImagePro`, `ImageDrawTextPro`. | Master plan D17: the header is 6.1-dev and the library is 6.0.0. `pengu check` and `pengu build` are both clean and the failure only appears at link time, which is why the symbol check is mandatory before claiming case (a). |
| D8 | `GenImageFontAtlas` is **not** wrapped here: `raylibx_text` already exposes it as `font_atlas_image`. | Master plan D5/D6, one owner per symbol. Its `Rectangle**` out-parameter is freed inside that wrapper. |
| D9 | The nine `gen_image_*` factories, `image_from_text` and `image_from_text_ex` are module-level, not methods. | They have no receiver: they build an image from scratch. They are also the reason this family is unusually well covered (D10). |
| D10 | The family is **largely testable in CI**, and the boundary was measured rather than assumed: the generators, every transform, every draw and every pixel reader are pure CPU work over a heap buffer and need no window. Only **four** entries need a graphics context: `load_image_from_texture` (a GPU read-back), `load_image_from_screen`, and the two text renderers, which walk the default font's glyph table — null before `InitWindow`, and the `text` family measured that touching it segfaults. | Measured in C headless: `GenImageColor(4,3,RED)` gives a 4x3 image with format 7, `ImageCrop`/`ImageFlipHorizontal`/`ImageResize` change it in place, `GetImageColor` reads it back, `LoadImageColors` and `LoadImagePalette` allocate and can be freed. That is why this plan asserts pixels instead of only dimensions. |
| D11 | `export_image_to_memory` copies the buffer and then calls `MemFree`, and `load_image*` return `maybe raylib.Image` checked with `IsImageValid`. | The header says the exported buffer "must be MemFree()" (`include/raylib.h:1372`), so the wrapper owns releasing it; the loaders use `IsImageValid` as the predicate, which is the same one raylib itself documents. |
| D12 | `raylib.Image.data` is a `ref to byte` into raylib-owned memory. It is documented as read-only-in-practice and never `banish`ed. | Contract §8: the wrapper returns owned values and remembers the lifetime of a view. `unload_image` frees the buffer, after which the `Image` value must not be used, and `copy`/`region`/`channel` exist for when an independent buffer is what the caller wants. |

### ✨ Enchantings

No `@mutates` anywhere: the 45 mutating methods return `void` (D3) and the seven reading methods return a value, so the compiler generates no `get_*` form.

#### `enchanting raylib.Image` — 52 methods

##### Transforms and pixel access (33)

| Method | Signature | C backing |
|---|---|---|
| `to_format` | `with new_format as raylib.PixelFormat into void` | `ImageFormat` |
| `to_power_of_two` | `with fill as raylib.Color into void` | `ImageToPOT` |
| `crop` | `with rect as raylib.Rectangle into void` | `ImageCrop` |
| `crop_to_alpha` | `with threshold as f32 into void` | `ImageAlphaCrop` |
| `clear_alpha` | `with color as raylib.Color, threshold as f32 into void` | `ImageAlphaClear` |
| `apply_alpha_mask` | `with mask as raylib.Image into void` | `ImageAlphaMask` |
| `premultiply_alpha` | `into void` | `ImageAlphaPremultiply` |
| `blur_gaussian` | `with blur_size as int into void` | `ImageBlurGaussian` |
| `convolve` | `with kernel as slice of f32 into void` | `ImageKernelConvolution` |
| `resize` | `with width as int, height as int into void` | `ImageResize` |
| `resize_nearest` | `with width as int, height as int into void` | `ImageResizeNN` |
| `resize_canvas` | `with width as int, height as int, offset_x as int, offset_y as int, fill as raylib.Color into void` | `ImageResizeCanvas` |
| `generate_mipmaps` | `into void` | `ImageMipmaps` |
| `dither` | `with r_bpp as int, g_bpp as int, b_bpp as int, a_bpp as int into void` | `ImageDither` |
| `flip_vertical` | `into void` | `ImageFlipVertical` |
| `flip_horizontal` | `into void` | `ImageFlipHorizontal` |
| `rotate` | `with degrees as int into void` | `ImageRotate` |
| `rotate_cw` | `into void` | `ImageRotateCW` |
| `rotate_ccw` | `into void` | `ImageRotateCCW` |
| `tint` | `with color as raylib.Color into void` | `ImageColorTint` |
| `invert` | `into void` | `ImageColorInvert` |
| `to_grayscale` | `into void` | `ImageColorGrayscale` |
| `adjust_contrast` | `with contrast as int into void` | `ImageColorContrast` |
| `adjust_brightness` | `with brightness as int into void` | `ImageColorBrightness` |
| `replace_color` | `with color as raylib.Color, replacement as raylib.Color into void` | `ImageColorReplace` |
| `copy` | `into raylib.Image` | `ImageCopy` |
| `region` | `with rect as raylib.Rectangle into raylib.Image` | `ImageFromImage` |
| `channel` | `with selected_channel as int into raylib.Image` | `ImageFromChannel` |
| `colors` | `into maybe (list of raylib.Color)` | `LoadImageColors` |
| `palette` | `with max_size as int into list of raylib.Color` | `LoadImagePalette` |
| `alpha_border` | `with threshold as f32 into raylib.Rectangle` | `GetImageAlphaBorder` |
| `color_at` | `with x as int, y as int into raylib.Color` | `GetImageColor` |
| `clear` | `with color as raylib.Color into void` | `ImageClearBackground` |

##### Drawing (19)

| Method | Signature | C backing |
|---|---|---|
| `draw_pixel` | `with x as int, y as int, color as raylib.Color into void` | `ImageDrawPixel` |
| `draw_pixel_at` | `with position as raylib.Vector2, color as raylib.Color into void` | `ImageDrawPixelV` |
| `draw_line` | `with x1 as int, y1 as int, x2 as int, y2 as int, color as raylib.Color into void` | `ImageDrawLine` |
| `draw_line_between` | `with start as raylib.Vector2, end as raylib.Vector2, color as raylib.Color into void` | `ImageDrawLineV` |
| `draw_line_thick` | `with start as raylib.Vector2, end as raylib.Vector2, thick as int, color as raylib.Color into void` | `ImageDrawLineEx` |
| `draw_triangle` | `with v1 as raylib.Vector2, v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangle` |
| `draw_triangle_outline` | `with v1 as raylib.Vector2, v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangleLines` |
| `draw_triangle_fan` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangleFan` |
| `draw_triangle_strip` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangleStrip` |
| `draw_rectangle` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `ImageDrawRectangle` |
| `draw_rectangle_at` | `with position as raylib.Vector2, extent as raylib.Vector2, color as raylib.Color into void` | `ImageDrawRectangleV` |
| `draw_rectangle_rec` | `with rect as raylib.Rectangle, color as raylib.Color into void` | `ImageDrawRectangleRec` |
| `draw_rectangle_outline` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `ImageDrawRectangleLines` |
| `draw_circle` | `with center_x as int, center_y as int, radius as int, color as raylib.Color into void` | `ImageDrawCircle` |
| `draw_circle_at` | `with center as raylib.Vector2, radius as int, color as raylib.Color into void` | `ImageDrawCircleV` |
| `draw_circle_outline` | `with center_x as int, center_y as int, radius as int, color as raylib.Color into void` | `ImageDrawCircleLines` |
| `draw_circle_outline_at` | `with center as raylib.Vector2, radius as int, color as raylib.Color into void` | `ImageDrawCircleLinesV` |
| `draw_text` | `with text as string, x as int, y as int, font_size as int, color as raylib.Color into void` | `ImageDrawText` |
| `draw_text_ex` | `with font as raylib.Font, text as string, position as raylib.Vector2, font_size as f32, spacing as f32, tint as raylib.Color into void` | `ImageDrawTextEx` |

### 🔧 Module-level functions (22)

| Function | Signature | C backing |
|---|---|---|
| `is_image_valid` | `with image as raylib.Image into bool` | `IsImageValid` |
| `unload_image` | `with image as raylib.Image into void` | `UnloadImage` |
| `load_image` | `with path as string into maybe raylib.Image` | `LoadImage` |
| `load_image_raw` | `with path as string, width as int, height as int, format as raylib.PixelFormat, header_size as int into maybe raylib.Image` | `LoadImageRaw` |
| `load_image_from_memory` | `with file_type as string, data as slice of byte into maybe raylib.Image` | `LoadImageFromMemory` |
| `load_image_from_texture` | `with texture as raylib.Texture2D into maybe raylib.Image` | `LoadImageFromTexture` |
| `load_image_from_screen` | `into maybe raylib.Image` | `LoadImageFromScreen` |
| `export_image` | `with image as raylib.Image, path as string into bool` | `ExportImage` |
| `export_image_to_memory` | `with image as raylib.Image, file_type as string into maybe (list of byte)` | `ExportImageToMemory` |
| `export_image_as_code` | `with image as raylib.Image, path as string into bool` | `ExportImageAsCode` |
| `gen_image_color` | `with width as int, height as int, color as raylib.Color into raylib.Image` | `GenImageColor` |
| `gen_image_gradient_linear` | `with width as int, height as int, direction as int, start as raylib.Color, end as raylib.Color into raylib.Image` | `GenImageGradientLinear` |
| `gen_image_gradient_radial` | `with width as int, height as int, density as f32, inner as raylib.Color, outer as raylib.Color into raylib.Image` | `GenImageGradientRadial` |
| `gen_image_gradient_square` | `with width as int, height as int, density as f32, inner as raylib.Color, outer as raylib.Color into raylib.Image` | `GenImageGradientSquare` |
| `gen_image_checked` | `with width as int, height as int, checks_x as int, checks_y as int, col1 as raylib.Color, col2 as raylib.Color into raylib.Image` | `GenImageChecked` |
| `gen_image_white_noise` | `with width as int, height as int, factor as f32 into raylib.Image` | `GenImageWhiteNoise` |
| `gen_image_perlin_noise` | `with width as int, height as int, offset_x as int, offset_y as int, scale as f32 into raylib.Image` | `GenImagePerlinNoise` |
| `gen_image_cellular` | `with width as int, height as int, tile_size as int into raylib.Image` | `GenImageCellular` |
| `gen_image_text` | `with width as int, height as int, text as string into raylib.Image` | `GenImageText` |
| `image_from_text` | `with text as string, font_size as int, color as raylib.Color into raylib.Image` | `ImageText` |
| `image_from_text_ex` | `with font as raylib.Font, text as string, font_size as f32, spacing as f32, tint as raylib.Color into raylib.Image` | `ImageTextEx` |
| `pixel_data_size` | `with width as int, height as int, format as raylib.PixelFormat into int` | `GetPixelDataSize` |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `load_image` | `maybe raylib.Image` | `IsImageValid` after the call |
| `load_image_raw` | `maybe raylib.Image` | `IsImageValid` |
| `load_image_from_memory` | `maybe raylib.Image` | empty slice, or `IsImageValid` |
| `load_image_from_texture` | `maybe raylib.Image` | `IsImageValid` |
| `load_image_from_screen` | `maybe raylib.Image` | `IsImageValid` |
| `export_image_to_memory` | `maybe (list of byte)` | raylib returns a null pointer when it cannot encode |
| `Image.colors` | `maybe (list of raylib.Color)` | raylib returns a null pointer for an invalid image |

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `Image.convolve` | `kernel as slice of f32` |
| `Image.draw_triangle_fan`, `Image.draw_triangle_strip` | `points as slice of raylib.Vector2` |
| `load_image_from_memory` | `data as slice of byte` |

Every one guards the empty slice: a zero-length kernel or vertex list draws nothing, and an empty byte slice is `maybe none`.

### 📦 Multiple returns `(T, U)`

**None apply**, and that is a deliberate outcome: the three out-parameter cases fold into `.length` (`palette`, `export_image_to_memory`) or into a copy sized by `width * height` (`colors`), and the two that cannot fold are skipped (D6).

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | every path, extension and text parameter |
| raw `Color*` → owned `list of raylib.Color` | `ffi.list_from_ptr of raylib.Color` | `colors`, `palette` |
| raw `byte*` → owned `list of byte` | `ffi.list_of_bytes_from_ptr` | `export_image_to_memory` |
| null check | `ffi.is_null` | every `maybe` |

### 💡 Compilable examples

```pengu
# Example 1 — generate, draw, transform, read back
import raylib
import raylibx.images as images

weave main into int:
    var img as raylib.Image is calling images.gen_image_color with 32, 32, raylib.RED
    defer calling images.unload_image with img
    calling img.draw_circle with 16, 16, 8, raylib.WHITE
    calling img.draw_rectangle with 0, 0, 4, 4, raylib.BLUE
    calling img.resize with 64, 64
    var pixel as raylib.Color is calling img.color_at with 20, 20
    var ok as bool is calling images.is_image_valid with img
    return 0
```

```pengu
# Example 2 — the producers and the owning readers
import raylib
import raylibx.images as images

weave main into int:
    var src as raylib.Image is calling images.gen_image_checked with 16, 16, 4, 4, raylib.RED, raylib.BLUE
    defer calling images.unload_image with src
    var clone as raylib.Image is calling src.copy
    defer calling images.unload_image with clone
    var part as raylib.Image is calling src.region with (with x is 0.0, y is 0.0, width is 8.0, height is 8.0)
    defer calling images.unload_image with part
    var mask as raylib.Image is calling src.channel with 0
    defer calling images.unload_image with mask
    var pixels as maybe (list of raylib.Color) is calling src.colors
    var pal as list of raylib.Color is calling src.palette with 16
    defer banish pal
    return 0
```

```pengu
# Example 3 — encode in memory and compute buffer sizes
import raylib
import raylibx.images as images

weave main into int:
    var img as raylib.Image is calling images.gen_image_gradient_linear with 8, 8, 0, raylib.BLACK, raylib.WHITE
    defer calling images.unload_image with img
    var blob as maybe (list of byte) is calling images.export_image_to_memory with img, ".png"
    var needed as int is calling images.pixel_data_size with 8, 8, raylib.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
    return needed
```

### 🧪 Test plan

**43 tests, all in CI, none needing a window.** This is the best-covered family of the module because the whole image pipeline is CPU work, which the plan verified before promising tests (D10). The assertions read pixels rather than only counting them:

- **The nine generators**: dimensions, validity, and a pixel value; `gen_image_color` with `raylib.BLANK` is fully transparent; the linear gradient is darker at one end than the other; the noise and cellular generators honour the requested size.
- **`copy` is independent**: the clone keeps its own pixel after the original is cleared — the assertion that proves the copy does not alias.
- **`region` / `channel`**: the extracted region has the requested size; the channel image comes back in the grayscale format.
- **`colors`**: one entry per pixel (`width * height`), with the right colour; **`palette`** of a solid image has exactly one entry.
- **`alpha_border`** of a fully opaque image is the whole image.
- **`color_at` after `draw_pixel`**: the pixel written is the pixel read, alpha included.
- **Every transform**: `crop`, `resize`, `resize_nearest`, `resize_canvas` (content preserved, new area transparent), `rotate_cw`/`rotate_ccw` (dimensions swapped), `to_format` (format field changes), `to_power_of_two` (3x3 becomes 4x4), `clear`, `tint with black`, `invert`, `to_grayscale` (channels equal), `adjust_contrast`, `adjust_brightness`, `replace_color`, `generate_mipmaps`, `blur_gaussian`, `dither`, `convolve` with a 3x3 identity kernel (colour preserved) and with an empty kernel (no-op), `crop_to_alpha`, `clear_alpha`, `apply_alpha_mask`, `premultiply_alpha`.
- **All 19 draws in one test**, followed by a pixel read that proves a circle landed; plus the empty-slice no-op for the two slice draws.
- **`is_image_valid`** and **`pixel_data_size`** (measured: 4x4 `R8G8B8A8` is 64, `R8G8B8` is 48).
- **The failure paths**: `load_image`, `load_image_raw` and `load_image_from_memory` are `maybe none` for a missing file, an empty buffer and a bogus buffer.
- **The file IO**: `export_image_to_memory` produces a non-empty PNG blob; `export_image` and `export_image_as_code` write to a temp path that is removed with `defer` (the `files` family's rule, so the suite leaves no debris).
- **`images_api_probe`**: type-checks the four window-bound entries without calling them.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `LoadImageAnim`, `LoadImageAnimFromMemory` | the frame count cannot be returned (D6) |
| `ImageDrawLineStrip`, `ImageDrawTriangleGradient`, `ImageDrawRectanglePro`, `ImageDrawRectangleLinesEx`, `ImageDrawRectangleGradientEx`, `ImageDrawCircleGradient`, `ImageDrawImage`, `ImageDrawImageEx`, `ImageDrawImageRec`, `ImageDrawImagePro`, `ImageDrawTextPro` | raylib 6.1 only; not exported by the installed library (D7) |
| `GenImageFontAtlas` | `raylibx_text` owns it (D8) |
| `UnloadImageColors`, `UnloadImagePalette` | internal releases called by `Image.colors` and `Image.palette` (D4) |
| `LoadTextureFromImage`, `LoadTextureCubemap` | **not this family**: they return a `Texture2D` and belong to `textures` (master plan D6) |

Coverage audit: of the 90 image-bucket functions, **74 are public wrappers** (52 methods on `raylib.Image` and 22 module functions), **2 are internal releases**, **11 are unavailable in the installed library**, **2 are skipped for the tuple rule** and **1 is owned by another family**. The method registry gains the 52 `raylib.Image` names listed above; **no other family may add an `Image` method**.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/images.pengu`
- Dueña en el plan maestro: familia `images` de `docs/plans/raylibx.md` (v0.1.2), quinta en su orden de implementación
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: el grupo de imágenes tiene **90** funciones. De ellas, **11 no las exporta la biblioteca instalada** (son añadidos de raylib 6.1, plan maestro D17), **una pertenece a otra familia** (`GenImageFontAtlas`, ya envuelta como `font_atlas_image` de `raylibx_text`) y **dos no se pueden envolver** (D6). Quedan **76 candidatas: 74 wrappers públicos y 2 liberaciones internas**. | Enumerado desde `pengu/raylib.d.pengu` y cruzado con `tools/check_binding_symbols.py`. No hay restos sin asignar: un script comprueba que cada candidata está exactamente en una de las tres listas. |
| D2 | **La familia está dominada por métodos sobre `raylib.Image`**: 52 de los 74. Todo mutador, todo dibujo y todo lector de píxeles recibe la imagen como sujeto, así que `img.crop with rect` y `img.draw_circle with 8, 8, 4, raylib.RED` sustituyen llamadas al binding sensibles al orden de argumentos. | Contrato §6.1. El registro del plan maestro ya reservaba `raylib.Image` para esta familia; este plan lo rellena. |
| D3 | Las 25 transformaciones y los 20 dibujos devuelven `**void**` y mutan en su sitio, así que **no** son `@mutates`: `@mutates` exige devolver el tipo del propio receptor (contrato §4), y estos no devuelven nada. Los tres productores (`copy`, `region`, `channel`) devuelven una imagen **nueva**. | La misma forma que los mutadores de `rcamerax`. La distinción importa al llamador: las siete entradas que devuelven `raylib.Image` entregan un recurso que hay que liberar aparte, y sus docstrings lo dicen. |
| D4 | Los lectores de píxeles se pliegan en valores con posesión de PenguScript y liberan el búfer de raylib dentro: `colors` → `maybe (list of raylib.Color)` (raylib devuelve nulo para una imagen inválida, y el recuento es `width * height`), `palette` → `list of raylib.Color` (raylib informa el recuento por out-param, así que se pliega en `.length`), `alpha_border` → `raylib.Rectangle`, `color_at` → `raylib.Color`. | Contrato §3 y §5. `UnloadImageColors` y `UnloadImagePalette` son por tanto **liberaciones internas**, no wrappers públicos. |
| D5 | `ImageKernelConvolution` recibe `slice of f32`, y los dos dibujos con slice reciben `slice of raylib.Vector2`; los tres guardan el slice vacío y convierten por `void*`. | Contrato §5 para la forma de slice, y plan maestro D19 / D13 de `shapes` para la ruta `void*`: un `ref to frozen raylib.Vector2` tipado hace que el compilador emita un cast de C inválido. Un kernel vacío es un no-op en vez de una lectura del elemento cero. |
| D6 | **Se omiten dos funciones porque su segundo resultado no se puede devolver**: `LoadImageAnim` y `LoadImageAnimFromMemory`. Las dos informan el número de fotogramas por un out-param `int *`, y el contrato §4 prohíbe una tupla cuando uno de los componentes es un out-param. | El recuento no se recupera de la imagen: raylib guarda los fotogramas apilados verticalmente, y sin el recuento el llamador no puede saber cuántos hay, así que envolver solo el cargador entregaría un recurso que nadie puede usar. Se registra en vez de omitirse en silencio. |
| D7 | **Se omiten once funciones porque la biblioteca instalada no las exporta**: `ImageDrawLineStrip`, `ImageDrawTriangleGradient`, `ImageDrawRectanglePro`, `ImageDrawRectangleLinesEx`, `ImageDrawRectangleGradientEx`, `ImageDrawCircleGradient`, `ImageDrawImage`, `ImageDrawImageEx`, `ImageDrawImageRec`, `ImageDrawImagePro`, `ImageDrawTextPro`. | Plan maestro D17: el header es 6.1-dev y la biblioteca es 6.0.0. `pengu check` y `pengu build` salen limpios y el fallo solo aparece al enlazar, y por eso la comprobación de símbolos es obligatoria antes de declarar el caso (a). |
| D8 | `GenImageFontAtlas` **no** se envuelve aquí: `raylibx_text` ya la expone como `font_atlas_image`. | Plan maestro D5/D6, un dueño por símbolo. Su out-param `Rectangle**` se libera dentro de aquel wrapper. |
| D9 | Las nueve factorías `gen_image_*`, `image_from_text` e `image_from_text_ex` son de módulo, no métodos. | No tienen receptor: construyen una imagen desde cero. Son además la razón de que esta familia esté inusualmente bien cubierta (D10). |
| D10 | La familia es **mayormente testeable en CI**, y la frontera se midió en vez de asumirse: los generadores, todas las transformaciones, todos los dibujos y todos los lectores de píxeles son trabajo puro de CPU sobre un búfer del montón y no necesitan ventana. Solo **cuatro** entradas necesitan contexto gráfico: `load_image_from_texture` (una lectura de GPU), `load_image_from_screen` y los dos renderizadores de texto, que recorren la tabla de glifos de la fuente por defecto — nula antes de `InitWindow`, y la familia `text` midió que tocarla revienta. | Medido en C sin ventana: `GenImageColor(4,3,RED)` da una imagen 4x3 con formato 7, `ImageCrop`/`ImageFlipHorizontal`/`ImageResize` la cambian en su sitio, `GetImageColor` la relee, y `LoadImageColors` y `LoadImagePalette` reservan memoria que se puede liberar. Por eso este plan asegura píxeles y no solo dimensiones. |
| D11 | `export_image_to_memory` copia el búfer y después llama a `MemFree`, y los `load_image*` devuelven `maybe raylib.Image` comprobado con `IsImageValid`. | El header dice que el búfer exportado "must be MemFree()" (`include/raylib.h:1372`), así que el wrapper se hace cargo de liberarlo; los cargadores usan `IsImageValid` como predicado, que es el mismo que documenta raylib. |
| D12 | `raylib.Image.data` es un `ref to byte` dentro de memoria que posee raylib. Se documenta como de solo lectura en la práctica y **nunca** se le hace `banish`. | Contrato §8: el wrapper devuelve valores con posesión y recuerda el tiempo de vida de una vista. `unload_image` libera el búfer, y después el valor `Image` no se debe usar; `copy`/`region`/`channel` existen para cuando lo que hace falta es un búfer independiente. |

### ✨ Enchantings

Sin `@mutates` en ningún sitio: los 45 métodos que mutan devuelven `void` (D3) y los siete que leen devuelven un valor, así que el compilador no genera ninguna forma `get_*`.

#### `enchanting raylib.Image` — 52 métodos

##### Transformaciones y acceso a píxeles (33)

| Método | Firma | C backing |
|---|---|---|
| `to_format` | `with new_format as raylib.PixelFormat into void` | `ImageFormat` |
| `to_power_of_two` | `with fill as raylib.Color into void` | `ImageToPOT` |
| `crop` | `with rect as raylib.Rectangle into void` | `ImageCrop` |
| `crop_to_alpha` | `with threshold as f32 into void` | `ImageAlphaCrop` |
| `clear_alpha` | `with color as raylib.Color, threshold as f32 into void` | `ImageAlphaClear` |
| `apply_alpha_mask` | `with mask as raylib.Image into void` | `ImageAlphaMask` |
| `premultiply_alpha` | `into void` | `ImageAlphaPremultiply` |
| `blur_gaussian` | `with blur_size as int into void` | `ImageBlurGaussian` |
| `convolve` | `with kernel as slice of f32 into void` | `ImageKernelConvolution` |
| `resize` | `with width as int, height as int into void` | `ImageResize` |
| `resize_nearest` | `with width as int, height as int into void` | `ImageResizeNN` |
| `resize_canvas` | `with width as int, height as int, offset_x as int, offset_y as int, fill as raylib.Color into void` | `ImageResizeCanvas` |
| `generate_mipmaps` | `into void` | `ImageMipmaps` |
| `dither` | `with r_bpp as int, g_bpp as int, b_bpp as int, a_bpp as int into void` | `ImageDither` |
| `flip_vertical` | `into void` | `ImageFlipVertical` |
| `flip_horizontal` | `into void` | `ImageFlipHorizontal` |
| `rotate` | `with degrees as int into void` | `ImageRotate` |
| `rotate_cw` | `into void` | `ImageRotateCW` |
| `rotate_ccw` | `into void` | `ImageRotateCCW` |
| `tint` | `with color as raylib.Color into void` | `ImageColorTint` |
| `invert` | `into void` | `ImageColorInvert` |
| `to_grayscale` | `into void` | `ImageColorGrayscale` |
| `adjust_contrast` | `with contrast as int into void` | `ImageColorContrast` |
| `adjust_brightness` | `with brightness as int into void` | `ImageColorBrightness` |
| `replace_color` | `with color as raylib.Color, replacement as raylib.Color into void` | `ImageColorReplace` |
| `copy` | `into raylib.Image` | `ImageCopy` |
| `region` | `with rect as raylib.Rectangle into raylib.Image` | `ImageFromImage` |
| `channel` | `with selected_channel as int into raylib.Image` | `ImageFromChannel` |
| `colors` | `into maybe (list of raylib.Color)` | `LoadImageColors` |
| `palette` | `with max_size as int into list of raylib.Color` | `LoadImagePalette` |
| `alpha_border` | `with threshold as f32 into raylib.Rectangle` | `GetImageAlphaBorder` |
| `color_at` | `with x as int, y as int into raylib.Color` | `GetImageColor` |
| `clear` | `with color as raylib.Color into void` | `ImageClearBackground` |

##### Dibujo (19)

| Método | Firma | C backing |
|---|---|---|
| `draw_pixel` | `with x as int, y as int, color as raylib.Color into void` | `ImageDrawPixel` |
| `draw_pixel_at` | `with position as raylib.Vector2, color as raylib.Color into void` | `ImageDrawPixelV` |
| `draw_line` | `with x1 as int, y1 as int, x2 as int, y2 as int, color as raylib.Color into void` | `ImageDrawLine` |
| `draw_line_between` | `with start as raylib.Vector2, end as raylib.Vector2, color as raylib.Color into void` | `ImageDrawLineV` |
| `draw_line_thick` | `with start as raylib.Vector2, end as raylib.Vector2, thick as int, color as raylib.Color into void` | `ImageDrawLineEx` |
| `draw_triangle` | `with v1 as raylib.Vector2, v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangle` |
| `draw_triangle_outline` | `with v1 as raylib.Vector2, v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangleLines` |
| `draw_triangle_fan` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangleFan` |
| `draw_triangle_strip` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `ImageDrawTriangleStrip` |
| `draw_rectangle` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `ImageDrawRectangle` |
| `draw_rectangle_at` | `with position as raylib.Vector2, extent as raylib.Vector2, color as raylib.Color into void` | `ImageDrawRectangleV` |
| `draw_rectangle_rec` | `with rect as raylib.Rectangle, color as raylib.Color into void` | `ImageDrawRectangleRec` |
| `draw_rectangle_outline` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `ImageDrawRectangleLines` |
| `draw_circle` | `with center_x as int, center_y as int, radius as int, color as raylib.Color into void` | `ImageDrawCircle` |
| `draw_circle_at` | `with center as raylib.Vector2, radius as int, color as raylib.Color into void` | `ImageDrawCircleV` |
| `draw_circle_outline` | `with center_x as int, center_y as int, radius as int, color as raylib.Color into void` | `ImageDrawCircleLines` |
| `draw_circle_outline_at` | `with center as raylib.Vector2, radius as int, color as raylib.Color into void` | `ImageDrawCircleLinesV` |
| `draw_text` | `with text as string, x as int, y as int, font_size as int, color as raylib.Color into void` | `ImageDrawText` |
| `draw_text_ex` | `with font as raylib.Font, text as string, position as raylib.Vector2, font_size as f32, spacing as f32, tint as raylib.Color into void` | `ImageDrawTextEx` |

### 🔧 Funciones a nivel de módulo (22)

| Función | Firma | C backing |
|---|---|---|
| `is_image_valid` | `with image as raylib.Image into bool` | `IsImageValid` |
| `unload_image` | `with image as raylib.Image into void` | `UnloadImage` |
| `load_image` | `with path as string into maybe raylib.Image` | `LoadImage` |
| `load_image_raw` | `with path as string, width as int, height as int, format as raylib.PixelFormat, header_size as int into maybe raylib.Image` | `LoadImageRaw` |
| `load_image_from_memory` | `with file_type as string, data as slice of byte into maybe raylib.Image` | `LoadImageFromMemory` |
| `load_image_from_texture` | `with texture as raylib.Texture2D into maybe raylib.Image` | `LoadImageFromTexture` |
| `load_image_from_screen` | `into maybe raylib.Image` | `LoadImageFromScreen` |
| `export_image` | `with image as raylib.Image, path as string into bool` | `ExportImage` |
| `export_image_to_memory` | `with image as raylib.Image, file_type as string into maybe (list of byte)` | `ExportImageToMemory` |
| `export_image_as_code` | `with image as raylib.Image, path as string into bool` | `ExportImageAsCode` |
| `gen_image_color` | `with width as int, height as int, color as raylib.Color into raylib.Image` | `GenImageColor` |
| `gen_image_gradient_linear` | `with width as int, height as int, direction as int, start as raylib.Color, end as raylib.Color into raylib.Image` | `GenImageGradientLinear` |
| `gen_image_gradient_radial` | `with width as int, height as int, density as f32, inner as raylib.Color, outer as raylib.Color into raylib.Image` | `GenImageGradientRadial` |
| `gen_image_gradient_square` | `with width as int, height as int, density as f32, inner as raylib.Color, outer as raylib.Color into raylib.Image` | `GenImageGradientSquare` |
| `gen_image_checked` | `with width as int, height as int, checks_x as int, checks_y as int, col1 as raylib.Color, col2 as raylib.Color into raylib.Image` | `GenImageChecked` |
| `gen_image_white_noise` | `with width as int, height as int, factor as f32 into raylib.Image` | `GenImageWhiteNoise` |
| `gen_image_perlin_noise` | `with width as int, height as int, offset_x as int, offset_y as int, scale as f32 into raylib.Image` | `GenImagePerlinNoise` |
| `gen_image_cellular` | `with width as int, height as int, tile_size as int into raylib.Image` | `GenImageCellular` |
| `gen_image_text` | `with width as int, height as int, text as string into raylib.Image` | `GenImageText` |
| `image_from_text` | `with text as string, font_size as int, color as raylib.Color into raylib.Image` | `ImageText` |
| `image_from_text_ex` | `with font as raylib.Font, text as string, font_size as f32, spacing as f32, tint as raylib.Color into raylib.Image` | `ImageTextEx` |
| `pixel_data_size` | `with width as int, height as int, format as raylib.PixelFormat into int` | `GetPixelDataSize` |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `load_image` | `maybe raylib.Image` | `IsImageValid` tras la llamada |
| `load_image_raw` | `maybe raylib.Image` | `IsImageValid` |
| `load_image_from_memory` | `maybe raylib.Image` | slice vacío, o `IsImageValid` |
| `load_image_from_texture` | `maybe raylib.Image` | `IsImageValid` |
| `load_image_from_screen` | `maybe raylib.Image` | `IsImageValid` |
| `export_image_to_memory` | `maybe (list of byte)` | raylib devuelve puntero nulo cuando no puede codificar |
| `Image.colors` | `maybe (list of raylib.Color)` | raylib devuelve puntero nulo para una imagen inválida |

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `Image.convolve` | `kernel as slice of f32` |
| `Image.draw_triangle_fan`, `Image.draw_triangle_strip` | `points as slice of raylib.Vector2` |
| `load_image_from_memory` | `data as slice of byte` |

Todas guardan el slice vacío: un kernel o una lista de vértices de longitud cero no dibujan nada, y un slice de bytes vacío es `maybe none`.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica**, y es un resultado deliberado: los tres casos con out-param se pliegan en `.length` (`palette`, `export_image_to_memory`) o en una copia dimensionada por `width * height` (`colors`), y los dos que no se pueden plegar se omiten (D6).

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | todo parámetro de ruta, extensión y texto |
| `Color*` crudo → `list of raylib.Color` con posesión | `ffi.list_from_ptr of raylib.Color` | `colors`, `palette` |
| `byte*` crudo → `list of byte` con posesión | `ffi.list_of_bytes_from_ptr` | `export_image_to_memory` |
| comprobación de nulo | `ffi.is_null` | todos los `maybe` |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — generar, dibujar, transformar y releer
import raylib
import raylibx.images as images

weave main into int:
    var img as raylib.Image is calling images.gen_image_color with 32, 32, raylib.RED
    defer calling images.unload_image with img
    calling img.draw_circle with 16, 16, 8, raylib.WHITE
    calling img.draw_rectangle with 0, 0, 4, 4, raylib.BLUE
    calling img.resize with 64, 64
    var pixel as raylib.Color is calling img.color_at with 20, 20
    var ok as bool is calling images.is_image_valid with img
    return 0
```

```pengu
# Ejemplo 2 — los productores y los lectores con posesión
import raylib
import raylibx.images as images

weave main into int:
    var src as raylib.Image is calling images.gen_image_checked with 16, 16, 4, 4, raylib.RED, raylib.BLUE
    defer calling images.unload_image with src
    var clone as raylib.Image is calling src.copy
    defer calling images.unload_image with clone
    var part as raylib.Image is calling src.region with (with x is 0.0, y is 0.0, width is 8.0, height is 8.0)
    defer calling images.unload_image with part
    var mask as raylib.Image is calling src.channel with 0
    defer calling images.unload_image with mask
    var pixels as maybe (list of raylib.Color) is calling src.colors
    var pal as list of raylib.Color is calling src.palette with 16
    defer banish pal
    return 0
```

```pengu
# Ejemplo 3 — codificar en memoria y calcular tamaños de búfer
import raylib
import raylibx.images as images

weave main into int:
    var img as raylib.Image is calling images.gen_image_gradient_linear with 8, 8, 0, raylib.BLACK, raylib.WHITE
    defer calling images.unload_image with img
    var blob as maybe (list of byte) is calling images.export_image_to_memory with img, ".png"
    var needed as int is calling images.pixel_data_size with 8, 8, raylib.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
    return needed
```

### 🧪 Plan de tests

**43 tests, todos en CI, ninguno necesita ventana.** Es la familia mejor cubierta del módulo porque toda la tubería de imágenes es trabajo de CPU, cosa que el plan verificó antes de prometer tests (D10). Las aserciones leen píxeles en vez de solo contarlos:

- **Los nueve generadores**: dimensiones, validez y un valor de píxel; `gen_image_color` con `raylib.BLANK` es totalmente transparente; el degradado lineal es más oscuro en un extremo que en el otro; los generadores de ruido y celular respetan el tamaño pedido.
- **`copy` es independiente**: el clon conserva su píxel después de limpiar el original — la aserción que demuestra que la copia no aliasa.
- **`region` / `channel`**: la región extraída tiene el tamaño pedido; la imagen de canal vuelve en formato escala de grises.
- **`colors`**: una entrada por píxel (`width * height`), con el color correcto; **`palette`** de una imagen sólida tiene exactamente una entrada.
- **`alpha_border`** de una imagen totalmente opaca es la imagen entera.
- **`color_at` después de `draw_pixel`**: el píxel escrito es el píxel leído, alfa incluido.
- **Todas las transformaciones**: `crop`, `resize`, `resize_nearest`, `resize_canvas` (contenido conservado, área nueva transparente), `rotate_cw`/`rotate_ccw` (dimensiones intercambiadas), `to_format` (cambia el campo de formato), `to_power_of_two` (3x3 pasa a 4x4), `clear`, `tint with black`, `invert`, `to_grayscale` (canales iguales), `adjust_contrast`, `adjust_brightness`, `replace_color`, `generate_mipmaps`, `blur_gaussian`, `dither`, `convolve` con un kernel identidad 3x3 (color conservado) y con un kernel vacío (no-op), `crop_to_alpha`, `clear_alpha`, `apply_alpha_mask`, `premultiply_alpha`.
- **Los 19 dibujos en un solo test**, seguidos de una lectura de píxel que demuestra que un círculo aterrizó; más el no-op de slice vacío para los dos dibujos con slice.
- **`is_image_valid`** y **`pixel_data_size`** (medido: 4x4 en `R8G8B8A8` son 64, en `R8G8B8` son 48).
- **Las rutas de fallo**: `load_image`, `load_image_raw` y `load_image_from_memory` son `maybe none` para un fichero ausente, un búfer vacío y un búfer basura.
- **La E/S de ficheros**: `export_image_to_memory` produce un blob PNG no vacío; `export_image` y `export_image_as_code` escriben en una ruta temporal que se borra con `defer` (la regla de la familia `files`, para que la suite no deje restos).
- **`images_api_probe`**: comprueba de tipos las cuatro entradas ligadas a ventana sin llamarlas.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `LoadImageAnim`, `LoadImageAnimFromMemory` | el número de fotogramas no se puede devolver (D6) |
| `ImageDrawLineStrip`, `ImageDrawTriangleGradient`, `ImageDrawRectanglePro`, `ImageDrawRectangleLinesEx`, `ImageDrawRectangleGradientEx`, `ImageDrawCircleGradient`, `ImageDrawImage`, `ImageDrawImageEx`, `ImageDrawImageRec`, `ImageDrawImagePro`, `ImageDrawTextPro` | solo raylib 6.1; la biblioteca instalada no las exporta (D7) |
| `GenImageFontAtlas` | la posee `raylibx_text` (D8) |
| `UnloadImageColors`, `UnloadImagePalette` | liberaciones internas que llaman `Image.colors` e `Image.palette` (D4) |
| `LoadTextureFromImage`, `LoadTextureCubemap` | **no son de esta familia**: devuelven un `Texture2D` y pertenecen a `textures` (plan maestro D6) |

Auditoría de cobertura: de las 90 funciones del grupo de imágenes, **74 son wrappers públicos** (52 métodos de `raylib.Image` y 22 funciones de módulo), **2 son liberaciones internas**, **11 no están disponibles en la biblioteca instalada**, **2 se omiten por la regla de la tupla** y **1 la posee otra familia**. El registro de métodos gana los 52 nombres de `raylib.Image` listados arriba; **ninguna otra familia puede añadir un método a `Image`**.
