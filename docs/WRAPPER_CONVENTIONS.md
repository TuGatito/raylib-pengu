# Wrapper Conventions — raylib-pengu

| Campo | Valor |
|---|---|
| Versión | `v0.1.2` |
| Fecha | 2025-10-15 |
| Estado | Aprobado |
| Ámbito | Aplica a los wrappers `raylibx`, `raymathx`, `rcamerax`, `rgesturesx`, `rlglx` |
| Referencias | `LANGUAGE_Spanish.md` (referencia del lenguaje), `PenguScriptGuideSpanish.md` (guía de estilo Pengunic), `pengu/*.d.pengu` (bindings, capa 1) |

Este documento es el contrato de diseño de la **capa 2** del proyecto. Todo `.md` de Fase 1 y todo `.pengu` de Fase 2 se miden contra él.

---

## 0. 📌 Propósito y alcance

Este documento fija las decisiones que las guías dejan abiertas para el caso concreto de raylib: cómo se nombra cada categoría de símbolo C, cuándo una función se envuelve en `maybe T`, cuándo se expone el par mutante/puro de `@mutates`, cómo se traduce un `(T* ptr, int count)` de C, y qué no se envuelve nunca. Su único objetivo es que los cinco wrappers se escriban igual sin renegociar criterio módulo a módulo.

No es un tutorial de PenguScript ni una guía de estilo. La sintaxis y la semántica son competencia exclusiva de `LANGUAGE_Spanish.md`; la nomenclatura general, la documentación `##`, los tests y los anti-patrones son competencia de `PenguScriptGuideSpanish.md`. Aquí solo se decide lo que esas dos guías no resuelven: la traducción mecánica de la surface FFI de raylib a API Pengunic.

Se decide aquí la política de nombres por categoría de símbolo C, la política de `maybe`, la política de `@mutates`, la política de `slice`, la política de `std.ffi`, la política de liberación, los criterios de skip, el método de verificación de coste cero, la plantilla del `.md` por módulo y el orden de implementación. La regla de oro que gobierna todo lo demás: **el wrapper no cubre el 100 % del binding; hace que el 20 % más usado se lea como PenguScript**.

---

## 1. 🏗️ Arquitectura de dos capas

```
pengu/
├── raylib.d.pengu          ← binding (capa 1: FFI pura, se regenera con `pengu bind`)
├── raylibx.pengu           ← wrapper (capa 2: Pengunic, escrito a mano)
├── raymath.d.pengu
├── raymathx.pengu
├── rcamera.d.pengu
├── rcamerax.pengu
├── rgestures.d.pengu
├── rgesturesx.pengu
├── rlgl.d.pengu
└── rlglx.pengu
```

| Regla | Detalle |
|---|---|
| El binding no se toca | `*.d.pengu` es 1 a 1 con el header C. Se regenera con `pengu bind`, nunca se edita a mano. |
| El wrapper no duplica tipos | Ningún `rune`/`omen`/`alias` se redeclara en la capa 2. Los tipos vienen de `import raymath`, `import raylib`, etc. |
| El wrapper siempre importa el binding | `raymathx.pengu` empieza por `import raymath`. |
| El wrapper no tiene directivas de binding | Prohibidos `include`, `link`, `insignia`, `declare` y `antiquus` en la capa 2. |
| El wrapper se importa solo | El usuario escribe `import raymathx` junto al binding: los dos imports son explícitos (`import raylib` + `import raylibx`). No se asume reexport transitivo. |
| Los ejemplos usan nombres cualificados | `raylib.Vector2` para el tipo, `raylibx.load_texture` para el wrapper. Nunca `Vector2` desnudo ni `load_texture` sin módulo. |
| `enchanting` sobre el nombre cualificado | El objetivo del bloque es `enchanting raylib.Vector2:`, nunca `enchanting Vector2:`. El tipo `Vector2` lo declara `raylib.d.pengu` (ver §4). |
| **Alias de tipo: `ritual` y nombres duplicados** | Un `alias` comparte la tabla de métodos del tipo subyacente. Consecuencias verificadas con `pengu 2.4.0`: (a) un `ritual` declarado dentro de `enchanting raylib.Quaternion:` **no es alcanzable** (`calling Quaternion.<ritual>` da `E0004`), porque `Quaternion` es `alias Quaternion as Vector4`; los constructores de quaternion van a nivel de módulo; (b) el **mismo nombre de método en dos bloques del alias** emite el símbolo C dos veces y rompe el build de C (`gcc: redefinition of 'Vector4_add'`), y `pengu check` **no** lo detecta porque cada bloque es válido por separado. Regla: un nombre, un solo bloque. |
| **Excepción de invocación `ritual`** | La llamada a un `ritual` usa el nombre **desnudo** del tipo: `calling Vector2.new with …`, no `calling raylib.Vector2.new with …`. La forma de tres segmentos es `E0004` (verificado con `pengu 2.4.0`: `Type 'raylib' has no method 'new'`). Cualificar es obligatorio en el objetivo del `enchanting` (`enchanting raylib.Vector2:`) y en las anotaciones de tipo (`var v as raylib.Vector2`), y prohibido en la invocación del `ritual`. |
| Ausencia de `declare` = binding incompleto | Si el wrapper parece necesitar un `declare`, hay que regenerar el binding, no añadirlo. |

**Corolario verificable.** `pengu check` sobre cualquier `*.pengu` de la capa 2 no debe reportar `E0004` por símbolos de raylib. Si lo hace, falta una declaración en el `.d.pengu`. En particular, `Vector2`, `Vector3`, `Vector4`, `Quaternion` y `Matrix` los declara `raylib.d.pengu`, así que el objetivo correcto en `raymathx.pengu` es `enchanting raylib.Vector2:` aunque el método envuelva una función de `raymath` (ver `pengu/raymath.d.pengu:15`).

---

## 2. 📛 Convenciones de nombres (C → Pengunic)

Tabla por **categoría de símbolo C**. La enumeración símbolo a símbolo es Fase 1. Las reglas generales de nomenclatura vienen de `PenguScriptGuideSpanish.md` §2 y no se repiten aquí.

| Categoría C | Patrón C | Patrón Pengunic | Ejemplo C → Pengu |
|---|---|---|---|
| Constructor de valor | `Gen*`, `New*` que devuelven por valor | `ritual new` o `ritual from_*` | `GenMeshCube` → `Mesh.from_cube` |
| Carga con fallo | `Load*` emparejado con `Is*Valid` | función de módulo `load_*`, `maybe T` | `LoadTexture` → `raylibx.load_texture` (ver §3) |
| Predicado de estado global | `Is*`, `WindowShouldClose` | función de módulo `is_*` / nombre del hecho | `IsWindowMinimized` → `is_window_minimized` |
| Predicado sobre una instancia | `Is*Valid` con el tipo como primer parámetro | método `is_valid` | `IsTextureValid` → `tex.is_valid` |
| Colisión / pertenencia | `CheckCollision*` | método `overlaps` / `contains_*` / `intersects` | `CheckCollisionRecs` → `r.overlaps with other` |
| Conversión de valor | `XxxToYyy`, `Color*` | método `to_yyy` | `ColorToInt` → `c.to_int` |
| Conversión con fallo | `*FindIndex`, `*ToInteger` de texto | `parse_*` / `find_*` → `maybe T` | `TextFindIndex` → `maybe int` |
| Getter de campo de struct | `Get*` que devuelve el tipo tal cual | acceso directo al campo, sin wrapper | `texture.width` (ya es campo) |
| Consulta de estado global | `Get*` sin argumentos | función de módulo en `snake_case` | `GetScreenWidth` → `screen_width` |
| Mutador in-place | función cuyo primer parámetro es `ref to T` | método ordinario que muta vía `self` | `CameraMoveForward` → `cam.move_forward with …` |
| Par mutante/puro | función pura que devuelve el tipo del receptor | `@mutates weave <nombre>` + `get_<nombre>` | `Vector2Normalize` → `v.normalize` / `v.get_normalize` |
| Acción sin retorno | `Draw*`, `Set*` | verbo transitivo | `DrawRectangle` → `rect.draw` |
| Liberación | `Unload*` | no se envuelve nunca | `UnloadTexture` → `defer calling raylib.UnloadTexture with tex` |
| Recuento | `Get*Count` | función de módulo sustantivo | `GetTouchPointCount` → `touch_count` |
| Búsqueda | `Find*`, `Search*` | `find_*` → `maybe T` | ver §3 |
| Formateador | `TextFormat` y similares | `format_*` / `describe_*` | `TextFormat` → `format_text` |
| Exportación con éxito/fallo | `Export*` que devuelven `bool` | `export_*` → `result of void to ExportError` | ver §3 |

### Reglas cerradas (todas las categorías)

| Regla | Ejemplo |
|---|---|
| Prohibido el gerundio en `-ing` | `loading_texture` mal; `load_texture` bien (`PenguScriptGuideSpanish.md` §2.3) |
| Prohibidos los prefijos húngaros | `str_path` mal; `path` bien |
| Prohibido `create`/`make`/`build`/`init` como constructor | `Color.make` mal; `ritual new` bien |
| Prohibida la redundancia tipo-hablante | `texture_get_texture_width` mal; `texture.width` bien |
| Nombres de 1–2 letras solo para índices cortos | `i`, `j`, `k` bien; `tx` para "texture" mal |
| Un método no repite el nombre del tipo | `Texture.load_texture` para un `ritual` del tipo `Texture` bien; `texture.width` bien |
| Un acceso a campo directo no se envuelve | `tex.width` no genera método; envolverlo es violación de skip (§9) |
| Prefijo `_` = privado del módulo | Los helpers internos del wrapper van en `_snake_case` (`E0043`) |

### Constantes y variantes de `omen`

| Origen C | Forma Pengunic | Ejemplo |
|---|---|---|
| `#define RAYWHITE ((Color){...})` | `const SCREAMING_SNAKE_CASE` con el nombre C intacto | `raylib.RAYWHITE` |
| `Color` literal exportado por raylib | `const` de módulo con el nombre C | `raylib.LIGHTGRAY`, `raylib.DARKGRAY`, `raylib.BLANK` |
| `enum ConfigFlags { FLAG_VSYNC_HINT = 64, … }` | variante de `omen` con el nombre C | `raylib.ConfigFlags.FLAG_VSYNC_HINT`, o `raylib.FLAG_VSYNC_HINT` |
| `enum KeyboardKey { KEY_A = 65, … }` | variante de `omen` con el nombre C | `raylib.KEY_A` |
| `enum Gesture { GESTURE_TAP = 1, … }` | variante de `omen` con el nombre C | `raylib.GESTURE_TAP` |

**Decisión cerrada:** los `RAYWHITE`/`LIGHTGRAY`/`COLOR_*` y toda variante de `omen` **conservan su nombre C en `SCREAMING_SNAKE_CASE`**. Renombrarlos rompería la correspondencia con la documentación de raylib, que es la referencia que el usuario consulta. No se envuelven ni se re-exportan: se usan cualificados (`raylib.RAYWHITE`) o sin cualificar, como admite `LANGUAGE_Spanish.md` §14.2.

**Prohibición derivada:** el wrapper no declara constantes nuevas con nombres en minúscula para duplicar una constante C (`const white as Color is raylib.RAYWHITE` queda prohibido).

---

## 2.5 🌐 Política de idioma

| Artefacto | Idioma | Razón |
|---|---|---|
| Nombres de símbolos (`weave`, `rune`, campos, parámetros) | Inglés | `PenguScriptGuideSpanish.md` §2 |
| Docstrings `##` en `.pengu` | **Inglés** | Coincide con la convención del lenguaje y con los hovers del LSP, que mezclan símbolos C (en inglés) y descripciones |
| Comentarios `#` internos y de sección | Libre | No se impone; el mantenedor elige |
| Mensajes de `panic` y errores de runtime | Inglés | Coincide con el runtime de PenguScript |
| Nombres de `test "..."` | Inglés | Coincide con el patrón de `tests/std_programs/` del repo |
| `docs/WRAPPER_CONVENTIONS.md` | Español | Documento de trabajo interno del equipo |
| `docs/plans/<modulex>.md` | **Bilingüe (EN canónico + ES traducción)** | El inglés es canónico; el español es no normativo y se sincroniza sección a sección (§14) |
| Mensajes de diagnóstico y comentarios del C generado | (los emite el compilador) | No aplica |

**Regla dura:** todo `##` de un método público va en inglés. Todo bloque `## Ejemplo` con ` ```pengu ` dentro de un `##` va en inglés también. La documentación de módulo (`## <modulex>.pengu` al inicio) va en inglés. No hay excepciones.

---

## 3. 🎁 Política `maybe T` (wrappers de carga y fallo)

**Regla general:** toda función C que falla por un **recurso externo** (fichero ausente, driver, memoria del sistema de la GPU, dispositivo de audio) se envuelve en `maybe T`. Toda función que solo puede fallar por OOM del runtime no se envuelve: el runtime aborta con `[PENGU] out of memory`.

| Se envuelve en `maybe T` | Motivo | C backing real | Predicado de éxito |
|---|---|---|---|
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadTexture` | `call raylib.IsTextureValid with tex` |
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadFont`, `LoadFontEx`, `LoadFontFromMemory`, `LoadFontFromImage` | `raylib.IsFontValid` |
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadImage`, `LoadImageRaw`, `LoadImageAnim`, `LoadImageAnimFromMemory`, `LoadImageFromMemory`, `LoadImageFromTexture`, `LoadImageFromScreen` | `raylib.IsImageValid` |
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadSound`, `LoadSoundFromWave`, `LoadSoundAlias` | `raylib.IsSoundValid` |
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadMusicStream`, `LoadMusicStreamFromMemory` | `raylib.IsMusicValid` |
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadModel`, `LoadModelFromMesh`, `LoadRenderTexture`, `LoadRenderTextureEx`, `LoadAudioStream` | `raylib.IsModelValid`, `IsRenderTextureValid`, `IsAudioStreamValid` |
| `Load*` con `Is*Valid` hermano | recurso externo | `LoadShader`, `LoadShaderFromMemory` | `raylib.IsShaderValid` |
| `Load*` que devuelve puntero o `char*` | puede ser `NULL` | `LoadFileData` → `maybe slice of byte`; `LoadFileText` → `maybe string` | `call ffi.is_null with …` |
| `Load*` con `out count` | `count == 0` = nada que cargar | `LoadCodepoints`, `LoadImagePalette`, `LoadFontData`, `LoadImageAnim` | comparar el out-param |
| `Export*` y `Save*` que devuelven `bool` | E/S de fichero | `ExportImage`, `ExportImageAsCode`, `ExportImageToMemory`, `ExportFontAsCode`, `ExportMesh`, `ExportMeshAsCode`, `ExportDataAsCode`, `ExportAutomationEventList`, `ExportWave`, `ExportWaveAsCode`, `SaveFileData`, `SaveFileText` | el propio `bool` |
| `CompressData` / `DecompressData` / `EncodeDataBase64` / `DecodeDataBase64` | devuelven puntero con `out size` | `maybe slice of byte` / `maybe string` | puntero no nulo |
| `ComputeCRC32` / `ComputeMD5` / `ComputeSHA1` / `ComputeSHA256` | devuelven hash; los tres últimos con `ref to u32` | nunca envuelven en `maybe`: el algoritmo no falla | no aplica |

**Variantes de `Load*` con out-param.** Cuando el binding declara un `ref to int` de recuento, hay tres sub-formas y cada una tiene su criterio.

| Sub-forma | Funciones reales | Wrapper |
|---|---|---|
| El out-param es la longitud y el puntero es el array | `LoadImageColors`, `LoadImagePalette`, `LoadWaveSamples` | `maybe slice of T` (el `count` se pliega en `.length`; si el recuento es 0, `maybe none`) |
| El puntero y el out-param son un par carga/recuento | `LoadFileData`, `LoadCodepoints`, `LoadTextLines`, `LoadMaterials`, `LoadModelAnimations`, `LoadFontData`, `LoadImageAnim`, `LoadImageAnimFromMemory` | `maybe slice of T` (o `maybe string`) más un `load_*_counted` que devuelve la longitud cuando el wrapper no quiera copiar |
| El out-param es una longitud y el primer parámetro es una entrada | `LoadFontEx`, `LoadFontFromMemory` (§5) | el wrapper acepta `slice of int` y usa `codepoints.length` |

### Casos que no se envuelven

| NO se envuelve | Motivo |
|---|---|
| `Vector2Add`, `MatrixMultiply`, toda la matemática pura por valor | nunca falla; devuelve struct |
| `GetScreenWidth`, `GetMonitorCount`, `touch_count` | getter trivial, no puede fallar (`LANGUAGE_Spanish.md` §12, decisión D5) |
| `GenImageColor`, `GenMeshCube`, `GenMeshSphere` | constructor por valor; la generación no toca el disco |
| `MemAlloc`, `MemRealloc`, `list`/`map` de PenguScript | solo OOM; el runtime aborta |
| `InitWindow`, `SetConfigFlags`, `CloseWindow` | efecto global sin canal de fallo (ver §9) |
| `IsKeyDown`, `IsMouseButtonPressed`, `IsGestureDetected` | ya devuelven `bool`; el predicado **es** el valor |

**Forma canónica del wrapper de carga.** Se declara un `weave` de módulo cuando el destino no tiene un tipo natural como receptor, y un `ritual` cuando sí lo tiene. El predicado se consulta **siempre** contra el binding, nunca se reimplementa:

```pengu
## Loads a texture from disk.
##
## ## Returns
## `some` with the loaded texture, or `maybe none` if raylib rejects it.
##
## ## Memory
## The texture owns raylib memory. Release it with
## `defer calling raylib.UnloadTexture with tex`.
weave load_texture with path as string into maybe raylib.Texture2D:
    let c_path as ref to frozen char is calling ffi.cstr_from_string with path
    var tex as raylib.Texture2D is calling raylib.LoadTexture with c_path
    if calling raylib.IsTextureValid with tex:
        return some tex
    return maybe none
```

**Prohibiciones:** no se inventa un predicado propio, no se devuelve un `bool` de éxito donde corresponde un `maybe` (`PenguScriptGuideSpanish.md` §14.8), y no se devuelve un struct "inválido" en lugar de `maybe none`.

---

## 4. 🔄 Política `@mutates` (par mutante/puro)

**Regla general:** un método de `enchanting T:` cuyo valor de retorno es **el propio tipo del receptor** y cuya operación transforma el receptor se declara `@mutates weave <nombre> into T:`. El compilador genera la forma pura `get_<nombre>` de manera automática; **no se declara a mano**.

| Hecho verificado | Consecuencia |
|---|---|
| `@mutates` requiere bloque `enchanting`, retorno del tipo del receptor y cuerpo puro | si no se cumple, `E0067` (`LANGUAGE_Spanish.md` §10.1) |
| Declarar `weave get_<nombre>` junto a `@mutates weave <nombre>` | `E0068`; la escritura `get_` está reservada para la forma pura |
| Usar el nombre mutante donde se espera un valor | `E0066`; ahí va `get_<nombre>` |
| El receptor debe ser escribible | `calling let_v.normalize` es `E0006` |
| El cuerpo no puede asignar al receptor | `set self` es `E0006`; `self->field` dentro del cuerpo es `E0003` |
| Un nombre mutante no participa en cadenas | es una sentencia; los `get_*` sí encadenan (`PenguScriptGuideSpanish.md` §14.15, §16.5) |

### Cuándo sí: operación pura de C expuesta como mutación del receptor

En raymath **ninguna** de estas funciones muta en C: todas toman el vector por valor y devuelven uno nuevo (`RMAPI Vector2 Vector2Normalize(Vector2 v)`). El wrapper, aun así, las expone como par mutante/puro porque el algoritmo es conceptualmente in-place y el coste es cero (§10).

```pengu
import raylib
import raymath

enchanting raylib.Vector2:
    @mutates
    weave normalize into raylib.Vector2:
        return calling raymath.Vector2Normalize with (essence of self)

    @mutates
    weave add with other as raylib.Vector2 into raylib.Vector2:
        return calling raymath.Vector2Add with (essence of self), other
```

Uso en el sitio de llamada, ya verificado con `pengu expand`:

```pengu
calling v.normalize                                       # v = Vector2Normalize(v)
calling v.add with (calling Vector2.new with 1.0, 1.0)
var u as raylib.Vector2 is calling v.get_normalize        # forma pura
```

### Cuándo no: la operación C es pura por naturaleza

`Vector2Length`, `Vector2DotProduct`, `Vector2Distance`, `Vector2Angle`, `Vector2Rotate`, `Vector2Lerp`, `Vector2Transform`, `Vector2Reflect`, `Vector2Refract`, `Vector2Min`, `Vector2Max`, `Vector2Clamp` **no** llevan `@mutates`. Devuelven un valor escalar (consulta) o un valor derivado que no es "el receptor transformado en su sitio" (`PenguScriptGuideSpanish.md` §6.7: los predicados y las conversiones no participan del desdoblamiento).

| Forma | Cuándo | Ejemplo |
|---|---|---|
| `@mutates weave <nombre> into T` | el resultado se asigna de vuelta al receptor | `v.normalize`, `q.normalize`, `m.transpose` |
| `weave <nombre> into T` sin `@mutates` | el resultado es un valor nuevo e independiente | `v.rotate with 1.57`, `v.lerp with other, 0.5` |
| `weave <nombre> into <escalar>` | consulta | `v.length`, `v.dot with other`, `v.distance_to with other` |
| `weave <nombre> into void` con receptor `ref to T` | mutación real a través de un puntero | `cam.move_forward with 1.0, true` (ver abajo) |

### Mutación real por puntero: `ref to T` sin `@mutates`

Cuando el C recibe un `ref to T` y escribe a través de él, el receptor ya es una referencia: se escribe un `weave … into void` ordinario y se pasa `self` tal cual. Es el caso de las 12 funciones de `rcamera.d.pengu`:

```pengu
import raylib
import rcamera

enchanting raylib.Camera3D:
    weave move_forward with distance as f32, in_plane as bool into void:
        calling rcamera.CameraMoveForward with self, distance, in_plane

    weave yaw with angle as f32, around_target as bool into void:
        calling rcamera.CameraYaw with self, angle, around_target

    weave forward into raylib.Vector3:
        return calling rcamera.GetCameraForward with self
```

`@mutates` no aplica aquí porque el retorno es `void`, no el tipo del receptor. Forzarlo es `E0067`.

---

## 5. ✂️ Política de `slice` (funciones C con `(T* ptr, int count)`)

**Regla general:** toda función C cuya firma sea `(T* ptr, int count)` —o `(const T* arr, int n)`— y que trate el puntero como array de `count` elementos se envuelve aceptando `slice of T`. El wrapper toma la longitud de `pts.length` y obtiene el puntero desde el primer elemento.

### Patrón canónico (verificado con `pengu expand`)

```pengu
import raylib

weave draw_triangle_fan with pts as slice of raylib.Vector2, color as raylib.Color into void:
    if (pts.length) == 0:
        return
    let raw as ref to frozen raylib.Vector2 is transmute (sigil of (pts at 0)) to ref to frozen raylib.Vector2
    calling raylib.DrawTriangleFan with raw, (pts.length), color
```

- `essence of pts` **no compila** sobre un `slice` (`E0008`: `'essence of' requires reference type (ref to T)`). La forma válida es `sigil of (pts at 0)`.
- La guarda de longitud vacía es obligatoria: `pts at 0` sobre un slice vacío dispara el chequeo de límites en runtime.
- El `transmute` emite `W0001` (`LANGUAGE_Spanish.md` §6.4). Es el único caso, junto con `ref to T` → `ref to frozen T` (§7), en que se tolera.

### Familias reales que caen en este patrón

| Familia | Firmas exactas del binding | Receptor natural |
|---|---|---|
| `DrawLineStrip` | `points as ref to frozen Vector2, pointCount as int, color as Color` | módulo |
| `DrawTriangleFan` | `points as ref to frozen Vector2, pointCount as int, color as Color` | módulo |
| `DrawTriangleStrip` | `points as ref to frozen Vector2, pointCount as int, color as Color` | módulo |
| `DrawSplineLinear` / `Basis` / `CatmullRom` / `BezierQuadratic` / `BezierCubic` | `points as ref to frozen Vector2, pointCount as int, thick as f32, color as Color` | módulo |
| `DrawTriangleStrip3D` | `points as ref to frozen Vector3, pointCount as int, color as Color` | módulo |
| `CheckCollisionPointPoly` | `point as Vector2, points as ref to frozen Vector2, pointCount as int` | módulo (el polígono es el sujeto) |
| `ImageDrawLineStrip` / `ImageDrawTriangleFan` / `ImageDrawTriangleStrip` | `dst as ref to Image, points as ref to frozen Vector2, pointCount as int, color as Color` | `Image` |
| `DrawTextCodepoints` / `MeasureTextCodepoints` | `font as Font, codepoints as ref to frozen int, codepointCount as int, …` | `Font` |
| `LoadFontEx` / `LoadFontFromMemory` | `… codepoints as ref to frozen int, codepointCount as int` | `Font` (carga, §3) |
| `LoadUTF8` | `codepoints as ref to frozen int, length as int` | módulo → `string` |
| `GenImageFontAtlas` | `glyphs as ref to frozen GlyphInfo, glyphRecs as ref to ref to Rectangle, glyphCount as int, …` | módulo |
| `LoadDirectoryFiles` / `LoadDirectoryFilesEx` / `LoadDroppedFiles` | devuelven `FilePathList` (`count` + `paths as ref to ref to char`) | módulo → `list of string` |
| `DrawMeshInstanced` | `transforms as ref to frozen Matrix, instances as int` | módulo |
| `ImageKernelConvolution` | `kernel as ref to frozen f32, kernelSize as int` | `Image` |
| `rlSetUniformMatrices` | `mat as ref to frozen Matrix, count as int` | `rlgl` (ver §9: probablemente no se envuelve) |
| `TextJoin` | `textList as ref to ref to char, count as int` | módulo (el `count` es la longitud) |

**Criterio de aplicación mecánica:** si el binding declara dos parámetros contiguos `<nombre> as ref to [frozen] T` (o `ref to ref to char`) y `<otro> as int` donde el segundo es un recuento del primero, se aplica esta política. Si el segundo entero no es un recuento sino una `position`, `size` o `stride`, **no** aplica.

**Degradación honesta:** cuando el array está aplanado a un escalar en el binding (`float3`, `float16` en `raymath.d.pengu`; `GestureEvent.pointId`/`position`) no hay slice posible y la función no se envuelve: se reporta como defecto de binding, no se parchea en la capa 2.

---

## 6. 📦 Política de retornos múltiples `(T, U)`

**No aplica en este proyecto.** Ningún `declare` de los cinco bindings devuelve una tupla (verificado: cero coincidencias de `into (` en `pengu/*.d.pengu`).

El motivo es estructural, no una omisión: en raylib los "dos valores" siempre toman una de estas cuatro formas, y todas tienen ya un destino normativo mejor que la tupla.

| Patrón C real | Lo que devuelve el binding | Política |
|---|---|---|
| `Vector2 GetWindowPosition(void)` | un `rune` (`Vector2`) | struct completo, sin tupla |
| `unsigned char *LoadFileData(const char *fileName, int *dataSize)` | puntero + out-param `ref to int` | `maybe slice of byte` (§3): el `count` se pliega en `.length` |
| `bool SaveFileData(...)` | `bool` suelto | `result of void to ExportError` (§3) |
| `int TextFindIndex(const char *text, const char *search)` | `int` con `-1` como fallo | `maybe int` (§3) |

**Criterio para el raro caso futuro:** se admite tupla solo si los dos valores se desestructuran en la misma sentencia, ninguno de ellos es un indicador de éxito y ninguno es un out-param. Si aparecen esas condiciones, se marca `(revisable en Fase 1)`. Los nombres de los componentes siguen `PenguScriptGuideSpanish.md` §17.2 y la desestructuración es la de §17.3.

---

## 7. 🌉 Política de `std.ffi`

**Regla dura:** `std.ffi` se usa **solo** en la capa 2. Los bindings `.d.pengu` son 1 a 1 con C y no contienen ninguna llamada a `ffi.*` (verificado). El wrapper es quien traduce.

| Necesitas | Usa | ¿Asigna? | Limpieza |
|---|---|---|---|
| `string` → `ref to char` para C | `ffi.cstr_from_string` | no (vista) | ninguna; válida mientras el `string` viva |
| `char*` de C → `string` | `ffi.string_from_cstr` | sí | `banish` |
| `ref to char` de C → `string` con longitud | `ffi.string_from_cstr_n` | sí | `banish` |
| `ref to byte` + count → `string` | `ffi.string_from_bytes` | sí | `banish` |
| puntero + longitud → `slice of T` | `ffi.slice_from_ptr of T` | no | ninguna |
| puntero + longitud → `slice of byte` | `ffi.slice_of_bytes_from_ptr` | no | ninguna |
| puntero nulo / no nulo | `ffi.is_null`, `ffi.is_valid`, `ffi.null_void`, `ffi.null_char` | no | ninguna |
| puntero + count → `list of T` copiada | `ffi.list_from_ptr of T` | sí | `banish` (y `pengu_banish_string_list` si es `list of string`) |
| `slice of T` → puntero C | `transmute (sigil of (pts at 0)) to ref to frozen T` | no | ninguna |
| `ref to T` → `ref to frozen T` | `transmute` | no | ninguna |
| `ref to T` → `ref to void` | `transmute p to ref to void` | no | ninguna |
| tamaño de `T` en compile-time | `ffi.size_of of T`, `ffi.alignment_of of T` | no | ninguna |

### Advertencia obligatoria sobre `transmute`

Cada `transmute` emite `[W0001] UnsafeTransmuteWarning` (`LANGUAGE_Spanish.md` §6.4 y §22). Un wrapper que abusa de `transmute` deja el log de compilación sucio y oculta las advertencias que sí importan.

**Confinamiento:** `transmute` se permite únicamente en dos situaciones y en ningún otro lugar.

1. `slice of T` → `ref to frozen T` dentro de un wrapper de slice (§5).
2. `ref to T` → `ref to frozen T` cuando el binding declara `ref to frozen T` y el valor local es `ref to T` (`std.ffi` no ofrece esta conversión).

`ref to T` → `ref to void` **no** cuenta como abuso: es la conversión comodín admitida por `LANGUAGE_Spanish.md` §13.2 y el chequeador la acepta como asignación directa en muchos casos. Aun así, se prefiere la conversión implícita cuando compila.

**Regla de oro:** cada uso de `std.ffi` debe estar justificado por una función C que cruza la frontera. Si no hay frontera, no hay `ffi`.

### Frontera de cadenas

Las funciones C que reciben `ref to frozen char` **no** aceptan un valor `string` por conversión implícita: solo los literales de cadena decaen automáticamente. Verificado: `calling raylib.LoadTexture with path` da `E0005` cuando `path as string`; `calling raylib.LoadTexture with "a.png"` compila.

Por tanto el wrapper que recibe `string` y lo pasa a C **siempre** interpone `ffi.cstr_from_string`:

```pengu
let c_path as ref to frozen char is calling ffi.cstr_from_string with path
```

El `ref to char` que devuelve `cstr_from_string` fluye a `ref to frozen char` sin `transmute` (`LANGUAGE_Spanish.md` §13.2, fila `ref to char` → `ref to frozen char`).

---

## 8. 🧹 Política de liberación de memoria

**Raylib no usa `banish`.** Todo recurso que raylib asigna con su propio asignador interno se libera con su propio `Unload*` (`PenguScriptGuideSpanish.md` §8.5 y §9.5). `banish` queda reservado a la memoria del runtime de PenguScript.

| Recurso | Limpieza en el sitio de uso |
|---|---|
| `Texture2D` | `defer calling raylib.UnloadTexture with tex` |
| `RenderTexture2D` | `defer calling raylib.UnloadRenderTexture with rt` |
| `Image` | `defer calling raylib.UnloadImage with img` |
| `Font` | `defer calling raylib.UnloadFont with f` |
| `Sound` | `defer calling raylib.UnloadSound with s` |
| `Music` | `defer calling raylib.UnloadMusicStream with m` |
| `Wave` | `defer calling raylib.UnloadWave with w` |
| `Model` | `defer calling raylib.UnloadModel with m` |
| `Shader` | `defer calling raylib.UnloadShader with s` |
| `Mesh` | `defer calling raylib.UnloadMesh with m` |
| `Material` | `defer calling raylib.UnloadMaterial with m` |
| `AudioStream` / `Sound` alias / `VrStereoConfig` | `UnloadAudioStream` / `UnloadSoundAlias` / `UnloadVrStereoConfig` |
| `AutomationEventList` | `defer calling raylib.UnloadAutomationEventList with l` |
| `FilePathList` | `UnloadDirectoryFiles` (o `UnloadDroppedFiles`) |
| `ModelAnimation` | `UnloadModelAnimations with anims, count` |
| `ref to Color` de `LoadImageColors` / `LoadImagePalette` | `UnloadImageColors` / `UnloadImagePalette` |
| `ref to GlyphInfo` de `LoadFontData` | `UnloadFontData with glyphs, count` |
| `ref to int` de `LoadCodepoints` / `LoadRandomSequence` | `UnloadCodepoints` / `UnloadRandomSequence` |
| `ref to f32` de `LoadWaveSamples` | `UnloadWaveSamples with samples` |
| `ref to byte` / `ref to char` de `LoadFileData` / `LoadFileText` / `LoadUTF8` | `UnloadFileData` / `UnloadFileText` / `UnloadUTF8` |
| `ref to ref to char` de `LoadTextLines` | `UnloadTextLines with lines, count` |
| `ref to void` de `MemAlloc` / `MemRealloc` | `defer calling raylib.MemFree with ptr` |
| `string` nuevo (interpolación, `ffi.string_from_cstr`), `list`, `map` | `banish` / `defer banish` |
| `slice of T` | nada: es una vista y `banish` lo rechaza con `E0008` |
| `ref to T` que apunta a memoria de raylib | el `Unload*` del recurso dueño, nunca `banish` |
| `ref to char` de `GetClipboardText` / `GetMonitorName` | nada: raylib las gestiona internamente |

**Regla dura:** el wrapper **nunca** envuelve `Unload*` como método del tipo. El `defer` en el sitio de uso es más claro y más flexible, y permite liberar antes de que el valor salga de ámbito.

**Decisión sobre `Nexus` y prohibición derivada.** No se declara `bind` de ningún tipo raylib a un concept `Nexus` en el primer pase: permitir `banish tex` como destructor natural introduce magia en un tipo que ya tiene una rutina de limpieza nombrada por raylib y documentada en el header, y `banish tex` sobre un `Texture2D` compila (el struct no es `Nexus`) y filtra o corrompe. Cero `banish` sobre handles de raylib. `(revisable en Fase 1 si aparece un caso de uso real.)`

---

## 9. 🚫 Criterios de skip (cuándo NO envolver)

Sin esta sección, cada `.md` de Fase 1 se llena de métodos redundantes. **El wrapper no cubre el 100 % del binding.**

| Nº | No envolver | Ejemplo real | Motivo |
|---|---|---|---|
| 1 | Lo que ya es idiomático | `GetScreenWidth`, `GetMonitorCount`, `GetTouchPointCount` | el binding ya es una llamada clara; envolver solo añade un salto |
| 2 | Lo superseded por un método del wrapper | `raylib.Vector2Add` si `Vector2.add` ya existe como par `@mutates` | duplicar la superficie multiplica los caminos de revisión |
| 3 | Accesos a campo directo | `tex.width`, `img.height`, `cam.fovy` | el campo ya es público y se lee sin función |
| 4 | Los `Unload*` | `UnloadTexture`, `UnloadFont`, `UnloadRenderTexture` | la política es `defer calling raylib.Unload*` (§8) |
| 5 | Variádicos crudos de C | `TraceLog` (`text as ref to frozen char, ...`), `TextFormat` (`...`) | PenguScript no puede construir la lista variádica; se expone una versión tipada (`format_text`) o el binding directo |
| 6 | Callbacks de C con `va_list` o punteros a función sin contexto | `SetTraceLogCallback`, `SetLoadFileDataCallback`, `SetLoadFileTextCallback` | no hay closures en PenguScript; el binding ya es la interfaz correcta |
| 7 | Punteros opacos que el usuario nunca manipula | `ref to rAudioBuffer`, `ref to rAudioProcessor` | el binding ya es la abstracción correcta |
| 8 | Configuración global de un solo uso | `SetConfigFlags`, `SetTraceLogLevel`, `InitWindow`, `CloseWindow` | se llama una vez; envolver no reduce tokens |
| 9 | Toda la capa OpenGL cruda de `rlgl` | `rlBegin`, `rlVertex2f`, `rlLoadTexture`, `rlPushMatrix`, `rlDrawVertexArray` | `rlglx` puede concluir "no envolver casi nada; usar el binding directo", y esa conclusión es un entregable válido |
| 10 | Funciones de automatización y VR de bajo uso | `LoadAutomationEventList`, `SetAutomationEventBaseFrame`, `SetVrStereoConfig` | fuera del 20 % más usado |
| 11 | Geometría de mallas generada | `GenMeshCube`, `GenMeshSphere`, `GenMeshPlane` | ya devuelven un valor puro; a lo sumo un `ritual from_*` en el tipo, nunca un método con otro nombre |
| 12 | Funciones de formato de archivo con `Memory`/`Raw` duplicadas | `LoadImageRaw` frente a `LoadImage` | el wrapper expone la variante común; la cruda queda en el binding |
| 13 | Predicados de igualdad | `ColorIsEqual`, `TextIsEqual` | el binding devuelve `bool` y el operador `==` no existe para estos tipos; envolver no los hace más cortos |

**Criterio de decisión (aplicable mecánicamente en cada `.md`):** una función se envuelve solo si concurren las tres condiciones.

1. Reduce el número de tokens de un ejemplo real de uso.
2. Existe un receptor natural en el dominio (un tipo de raylib) **o** renombra un `Get*`/`Check*` con un verbo/sustantivo Pengunic.
3. No está en la tabla de arriba.

Si falta cualquiera de las tres, la función va a la sección "NO se envuelve" del `.md` con su motivo.

---

## 10. ⚡ Coste cero (verificación)

Todo `enchanting` debe monomorfizar a una llamada C directa. **Definition of Done:** un wrapper que introduce una copia es un bug de diseño y se reescribe.

### Método de verificación (obligatorio en Fase 2)

1. Escribir un programa mínimo que use el método.
2. `pengu expand programa.pengu -o bundle.c`.
3. Inspeccionar el `bundle.c` generado.
4. Comparar con la llamada directa a la función C.

### Patrón esperado frente a patrón prohibido

```c
/* Correcto: la forma mutante asigna el retorno al receptor */
v = Vector2_add(&v, other);

/* Correcto: la forma pura es la misma función, sin asignación */
Vector2 w = Vector2_add(&v, other);

/* Prohibido: el wrapper introduce un temporal y copia */
Vector2 _tmp = v;
_tmp = Vector2Normalize(_tmp);
memcpy(&v, &_tmp, sizeof(Vector2));
```

**Verificado en este repositorio** con `pengu 2.4.0` sobre un wrapper de `raymath.Vector2`: el cuerpo `return calling raymath.Vector2Add with (essence of self), other` emite `Vector2 _ret_1 = Vector2Add((*self), other); return _ret_1;`, y el sitio de llamada baja a `v = Vector2_add(&v, (Vector2_new(1.0f, 1.0f)));` para la forma mutante y `Vector2 w = Vector2_add(&v, …);` para la pura.

No hay estructura temporal ni `memcpy`: `@mutates` baja a una asignación del retorno y la forma pura a la misma llamada sin asignación. Se comprueba en Fase 1 con el procedimiento de arriba.

### Costes que sí se aceptan

| Coste | Dónde | Por qué se acepta |
|---|---|---|
| `transmute` → `W0001` | wrappers de `slice` (§5) y de `ref to T` → `ref to frozen T` (§7) | no existe alternativa segura en el lenguaje |
| Chequeo de límites en `pts at 0`, `ffi.cstr_from_string` | wrappers de `slice` y wrappers que reciben `string` y llaman a C | el slice es una vista sobre memoria ajena; sin la conversión hay `E0005` |
| `pengu_frame_push`/`pop` por llamada | todo `weave` no inline | es del runtime, no del wrapper; se elimina con `weave inline` si el perfil lo justifica |

---

## 11. 📝 Documentación `##` (obligatoria en cada método público)

Reglas resumidas de `PenguScriptGuideSpanish.md` §11. No se duplican las generales; se fijan las específicas del proyecto.

| Regla | Detalle |
|---|---|
| **Idioma** | **Inglés.** Regla dura de §2.5. Los títulos de sección también: `## ## Parameters`, `## ## Returns`, `## ## Memory`, `## ## Example` |
| Una línea de resumen, línea en blanco, detalles | nunca un párrafo de resumen |
| Secciones en `## ## Nombre` | `Parameters`, `Returns`, `Memory`, `Example` |
| `## Example` en bloque ` ```pengu ` | el código debe compilar sobre los bindings reales |
| `##` precede **inmediatamente** al símbolo | sin línea en blanco intermedia |
| Semántica de liberación explícita siempre | "the returned `list` is new; release it with `banish`", "the `slice` borrows from `self`; do not `banish` it", "no allocation" |
| Nunca documentar lo obvio | `## Returns an int` está prohibido; documentar **qué significa** |
| El módulo lleva docstring antes de las directivas | `PenguScriptGuideSpanish.md` §11.1; en inglés |

**Obligación específica de raylib:** todo método que devuelve un handle de raylib (`Texture2D`, `Image`, `Font`, `Sound`, `Music`, `Model`, `Shader`, `Wave`, `RenderTexture2D`) documenta en `## ## Memory` el `Unload*` concreto que le corresponde.

### Ejemplo completo de referencia

```pengu
## Loads a texture from disk and verifies raylib accepted it.
##
## ## Parameters
## - `path`: file path. Converted to `char*` via `ffi.cstr_from_string`;
##   the pointer is only valid while `path` lives.
##
## ## Returns
## `some` with the texture ready for `raylib.DrawTexture`, or `maybe none`
## if raylib could not decode the file. A missing file and an unknown format
## are indistinguishable: both are `maybe none`.
##
## ## Memory
## On success the texture owns raylib memory. Release it with
## `defer calling raylib.UnloadTexture with tex`. It is not a `list` or a
## `string`: it does not take `banish`.
##
## ## Example
## ```pengu
## var tex as maybe raylib.Texture2D is calling raylibx.load_texture with "assets/logo.png"## if tex is present:
##     defer calling raylib.UnloadTexture with tex.value
##     calling raylib.DrawTexture with tex.value, 0, 0, raylib.RAYWHITE
## ```
weave load_texture with path as string into maybe raylib.Texture2D:
    let c_path as ref to frozen char is calling ffi.cstr_from_string with path
    var tex as raylib.Texture2D is calling raylib.LoadTexture with c_path
    if calling raylib.IsTextureValid with tex:
        return some tex
    return maybe none
```

**Prohibición:** un método público sin `##` es un incumplimiento de la Definition of Done (§13), no una omisión de estilo.

---

## 12. 🧪 Tests inline (cobertura mínima por método público)

**Regla:** cada `weave`/método público tiene **al menos 3 tests inline**.

| Test | Qué cubre |
|---|---|
| Caso feliz | el camino normal con datos válidos |
| Caso borde | vacío, cero, máximo, mínimo, slice de longitud 0, cadena vacía |
| Caso de error documentado | `maybe none`, `result` con error, fichero ausente, `Is*Valid` falso |

**Ubicación:** en el mismo `.pengu` que la función, al final del archivo, bajo el comentario `# --- Tests ---` (`PenguScriptGuideSpanish.md` §12.3).

**Nombres:** oración declarativa, nunca `test_1` ni `test_works` (§12.1).

**Aserciones:** `std.ward`. Funciones disponibles y útiles para este proyecto: `assert_true`, `assert_false`, `assert_eq_int`, `assert_eq_bool`, `assert_eq_string`, `assert_eq_float`, `assert_almost_eq`, `assert_in_range_float`, `assert_maybe_present`, `assert_maybe_none`, `assert_list_len_int`, `assert_string_empty`, `assert_string_not_empty`.

**Límite práctico:** los métodos que tocan GPU, audio, ventana o disco no se pueden ejecutar en un test de unidad. Para esos la obligación se degrada a:

1. Un test que verifique la rama de fallo sin recurso (ruta inexistente → `maybe none`), marcado como `(requiere ejecución, no CI)`.
2. Un test que verifique el cálculo puro equivalente cuando exista (p. ej. `Vector2.get_add`, `Vector2.length`).

```pengu
# --- Tests ---

test "Vector2.get_add sums both components":
    let a is calling Vector2.new with 1.0, 2.0
    let b is calling Vector2.new with 3.0, 4.0
    let c is calling a.get_add with b
    calling ward.assert_eq_float with c.x, 4.0
    calling ward.assert_eq_float with c.y, 6.0

test "Vector2.get_add with the zero vector is identity":
    let a is calling Vector2.new with 1.0, 2.0
    let c is calling a.get_add with (calling Vector2.zero)
    calling ward.assert_eq_float with c.x, 1.0
    calling ward.assert_eq_float with c.y, 2.0

test "load_texture returns maybe none for a missing file":
    let t is calling load_texture with "no-such-file.png"
    calling ward.assert_maybe_none with t
```

**Excepción de los tests inline:** el test vive en el mismo `.pengu` que la función, así que la llama por su **nombre local** (`calling load_texture`), no cualificada por el módulo (`raylibx.load_texture` es `E0004` dentro del propio módulo). La cualificación de §1 aplica al código de usuario y a los ejemplos, no a los tests internos del wrapper.

---

## 13. ✅ Definition of Done por wrapper

Checklist que se copia a cada `.md` de Fase 1 y que se verifica antes de entregar cualquier `.pengu` de Fase 2.

- [ ] `pengu check` pasa sin warnings.
- [ ] `pengu build` compila.
- [ ] `pengu test` pasa.
- [ ] Cada `weave`/método público tiene docstring `##` completo, con `## ## Memoria` cuando devuelve un recurso.
- [ ] Cada método público tiene ≥3 tests inline (o la degradación justificada de §12).
- [ ] Cada `@mutates weave <nombre>` expone su forma pura `get_<nombre>` sin declararla a mano (declararla es `E0068`).
- [ ] Cada método envuelto monomorfiza a una llamada C directa, verificado con `pengu expand`.
- [ ] No aparece `transmute` fuera de los wrappers de `slice` y de `ref to T` → `ref to frozen T`.
- [ ] Cero `banish` sobre handles de raylib: solo `defer calling raylib.Unload*` o `raylib.MemFree`.
- [ ] Cero `include`, `link`, `insignia`, `declare` y `antiquus` en el wrapper.
- [ ] Todos los `enchanting` usan el nombre cualificado del tipo (`enchanting raylib.Camera:`); la invocación del `ritual` usa el nombre desnudo (`calling Vector2.new with …`), nunca la forma de tres segmentos.
- [ ] La sección "NO se envuelve" del `.md` se respeta: no hay métodos colados.
- [ ] Ninguna función de la tabla de skip (§9) aparece envuelta sin justificación escrita.
- [ ] El módulo lleva docstring de módulo antes de las directivas de import, **en inglés**.
- [ ] Todos los `##` docstrings están en inglés, incluidos los títulos de sección (`## ## Parameters`, `## ## Returns`, `## ## Memory`, `## ## Example`).
- [ ] Si el módulo es bilingüe (es un `.md` de Fase 1): las dos mitades (EN y ES) tienen el mismo número de filas en cada tabla y las mismas decisiones. Divergencia entre mitades = no aprobado.

---

## 14. 📋 Plantilla del `.md` por módulo (Fase 1)

Cada plan de Fase 1 (`docs/plans/raymathx.md`, `docs/plans/rgesturesx.md`, …) es un único archivo **bilingüe**: inglés canónico arriba, español no normativo abajo. La traducción se sincroniza sección a sección; si algo discrepa, gana el inglés. Las dos mitades deben tener el mismo número de filas en cada tabla y las mismas decisiones.

La plantilla se copia tal cual.

````markdown
# Plan: <modulex>.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/<module>.d.pengu`
- Wrapper target: `pengu/<modulex>.pengu`
- Dependencies: `import <module>`, `import <modulex>`, `import std.ffi` (if any)
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (vX.Y.Z)

### 🎯 Module-specific decisions
(only if they diverge from the conventions doc; otherwise "None")

### ✨ Enchantings
#### `enchanting <module>.<Type>`
| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `new` | ritual | `with x, y into <Type>` | (inline) | constructor |
| `<name>` | @mutates | `with <args> into <Type>` | `<CFunc>` | returns self |
| `get_<name>` | pure | `with <args> into <Type>` | `<CFunc>` | pure form |
| `<query>` | pure | `into <Ret>` | `<CFunc>` | |
| ... | | | | |

### 🔧 Module-level functions
(only those that are not natural methods on a type)

### 🎁 `maybe T` wrappers
| Wrapper | C backing | Success predicate |
|---|---|---|

### ✂️ `slice` wrappers
| Wrapper | C backing | Notes |
|---|---|---|

### 📦 Multiple returns `(T, U)`
| Wrapper | C backing | Why a tuple |
|---|---|---|

### 🌉 `std.ffi` usage
| Site | ffi function | Reason |
|---|---|---|

### 💡 Compilable examples
```pengu
# Must pass `pengu check`
import <module>
import <modulex>
weave main into int:
    ...
    return 0
```

### 🧪 Test plan
- `test "<description>":`
- ...

### 🚫 Not wrapped (with reason)
| C symbol | Reason |
|---|---|
| `<CFunc>` | Covered by `<method>` |
| ... | ... |

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/<module>.d.pengu`
- Wrapper destino: `pengu/<modulex>.pengu`
- Dependencias: `import <module>`, `import <modulex>`, `import std.ffi` (si aplica)
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (vX.Y.Z)

### 🎯 Decisiones específicas del módulo
(solo si difieren del documento de convenciones; si no, "Ninguna")

### ✨ Enchantings
#### `enchanting <module>.<Tipo>`
| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `new` | ritual | `with x, y into <Tipo>` | (inline) | constructor |
| `<nombre>` | @mutates | `with <args> into <Tipo>` | `<FuncC>` | devuelve self |
| `get_<nombre>` | puro | `with <args> into <Tipo>` | `<FuncC>` | forma pura |
| `<consulta>` | puro | `into <Ret>` | `<FuncC>` | |
| ... | | | | |

### 🔧 Funciones a nivel de módulo
(solo las que no son métodos naturales sobre un tipo)

### 🎁 Wrappers `maybe T`
| Wrapper | C backing | Predicado de éxito |
|---|---|---|

### ✂️ Wrappers de `slice`
| Wrapper | C backing | Notas |
|---|---|---|

### 📦 Retornos múltiples `(T, U)`
| Wrapper | C backing | Por qué tupla |
|---|---|---|

### 🌉 Uso de `std.ffi`
| Punto | Función ffi | Motivo |
|---|---|---|

### 💡 Ejemplos compilables
```pengu
# Debe pasar `pengu check`
import <module>
import <modulex>
weave main into int:
    ...
    return 0
```

### 🧪 Plan de tests
- `test "<descripción>":`
- ...

### 🚫 NO se envuelve (con motivo)
| Símbolo C | Motivo |
|---|---|
| `<FuncC>` | Cubierto por `<método>` |
| ... | ... |
````

**Regla añadida a §13:** un `.md` de Fase 1 está completo cuando las dos mitades (EN y ES) tienen el mismo número de filas en cada tabla y las mismas decisiones.

---

## 15. 🗺️ Orden de implementación

| Orden | Módulo | Rol | Qué fija |
|---|---|---|---|
| 1 | `raymathx` | piloto | el estilo completo: `@mutates`, formas puras, `ritual new`, tests de matemática pura |
| 2 | `rgesturesx` | confirmación | el patrón en un módulo diminuto (2 `declare`, 1 `rune`, 1 `omen`); decide qué hacer con la ABI averiada de `GestureEvent` |
| 3 | `rcamerax` | structs mutados por puntero | el patrón de `weave … into void` con receptor `ref to T` sobre 12 funciones |
| 4 | `raylibx` | el grande | se trocea en sub-`.md` por familia: window, input, drawing 2D, drawing 3D, text, textures, images, colors, models, audio, files |
| 5 | `rlglx` | cierre | el `.md` puede concluir "no envolver casi nada; usar el binding directo". Esa conclusión es un entregable válido |

**Motivos del orden:** `raymathx` no toca GPU, ventana ni fichero, así que es el único módulo con tests inline ejecutables en CI y sirve de banco de pruebas del estilo; `rgesturesx` y `rcamerax` confirman el patrón con receptores por puntero; `raylibx` es el 80 % del trabajo y `rlglx` es la capa que casi nadie usa directamente.

**Estructura de `raylibx` (fachada + familias en subpaquete):** `raylib.d.pengu` tiene 2019 líneas; un wrapper monolítico lo superaría y rompería `PenguScriptGuideSpanish.md` §3.2. Por eso `raylibx` se descompone en familias, una fachada y una carpeta:

```
pengu/
├── raylibx.pengu              ← fachada: solo `import` de las familias, cero símbolos propios
├── raylibx/
│   ├── colors.pengu           ← módulo `raylibx.colors`
│   ├── files.pengu            ← módulo `raylibx.files`
│   ├── shapes.pengu
│   ├── shapes3d.pengu
│   ├── text.pengu
│   ├── input.pengu
│   ├── images.pengu
│   ├── textures.pengu
│   ├── drawing.pengu
│   ├── window.pengu
│   ├── shaders.pengu
│   ├── models.pengu
│   └── audio.pengu
└── raylib.d.pengu             ← el binding, hermano de la carpeta
```

- `pengu/raylibx.pengu` **solo** contiene los trece `import raylibx.<familia> as <familia>` y el docstring de módulo. Cero `enchanting`, cero `weave`, cero `const`. **Es el punto de entrada de integración**: `pengu check --entry pengu/raylibx.pengu`, `pengu build --entry pengu/raylibx.pengu` y `pengu test --entry pengu/raylibx.pengu` compilan, enlazan y ejecutan las trece familias a la vez. Es la única forma de detectar una colisión de símbolos C entre dos familias (los métodos de `enchanting` no llevan prefijo de módulo, así que el checo por fichero no la ve) y la única forma de detectar **dependencias de orden entre familias**: la suite integrada encontró cuatro tests que asumían el estado global virgen del proceso (la asimetría de `is_gamepad_button_up`, el eje en reposo de un mando real, el nombre del mando y el rectángulo de `SetShapesTexture`, que `InitWindow` cambia al cargar la fuente por defecto). Las suites por familia los ocultaban porque cada una corría en su propio proceso.
- **No hay re-exportación en PenguScript** (`@export` nombra un símbolo C, no un miembro de módulo), así que `import raylibx` **no** expone la superficie de las familias. El usuario importa las familias que necesita y llama a través del alias: `import raylibx.text as text` y luego `calling text.split_text with …`.
- Un `.md` por familia en `docs/plans/raylibx_<familia>.md`, con la plantilla bilingüe de §14.
- **Aviso de herramienta (v0.1.3):** `pengu expand` resuelve los `import` contra el **directorio de trabajo**, mientras que `check`, `build` y `test` los resuelven contra el `src_dir` del manifiesto. Verificar un ejemplo desde la raíz con `pengu expand pengu/<archivo>.pengu` falla con `Cannot resolve imported module 'raylib'` aunque `pengu check --entry` sobre el mismo archivo salga limpio. Para verificar ejemplos, usa `check` desde la raíz o `expand` desde dentro de `pengu/`.
- **Las familias no llevan `insignia`**: `pengu 2.4.0` ya manglea las funciones de módulo con el nombre del módulo (`raylibx_text_split_text`), así que dos familias hermanas no pueden colisionar. Los métodos de `enchanting` **no** llevan prefijo, así que un nombre de método solo puede existir en una familia: eso lo gobierna el registro global de `docs/plans/raylibx.md` D5.
- La familia `rlglx` (§15, orden 5) es un caso aparte: su `.md` puede concluir "no envolver casi nada; usar el binding directo", y esa conclusión es un entregable válido.

**Nota de tooling (v0.1.3):** la nota de v0.1.2 que declaraba el subpaquete **rechazado** por el resolutor de `pengu 2.4.0` **queda corregida**: el layout `pengu/raylibx/<familia>.pengu` (módulos `raylibx.<familia>`) resuelve `import raylib` sin problema, y está verificado con las trece familias reales sobre la misma versión `pengu 2.4.0` — `pengu check` limpio, `pengu build` con enlace correcto (218 KB, cero referencias sin definir) y la suite completa ejecutada. La explicación más probable del error original es que la sonda que lo produjo vivía en `src/`, un directorio que **no** es una raíz configurada (`src_dir = "pengu"`), donde `import raylib` no puede resolverse por diseño. Detalle y evidencia en `docs/plans/raylibx.md` D16.


---

## 16. 📚 Glosario rápido

| Término | Definición de una línea | Referencia |
|---|---|---|
| `enchanting` | bloque que asocia métodos a un tipo; `self` es `ref to T` | `§10.1` |
| `ritual` | método asociado (estático) invocado sobre el nombre del tipo, sin `self` | `§8.5`, `§10.1` |
| `@mutates` | método que devuelve el tipo del receptor; el call site asigna el resultado de vuelta y expone la forma pura `get_<nombre>` | `§10.1` |
| `shard` | parámetro de tipo genérico; se monomorfiza en compile-time | `§11.1` |
| `where` | cláusula de bounds sobre un `shard` | `§10.5`, `§11.2` |
| `bind` / `concept` | contrato de compile-time y su implementación; no hay despacho dinámico | `§10.2`, `§10.3` |
| `derive` | implementaciones automáticas de conceptos integrados (`Par`, `Ordo`, `Nexus`, …) | `§9.1.2` |
| `slice` | vista sin posesión sobre elementos contiguos; nunca se libera | `§4.2`, `§15.3` |
| `banish` / `defer` / `errdefer` | liberación explícita; `defer` la programa para la salida del ámbito (LIFO) y `errdefer` solo para un retorno de error | `§13` |
| `essence of` / `sigil of` | desreferenciar un `ref to T` / tomar la dirección de un lvalue | `§6.4` |
| `transmute` | reinterpretación de bits entre tipos; emite `W0001` | `§6.4` |
| `frozen` | cualificador de solo lectura del pointee; equivale a `const` de C | `§9.5` |
| `maybe T` / `result of T to E` | valor presente o ausente / valor correcto o error tipado | `§12` |
| `antiquus` | bloque de C embebido; prohibido en la capa 2 | `§9.6` |
| `declare` / `insignia` | firma tipada de una función C externa y prefijo C del módulo; solo en `.d.pengu` | `§8.2`, `§14.2` |

Las referencias de esta tabla son secciones de `LANGUAGE_Spanish.md`.

---

## 17. ✍️ Historial de cambios

| Versión | Fecha | Cambios | Autor |
|---|---|---|---|
| `v0.1.0` | 2025-10-15 | Borrador inicial | agente |
| `v0.1.2` | 2025-10-15 | Corrección de tooling descubierta en Fase 1: el layout de subdirectorio `pengu/raylibx/<familia>.pengu` **no resuelve** en `pengu 2.4.0` (`Cannot resolve imported module 'raylib'`); §15 pasa al layout plano `pengu/raylibx_<familia>.pengu`, hermano del binding. Verificado también que el compilador manglea las funciones de módulo con el nombre del módulo, así que las familias no necesitan `insignia` para no colisionar. Detalle en `docs/plans/raylibx.md` D4/D16. | agente |
| `v0.1.1` | 2025-10-15 | Correcciones de revisión + política de idioma: dos imports explícitos (§1), loaders de módulo (§2), política de idioma (§2.5), target `raylib.Vector2` (§4), docstrings en inglés (§11), plantilla bilingüe (§14), fachada de `raylibx` (§15), y dos excepciones verificadas con el compilador (invocación de `ritual` y tests en el propio módulo) | agente |
