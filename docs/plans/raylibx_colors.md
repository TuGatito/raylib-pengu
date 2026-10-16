# Plan: colors.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/colors.pengu`
- Owner in the master plan: family `colors` of `docs/plans/raylibx.md` (v0.1.2), first in its order of implementation
- Dependencies: `import raylib`, `import raymath` (the family hands `Vector3`/`Vector4` back and forth, so the type has to be in scope)
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified for this bucket: **case (a) complete**. The colour surface is exactly 14 `declare`s, all present: `ColorIsEqual`, `Fade`, `ColorToInt`, `ColorNormalize`, `ColorFromNormalized`, `ColorToHSV`, `ColorFromHSV`, `ColorTint`, `ColorBrightness`, `ColorContrast`, `ColorAlpha`, `ColorAlphaBlend`, `ColorLerp`, `GetColor`. `SetPixelColor` and `GetPixelColor` are the two raw-pixel outliers (D7). | Enumerated against `include/raylib.h:1487-1502`. Nothing missing. |
| D2 | The 10 value transforms that take a colour as their subject are **methods on `raylib.Color`**: `to_int`, `to_normalized`, `to_hsv`, `with_alpha`, `tint_with`, `brighten_by`, `contrast_with`, `blend_over`, `lerp_to`, `is_equal`. | Contract §6.1: "does the first argument *is* the subject?" gives `yes` for every one of them (`ColorTint(Color color, Color tint)` transforms `color`). |
| D3 | The four constructors are **`ritual`s on `raylib.Color`**: `from_hex`, `from_hsv`, `from_normalized`, plus `from_int` (wrapper-only, D5). | `PenguScriptGuideSpanish.md` §6.2 and contract §2: `from_*` is the canonical constructor naming, and `ritual` is how a constructor is spelled. Verified: `calling Color.from_hex with 0xFF0000FF` resolves. |
| D4 | `ColorNormalize` → `to_normalized`, and `ColorFromNormalized` → `from_normalized`. **Not** `normalize`. | `PixelFormat`, `TextureFilter` and `ColorNormalize` are three unrelated "normalize" operations in raylib; `to_normalized`/`from_normalized` say what actually crosses the boundary (a `Vector4` in `[0, 1]`). |
| D5 | `Color.from_int` is added even though the binding has **no** `ColorFromInt` counterpart, implemented inline from the four byte fields. | `ColorToInt` is the documented packing (`0xRRGGBBAA`, `include/raylib.h:1489`) and a round trip is what callers actually want. It is wrapper-only, like `Vector3.splat` in `raymathx`, and the docstring says so. |
| D6 | `ColorIsEqual` is wrapped as a **module-level** `is_equal` **and** the binding's `bool` is taken as it is. | Unlike the `Equals` family in `raymath` (which returns `int` with `EPSILON`-based comparison), `ColorIsEqual` is an exact `bool` comparison of four bytes (`include/raylib.h:1487`), so the `raymathx` rationale for skipping does not apply. It is module-level rather than a method because equality has no privileged receiver — the master plan's registry records `is_equal` as a `colors` module function, and this keeps the method table free for the transforms. |
| D7 | `SetPixelColor` and `GetPixelColor` are **not wrapped**. | Both operate on a raw `void*` into foreign memory with a `PixelFormat` tag; a `maybe` or a `ref to frozen void` parameter would just be the binding with extra ceremony, and getting the format or the pointer wrong is memory corruption the wrapper cannot prevent (contract §9 rows 6–7). Callers use the binding directly. |
| D8 | `ColorLerp` → `lerp_to` as a method, not `lerp`. | Consistent with `raymathx` (`Vector2.lerp_to`) and with the contract's mutator/pure naming; `lerp_to with other, t` reads as "interpolate towards `other`". |
| D9 | No parameter defaults are invented. | `ColorAlpha`, `ColorBrightness` and `ColorContrast` have documented ranges (`[0..1]`, `[-1..1]`) that the C code does **not** clamp; a default would hide that. The docstrings state the ranges and say the C behaviour is passed through unchanged. |
| D10 | The constants (`RAYWHITE`, `LIGHTGRAY`, …, 26 of them) stay in the binding and are **not** re-exported. | Contract §2 and the master plan D8. `import raylib` already exposes them. |
| D11 | No `maybe`, no `slice`, no `std.ffi`. | Every wrapped function is arithmetic over four bytes; none can fail, none takes an array, and none crosses a string or pointer boundary (the two that do are skipped, D7). |

### ✨ Enchantings

No `@mutates`: every method returns a new `Color` or a scalar and leaves the receiver alone (contract §4), so the compiler generates no `get_*` form. The rituals are the only constructors.

#### `enchanting raylib.Color`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `from_hex` | ritual | `with hex as u32 into raylib.Color` | `GetColor` | `0xRRGGBBAA`, as the header documents |
| `from_int` | ritual | `with packed as int into raylib.Color` | (inline) | wrapper-only inverse of `to_int` (D5) |
| `from_hsv` | ritual | `with hue as f32, saturation as f32, value as f32 into raylib.Color` | `ColorFromHSV` | hue in `[0..360]`, saturation/value in `[0..1]` |
| `from_normalized` | ritual | `with v as raylib.Vector4 into raylib.Color` | `ColorFromNormalized` | components in `[0..1]` |
| `is_equal` | pure | `with other as raylib.Color into bool` | `ColorIsEqual` | exact byte comparison; also exposed as the module function `is_equal` (D6) |
| `to_int` | pure | `into int` | `ColorToInt` | packed `0xRRGGBBAA` |
| `to_normalized` | pure | `into raylib.Vector4` | `ColorNormalize` | components in `[0..1]` |
| `to_hsv` | pure | `into raylib.Vector3` | `ColorToHSV` | `x` hue `[0..360]`, `y` saturation, `z` value |
| `with_alpha` | pure | `with alpha as f32 into raylib.Color` | `ColorAlpha` | `[0..1]`; **not clamped by C** (D9) |
| `tint_with` | pure | `with other as raylib.Color into raylib.Color` | `ColorTint` | component-wise multiply |
| `brighten_by` | pure | `with factor as f32 into raylib.Color` | `ColorBrightness` | `[-1..1]` |
| `contrast_with` | pure | `with factor as f32 into raylib.Color` | `ColorContrast` | `[-1..1]` |
| `blend_over` | pure | `with other as raylib.Color, tint as raylib.Color into raylib.Color` | `ColorAlphaBlend` | `self` is the **source** and `other` the destination; C argument order is reversed deliberately (see below) |
| `lerp_to` | pure | `with other as raylib.Color, t as f32 into raylib.Color` | `ColorLerp` | `t` in `[0..1]` |

> `blend_over` reverses the C arguments on purpose. `ColorAlphaBlend(dst, src, tint)` blends `src` **into** `dst`, so a method whose receiver is the source must call `ColorAlphaBlend with other, (essence of self), tint`. Reading `front.blend_over with back, tint` as "draw `front` over `back`" is the whole point of the name; the family test asserts the direction.

### 🔧 Module-level functions

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `is_equal` | `with a as raylib.Color, b as raylib.Color into bool` | `ColorIsEqual` | the privileged-receiver-free form of the method (D6) |
| `fade` | `with color as raylib.Color, alpha as f32 into raylib.Color` | `Fade` | raylib's own name for `with_alpha`; kept because the binding calls it `Fade` and the header documents `alpha` as `[0..1]` |

`fade` and `Color.with_alpha` are the same operation under two names. That is deliberate and matches how `std.tally` exposes both `xs.sum` and `tally.sum with xs` (`PenguScriptGuideSpanish.md` §6.1), and the master plan records `Fade` as owned by this family.

### 🎁 `maybe T` wrappers

**None apply.** Every wrapped function is arithmetic over four bytes: no external resource, no nullable pointer, no failure channel. The two functions that *can* corrupt memory (`SetPixelColor`, `GetPixelColor`) are skipped rather than wrapped (D7).

### ✂️ `slice` wrappers

**None apply.** No colour function takes `(T* ptr, int count)`; the only pointer parameters in the bucket belong to the two skipped pixel functions.

### 📦 Multiple returns `(T, U)`

**None apply.** The functions that return several components already return a raylib type: `ColorNormalize` → `Vector4`, `ColorToHSV` → `Vector3`. No tuple is needed and none is invented.

### 🌉 `std.ffi` usage

**None apply, reason: no string and no foreign pointer.** The whole family is `Color`, `Vector3`, `Vector4`, `f32`, `int`, `u32` and `bool`. The two functions with a `void*` parameter are out of scope (D7).

### 💡 Compilable examples

```pengu
# Example 1 — round-tripping a colour through every representation
import raylib
import raymath
import raylibx.colors as colors

weave main into int:
    var c as raylib.Color is calling Color.from_hex with 0xFF0000FF
    var packed as int is calling c.to_int
    var same as raylib.Color is calling Color.from_int with packed
    var hsv as raylib.Vector3 is calling c.to_hsv
    var back as raylib.Color is calling Color.from_hsv with hsv.x, hsv.y, hsv.z
    var unit as raylib.Vector4 is calling c.to_normalized
    var again as raylib.Color is calling Color.from_normalized with unit
    var equal as bool is calling colors.is_equal with c, same
    return 0
```

```pengu
# Example 2 — the transforms, and the blend direction
import raylib
import raymath
import raylibx.colors as colors

weave main into int:
    var base as raylib.Color is calling Color.from_hex with 0x204060FF
    var faded as raylib.Color is calling base.with_alpha with 0.5
    var brighter as raylib.Color is calling base.brighten_by with 0.25
    var softer as raylib.Color is calling base.contrast_with with -0.25
    var tinted as raylib.Color is calling base.tint_with with raylib.RAYWHITE
    var mixed as raylib.Color is calling base.lerp_to with raylib.BLACK, 0.5
    var front as raylib.Color is calling Color.from_hex with 0x00FF00FF
    var over as raylib.Color is calling front.blend_over with base, raylib.RAYWHITE
    var also as raylib.Color is calling colors.fade with base, 0.5
    return 0
```

### 🧪 Test plan

The whole family is CI-testable: no window, no GPU, no file. Three tests per public entry, with values taken from the real functions.

- **`from_hex`**: `0xFF0000FF` gives red `(255, 0, 0, 255)`; `0x00000000` gives transparent black; the alpha byte lands in `a` (`0x11223344` → `(0x11, 0x22, 0x33, 0x44)`).
- **`from_int`**: `to_int` then `from_int` is the identity for three fixed colours; the packed byte order is asserted explicitly. Measured in C: `GetColor(0x11223344)` gives `(0x11, 0x22, 0x33, 0x44)` and `ColorToInt` packs it back to `0x11223344`, which the inline `from_int` shifts out with the same `>> 24 / >> 16 / >> 8 / & 0xFF` layout.
- **`from_hsv`**: hue `0` is red; saturation `0` is grey (r == g == b); value `0` is black.
- **`from_normalized`**: `(1, 1, 1, 1)` is white; `(0, 0, 0, 0)` is transparent black; `(0.5, 0.5, 0.5, 1)` is mid-grey.
- **`is_equal`**: a colour equals itself; two colours differing only in alpha are **not** equal; the module function and the method agree on the same pair.
- **`to_int`**: red packs to `0xFF0000FF`; black is `0x000000FF` (opaque) and transparent black is `0x00000000`; the value fits in `int` for `a == 255`.
- **`to_normalized`**: white is `(1, 1, 1, 1)`; black is `(0, 0, 0, 1)`; every component stays inside `[0, 1]`.
- **`to_hsv`**: pure red has hue `0` and value `1`; grey has saturation `0`; `from_hsv` round-trips `to_hsv` for three colours within the byte quantisation.
- **`with_alpha`**: `0.0` makes the colour transparent; `1.0` leaves `a` at `255`; the RGB bytes are untouched.
- **`tint_with`**: tinting with white is the identity; tinting with black gives `(0, 0, 0, a)`; tinting with itself darkens unless the colour is white (asserted as a documented caveat, not an identity).
- **`brighten_by`**: `0.0` is the identity; `+1.0` drives the colour towards white; `-1.0` drives it towards black.
- **`contrast_with`**: `0.0` is the identity; a positive factor pushes away from mid-grey; the alpha byte is preserved.
- **`blend_over`**: a fully transparent source leaves the destination unchanged; a fully opaque source replaces it; the direction is asserted by blending red over blue and checking the result is red (this is the test that pins D2's argument reversal).
- **`lerp_to`**: `t = 0.0` is the receiver; `t = 1.0` is the target; `t = 0.5` is between the two on every channel.
- **`fade`**: agrees with `Color.with_alpha` on the same inputs; `alpha = 0.0` clears the alpha byte; `alpha = 1.0` preserves it.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `SetPixelColor` | operates on a raw `void*` destination with a `PixelFormat` tag; the wrapper cannot make it safer, only longer (D7, contract §9 row 7) |
| `GetPixelColor` | same, reading from a `const void*` (D7) |
| `ColorNormalize`, `ColorFromNormalized`, `ColorToHSV`, `ColorFromHSV`, `ColorTint`, `ColorBrightness`, `ColorContrast`, `ColorAlpha`, `ColorAlphaBlend`, `ColorLerp`, `ColorToInt`, `ColorIsEqual`, `Fade`, `GetColor` | **Wrapped**, one entry each (see the tables above); listed here only to record that the bucket is 14 of 16 |
| The 26 `Color` constants (`RAYWHITE`, `LIGHTGRAY`, …) | not wrapped and not re-exported: they are binding `const`s and keep their C spelling (D10, contract §2) |
| `ImageColorTint`, `ImageColorContrast`, `ImageColorBrightness` and the other `ImageColor*` mutators | **not this family**: they are `Image` methods and belong to `raylibx_images` (master plan D5/D6) |

Coverage audit: of the 16 colour-related `declare`s, **14 are wrapped** (10 methods + 4 rituals, plus the module functions `is_equal` and `fade`) and **2 are skipped** (`SetPixelColor`, `GetPixelColor`). The method registry entry for `raylib.Color` is therefore: `is_equal`, `to_int`, `to_normalized`, `to_hsv`, `with_alpha`, `tint_with`, `brighten_by`, `contrast_with`, `blend_over`, `lerp_to`, and the rituals `from_hex`, `from_int`, `from_hsv`, `from_normalized`. **No other family may add a method to `raylib.Color`.**

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/colors.pengu`
- Dueña en el plan maestro: familia `colors` de `docs/plans/raylibx.md` (v0.1.2), primera en su orden de implementación
- Dependencias: `import raylib`, `import raymath` (la familia devuelve y recibe `Vector3`/`Vector4`, así que el tipo tiene que estar en scope)
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada para este grupo: **caso (a) completo**. La superficie de color son exactamente 14 `declare`, todos presentes: `ColorIsEqual`, `Fade`, `ColorToInt`, `ColorNormalize`, `ColorFromNormalized`, `ColorToHSV`, `ColorFromHSV`, `ColorTint`, `ColorBrightness`, `ColorContrast`, `ColorAlpha`, `ColorAlphaBlend`, `ColorLerp`, `GetColor`. `SetPixelColor` y `GetPixelColor` son los dos casos crudos de píxel (D7). | Enumerado contra `include/raylib.h:1487-1502`. No falta ninguno. |
| D2 | Las 10 transformaciones de valor que tienen un color como sujeto son **métodos sobre `raylib.Color`**: `to_int`, `to_normalized`, `to_hsv`, `with_alpha`, `tint_with`, `brighten_by`, `contrast_with`, `blend_over`, `lerp_to`, `is_equal`. | Contrato §6.1: "¿es el primer argumento *el* sujeto?" da `yes` en todas (`ColorTint(Color color, Color tint)` transforma `color`). |
| D3 | Los cuatro constructores son **`ritual` sobre `raylib.Color`**: `from_hex`, `from_hsv`, `from_normalized`, más `from_int` (solo wrapper, D5). | `PenguScriptGuideSpanish.md` §6.2 y contrato §2: `from_*` es el nombre canónico de constructor, y `ritual` es cómo se escribe un constructor. Verificado: `calling Color.from_hex with 0xFF0000FF` resuelve. |
| D4 | `ColorNormalize` → `to_normalized` y `ColorFromNormalized` → `from_normalized`. **No** `normalize`. | `PixelFormat`, `TextureFilter` y `ColorNormalize` son tres "normalize" sin relación en raylib; `to_normalized`/`from_normalized` dicen qué cruza de verdad la frontera (un `Vector4` en `[0, 1]`). |
| D5 | Se añade `Color.from_int` aunque el binding **no** tenga `ColorFromInt`, implementado en línea desde los cuatro campos de byte. | `ColorToInt` es el empaquetado documentado (`0xRRGGBBAA`, `include/raylib.h:1489`) y lo que el llamador quiere es la ida y vuelta. Es solo-wrapper, como `Vector3.splat` en `raymathx`, y el docstring lo dice. |
| D6 | `ColorIsEqual` se envuelve como `is_equal` **de módulo** y se toma el `bool` del binding tal cual. | A diferencia de la familia `Equals` de `raymath` (que devuelve `int` con comparación por `EPSILON`), `ColorIsEqual` es un `bool` de comparación exacta de cuatro bytes (`include/raylib.h:1487`), así que el motivo de `raymathx` para omitirlo no aplica. Es de módulo y no método porque la igualdad no tiene receptor privilegiado; el registro del plan maestro asigna `is_equal` como función de módulo de `colors` y así la tabla de métodos queda libre para las transformaciones. |
| D7 | `SetPixelColor` y `GetPixelColor` **no se envuelven**. | Las dos operan sobre un `void*` crudo en memoria ajena con una etiqueta `PixelFormat`; un `maybe` o un parámetro `ref to frozen void` sería el binding con ceremonia extra, y equivocarse de formato o de puntero es corrupción de memoria que el wrapper no puede evitar (contrato §9 filas 6–7). El llamador usa el binding directamente. |
| D8 | `ColorLerp` → `lerp_to` como método, no `lerp`. | Coherente con `raymathx` (`Vector2.lerp_to`) y con la nomenclatura mutador/puro del contrato; `lerp_to with other, t` se lee como "interpola hacia `other`". |
| D9 | No se inventan valores por defecto. | `ColorAlpha`, `ColorBrightness` y `ColorContrast` tienen rangos documentados (`[0..1]`, `[-1..1]`) que el C **no** acota; un valor por defecto escondería eso. Los docstrings declaran los rangos y dicen que el comportamiento C se pasa sin cambios. |
| D10 | Las constantes (`RAYWHITE`, `LIGHTGRAY`, …, 26) se quedan en el binding y **no** se reexportan. | Contrato §2 y plan maestro D8. `import raylib` ya las expone. |
| D11 | Sin `maybe`, sin `slice`, sin `std.ffi`. | Todas las funciones envueltas son aritmética sobre cuatro bytes; ninguna puede fallar, ninguna recibe un array y ninguna cruza una frontera de cadena o puntero (las dos que sí lo hacen se omiten, D7). |

### ✨ Enchantings

Sin `@mutates`: cada método devuelve un `Color` nuevo o un escalar y deja intacto al receptor (contrato §4), así que el compilador no genera ninguna forma `get_*`. Los `ritual` son los únicos constructores.

#### `enchanting raylib.Color`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `from_hex` | ritual | `with hex as u32 into raylib.Color` | `GetColor` | `0xRRGGBBAA`, como documenta el header |
| `from_int` | ritual | `with packed as int into raylib.Color` | (inline) | inverso de `to_int`, solo-wrapper (D5) |
| `from_hsv` | ritual | `with hue as f32, saturation as f32, value as f32 into raylib.Color` | `ColorFromHSV` | hue en `[0..360]`, saturation/value en `[0..1]` |
| `from_normalized` | ritual | `with v as raylib.Vector4 into raylib.Color` | `ColorFromNormalized` | componentes en `[0..1]` |
| `is_equal` | puro | `with other as raylib.Color into bool` | `ColorIsEqual` | comparación exacta de bytes; también existe como función de módulo `is_equal` (D6) |
| `to_int` | puro | `into int` | `ColorToInt` | empaquetado `0xRRGGBBAA` |
| `to_normalized` | puro | `into raylib.Vector4` | `ColorNormalize` | componentes en `[0..1]` |
| `to_hsv` | puro | `into raylib.Vector3` | `ColorToHSV` | `x` hue `[0..360]`, `y` saturation, `z` value |
| `with_alpha` | puro | `with alpha as f32 into raylib.Color` | `ColorAlpha` | `[0..1]`; el C **no** lo acota (D9) |
| `tint_with` | puro | `with other as raylib.Color into raylib.Color` | `ColorTint` | multiplicación componente a componente |
| `brighten_by` | puro | `with factor as f32 into raylib.Color` | `ColorBrightness` | `[-1..1]` |
| `contrast_with` | puro | `with factor as f32 into raylib.Color` | `ColorContrast` | `[-1..1]` |
| `blend_over` | puro | `with other as raylib.Color, tint as raylib.Color into raylib.Color` | `ColorAlphaBlend` | `self` es la **fuente** y `other` el destino; el orden de argumentos C se invierte a propósito (ver abajo) |
| `lerp_to` | puro | `with other as raylib.Color, t as f32 into raylib.Color` | `ColorLerp` | `t` en `[0..1]` |

> `blend_over` invierte los argumentos C a propósito. `ColorAlphaBlend(dst, src, tint)` mezcla `src` **dentro de** `dst`, así que un método cuyo receptor es la fuente debe llamar `ColorAlphaBlend with other, (essence of self), tint`. Leer `front.blend_over with back, tint` como "dibuja `front` sobre `back`" es justo el objetivo del nombre; el test de la familia asegura la dirección.

### 🔧 Funciones a nivel de módulo

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `is_equal` | `with a as raylib.Color, b as raylib.Color into bool` | `ColorIsEqual` | la forma sin receptor privilegiado del método (D6) |
| `fade` | `with color as raylib.Color, alpha as f32 into raylib.Color` | `Fade` | el nombre que raylib da a `with_alpha`; se conserva porque el binding la llama `Fade` y el header documenta `alpha` como `[0..1]` |

`fade` y `Color.with_alpha` son la misma operación con dos nombres. Es deliberado y coincide con cómo `std.tally` expone `xs.sum` y `tally.sum with xs` (`PenguScriptGuideSpanish.md` §6.1), y el plan maestro registra `Fade` como propiedad de esta familia.

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** Todas las funciones envueltas son aritmética sobre cuatro bytes: sin recurso externo, sin puntero anulable, sin canal de fallo. Las dos que *sí* pueden corromper memoria (`SetPixelColor`, `GetPixelColor`) se omiten en vez de envolverse (D7).

### ✂️ Wrappers de `slice`

**Ninguno aplica.** Ninguna función de color recibe `(T* ptr, int count)`; los únicos parámetros puntero del grupo pertenecen a las dos funciones de píxel omitidas.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Las funciones que devuelven varios componentes ya devuelven un tipo de raylib: `ColorNormalize` → `Vector4`, `ColorToHSV` → `Vector3`. No hace falta tupla y no se inventa ninguna.

### 🌉 Uso de `std.ffi`

**Ninguno aplica, motivo: ni cadenas ni punteros ajenos.** Toda la familia es `Color`, `Vector3`, `Vector4`, `f32`, `int`, `u32` y `bool`. Las dos funciones con parámetro `void*` quedan fuera de alcance (D7).

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — ida y vuelta por todas las representaciones
import raylib
import raymath
import raylibx.colors as colors

weave main into int:
    var c as raylib.Color is calling Color.from_hex with 0xFF0000FF
    var packed as int is calling c.to_int
    var same as raylib.Color is calling Color.from_int with packed
    var hsv as raylib.Vector3 is calling c.to_hsv
    var back as raylib.Color is calling Color.from_hsv with hsv.x, hsv.y, hsv.z
    var unit as raylib.Vector4 is calling c.to_normalized
    var again as raylib.Color is calling Color.from_normalized with unit
    var equal as bool is calling colors.is_equal with c, same
    return 0
```

```pengu
# Ejemplo 2 — las transformaciones y la dirección del blend
import raylib
import raymath
import raylibx.colors as colors

weave main into int:
    var base as raylib.Color is calling Color.from_hex with 0x204060FF
    var faded as raylib.Color is calling base.with_alpha with 0.5
    var brighter as raylib.Color is calling base.brighten_by with 0.25
    var softer as raylib.Color is calling base.contrast_with with -0.25
    var tinted as raylib.Color is calling base.tint_with with raylib.RAYWHITE
    var mixed as raylib.Color is calling base.lerp_to with raylib.BLACK, 0.5
    var front as raylib.Color is calling Color.from_hex with 0x00FF00FF
    var over as raylib.Color is calling front.blend_over with base, raylib.RAYWHITE
    var also as raylib.Color is calling colors.fade with base, 0.5
    return 0
```

### 🧪 Plan de tests

Toda la familia es testeable en CI: sin ventana, sin GPU, sin fichero. Tres tests por entrada pública, con valores tomados de las funciones reales.

- **`from_hex`**: `0xFF0000FF` da rojo `(255, 0, 0, 255)`; `0x00000000` da negro transparente; el byte alfa cae en `a` (`0x11223344` → `(0x11, 0x22, 0x33, 0x44)`).
- **`from_int`**: `to_int` y luego `from_int` es la identidad para tres colores fijos; el orden de bytes empaquetado se asegura explícitamente. Medido en C: `GetColor(0x11223344)` da `(0x11, 0x22, 0x33, 0x44)` y `ColorToInt` lo empaqueta de vuelta a `0x11223344`, que el `from_int` en línea extrae con el mismo esquema `>> 24 / >> 16 / >> 8 / & 0xFF`.
- **`from_hsv`**: hue `0` es rojo; saturación `0` es gris (r == g == b); valor `0` es negro.
- **`from_normalized`**: `(1, 1, 1, 1)` es blanco; `(0, 0, 0, 0)` es negro transparente; `(0.5, 0.5, 0.5, 1)` es gris medio.
- **`is_equal`**: un color es igual a sí mismo; dos colores que difieren solo en alfa **no** son iguales; la función de módulo y el método coinciden en el mismo par.
- **`to_int`**: el rojo empaqueta a `0xFF0000FF`; el negro es `0x000000FF` (opaco) y el negro transparente `0x00000000`; el valor cabe en `int` con `a == 255`.
- **`to_normalized`**: el blanco es `(1, 1, 1, 1)`; el negro es `(0, 0, 0, 1)`; cada componente se queda en `[0, 1]`.
- **`to_hsv`**: el rojo puro tiene hue `0` y valor `1`; el gris tiene saturación `0`; `from_hsv` hace ida y vuelta con `to_hsv` para tres colores dentro de la cuantización de byte.
- **`with_alpha`**: `0.0` deja el color transparente; `1.0` deja `a` en `255`; los bytes RGB no se tocan.
- **`tint_with`**: tintar con blanco es la identidad; tintar con negro da `(0, 0, 0, a)`; tintar consigo mismo oscurece salvo si el color es blanco (se asegura como advertencia documentada, no como identidad).
- **`brighten_by`**: `0.0` es la identidad; `+1.0` lleva el color hacia el blanco; `-1.0` lo lleva hacia el negro.
- **`contrast_with`**: `0.0` es la identidad; un factor positivo lo aleja del gris medio; el byte alfa se conserva.
- **`blend_over`**: una fuente totalmente transparente deja el destino intacto; una fuente totalmente opaca lo reemplaza; la dirección se asegura mezclando rojo sobre azul y comprobando que el resultado es rojo (es el test que fija la inversión de argumentos de D2).
- **`lerp_to`**: `t = 0.0` es el receptor; `t = 1.0` es el objetivo; `t = 0.5` queda entre los dos en todos los canales.
- **`fade`**: coincide con `Color.with_alpha` en las mismas entradas; `alpha = 0.0` limpia el byte alfa; `alpha = 1.0` lo conserva.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `SetPixelColor` | opera sobre un destino `void*` crudo con una etiqueta `PixelFormat`; el wrapper no puede hacerlo más seguro, solo más largo (D7, contrato §9 fila 7) |
| `GetPixelColor` | igual, leyendo de un `const void*` (D7) |
| `ColorNormalize`, `ColorFromNormalized`, `ColorToHSV`, `ColorFromHSV`, `ColorTint`, `ColorBrightness`, `ColorContrast`, `ColorAlpha`, `ColorAlphaBlend`, `ColorLerp`, `ColorToInt`, `ColorIsEqual`, `Fade`, `GetColor` | **Envuelvos**, una entrada cada uno (ver las tablas de arriba); se listan aquí solo para dejar constancia de que el grupo es 14 de 16 |
| Las 26 constantes de `Color` (`RAYWHITE`, `LIGHTGRAY`, …) | no se envuelven ni se reexportan: son `const` del binding y conservan su grafía C (D10, contrato §2) |
| `ImageColorTint`, `ImageColorContrast`, `ImageColorBrightness` y el resto de mutadores `ImageColor*` | **no son de esta familia**: son métodos de `Image` y pertenecen a `raylibx_images` (plan maestro D5/D6) |

Auditoría de cobertura: de los 16 `declare` relacionados con color, **14 se envuelven** (10 métodos + 4 rituales, más las funciones de módulo `is_equal` y `fade`) y **2 se omiten** (`SetPixelColor`, `GetPixelColor`). La entrada del registro de métodos para `raylib.Color` es, por tanto: `is_equal`, `to_int`, `to_normalized`, `to_hsv`, `with_alpha`, `tint_with`, `brighten_by`, `contrast_with`, `blend_over`, `lerp_to`, y los rituales `from_hex`, `from_int`, `from_hsv`, `from_normalized`. **Ninguna otra familia puede añadir un método a `raylib.Color`.**
