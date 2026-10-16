# Plan: rgesturesx.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/rgestures.d.pengu`
- Wrapper target: `pengu/rgesturesx.pengu`
- Dependencies: `import raylib`, `import rgestures`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete** for what the header exports to a normal translation unit. `rgestures.h` has exactly 2 unconditional function declarations — `ProcessGestureEvent`, `UpdateGestures` — and the binding declares both. | `SetGesturesEnabled`, `IsGestureDetected` and the five getters sit behind `#if defined(RGESTURES_STANDALONE)` (`include/rgestures.h:128-137`), so they are *not* part of a raylib consumer's API. In that build they are raylib's own, and `pengu/raylib.d.pengu:1158-1172` declares them. |
| D2 | The usable gesture surface lives in **`raylib.d.pengu`**, not in `rgestures.d.pengu`. `rgesturesx` wraps the raylib gesture API and imports both bindings. | This is the first wrapper whose useful surface is not its nominally matching binding. It is not a workaround: in any program that links raylib (the only supported configuration; `raylib.d.pengu` is the one that emits `include "raylib.h"`), `SetGesturesEnabled`/`IsGestureDetected`/`GetGesture*` are the raylib symbols. Wrapping the `rgestures` copies under `RGESTURES_STANDALONE` would be wrong: they are not exported by the library this project links. |
| D3 | **No `enchanting` blocks.** All nine entries are module-level `weave`s. | Contract §6.1: the subject is global input state, not a receiver. `calling rgesturesx.is_detected with …` reads correctly; there is no type to enchant. `GestureEvent` is the only rune in the binding and it is unusable (D4), so the enchantings section is empty by design. |
| D4 | `ProcessGestureEvent` is **not wrapped**. `GestureEvent.pointId` and `.position` are declared as **scalars**, but in C they are `int pointId[8]` and `Vector2 position[8]`; 7 of the 8 slots of each array cannot be written from PenguScript. | `include/rgestures.h:105-110` defines the struct with two 8-element arrays; `pengu bind` flattened them to one lane each. A wrapper could only ever transmit a single touch point, and multi-touch is exactly what this function exists for. It is a binding defect (missing declaration), so it is reported rather than worked around: contract §1 forbids the wrapper from adding `declare`. |
| D5 | `UpdateGestures` is **not wrapped** either. | It is `void UpdateGestures(void)`, a one-line frame tick, and raylib already calls it from its own input pump in the normal flow. A wrapper would be a pure alias with no naming or token gain (contract §9, criterion 1). |
| D6 | `detected` returns the raw `int` code, not a `Gesture`: it stays `int`, matching the binding. | `GetGestureDetected` returns `GESTURE_NONE` (`0`) when nothing is active, so a plain `Gesture` return would have to smuggle a "nothing" value into the type. `maybe Gesture` would model that correctly, but a runtime `int` → `Gesture` cast is rejected (`E0005: Cannot cast 'int' to 'Gesture'`, verified), and dispatching over the eleven variants with `judge` buys nothing over comparing the code. Callers compare against `raylib.GESTURE_*`, which are plain integer constants. |
| D7 | `enable` takes a `slice of raylib.Gesture` and folds it into the `u32` bitmask the C API wants; `disable` passes `0`. | The flag word has no binding-level type of its own, and an array literal cannot be passed in argument position (verified: `E0005: Array literal cannot be passed directly`), so the slice form is the one that works at the call site: `calling rgesturesx.enable with (kinds at 0 to 2)`. |
| D8 | Bit flags are combined with `\|`, never `or`. | `SetGesturesEnabled` takes a `u32` mask; `or` is boolean-only in PenguScript (`E0005: Logical operator 'or' requires bool, got 'u32'`, verified). |
| D9 | Names carry their unit: `hold_seconds`, `drag_angle`, `pinch_angle`; the vectors are `drag_direction` and `pinch_delta`. | Contract §2: `Get*` without a receiver becomes a module-level noun. The unit matters because the API mixes radians (`*Angle`) with a vector (`*Vector`), and the pinch vector is a *delta*, not a direction. |
| D10 | The five getters and both predicates are wrapped; nothing is renamed to `get_*`. | None of them is a `@mutates` pair: every one returns a value and leaves the global state alone, so there is no pure/mutating split and no generated `get_*` (contract §4). |
| D11 | The wrapper does not enable gestures or initialise anything on load. | Contract §9: single-shot global configuration stays at the call site. `enable`/`disable` are explicit and the user decides when. |

### ✨ Enchantings

**None apply.** The binding's only rune is `GestureEvent`, and passing it is unsafe from PenguScript (D4); every other gesture symbol is a free function over global input state, so there is no receiver to enchant (D3). The `TouchAction` omen stays available through `import rgestures` for callers that build a partial `GestureEvent` by hand.

### 🔧 Module-level functions

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `enable` | `with gestures as slice of raylib.Gesture into void` | `raylib.SetGesturesEnabled` | ORs the slice into the flag word; an empty slice is a no-op |
| `disable` | `into void` | `raylib.SetGesturesEnabled` | passes `0` |
| `is_detected` | `with kind as raylib.Gesture into bool` | `raylib.IsGestureDetected` | the C check is `(enabledFlags & current) == kind`, so it already covers combinations |
| `detected` | `into int` | `raylib.GetGestureDetected` | `0` = `GESTURE_NONE`; compare against `raylib.GESTURE_*` (D6) |
| `hold_seconds` | `into f32` | `raylib.GetGestureHoldDuration` | seconds |
| `drag_direction` | `into raylib.Vector2` | `raylib.GetGestureDragVector` | `(0, 0)` when no drag is active |
| `drag_angle` | `into f32` | `raylib.GetGestureDragAngle` | radians |
| `pinch_delta` | `into raylib.Vector2` | `raylib.GetGesturePinchVector` | pinch delta, not a direction |
| `pinch_angle` | `into f32` | `raylib.GetGesturePinchAngle` | radians |

### 🎁 `maybe T` wrappers

**None apply.** No gesture entry point can fail for an external reason: every one of them reads state that raylib keeps in its own process, and all of them are safe to call before any window or input exists (verified headless: they return `0` / `(0, 0)` instead of faulting). The one place where absence is real — "no gesture is currently active" — is modelled by the `0` return of `detected` (D6), not by a `maybe`, because the caller compares an `int` code rather than unwrapping a container.

### ✂️ `slice` wrappers

**None apply as pointer-and-count reconstruction.** One entry point *accepts* a slice (`enable`), but it is not the `(T* ptr, int count)` C shape of contract §5: the wrapper folds the slice into a single `u32` bitmask and calls `SetGesturesEnabled with flags`. There is no pointer to rebuild and no count to pass, so no `std.ffi` and no `transmute` are involved.

### 📦 Multiple returns `(T, U)`

**None apply.** Every function returns one value or nothing. The closest candidate, "the active gesture kind", is a single `int` (D6); the drag and pinch pairs are two independent getters with different types and no shared lifetime, so a tuple would invent a relationship the API does not have.

### 🌉 `std.ffi` usage

**None apply, reason: the gesture API is numeric and by-value.** The nine entries pass `u32`, `bool`, `int`, `f32` and `Vector2`; there is no `char*`, no `void*` and no pointer the wrapper has to reinterpret. `import std.ffi` is therefore **not** in the dependency list.

### 💡 Compilable examples

```pengu
# Example 1 — enabling a set of gestures and reading one back
import raylib
import rgesturesx

weave main into int:
    var kinds as array of raylib.Gesture with size 2 is [raylib.GESTURE_TAP, raylib.GESTURE_DRAG]
    calling rgesturesx.enable with (kinds at 0 to 2)
    var tapped as bool is calling rgesturesx.is_detected with raylib.GESTURE_TAP
    var kind as int is calling rgesturesx.detected
    if tapped:
        return 1
    calling rgesturesx.disable
    return kind
```

```pengu
# Example 2 — reading drag and pinch state every frame
import raylib
import rgesturesx

weave sample_drag into raylib.Vector2:
    return calling rgesturesx.drag_direction

weave main into int:
    var direction as raylib.Vector2 is calling sample_drag
    var angle as f32 is calling rgesturesx.drag_angle
    var pinch as raylib.Vector2 is calling rgesturesx.pinch_delta
    var pinch_angle as f32 is calling rgesturesx.pinch_angle
    var held as f32 is calling rgesturesx.hold_seconds
    return 0
```
### 🧪 Test plan

All nine entries run in CI: they only touch raylib's internal gesture state, so no window, GPU or injected input is needed (verified with `pengu test` on a headless run). Three tests per public function, plus the documented caveats:

- **`enable`**: a single kind enables without error; a two-kind slice enables both; an empty slice is a no-op; ORing is idempotent when the same kind is listed twice.
- **`disable`**: disabling after enabling leaves `is_detected` false; calling it twice is a no-op; `detected` still returns a valid code afterwards.
- **`is_detected`**: false before any event even when the kind is enabled (the C check ANDs against the current gesture); false for a kind that was never enabled; true only when the current gesture matches an enabled kind (documented as requiring injected input, not asserted in CI).
- **`detected`**: returns `GESTURE_NONE` (`0`) before any event; the returned code is one of the `raylib.GESTURE_*` values; a fresh call does not change the enabled flags.
- **`hold_seconds`**: `0` before any event; non-negative; finite.
- **`drag_direction`**: `(0, 0)` before any event; both lanes finite; not aliased to `pinch_delta`.
- **`drag_angle`**: `0` before any event; finite; units documented as radians.
- **`pinch_delta`**: `(0, 0)` before any event; both lanes finite; independent of `drag_direction`.
- **`pinch_angle`**: `0` before any event; finite; units documented as radians.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `ProcessGestureEvent` | D4: the binding flattens `int pointId[8]` and `Vector2 position[8]` to one lane each, so 7 of 8 touch points of each array can never be set from PenguScript. Passing it by value would always describe a single-touch event. Binding defect: regenerate `rgestures.d.pengu` so the two fields keep their array shape. |
| `UpdateGestures` | D5: a `void` one-liner already driven by raylib's input pump; wrapping it gains neither tokens nor clarity (contract §9 criterion 1). |
| `SetGesturesEnabled` (raylib binding) | **Wrapped** as `enable` / `disable` (D7). |
| `IsGestureDetected` (raylib binding) | **Wrapped** as `is_detected` (D10). |
| `GetGestureDetected` (raylib binding) | **Wrapped** as `detected`; returns `int` by design (D6). |
| `GetGestureHoldDuration`, `GetGestureDragVector`, `GetGestureDragAngle`, `GetGesturePinchVector`, `GetGesturePinchAngle` (raylib binding) | **Wrapped** as `hold_seconds`, `drag_direction`, `drag_angle`, `pinch_delta`, `pinch_angle` (D9). |
| `rgestures.SetGesturesEnabled`, `rgestures.IsGestureDetected`, `rgestures.GetGesture*` | Do **not exist** in this build: they are declared only under `RGESTURES_STANDALONE` (`include/rgestures.h:128-137`). Depending on them would reference symbols the linked library does not export (D1, D2). |
| `GestureEvent.pointId[1..7]`, `GestureEvent.position[1..7]` | Unreachable from PenguScript: the binding declares a single scalar lane for each (D4). |
| `TouchAction` omen | Not wrapped, and not re-declared: it is part of the binding and stays reachable through `import rgestures`. It belongs to the unusable `GestureEvent` path. |
| `MAX_TOUCH_POINTS`, `PI` | Not wrapped: plain constants already exported by `rgestures.d.pengu`; re-exporting them adds a second name for the same value (contract §2). |
| The 7 constants inside `RGESTURES_IMPLEMENTATION` (`FORCE_TO_SWIPE`, `MINIMUM_DRAG`, `DRAG_TIMEOUT`, `MINIMUM_PINCH`, `TAP_TIMEOUT`, `PINCH_TIMEOUT`, `DOUBLETAP_RANGE`) | Do not exist in a consumer translation unit, so the binding does not export them. Tuning them means recompiling raylib, not wrapping. |

Coverage audit: of the 2 functions declared in `rgestures.d.pengu`, **0 are wrapped** (`ProcessGestureEvent` and `UpdateGestures` are both excluded, D4/D5) — which is the correct outcome, because neither is usable or useful from PenguScript. Of the 8 gesture functions declared in `raylib.d.pengu`, **8 are wrapped** across 9 entries (`disable` shares `SetGesturesEnabled` with `enable`).

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/rgestures.d.pengu`
- Wrapper destino: `pengu/rgesturesx.pengu`
- Dependencias: `import raylib`, `import rgestures`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo** para lo que el header exporta a una unidad de traducción normal. `rgestures.h` tiene exactamente 2 declaraciones de función incondicionales — `ProcessGestureEvent`, `UpdateGestures` — y el binding declara ambas. | `SetGesturesEnabled`, `IsGestureDetected` y los cinco getters están tras `#if defined(RGESTURES_STANDALONE)` (`include/rgestures.h:128-137`), así que **no** forman parte de la API de un consumidor de raylib. En esa compilación son de raylib, y `pengu/raylib.d.pengu:1158-1172` las declara. |
| D2 | La superficie usable de gestos vive en **`raylib.d.pengu`**, no en `rgestures.d.pengu`. `rgesturesx` envuelve la API de gestos de raylib e importa ambos bindings. | Es el primer wrapper cuya superficie útil no es su binding homónimo. No es un rodeo: en cualquier programa que enlace raylib (la única configuración soportada; `raylib.d.pengu` es el que emite `include "raylib.h"`), `SetGesturesEnabled`/`IsGestureDetected`/`GetGesture*` son los símbolos de raylib. Envolver las copias de `rgestures` bajo `RGESTURES_STANDALONE` sería incorrecto: no las exporta la biblioteca que este proyecto enlaza. |
| D3 | **Sin bloques `enchanting`.** Las nueve entradas son `weave` de módulo. | Contrato §6.1: el sujeto es estado global de entrada, no un receptor. `calling rgesturesx.is_detected with …` se lee bien; no hay tipo que encantar. `GestureEvent` es el único `rune` del binding y es inusable (D4), así que la sección de enchantings queda vacía por diseño. |
| D4 | `ProcessGestureEvent` **no se envuelve**. `GestureEvent.pointId` y `.position` se declaran como **escalares**, pero en C son `int pointId[8]` y `Vector2 position[8]`; 7 de las 8 posiciones de cada array no se pueden escribir desde PenguScript. | `include/rgestures.h:105-110` define el struct con dos arrays de 8 elementos; `pengu bind` los aplanó a un solo carril cada uno. Un wrapper solo podría transmitir un punto de toque, y el multi-toque es exactamente para lo que existe la función. Es un defecto del binding (declaración incompleta), así que se reporta en vez de rodearlo: el contrato §1 prohíbe que el wrapper añada `declare`. |
| D5 | `UpdateGestures` **tampoco se envuelve**. | Es `void UpdateGestures(void)`, un tick de una línea, y raylib ya lo llama desde su propio bombeo de entrada en el flujo normal. Un wrapper sería un alias puro sin ganancia de nombre ni de tokens (contrato §9, criterio 1). |
| D6 | `detected` devuelve el código `int` crudo, no un `Gesture`. | `GetGestureDetected` devuelve `GESTURE_NONE` (`0`) cuando no hay nada activo, así que un retorno `Gesture` tendría que colar un valor "nada" dentro del tipo. `maybe Gesture` modelaría eso correctamente, pero el cast de `int` a `Gesture` en runtime se rechaza (`E0005: Cannot cast 'int' to 'Gesture'`, verificado), y despachar las once variantes con `judge` no aporta nada sobre comparar el código. El llamador compara contra `raylib.GESTURE_*`, que son constantes enteras. |
| D7 | `enable` recibe `slice of raylib.Gesture` y lo pliega en la máscara `u32` que quiere la API C; `disable` pasa `0`. | La palabra de flags no tiene tipo propio en el binding, y un literal de array no se puede pasar en posición de argumento (verificado: `E0005: Array literal cannot be passed directly`), así que la forma con slice es la que funciona en el sitio de llamada: `calling rgesturesx.enable with (kinds at 0 to 2)`. |
| D8 | Los flags se combinan con `\|`, nunca con `or`. | `SetGesturesEnabled` recibe una máscara `u32`; `or` es solo booleano en PenguScript (`E0005: Logical operator 'or' requires bool, got 'u32'`, verificado). |
| D9 | Los nombres llevan su unidad: `hold_seconds`, `drag_angle`, `pinch_angle`; los vectores son `drag_direction` y `pinch_delta`. | Contrato §2: `Get*` sin receptor pasa a sustantivo de módulo. La unidad importa porque la API mezcla radianes (`*Angle`) con un vector (`*Vector`), y el vector de pinch es un *delta*, no una dirección. |
| D10 | Se envuelven los cinco getters y los dos predicados; nada se renombra a `get_*`. | Ninguno forma pareja `@mutates`: todos devuelven un valor y dejan intacto el estado global, así que no hay forma mutante ni `get_*` generado (contrato §4). |
| D11 | El wrapper no habilita gestos ni inicializa nada al cargarse. | Contrato §9: la configuración global de un solo uso se queda en el sitio de llamada. `enable`/`disable` son explícitos y el usuario decide cuándo. |

### ✨ Enchantings

**Ninguno aplica.** El único `rune` del binding es `GestureEvent`, y pasarlo es inseguro desde PenguScript (D4); el resto de símbolos de gestos son funciones libres sobre estado global de entrada, así que no hay receptor que encantar (D3). El `omen` `TouchAction` sigue disponible con `import rgestures` para quien construya a mano un `GestureEvent` parcial.

### 🔧 Funciones a nivel de módulo

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `enable` | `with gestures as slice of raylib.Gesture into void` | `raylib.SetGesturesEnabled` | hace OR del slice en la palabra de flags; un slice vacío no hace nada |
| `disable` | `into void` | `raylib.SetGesturesEnabled` | pasa `0` |
| `is_detected` | `with kind as raylib.Gesture into bool` | `raylib.IsGestureDetected` | la comprobación C es `(enabledFlags & current) == kind`, así que ya cubre combinaciones |
| `detected` | `into int` | `raylib.GetGestureDetected` | `0` = `GESTURE_NONE`; compara contra `raylib.GESTURE_*` (D6) |
| `hold_seconds` | `into f32` | `raylib.GetGestureHoldDuration` | segundos |
| `drag_direction` | `into raylib.Vector2` | `raylib.GetGestureDragVector` | `(0, 0)` si no hay arrastre activo |
| `drag_angle` | `into f32` | `raylib.GetGestureDragAngle` | radianes |
| `pinch_delta` | `into raylib.Vector2` | `raylib.GetGesturePinchVector` | delta de pinch, no una dirección |
| `pinch_angle` | `into f32` | `raylib.GetGesturePinchAngle` | radianes |

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** Ningún punto de entrada de gestos puede fallar por un recurso externo: todos leen estado que raylib guarda en su propio proceso, y todos son seguros de llamar antes de que exista ventana o entrada (verificado sin display: devuelven `0` / `(0, 0)` en lugar de fallar). El único sitio donde la ausencia es real — "no hay ningún gesto activo" — lo modela el retorno `0` de `detected` (D6), no un `maybe`, porque el llamador compara un código `int` en vez de desenvolver un contenedor.

### ✂️ Wrappers de `slice`

**Ninguno aplica como reconstrucción de puntero y recuento.** Un punto de entrada *acepta* un slice (`enable`), pero no es la forma C `(T* ptr, int count)` del contrato §5: el wrapper pliega el slice en una sola máscara `u32` y llama `SetGesturesEnabled with flags`. No hay puntero que reconstruir ni recuento que pasar, así que no intervienen ni `std.ffi` ni `transmute`.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Cada función devuelve un valor o nada. El candidato más cercano, "el tipo de gesto activo", es un único `int` (D6); los pares de arrastre y pinch son dos getters independientes con tipos distintos y sin tiempo de vida compartido, así que una tupla inventaría una relación que la API no tiene.

### 🌉 Uso de `std.ffi`

**Ninguno aplica, motivo: la API de gestos es numérica y por valor.** Las nueve entradas pasan `u32`, `bool`, `int`, `f32` y `Vector2`; no hay `char*`, ni `void*`, ni puntero que el wrapper tenga que reinterpretar. Por tanto `import std.ffi` **no** figura en las dependencias.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — habilitar un conjunto de gestos y leer uno de vuelta
import raylib
import rgesturesx

weave main into int:
    var kinds as array of raylib.Gesture with size 2 is [raylib.GESTURE_TAP, raylib.GESTURE_DRAG]
    calling rgesturesx.enable with (kinds at 0 to 2)
    var tapped as bool is calling rgesturesx.is_detected with raylib.GESTURE_TAP
    var kind as int is calling rgesturesx.detected
    if tapped:
        return 1
    calling rgesturesx.disable
    return kind
```

```pengu
# Ejemplo 2 — leer el estado de arrastre y pinch en cada frame
import raylib
import rgesturesx

weave sample_drag into raylib.Vector2:
    return calling rgesturesx.drag_direction

weave main into int:
    var direction as raylib.Vector2 is calling sample_drag
    var angle as f32 is calling rgesturesx.drag_angle
    var pinch as raylib.Vector2 is calling rgesturesx.pinch_delta
    var pinch_angle as f32 is calling rgesturesx.pinch_angle
    var held as f32 is calling rgesturesx.hold_seconds
    return 0
```
### 🧪 Plan de tests

Las nueve entradas se ejecutan en CI: solo tocan el estado interno de gestos de raylib, así que no hacen falta ventana, GPU ni entrada inyectada (verificado con `pengu test` en una ejecución sin display). Tres tests por función pública, más las advertencias documentadas:

- **`enable`**: habilitar un tipo no da error; un slice de dos tipos habilita ambos; un slice vacío no hace nada; el OR es idempotente si el mismo tipo se repite.
- **`disable`**: deshabilitar tras habilitar deja `is_detected` en falso; llamarlo dos veces no hace nada; `detected` sigue devolviendo un código válido después.
- **`is_detected`**: falso antes de cualquier evento aunque el tipo esté habilitado (la comprobación C hace AND contra el gesto actual); falso para un tipo nunca habilitado; verdadero solo cuando el gesto actual coincide con uno habilitado (documentado como dependiente de entrada inyectada, no se asegura en CI).
- **`detected`**: devuelve `GESTURE_NONE` (`0`) antes de cualquier evento; el código devuelto es uno de los `raylib.GESTURE_*`; una llamada nueva no altera los flags habilitados.
- **`hold_seconds`**: `0` antes de cualquier evento; no negativo; finito.
- **`drag_direction`**: `(0, 0)` antes de cualquier evento; ambos carriles finitos; no aliaseado con `pinch_delta`.
- **`drag_angle`**: `0` antes de cualquier evento; finito; unidades documentadas como radianes.
- **`pinch_delta`**: `(0, 0)` antes de cualquier evento; ambos carriles finitos; independiente de `drag_direction`.
- **`pinch_angle`**: `0` antes de cualquier evento; finito; unidades documentadas como radianes.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `ProcessGestureEvent` | D4: el binding aplana `int pointId[8]` y `Vector2 position[8]` a un carril cada uno, así que 7 de 8 puntos de toque de cada array nunca se pueden fijar desde PenguScript. Pasarlo por valor describiría siempre un evento de un solo toque. Defecto del binding: regenerar `rgestures.d.pengu` para que los dos campos conserven su forma de array. |
| `UpdateGestures` | D5: un `void` de una línea que raylib ya ejecuta desde su bombeo de entrada; envolverlo no da ni tokens ni claridad (contrato §9, criterio 1). |
| `SetGesturesEnabled` (binding de raylib) | **Envuelto** como `enable` / `disable` (D7). |
| `IsGestureDetected` (binding de raylib) | **Envuelto** como `is_detected` (D10). |
| `GetGestureDetected` (binding de raylib) | **Envuelto** como `detected`; devuelve `int` a propósito (D6). |
| `GetGestureHoldDuration`, `GetGestureDragVector`, `GetGestureDragAngle`, `GetGesturePinchVector`, `GetGesturePinchAngle` (binding de raylib) | **Envuelvos** como `hold_seconds`, `drag_direction`, `drag_angle`, `pinch_delta`, `pinch_angle` (D9). |
| `rgestures.SetGesturesEnabled`, `rgestures.IsGestureDetected`, `rgestures.GetGesture*` | **No existen** en esta compilación: solo se declaran bajo `RGESTURES_STANDALONE` (`include/rgestures.h:128-137`). Depender de ellas referenciaría símbolos que la biblioteca enlazada no exporta (D1, D2). |
| `GestureEvent.pointId[1..7]`, `GestureEvent.position[1..7]` | Inalcanzables desde PenguScript: el binding declara un único carril escalar para cada uno (D4). |
| `omen TouchAction` | No se envuelve ni se redeclara: es parte del binding y sigue accesible con `import rgestures`. Pertenece a la ruta inusable de `GestureEvent`. |
| `MAX_TOUCH_POINTS`, `PI` | No se envuelven: son constantes planas que `rgestures.d.pengu` ya exporta; reexportarlas añade un segundo nombre para el mismo valor (contrato §2). |
| Las 7 constantes dentro de `RGESTURES_IMPLEMENTATION` (`FORCE_TO_SWIPE`, `MINIMUM_DRAG`, `DRAG_TIMEOUT`, `MINIMUM_PINCH`, `TAP_TIMEOUT`, `PINCH_TIMEOUT`, `DOUBLETAP_RANGE`) | No existen en una unidad de traducción de consumidor, así que el binding no las exporta. Ajustarlas implica recompilar raylib, no envolver. |

Auditoría de cobertura: de las 2 funciones declaradas en `rgestures.d.pengu`, **0 se envuelven** (`ProcessGestureEvent` y `UpdateGestures` quedan fuera, D4/D5) — que es el resultado correcto, porque ninguna es usable ni útil desde PenguScript. De las 8 funciones de gestos declaradas en `raylib.d.pengu`, **8 se envuelven** en 9 entradas (`disable` comparte `SetGesturesEnabled` con `enable`).
