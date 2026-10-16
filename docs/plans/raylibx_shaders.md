# Plan: shaders.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/shaders.pengu`
- Owner in the master plan: family `shaders` of `docs/plans/raylibx.md` (v0.1.2)
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: the shader section holds **10** C functions, **all exported** by the installed library, and **all 10 are wrapped — nothing is skipped.** They become **15 wrappers**: 12 methods on `raylib.Shader` and 3 module-level lifecycle entries. | The first family with no exclusions at all. Nothing here is "already idiomatic": every entry either crosses the `void*` boundary, folds a `-1` sentinel or manages a GPU resource. |
| D2 | **`SetShaderValue` alone accounts for seven methods**: `set_float`, `set_int`, `set_vec2`, `set_vec3`, `set_vec4`, `set_floats`, `set_ints`. | Contract section 2: "una función C puede dar varios wrappers cuando lo que varía es el tipo". In the binding, one uniform upload needs a `void*`, a cast and a `SHADER_UNIFORM_*` enum; the typed methods remove all three, and the enum is chosen by the method name instead of by the caller. This is the largest single-C-function fan-out in the module. |
| D3 | **The silent-fallback trap, measured, and what the wrapper does about it.** raylib **never fails to return a shader**: a *missing file* and *empty source* both yield the **default** shader with `IsShaderValid() == true`. Only source that is non-empty and fails to compile reports `false`. The two loaders therefore check their precondition first — `load_shader` requires both paths to satisfy `IsPathFile`, `load_shader_from_memory` requires both sources to be non-empty — so `maybe none` means "your shader did not load" in **both** the precondition case and the compile-failure case. | Measured: `LoadShader("/tmp/nope_vs.glsl", "/tmp/nope_fs.glsl")` → `valid=1, id=3` (the default program), and `LoadShaderFromMemory("", "")` → `valid=1, id=3`, while `LoadShaderFromMemory("nonsense", "nonsense too")` → `valid=0, id=0`. Without the pre-check the binding would hand back a working shader that is not the caller's, silently, and the `maybe` would be a lie. |
| D4 | **Detecting a fallback is done through a uniform, not through `is_valid`.** The recipe, documented on `location`: ask for one of your own uniforms; a fallen-back shader has none of them, so `location` returns `maybe none`. | Measured: after a fallback, `GetShaderLocation(shader, "u_from_file")` is `-1`. This is the honest way to tell "my program is running" from "raylib substituted the default", and it is a property of the uniform table rather than a flag raylib exposes. |
| D5 | `location` and `location_attrib` return `maybe int`. | Measured: both return **`-1`** for a name the program does not declare, which is exactly the sentinel the contract folds. |
| D6 | The typed setters take the real types: `f32`, `int`, `raylib.Vector2`, `raylib.Vector3`, `raylib.Vector4`, `raylib.Matrix`, `raylib.Texture2D`. | The `void*` in the binding is the boundary, and the type is what the `SHADER_UNIFORM_*` enum was encoding. `set_matrix` and `set_texture` take their argument **by value** because their two dedicated C functions do. |
| D7 | `set_floats` and `set_ints` take a `slice` and use the slice's length as the element count. **Arrays of vectors are deliberately not exposed.** | raylib's count convention differs by type: for a scalar array it is the number of scalars, but for a `vec2` array it is the number of *elements*, so the same call reads `count` or `count * 2` floats. Exposing only the unambiguous case is safer than shipping a setter whose count means something a reader would guess wrong. Raising a `uniform vec2 u[N]` is still reachable through the binding, and the docstring says so. |
| D8 | **This is the first family where every wrapped function is asserted**, against a live window, and it includes a real GLSL 330 compile in CI. | Measured: `DISPLAY=:0` is present (master plan D21), and a shader load is a GLSL compile, so the whole family is exercisable: load, `is_valid`, both location lookups (present and missing), all nine setters, both array setters, both empty-array no-ops, and every failure path (empty source, half-empty source, invalid source, missing file, real files). |
| D9 | **The uniform *values* are not asserted, and the reason is measured.** This environment cannot read the framebuffer back: `LoadImageFromScreen()` after `ClearBackground(RED)` returns a valid image that is entirely **black**. | A pixel round-trip would have been the way to prove a uniform reached the GPU (render with the shader, read the pixel, compare). Since the read-back is broken here, the tests assert that the call path is accepted for a compiled program, and the plan records that verifying the transmitted value is **not possible in this environment** rather than pretending the setter test is stronger than it is. |
| D10 | The test sources are **raw triple-quoted strings** (`r"""…"""`). | GLSL is full of braces, which a normal literal reads as interpolation (`E0019`, measured while writing the test), and it is line-oriented, so `#version 330` needs a real newline rather than an escape. The language guide names shaders as the motivating case for raw literals, so this is the intended mechanism rather than a workaround. |
| D11 | `is_valid` is wrapped even though it is a zero-argument `bool` predicate. | Contract section 9 criterion 2 is satisfied: the shader is a natural receiver, so `prog.is_valid` beats `raylib.IsShaderValid with prog`. Its docstring also carries the D3 warning that it cannot detect a fallback. |
| D12 | One enchanting block, `enchanting raylib.Shader`, on the nominal name; the master plan's reserved method name `set_value` is **replaced** by the typed family of D2. | `Shader` has no alias, so there is no `Texture2D`-style trap. `set_value` as a single generic method would have kept the enum and the `void*` at the call site, which is precisely what this family exists to remove. |
| D13 | **The projection helpers the master plan listed under `shaders` are reassigned, not skipped.** `GetCameraMatrix` is already `rcamerax`'s `Camera3D.view_matrix` (contract §9 row 2, superseded), and the other seven — `GetWorldToScreen`, `GetWorldToScreenEx`, `GetWorldToScreen2D`, `GetScreenToWorld2D`, `GetScreenToWorldRay`, `GetScreenToWorldRayEx`, `GetCameraMatrix2D` — take a **camera** as their subject, so their natural receiver belongs to the family that owns the camera types. | The receiver test of contract §9 criterion 2 decides it: `camera.to_screen with position` is the wrapper that reduces tokens, and it belongs next to `view_matrix`, `forward` and the rest of the camera surface, not in a file about shaders. Recorded here as an open addendum (a 7-method addition to `rcamerax`, all pure math with no window needed) rather than quietly wrapped in the wrong module or quietly dropped. |

### ✨ Enchantings

#### `enchanting raylib.Shader` — 12 methods

| Method | Signature |
|---|---|
| `is_valid` | `into bool` |
| `location` | `with name as string into maybe int` |
| `location_attrib` | `with name as string into maybe int` |
| `set_float` | `with loc as int, value as f32 into void` |
| `set_int` | `with loc as int, value as int into void` |
| `set_vec2` | `with loc as int, value as raylib.Vector2 into void` |
| `set_vec3` | `with loc as int, value as raylib.Vector3 into void` |
| `set_vec4` | `with loc as int, value as raylib.Vector4 into void` |
| `set_matrix` | `with loc as int, value as raylib.Matrix into void` |
| `set_texture` | `with loc as int, value as raylib.Texture2D into void` |
| `set_floats` | `with loc as int, values as slice of f32 into void` |
| `set_ints` | `with loc as int, values as slice of int into void` |

### 🔧 Module-level functions (3)

| Function | Signature |
|---|---|
| `load_shader` | `with vs_path as string, fs_path as string into maybe raylib.Shader` |
| `load_shader_from_memory` | `with vs_code as string, fs_code as string into maybe raylib.Shader` |
| `unload_shader` | `with shader as raylib.Shader into void` |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `load_shader` | `maybe raylib.Shader` | `IsPathFile` on both paths, then `IsShaderValid` |
| `load_shader_from_memory` | `maybe raylib.Shader` | non-empty sources, then `IsShaderValid` |
| `Shader.location` | `maybe int` | `-1` for a name the program does not declare |
| `Shader.location_attrib` | `maybe int` | `-1` |

> Four of the fifteen wrappers return `maybe`, and the two loaders' predicate is the family's headline decision (D3).

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `Shader.set_floats` | `values as slice of f32` |
| `Shader.set_ints` | `values as slice of int` |

Both treat an empty slice as a no-op and pass the slice's length as raylib's element count (D7).

### 📦 Multiple returns `(T, U)`

**None apply.** No shader function returns a pair.

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | both loaders, both location lookups |
| value → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | the nine value setters |

### 💡 Compilable examples

```pengu
# Example 1 — compile a shader from source and upload a uniform
import raylib
import raylibx.shaders as shaders

weave main into int:
    var vs as string is r"#version 330\nvoid main() { }\n"
    var fs as string is r"#version 330\nuniform float u_time;\nout vec4 c;\nvoid main() { c = vec4(u_time); }\n"
    var loaded as maybe raylib.Shader is calling shaders.load_shader_from_memory with vs, fs
    if loaded is present:
        var prog as raylib.Shader is calling loaded.unwrap
        defer calling shaders.unload_shader with prog
        var loc as maybe int is calling prog.location with "u_time"
        if loc is present:
            var where as int is calling loc.unwrap
            calling prog.set_float with where, 1.5
    return 0
```

```pengu
# Example 2 — the fallback recipe: a missing uniform means raylib substituted the default
import raylib
import raylibx.shaders as shaders

weave main into int:
    var loaded as maybe raylib.Shader is calling shaders.load_shader with "vs.glsl", "fs.glsl"
    if loaded is present:
        var prog as raylib.Shader is calling loaded.unwrap
        defer calling shaders.unload_shader with prog
        var mine as maybe int is calling prog.location with "u_scalar"
        if mine is present:
            calling prog.set_vec4 with (calling mine.unwrap), (with x is 1.0, y is 0.0, z is 0.0, w is 1.0)
    return 0
```

```pengu
# Example 3 — the array setters
import raylib
import raylibx.shaders as shaders

weave main with vs as string, fs as string into int:
    var loaded as maybe raylib.Shader is calling shaders.load_shader_from_memory with vs, fs
    if loaded is present:
        var prog as raylib.Shader is calling loaded.unwrap
        defer calling shaders.unload_shader with prog
        var weights as list of f32 is [0.25, 0.5, 0.75]
        defer banish weights
        var loc as int is 0
        calling prog.set_floats with loc, (weights at 0 to (weights.length))
    return 0
```

### 🧪 Test plan

**Seven tests, every wrapped function asserted, against a live window.** This is the best-covered family in the module: the surface is small, self-contained and — uniquely — a shader load is a GLSL compile that a CI machine with a display can actually perform (D8).

- **A real shader compiles from memory and reports valid** — the vertex and fragment sources of D10, compiled by the driver, with `is_valid` true.
- **`location` finds a declared uniform and is `none` for a missing one** — `u_scalar` is `some` and non-negative; `u_does_not_exist` is `maybe none`. This is the sentinel of D5 and the fallback recipe of D4 in one test.
- **`location_attrib` does the same for a vertex attribute** — `vertexPosition` is `some`, `a_does_not_exist` is `none`.
- **Every typed setter is callable on a compiled program** — `set_float`, `set_int`, `set_vec2`, `set_vec3`, `set_vec4`, `set_matrix`, `set_texture`, `set_floats` and `set_ints`, each with a location obtained through the wrapper. What this asserts is the call path; the value itself is out of reach (D9).
- **An empty array is a no-op** for both array setters.
- **Every failure path returns `maybe none`**: empty sources, a half-empty pair, invalid GLSL, and a missing file. This is where D3 earns its place.
- **A shader loads from files that exist** — the sources are written to unique temporary paths, loaded through `load_shader`, checked for a uniform, and the files are removed with `defer` so the suite leaves nothing behind.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| *(none)* | the family wraps all 10 shader-section functions |

| Out of scope | Reason |
|---|---|
| `BeginShaderMode`, `EndShaderMode` | already wrapped by `raylibx_drawing` |
| `rlGetShaderIdDefault`, `rlGetShaderLocsDefault` | raw `rlgl` layer; `rlglx`'s business |
| `GetShaderUniforms` | not present in the binding or the header for raylib 6.0 |
| `GetWorldToScreen`, `GetWorldToScreenEx`, `GetWorldToScreen2D`, `GetScreenToWorld2D`, `GetScreenToWorldRay`, `GetScreenToWorldRayEx`, `GetCameraMatrix2D`, `GetCameraMatrix` | **reassigned to `rcamerax`**, which owns the camera types: the receiver is the camera (`camera.to_screen`, `camera.ray_from_screen`), and `GetCameraMatrix` is already that family's `view_matrix`. See D13 |

Coverage audit: **10 shader-section C functions, 10 wrapped, 0 not wrapped**, plus 8 projection functions reassigned to `rcamerax` (D13). They become 15 wrappers (12 methods and 3 module functions). The method registry gains the 12 `raylib.Shader` names; the reserved name `set_value` is released in favour of the typed family (D12).

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/shaders.pengu`
- Dueña en el plan maestro: familia `shaders` de `docs/plans/raylibx.md` (v0.1.2)
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: la sección de shaders tiene **10** funciones C, **todas exportadas** por la biblioteca instalada, y **las 10 se envuelven — no se omite ninguna.** Se convierten en **15 wrappers**: 12 métodos sobre `raylib.Shader` y 3 entradas de ciclo de vida a nivel de módulo. | La primera familia sin exclusiones. Aquí nada es "ya idiomático": cada entrada o cruza la frontera del `void*`, o pliega un centinela `-1`, o gestiona un recurso de GPU. |
| D2 | **Solo `SetShaderValue` da siete métodos**: `set_float`, `set_int`, `set_vec2`, `set_vec3`, `set_vec4`, `set_floats`, `set_ints`. | Contrato §2: "una función C puede dar varios wrappers cuando lo que varía es el tipo". En el binding, subir un uniform necesita un `void*`, un cast y un enum `SHADER_UNIFORM_*`; los métodos tipados quitan los tres, y el enum lo elige el nombre del método en vez del llamador. Es el mayor abanico desde una sola función C en todo el módulo. |
| D3 | **La trampa del fallback silencioso, medida, y lo que el wrapper hace con ella.** raylib **nunca falla al devolver un shader**: un *fichero ausente* y un *código fuente vacío* devuelven los dos el shader **por defecto** con `IsShaderValid() == true`. Solo un código no vacío que no compila informa `false`. Por eso los dos cargadores comprueban antes su precondición — `load_shader` exige que las dos rutas cumplan `IsPathFile`, `load_shader_from_memory` exige que las dos fuentes no estén vacías — de modo que `maybe none` significa "tu shader no se cargó" **tanto** en el caso de la precondición **como** en el de fallo de compilación. | Medido: `LoadShader("/tmp/nope_vs.glsl", "/tmp/nope_fs.glsl")` → `valid=1, id=3` (el programa por defecto), y `LoadShaderFromMemory("", "")` → `valid=1, id=3`, mientras que `LoadShaderFromMemory("nonsense", "nonsense too")` → `valid=0, id=0`. Sin la precomprobación el binding entregaría un shader que funciona pero que no es el del llamador, en silencio, y el `maybe` sería una mentira. |
| D4 | **Detectar un fallback se hace por un uniform, no por `is_valid`.** La receta, documentada en `location`: pregunta por un uniform tuyo; un shader sustituido no tiene ninguno, así que `location` devuelve `maybe none`. | Medido: tras un fallback, `GetShaderLocation(shader, "u_from_file")` es `-1`. Es la forma honesta de distinguir "mi programa está corriendo" de "raylib sustituyó el de por defecto", y es una propiedad de la tabla de uniforms, no un indicador que raylib exponga. |
| D5 | `location` y `location_attrib` devuelven `maybe int`. | Medido: las dos devuelven **`-1`** para un nombre que el programa no declara, que es exactamente el centinela que el contrato pliega. |
| D6 | Los setters tipados reciben los tipos reales: `f32`, `int`, `raylib.Vector2`, `raylib.Vector3`, `raylib.Vector4`, `raylib.Matrix`, `raylib.Texture2D`. | El `void*` del binding es la frontera, y el tipo es lo que estaba codificando el enum `SHADER_UNIFORM_*`. `set_matrix` y `set_texture` reciben su argumento **por valor** porque sus dos funciones C dedicadas lo hacen así. |
| D7 | `set_floats` y `set_ints` reciben un `slice` y usan su longitud como número de elementos. **Los arrays de vectores no se exponen a propósito.** | La convención de recuento de raylib cambia según el tipo: para un array de escalares es el número de escalares, pero para un array de `vec2` es el número de *elementos*, así que la misma llamada lee `count` o `count * 2` floats. Exponer solo el caso inequívoco es más seguro que enviar un setter cuyo recuento signifique algo que el lector adivinaría mal. Subir un `uniform vec2 u[N]` sigue siendo posible desde el binding, y el docstring lo dice. |
| D8 | **Es la primera familia donde se asegura cada función envuelta**, contra una ventana viva, e incluye una compilación GLSL 330 real en CI. | Medido: hay display (`DISPLAY=:0`, plan maestro D21), y cargar un shader es compilar GLSL, así que la familia entera es ejercitable: carga, `is_valid`, las dos búsquedas de localización (presente y ausente), los nueve setters, los dos setters de array, los dos no-ops de array vacío y todas las rutas de fallo (fuente vacía, medio par vacío, fuente inválida, fichero ausente, ficheros reales). |
| D9 | **Los *valores* de los uniforms no se aseguran, y el motivo está medido.** Este entorno no puede releer el framebuffer: `LoadImageFromScreen()` tras `ClearBackground(RED)` devuelve una imagen válida **enteramente negra**. | Un viaje de ida y vuelta por píxel habría sido la forma de demostrar que un uniform llegó a la GPU (dibujar con el shader, leer el píxel, comparar). Como la relectura está rota aquí, los tests aseguran que el camino de llamada se acepta para un programa compilado, y el plan registra que verificar el valor transmitido **no es posible en este entorno** en vez de fingir que el test de setters es más fuerte de lo que es. |
| D10 | Las fuentes de los tests son **cadenas raw con comillas triples** (`r"""…"""`). | El GLSL está lleno de llaves, que un literal normal lee como interpolación (`E0019`, medido al escribir el test), y es orientado a líneas, así que `#version 330` necesita un salto de línea real en vez de un escape. La guía del lenguaje nombra los shaders como el caso motivador de los literales raw, así que este es el mecanismo previsto y no un rodeo. |
| D11 | `is_valid` se envuelve aunque sea un predicado `bool` sin argumentos. | El criterio 2 del contrato §9 se cumple: el shader es un receptor natural, así que `prog.is_valid` gana a `raylib.IsShaderValid with prog`. Su docstring además lleva el aviso del D3 de que no puede detectar un fallback. |
| D12 | Un bloque `enchanting raylib.Shader`, sobre el nombre nominal; el nombre reservado `set_value` del plan maestro queda **sustituido** por la familia tipada del D2. | `Shader` no tiene alias, así que no hay trampa tipo `Texture2D`. `set_value` como método genérico único habría dejado el enum y el `void*` en el sitio de llamada, que es justo lo que esta familia existe para quitar. |
| D13 | **Los helpers de proyección que el plan maestro listaba bajo `shaders` se reasignan, no se omiten.** `GetCameraMatrix` ya es el `Camera3D.view_matrix` de `rcamerax` (contrato §9 fila 2, superseded), y los otros siete — `GetWorldToScreen`, `GetWorldToScreenEx`, `GetWorldToScreen2D`, `GetScreenToWorld2D`, `GetScreenToWorldRay`, `GetScreenToWorldRayEx`, `GetCameraMatrix2D` — tienen una **cámara** como sujeto, así que su receptor natural pertenece a la familia dueña de los tipos de cámara. | Lo decide el test de receptor del criterio 2 del contrato §9: `camera.to_screen with position` es el wrapper que reduce tokens, y va junto a `view_matrix`, `forward` y el resto de la superficie de cámara, no en un fichero sobre shaders. Se registra aquí como apéndice abierto (una adición de 7 métodos a `rcamerax`, toda matemática pura y sin ventana) en vez de envolverlo en silencio en el módulo equivocado u omitirlo en silencio. |

### ✨ Enchantings

#### `enchanting raylib.Shader` — 12 métodos

| Método | Firma |
|---|---|
| `is_valid` | `into bool` |
| `location` | `with name as string into maybe int` |
| `location_attrib` | `with name as string into maybe int` |
| `set_float` | `with loc as int, value as f32 into void` |
| `set_int` | `with loc as int, value as int into void` |
| `set_vec2` | `with loc as int, value as raylib.Vector2 into void` |
| `set_vec3` | `with loc as int, value as raylib.Vector3 into void` |
| `set_vec4` | `with loc as int, value as raylib.Vector4 into void` |
| `set_matrix` | `with loc as int, value as raylib.Matrix into void` |
| `set_texture` | `with loc as int, value as raylib.Texture2D into void` |
| `set_floats` | `with loc as int, values as slice of f32 into void` |
| `set_ints` | `with loc as int, values as slice of int into void` |

### 🔧 Funciones a nivel de módulo (3)

| Función | Firma |
|---|---|
| `load_shader` | `with vs_path as string, fs_path as string into maybe raylib.Shader` |
| `load_shader_from_memory` | `with vs_code as string, fs_code as string into maybe raylib.Shader` |
| `unload_shader` | `with shader as raylib.Shader into void` |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `load_shader` | `maybe raylib.Shader` | `IsPathFile` en las dos rutas, luego `IsShaderValid` |
| `load_shader_from_memory` | `maybe raylib.Shader` | fuentes no vacías, luego `IsShaderValid` |
| `Shader.location` | `maybe int` | `-1` para un nombre que el programa no declara |
| `Shader.location_attrib` | `maybe int` | `-1` |

> Cuatro de los quince wrappers devuelven `maybe`, y el predicado de los dos cargadores es la decisión estrella de la familia (D3).

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `Shader.set_floats` | `values as slice of f32` |
| `Shader.set_ints` | `values as slice of int` |

Las dos tratan un slice vacío como no-op y pasan la longitud del slice como recuento de elementos de raylib (D7).

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Ninguna función de shader devuelve un par.

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | los dos cargadores, las dos búsquedas de localización |
| valor → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | los nueve setters de valor |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — compilar un shader desde fuente y subir un uniform
import raylib
import raylibx.shaders as shaders

weave main into int:
    var vs as string is r"#version 330\nvoid main() { }\n"
    var fs as string is r"#version 330\nuniform float u_time;\nout vec4 c;\nvoid main() { c = vec4(u_time); }\n"
    var loaded as maybe raylib.Shader is calling shaders.load_shader_from_memory with vs, fs
    if loaded is present:
        var prog as raylib.Shader is calling loaded.unwrap
        defer calling shaders.unload_shader with prog
        var loc as maybe int is calling prog.location with "u_time"
        if loc is present:
            var where as int is calling loc.unwrap
            calling prog.set_float with where, 1.5
    return 0
```

```pengu
# Ejemplo 2 — la receta del fallback: un uniform ausente significa que raylib sustituyó el de por defecto
import raylib
import raylibx.shaders as shaders

weave main into int:
    var loaded as maybe raylib.Shader is calling shaders.load_shader with "vs.glsl", "fs.glsl"
    if loaded is present:
        var prog as raylib.Shader is calling loaded.unwrap
        defer calling shaders.unload_shader with prog
        var mine as maybe int is calling prog.location with "u_scalar"
        if mine is present:
            calling prog.set_vec4 with (calling mine.unwrap), (with x is 1.0, y is 0.0, z is 0.0, w is 1.0)
    return 0
```

```pengu
# Ejemplo 3 — los setters de array
import raylib
import raylibx.shaders as shaders

weave main with vs as string, fs as string into int:
    var loaded as maybe raylib.Shader is calling shaders.load_shader_from_memory with vs, fs
    if loaded is present:
        var prog as raylib.Shader is calling loaded.unwrap
        defer calling shaders.unload_shader with prog
        var weights as list of f32 is [0.25, 0.5, 0.75]
        defer banish weights
        var loc as int is 0
        calling prog.set_floats with loc, (weights at 0 to (weights.length))
    return 0
```

### 🧪 Plan de tests

**Siete tests, cada función envuelta asegurada, contra una ventana viva.** Es la familia mejor cubierta del módulo: la superficie es pequeña, autocontenida y — de forma única — cargar un shader es compilar GLSL, algo que una máquina de CI con display puede hacer de verdad (D8).

- **Un shader real compila desde memoria e informa válido** — las fuentes de vértice y fragmento del D10, compiladas por el driver, con `is_valid` verdadero.
- **`location` encuentra un uniform declarado y es `none` para uno ausente** — `u_scalar` es `some` y no negativo; `u_does_not_exist` es `maybe none`. Es el centinela del D5 y la receta del fallback del D4 en un solo test.
- **`location_attrib` hace lo mismo con un atributo de vértice** — `vertexPosition` es `some`, `a_does_not_exist` es `none`.
- **Cada setter tipado se puede llamar sobre un programa compilado** — `set_float`, `set_int`, `set_vec2`, `set_vec3`, `set_vec4`, `set_matrix`, `set_texture`, `set_floats` y `set_ints`, cada uno con una localización obtenida a través del wrapper. Lo que asegura es el camino de llamada; el valor queda fuera de alcance (D9).
- **Un array vacío es un no-op** para los dos setters de array.
- **Todas las rutas de fallo devuelven `maybe none`**: fuentes vacías, un par a medias, GLSL inválido y un fichero ausente. Aquí es donde el D3 se gana su sitio.
- **Un shader se carga desde ficheros que existen** — las fuentes se escriben en rutas temporales únicas, se cargan con `load_shader`, se comprueba un uniform, y los ficheros se borran con `defer` para que la suite no deje nada.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| *(ninguno)* | la familia envuelve las 10 funciones de la sección de shaders |

| Fuera de alcance | Motivo |
|---|---|
| `BeginShaderMode`, `EndShaderMode` | ya las envuelve `raylibx_drawing` |
| `rlGetShaderIdDefault`, `rlGetShaderLocsDefault` | capa cruda de `rlgl`; es cosa de `rlglx` |
| `GetShaderUniforms` | no existe en el binding ni en el header de raylib 6.0 |
| `GetWorldToScreen`, `GetWorldToScreenEx`, `GetWorldToScreen2D`, `GetScreenToWorld2D`, `GetScreenToWorldRay`, `GetScreenToWorldRayEx`, `GetCameraMatrix2D`, `GetCameraMatrix` | **reasignadas a `rcamerax`**, que posee los tipos de cámara: el receptor es la cámara (`camera.to_screen`, `camera.ray_from_screen`), y `GetCameraMatrix` ya es el `view_matrix` de esa familia. Ver D13 |

Auditoría de cobertura: **10 funciones C de la sección de shaders, 10 envueltas, 0 sin envolver**, más 8 funciones de proyección reasignadas a `rcamerax` (D13). Se convierten en 15 wrappers (12 métodos y 3 funciones de módulo). El registro de métodos gana los 12 nombres de `raylib.Shader`; el nombre reservado `set_value` queda liberado en favor de la familia tipada (D12).
