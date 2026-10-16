# Plan: input.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/input.pengu`
- Owner in the master plan: family `input` of `docs/plans/raylibx.md` (v0.1.2), eleventh in its order of implementation (brought forward)
- Dependencies: `import raylib`, `import std.ffi` (only for the two name getters)
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete and all 47 exported**. The header's "Input Handling Functions" and "Gestures and Touch Handling" sections hold exactly 47 functions and `tools/check_binding_symbols.py` confirms every one is exported by the installed library 6.0.0. **No version gap.** | Enumerated from the header sections and cross-checked against the dynamic symbols. |
| D2 | **The value of this family is type restoration, and nothing else is wrapped.** The binding flattens **every** enum parameter to `int` (`key as int`, `button as int`, `gamepad as int`, `axis as int`, `cursor as int`, `gesture as u32`, `flags as u32`). The wrapper restores `raylib.KeyboardKey`, `raylib.MouseButton`, `raylib.GamepadButton`, `raylib.GamepadAxis`, `raylib.MouseCursor` and `raylib.Gesture`, so `is_key_down with raylib.KEY_SPACE` replaces `raylib.IsKeyDown with (raylib.KEY_SPACE to int)`. | Contract §9's "already a `bool` predicate" row would otherwise rule these out, but the flattened enum is a real **boundary crossing** of the same kind as `const char*` → `string` in `files`, and it is the same justification the `files` plan used for wrapping `FileExists`. | **Corrected in v0.1.3, after measuring it:** the restoration is **documentation and a shorter call, not enforcement**. A parameter typed `raylib.KeyboardKey` accepts `raylib.MOUSE_BUTTON_LEFT` and even a raw `42` without a diagnostic (verified in a minimal probe on `pengu 2.4.0`), so the enum name states the intent and removes the explicit cast, but the checker will not catch a wrong enum. The family's value is therefore the shorter, self-documenting call -- which is what criterion 1 asks for -- and not type safety.
| D3 | **28 of the 47 are wrapped and 19 are skipped**, and the skip rule is mechanical: a function is wrapped only if it crosses a type boundary (D2) or has a failure sentinel (D5). A zero-argument getter that cannot fail is **not** wrapped, exactly as contract §9 requires ("el binding ya es una llamada clara; envolver solo añade un salto"). | Contract §9 rows 1 and 160, and §9's ordering row 417, which names `GetScreenWidth`, `GetMonitorCount` and `GetTouchPointCount`. This is why `mouse_position`, `mouse_delta`, the wheel getters, `touch_x`, `touch_y`, `touch_position`, `touch_point_count` and the five gesture value getters are absent from the wrapper: wrapping them would be a rename with a jump. The master plan's family description listed `GetMouse*`/`GetTouch*`/`GetGesture*`; this plan narrows that deliberately and records it. |
| D4 | No enchantings. Everything is a module-level function. | The master plan's registry closed `Vector2` (to `shapes`) and `Vector3` (to `shapes3d`), so no getter can become a method on the type it returns, and the input functions have no `raylib` type as their subject anyway. |
| D5 | The failure sentinels are wrapped as `maybe`, and each was **measured**, not assumed: `key_pressed`, `char_pressed`, `gamepad_button_pressed`, `touch_point_id` and `detected_gesture` → `maybe int`; `key_name` → `maybe string`. | Contract §3. Measured headless: `GetKeyPressed()` returns `0` (which is `KEY_NULL`), `GetCharPressed()` returns `0`, `GetTouchPointId(0)` returns `0` for a valid index and `-1` for an out-of-range one (`rcore.c`), and `GetKeyName` returns **`NULL`** — even for `KEY_A`, without a window. `GetGamepadButtonPressed()` returns `GAMEPAD_BUTTON_UNKNOWN`, which is **`0`**, not `-1` — the wrapper's predicate is `<= 0`. |
| D6 | `gamepad_name` returns a plain `string`, **not** `maybe string`. | Measured: `GetGamepadName(0)` returns a non-null **empty** string when no gamepad is connected, never `NULL` (`rcore.c` returns `CORE.Input.Gamepad.name[gamepad]`). A `maybe` would invent a failure that cannot happen. |
| D7 | `detected_gesture` returns `maybe int`, not `maybe raylib.Gesture`. | The int → enum direction is not expressible: `(raw to raylib.Gesture)` is a syntax error, and `transmute raw to raylib.Gesture` makes `pengu 2.4.0` emit `((raylib.Gesture)(raw))` — **invalid C**, because the compiler prints qualified type names (master plan D19, and the same defect `shapes` and `text` hit). The wrapper therefore returns the raw ordinal and the docstring gives the comparison idiom `g == (raylib.GESTURE_TAP to int)`, which is verified to work. |
| D8 | `enable_gestures` takes `slice of raylib.Gesture` and ORs the flags into the `u32` the binding wants. | Inherited from the archived `rgesturesx`: an array literal cannot be passed in argument position (`E0005`), and `or` cannot combine `u32` flags (`E0005: Logical operator 'or' requires bool, got 'u32'`), so the bits are combined with `|` in a loop. A single-gesture call is `enable_gestures with (list of raylib.Gesture)`. |
| D9 | The three mouse setters take a `raylib.Vector2` instead of the binding's loose coordinates: `set_mouse_position with position`, `set_mouse_offset with offset`, `set_mouse_scale with scale`. | They pair with the shape of the data the caller already has. `SetMousePosition`/`SetMouseOffset` take `int` components (the wrapper converts with `to int`), `SetMouseScale` takes `f32`. This is a parameter type, not a `Vector2` method, so the registry is respected (D4). |
| D10 | `SetExitKey` is **not wrapped**. | Master plan D14 classifies it as one-shot global configuration. It is recorded here rather than silently dropped, and this is the one place where the family would gain from being allowed an exception: see the note below. |
| D11 | No `slice` wrappers other than `enable_gestures`, no multiple returns, and `std.ffi` only for the two name getters. | The family is scalars, booleans and small structs. |

> **The `SetExitKey` question (D10).** The master plan puts it in the "one-shot global configuration" bucket with `SetConfigFlags` and `SetTraceLogLevel`. That grouping is defensible for config flags but weaker here: `SetExitKey` takes a `KeyboardKey`, so it is exactly the enum-restoration case that justifies the rest of this family, and a user who binds quit to Esc has to write `raylib.SetExitKey with (raylib.KEY_ESCAPE to int)`. I have followed the master plan rather than overriding it, and I am flagging it because it is a one-line change to add `set_exit_key with key as raylib.KeyboardKey into void` if the reviewer prefers.

| D12 | A **measurable asymmetry** in the `_up` predicates, recorded so nobody "fixes" it: with nothing happening, `is_key_up` and `is_mouse_button_up` are **`true`** (nothing is held), but all four `is_gamepad_button_*` are **`false`**, including `_up`, because raylib gates them on the gamepad being available. | Measured in C headless: `IsKeyUp(KEY_A) == 1`, `IsMouseButtonUp(LEFT) == 1`, and `IsGamepadButtonDown/Up/Pressed/Released(0, …)` are all `0`. The tests assert exactly that, and the docstrings of the gamepad predicates say an absent gamepad reports `false`. | **Measured later, through the facade, and it completes the picture:** the asymmetry is not a constant. With no window ever created, `IsGamepadAvailable(0)` is `false` and all four predicates are `false`; once GLFW has been initialised by any window, the real controller at `/dev/input/js0` becomes available, `is_gamepad_button_up` turns **`true`** for an unpressed button, `gamepad_name` returns the controller's name and a resting axis reads **`-0.0117647`** rather than `0.0` — which is exactly why dead zones exist. The family's tests branch on `IsGamepadAvailable` instead of assuming either state.

### ✨ Enchantings

**None.** See D4.

### 🔧 Module-level functions

#### Keyboard (8)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `is_key_pressed` | `with key as raylib.KeyboardKey into bool` | `IsKeyPressed` | |
| `is_key_pressed_repeat` | `with key as raylib.KeyboardKey into bool` | `IsKeyPressedRepeat` | true while the key auto-repeats |
| `is_key_down` | `with key as raylib.KeyboardKey into bool` | `IsKeyDown` | |
| `is_key_released` | `with key as raylib.KeyboardKey into bool` | `IsKeyReleased` | |
| `is_key_up` | `with key as raylib.KeyboardKey into bool` | `IsKeyUp` | |
| `key_pressed` | `into maybe int` | `GetKeyPressed` | `maybe none` when the queue is empty (`0` is `KEY_NULL`); compare with `(raylib.KEY_A to int)` |
| `char_pressed` | `into maybe int` | `GetCharPressed` | `maybe none` when there is no pending character; the value is a codepoint |
| `key_name` | `with key as raylib.KeyboardKey into maybe string` | `GetKeyName` | `maybe none` when raylib returns `NULL` (measured: it does so even for `KEY_A` without a window) |

#### Gamepad (8)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `is_gamepad_button_pressed` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonPressed` | `gamepad` is raylib's slot index `0..3`, not an enum |
| `is_gamepad_button_down` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonDown` | |
| `is_gamepad_button_released` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonReleased` | |
| `is_gamepad_button_up` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonUp` | |
| `gamepad_button_pressed` | `into maybe int` | `GetGamepadButtonPressed` | `maybe none` for `GAMEPAD_BUTTON_UNKNOWN`, which is `0` |
| `gamepad_axis_movement` | `with gamepad as int, axis as raylib.GamepadAxis into f32` | `GetGamepadAxisMovement` | `[-1..1]` |
| `gamepad_name` | `with gamepad as int into string` | `GetGamepadName` | empty string when no gamepad is connected (D6) |
| `set_gamepad_mappings` | `with mappings as string into int` | `SetGamepadMappings` | returns the number of mappings added; raylib does not document the failure value |

#### Mouse (8)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `is_mouse_button_pressed` | `with button as raylib.MouseButton into bool` | `IsMouseButtonPressed` | |
| `is_mouse_button_down` | `with button as raylib.MouseButton into bool` | `IsMouseButtonDown` | |
| `is_mouse_button_released` | `with button as raylib.MouseButton into bool` | `IsMouseButtonReleased` | |
| `is_mouse_button_up` | `with button as raylib.MouseButton into bool` | `IsMouseButtonUp` | |
| `set_mouse_position` | `with position as raylib.Vector2 into void` | `SetMousePosition` | components are truncated to `int` (D9) |
| `set_mouse_offset` | `with offset as raylib.Vector2 into void` | `SetMouseOffset` | components are truncated to `int` |
| `set_mouse_scale` | `with scale as raylib.Vector2 into void` | `SetMouseScale` | takes the `f32` components directly |
| `set_mouse_cursor` | `with cursor as raylib.MouseCursor into void` | `SetMouseCursor` | |

#### Touch (1)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `touch_point_id` | `with index as int into maybe int` | `GetTouchPointId` | `maybe none` for an out-of-range index (raylib returns `-1`) |

#### Gestures (3)

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `enable_gestures` | `with gestures as slice of raylib.Gesture into void` | `SetGesturesEnabled` | ORs the flags (D8); an empty slice disables every gesture |
| `is_gesture_detected` | `with gesture as raylib.Gesture into bool` | `IsGestureDetected` | |
| `detected_gesture` | `into maybe int` | `GetGestureDetected` | `maybe none` for `GESTURE_NONE`; see D7 for why it is an `int` |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `key_pressed` | `maybe int` | raylib returns `0`, which is `KEY_NULL` |
| `char_pressed` | `maybe int` | raylib returns `0` |
| `gamepad_button_pressed` | `maybe int` | raylib returns `GAMEPAD_BUTTON_UNKNOWN`, measured to be `0` |
| `touch_point_id` | `maybe int` | raylib returns `-1` for an index past `MAX_TOUCH_POINTS` |
| `detected_gesture` | `maybe int` | raylib returns `GESTURE_NONE` (`0`) |
| `key_name` | `maybe string` | raylib returns `NULL` |

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `enable_gestures` | `gestures as slice of raylib.Gesture` |

One guard: an empty slice enables nothing, which is also how the caller disables every gesture. The flags are combined with `|`, never with `or` (D8).

### 📦 Multiple returns `(T, U)`

**None apply.** Every function returns one scalar, one boolean, one `Vector2` or one `string`.

### 🌉 `std.ffi` usage

Only the two name getters cross a string boundary: `key_name` and `gamepad_name` copy a raylib-owned `const char*` with `ffi.string_from_cstr` and free nothing. `key_name` additionally null-checks with `ffi.is_null`, and its `transmute` to `ref to char` is the documented widening.

### 💡 Compilable examples

```pengu
# Example 1 — the type-restoration win
import raylib
import raylibx.input as input

weave main into int:
    var jump as bool is calling input.is_key_pressed with raylib.KEY_SPACE
    var firing as bool is calling input.is_mouse_button_down with raylib.MOUSE_BUTTON_LEFT
    var pad as bool is calling input.is_gamepad_button_down with 0, raylib.GAMEPAD_BUTTON_RIGHT_FACE_DOWN
    var axis as f32 is calling input.gamepad_axis_movement with 0, raylib.GAMEPAD_AXIS_LEFT_X
    var tapped as bool is calling input.is_gesture_detected with raylib.GESTURE_TAP
    return 0
```

```pengu
# Example 2 — the sentinel wrappers and the comparison idiom
import raylib
import raylibx.input as input

weave main into int:
    var typed as maybe int is calling input.key_pressed
    if typed is present:
        var k as int is calling typed.unwrap
        if k == (raylib.KEY_ESCAPE to int):
            return 1
    var name as maybe string is calling input.key_name with raylib.KEY_A
    var who as string is calling input.gamepad_name with 0
    var gesture as maybe int is calling input.detected_gesture
    return 0
```

```pengu
# Example 3 — the setters and the gesture flag slice
import raylib
import raylibx.input as input

weave main into int:
    var gestures as list of raylib.Gesture is list of raylib.Gesture
    defer banish gestures
    calling gestures.push with raylib.GESTURE_TAP
    calling gestures.push with raylib.GESTURE_DRAG
    calling input.enable_gestures with (gestures at 0 to (gestures.length))
    calling input.set_mouse_position with (with x is 100.0, y is 100.0)
    calling input.set_mouse_scale with (with x is 1.0, y is 1.0)
    calling input.set_mouse_cursor with raylib.MOUSE_CURSOR_CROSSHAIR
    return 0
```

### 🧪 Test plan

This is the **second family with a genuinely large CI-testable surface**, and unlike `text` none of it needs a window or a loaded resource: with no input happening, every predicate is `false`, every sentinel wrapper is `maybe none` and every getter returns a default. That makes the *negative* path the assertion, which is exactly the path a unit test can pin.

- **The 14 enum predicates** (`is_key_*`, `is_mouse_button_*`, `is_gamepad_button_*`, `is_gesture_detected`): each is asserted `false` headless with a real enum value, which proves both the type and the conversion. Three keys, two mouse buttons, two gamepad buttons and one gesture per predicate.
- **`key_pressed` / `char_pressed`**: `maybe none` when nothing is queued; two consecutive calls are both `none` (the queue does not invent values).
- **`gamepad_button_pressed`**: `maybe none` with no gamepad.
- **`touch_point_id`**: `maybe none` for an out-of-range index (`1000`) and `some 0` for index `0`, which is the measured distinction between "invalid index" and "valid index with id 0".
- **`detected_gesture`**: `maybe none` when no gesture is in progress.
- **`key_name`**: `maybe none` headless (measured); the docstring records that the same call returns a name once a window exists.
- **`gamepad_name`**: an empty string, **not** `maybe none`, with no gamepad connected (D6).
- **`set_gamepad_mappings`**: returns an `int` for an empty string and for a malformed mapping without crashing; the value is asserted to be non-negative rather than to a specific number, because raylib does not document it.
- **`set_mouse_position` / `set_mouse_offset` / `set_mouse_scale` / `set_mouse_cursor`**: callable headless without crashing; the assertion is that the call returns (`void`) and that a subsequent `raylib.GetMousePosition` still answers a finite `Vector2`. These mutate input state, so they are the closest this family gets to a side effect, and the test records that.
- **`enable_gestures`**: an empty slice is a no-op that does not read element zero; a two-element slice is accepted and `is_gesture_detected` stays `false` because nothing happened.
- **`gamepad_axis_movement`**: returns `0.0` for both axes of an absent gamepad.
- **Compile-only probe**: the two `maybe int` returns and the `maybe string` are additionally type-checked by a small `input_api_probe` that references every wrapped entry, so no signature can rot unnoticed.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `GetMouseX`, `GetMouseY` | zero-argument getter that cannot fail; `GetMousePosition` already gives both (contract §9, and `mouse_position` is itself skipped for the same reason below) |
| `GetMousePosition`, `GetMouseDelta` | zero-argument getter that cannot fail; the binding call is already clear (contract §9 rows 1 and 417) |
| `GetMouseWheelMove`, `GetMouseWheelMoveV` | same |
| `GetTouchX`, `GetTouchY`, `GetTouchPosition` | same, plus `GetTouchPointCount` is one of the three functions the contract names explicitly in §9 |
| `GetTouchPointCount` | named in contract §9 as the canonical "do not wrap" getter |
| `GetGestureHoldDuration`, `GetGestureDragVector`, `GetGestureDragAngle`, `GetGesturePinchVector`, `GetGesturePinchAngle` | zero-argument getters that cannot fail |
| `IsGamepadAvailable` | predicate that is already `bool` and takes no enum (the gamepad slot is a plain `int`); nothing to restore |
| `GetGamepadAxisCount` | query with an argument that cannot fail and carries no enum |
| `SetGamepadVibration` | setter that crosses no type boundary and has no failure channel; its four loose arguments are already clear at the call site |
| `SetExitKey` | master plan D14 (one-shot global configuration); see the note under D10 |

Coverage audit: of the 47 input-and-gesture functions, **28 are wrapped** (all module-level, no enchantings) and **19 are not**: 17 for the trivial-rename reason in D3, `SetGamepadVibration` for the same reason (it crosses no boundary either), and `SetExitKey` for D10. Every wrapped symbol is exported by the installed library.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/input.pengu`
- Dueña en el plan maestro: familia `input` de `docs/plans/raylibx.md` (v0.1.2), undécima en su orden de implementación (adelantada)
- Dependencias: `import raylib`, `import std.ffi` (solo para los dos getters de nombre)
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo y las 47 exportadas**. Las secciones "Input Handling Functions" y "Gestures and Touch Handling" del header tienen exactamente 47 funciones y `tools/check_binding_symbols.py` confirma que la biblioteca 6.0.0 instalada las exporta todas. **Sin desfase de versión.** | Enumerado desde las secciones del header y cruzado con los símbolos dinámicos. |
| D2 | **El valor de esta familia es restaurar tipos, y no se envuelve nada más.** El binding aplana **todos** los parámetros de enum a `int` (`key as int`, `button as int`, `gamepad as int`, `axis as int`, `cursor as int`, `gesture as u32`, `flags as u32`). El wrapper restaura `raylib.KeyboardKey`, `raylib.MouseButton`, `raylib.GamepadButton`, `raylib.GamepadAxis`, `raylib.MouseCursor` y `raylib.Gesture`, así que `is_key_down with raylib.KEY_SPACE` sustituye a `raylib.IsKeyDown with (raylib.KEY_SPACE to int)`. | La fila del contrato §9 sobre "predicados que ya son `bool`" los descartaría, pero el enum aplanado es una **frontera real** de la misma clase que `const char*` → `string` en `files`, y es la misma justificación que el plan de `files` usó para envolver `FileExists`. | **Corregido en v0.1.3, después de medirlo:** la restauración es **documentación y una llamada más corta, no comprobación**. Un parámetro tipado `raylib.KeyboardKey` acepta `raylib.MOUSE_BUTTON_LEFT` y hasta un `42` crudo sin diagnóstico (verificado en una sonda mínima sobre `pengu 2.4.0`), así que el nombre del enum declara la intención y quita el cast explícito, pero el comprobador no detectará un enum equivocado. El valor de la familia es por tanto la llamada más corta y autodocumentada —que es lo que pide el criterio 1— y no la seguridad de tipos.
| D3 | **Se envuelven 28 de las 47 y se omiten 19**, y la regla de omisión es mecánica: una función se envuelve solo si cruza una frontera de tipo (D2) o tiene un centinela de fallo (D5). Un getter sin argumentos que no puede fallar **no** se envuelve, exactamente como exige el contrato §9 ("el binding ya es una llamada clara; envolver solo añade un salto"). | Filas 1 y 160 del contrato §9, y su fila de orden 417, que nombra `GetScreenWidth`, `GetMonitorCount` y `GetTouchPointCount`. Por eso faltan del wrapper `mouse_position`, `mouse_delta`, los getters de la rueda, `touch_x`, `touch_y`, `touch_position`, `touch_point_count` y los cinco getters de valores de gestos: envolverlos sería un renombrado con salto. La descripción de familia del plan maestro listaba `GetMouse*`/`GetTouch*`/`GetGesture*`; este plan la estrecha a propósito y lo registra. |
| D4 | Sin enchantings. Todo son funciones de módulo. | El registro del plan maestro cerró `Vector2` (para `shapes`) y `Vector3` (para `shapes3d`), así que ningún getter puede ser método del tipo que devuelve, y las funciones de entrada no tienen de todos modos ningún tipo de `raylib` como sujeto. |
| D5 | Los centinelas de fallo se envuelven como `maybe`, y cada uno se **midió**, no se asumió: `key_pressed`, `char_pressed`, `gamepad_button_pressed`, `touch_point_id` y `detected_gesture` → `maybe int`; `key_name` → `maybe string`. | Contrato §3. Medido sin ventana: `GetKeyPressed()` devuelve `0` (que es `KEY_NULL`), `GetCharPressed()` devuelve `0`, `GetTouchPointId(0)` devuelve `0` para un índice válido y `-1` para uno fuera de rango (`rcore.c`), y `GetKeyName` devuelve **`NULL`** — incluso para `KEY_A`, sin ventana. `GetGamepadButtonPressed()` devuelve `GAMEPAD_BUTTON_UNKNOWN`, que es **`0`**, no `-1` — el predicado del wrapper es `<= 0`. |
| D6 | `gamepad_name` devuelve un `string` simple, **no** `maybe string`. | Medido: `GetGamepadName(0)` devuelve una cadena **vacía** no nula cuando no hay mando conectado, nunca `NULL` (`rcore.c` devuelve `CORE.Input.Gamepad.name[gamepad]`). Un `maybe` inventaría un fallo que no puede ocurrir. |
| D7 | `detected_gesture` devuelve `maybe int`, no `maybe raylib.Gesture`. | La dirección int → enum no es expresable: `(raw to raylib.Gesture)` es un error de sintaxis, y `transmute raw to raylib.Gesture` hace que `pengu 2.4.0` emita `((raylib.Gesture)(raw))` — **C inválido**, porque el compilador imprime nombres de tipo cualificados (plan maestro D19, y el mismo defecto que encontraron `shapes` y `text`). El wrapper devuelve por tanto el ordinal crudo y el docstring da el idioma de comparación `g == (raylib.GESTURE_TAP to int)`, que está verificado que funciona. |
| D8 | `enable_gestures` recibe `slice of raylib.Gesture` y combina los flags con OR en el `u32` que quiere el binding. | Heredado del archivado `rgesturesx`: un literal de array no se puede pasar en posición de argumento (`E0005`), y `or` no puede combinar flags `u32` (`E0005: Logical operator 'or' requires bool, got 'u32'`), así que los bits se combinan con `|` en un bucle. Una llamada con un solo gesto es `enable_gestures with (list of raylib.Gesture)`. |
| D9 | Los tres setters de ratón reciben un `raylib.Vector2` en vez de las coordenadas sueltas del binding: `set_mouse_position with position`, `set_mouse_offset with offset`, `set_mouse_scale with scale`. | Emparejan con la forma que ya tienen los datos del llamador. `SetMousePosition`/`SetMouseOffset` reciben componentes `int` (el wrapper convierte con `to int`); `SetMouseScale` recibe `f32`. Es un tipo de parámetro, no un método de `Vector2`, así que el registro se respeta (D4). |
| D10 | `SetExitKey` **no se envuelve**. | El plan maestro D14 lo clasifica como configuración global de un solo uso. Se registra aquí en vez de omitirse en silencio, y es el único punto donde la familia ganaría con una excepción: ver la nota de abajo. |
| D11 | Sin wrappers de `slice` salvo `enable_gestures`, sin retornos múltiples, y `std.ffi` solo para los dos getters de nombre. | La familia son escalares, booleanos y structs pequeños. |

> **La cuestión de `SetExitKey` (D10).** El plan maestro lo mete en el cajón de "configuración global de un solo uso" junto a `SetConfigFlags` y `SetTraceLogLevel`. La agrupación es defendible para los flags de configuración pero más débil aquí: `SetExitKey` recibe un `KeyboardKey`, así que es exactamente el caso de restauración de enum que justifica el resto de la familia, y quien quiera atar la salida a Esc tiene que escribir `raylib.SetExitKey with (raylib.KEY_ESCAPE to int)`. He seguido el plan maestro en vez de saltármelo, y lo señalo porque añadir `set_exit_key with key as raylib.KeyboardKey into void` es un cambio de una línea si la revisión lo prefiere.

| D12 | Una **asimetría medible** en los predicados `_up`, registrada para que nadie la "arregle": sin que pase nada, `is_key_up` e `is_mouse_button_up` son **`true`** (no hay nada pulsado), pero los cuatro `is_gamepad_button_*` son **`false`**, incluido `_up`, porque raylib los condiciona a que el mando esté disponible. | Medido en C sin ventana: `IsKeyUp(KEY_A) == 1`, `IsMouseButtonUp(LEFT) == 1`, y `IsGamepadButtonDown/Up/Pressed/Released(0, …)` son todos `0`. Los tests aseguran exactamente eso, y los docstrings de los predicados de mando dicen que un mando ausente informa `false`. | **Medido después, a través de la fachada, y completa el cuadro:** la asimetría no es una constante. Sin que se haya creado nunca una ventana, `IsGamepadAvailable(0)` es `false` y los cuatro predicados son `false`; una vez que cualquier ventana ha inicializado GLFW, el mando real de `/dev/input/js0` pasa a estar disponible, `is_gamepad_button_up` se vuelve **`true`** para un botón sin pulsar, `gamepad_name` devuelve el nombre del mando y un eje en reposo lee **`-0.0117647`** en vez de `0.0` — que es exactamente por lo que existen las zonas muertas. Los tests de la familia bifurcan según `IsGamepadAvailable` en vez de asumir ninguno de los dos estados.

### ✨ Enchantings

**Ninguno.** Ver D4.

### 🔧 Funciones a nivel de módulo

#### Teclado (8)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `is_key_pressed` | `with key as raylib.KeyboardKey into bool` | `IsKeyPressed` | |
| `is_key_pressed_repeat` | `with key as raylib.KeyboardKey into bool` | `IsKeyPressedRepeat` | verdadero mientras la tecla autorepite |
| `is_key_down` | `with key as raylib.KeyboardKey into bool` | `IsKeyDown` | |
| `is_key_released` | `with key as raylib.KeyboardKey into bool` | `IsKeyReleased` | |
| `is_key_up` | `with key as raylib.KeyboardKey into bool` | `IsKeyUp` | |
| `key_pressed` | `into maybe int` | `GetKeyPressed` | `maybe none` cuando la cola está vacía (`0` es `KEY_NULL`); compárese con `(raylib.KEY_A to int)` |
| `char_pressed` | `into maybe int` | `GetCharPressed` | `maybe none` cuando no hay carácter pendiente; el valor es un codepoint |
| `key_name` | `with key as raylib.KeyboardKey into maybe string` | `GetKeyName` | `maybe none` cuando raylib devuelve `NULL` (medido: lo hace incluso para `KEY_A` sin ventana) |

#### Mando (8)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `is_gamepad_button_pressed` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonPressed` | `gamepad` es el índice de ranura de raylib `0..3`, no un enum |
| `is_gamepad_button_down` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonDown` | |
| `is_gamepad_button_released` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonReleased` | |
| `is_gamepad_button_up` | `with gamepad as int, button as raylib.GamepadButton into bool` | `IsGamepadButtonUp` | |
| `gamepad_button_pressed` | `into maybe int` | `GetGamepadButtonPressed` | `maybe none` para `GAMEPAD_BUTTON_UNKNOWN`, que es `0` |
| `gamepad_axis_movement` | `with gamepad as int, axis as raylib.GamepadAxis into f32` | `GetGamepadAxisMovement` | `[-1..1]` |
| `gamepad_name` | `with gamepad as int into string` | `GetGamepadName` | cadena vacía cuando no hay mando conectado (D6) |
| `set_gamepad_mappings` | `with mappings as string into int` | `SetGamepadMappings` | devuelve el número de mapeos añadidos; raylib no documenta el valor de fallo |

#### Ratón (8)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `is_mouse_button_pressed` | `with button as raylib.MouseButton into bool` | `IsMouseButtonPressed` | |
| `is_mouse_button_down` | `with button as raylib.MouseButton into bool` | `IsMouseButtonDown` | |
| `is_mouse_button_released` | `with button as raylib.MouseButton into bool` | `IsMouseButtonReleased` | |
| `is_mouse_button_up` | `with button as raylib.MouseButton into bool` | `IsMouseButtonUp` | |
| `set_mouse_position` | `with position as raylib.Vector2 into void` | `SetMousePosition` | las componentes se truncan a `int` (D9) |
| `set_mouse_offset` | `with offset as raylib.Vector2 into void` | `SetMouseOffset` | las componentes se truncan a `int` |
| `set_mouse_scale` | `with scale as raylib.Vector2 into void` | `SetMouseScale` | recibe las componentes `f32` directamente |
| `set_mouse_cursor` | `with cursor as raylib.MouseCursor into void` | `SetMouseCursor` | |

#### Táctil (1)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `touch_point_id` | `with index as int into maybe int` | `GetTouchPointId` | `maybe none` para un índice fuera de rango (raylib devuelve `-1`) |

#### Gestos (3)

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `enable_gestures` | `with gestures as slice of raylib.Gesture into void` | `SetGesturesEnabled` | combina los flags con OR (D8); un slice vacío desactiva todos los gestos |
| `is_gesture_detected` | `with gesture as raylib.Gesture into bool` | `IsGestureDetected` | |
| `detected_gesture` | `into maybe int` | `GetGestureDetected` | `maybe none` para `GESTURE_NONE`; ver D7 para por qué es un `int` |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `key_pressed` | `maybe int` | raylib devuelve `0`, que es `KEY_NULL` |
| `char_pressed` | `maybe int` | raylib devuelve `0` |
| `gamepad_button_pressed` | `maybe int` | raylib devuelve `GAMEPAD_BUTTON_UNKNOWN`, medido como `0` |
| `touch_point_id` | `maybe int` | raylib devuelve `-1` para un índice más allá de `MAX_TOUCH_POINTS` |
| `detected_gesture` | `maybe int` | raylib devuelve `GESTURE_NONE` (`0`) |
| `key_name` | `maybe string` | raylib devuelve `NULL` |

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `enable_gestures` | `gestures as slice of raylib.Gesture` |

Una guarda: un slice vacío no activa nada, que es también como el llamador desactiva todos los gestos. Los flags se combinan con `|`, nunca con `or` (D8).

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Cada función devuelve un escalar, un booleano, un `Vector2` o un `string`.

### 🌉 Uso de `std.ffi`

Solo los dos getters de nombre cruzan una frontera de cadena: `key_name` y `gamepad_name` copian un `const char*` que posee raylib con `ffi.string_from_cstr` y no liberan nada. `key_name` además comprueba nulo con `ffi.is_null`, y su `transmute` a `ref to char` es el ensanchamiento documentado.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — la ganancia de restaurar tipos
import raylib
import raylibx.input as input

weave main into int:
    var jump as bool is calling input.is_key_pressed with raylib.KEY_SPACE
    var firing as bool is calling input.is_mouse_button_down with raylib.MOUSE_BUTTON_LEFT
    var pad as bool is calling input.is_gamepad_button_down with 0, raylib.GAMEPAD_BUTTON_RIGHT_FACE_DOWN
    var axis as f32 is calling input.gamepad_axis_movement with 0, raylib.GAMEPAD_AXIS_LEFT_X
    var tapped as bool is calling input.is_gesture_detected with raylib.GESTURE_TAP
    return 0
```

```pengu
# Ejemplo 2 — los wrappers de centinela y el idioma de comparación
import raylib
import raylibx.input as input

weave main into int:
    var typed as maybe int is calling input.key_pressed
    var name as maybe string is calling input.key_name with raylib.KEY_A
    var who as string is calling input.gamepad_name with 0
    var gesture as maybe int is calling input.detected_gesture
    return 0
```

```pengu
# Ejemplo 3 — los setters y el slice de flags de gestos
import raylib
import raylibx.input as input

weave main into int:
    var gestures as list of raylib.Gesture is list of raylib.Gesture
    defer banish gestures
    calling gestures.push with raylib.GESTURE_TAP
    calling gestures.push with raylib.GESTURE_DRAG
    calling input.enable_gestures with (gestures at 0 to (gestures.length))
    calling input.set_mouse_position with (with x is 100.0, y is 100.0)
    calling input.set_mouse_scale with (with x is 1.0, y is 1.0)
    calling input.set_mouse_cursor with raylib.MOUSE_CURSOR_CROSSHAIR
    return 0
```

### 🧪 Plan de tests

Es la **segunda familia con una superficie amplia realmente testeable en CI**, y a diferencia de `text` nada de ella necesita ventana ni recurso cargado: sin entrada, cada predicado es `false`, cada wrapper de centinela es `maybe none` y cada getter devuelve un valor por defecto. Eso convierte la *ruta negativa* en la aserción, que es justo la que un test unitario puede fijar.

- **Los 14 predicados de enum** (`is_key_*`, `is_mouse_button_*`, `is_gamepad_button_*`, `is_gesture_detected`): cada uno se asegura `false` sin ventana con un valor de enum real, lo que demuestra tanto el tipo como la conversión. Tres teclas, dos botones de ratón, dos botones de mando y un gesto por predicado.
- **`key_pressed` / `char_pressed`**: `maybe none` cuando no hay nada en cola; dos llamadas seguidas son ambas `none` (la cola no inventa valores).
- **`gamepad_button_pressed`**: `maybe none` sin mando.
- **`touch_point_id`**: `maybe none` para un índice fuera de rango (`1000`) y `some 0` para el índice `0`, que es la distinción medida entre "índice inválido" y "índice válido con id 0".
- **`detected_gesture`**: `maybe none` cuando no hay gesto en curso.
- **`key_name`**: `maybe none` sin ventana (medido); el docstring registra que la misma llamada devuelve un nombre en cuanto hay ventana.
- **`gamepad_name`**: cadena vacía, **no** `maybe none`, sin mando conectado (D6).
- **`set_gamepad_mappings`**: devuelve un `int` para la cadena vacía y para un mapeo malformado sin reventar; el valor se asegura no negativo en vez de un número concreto, porque raylib no lo documenta.
- **`set_mouse_position` / `set_mouse_offset` / `set_mouse_scale` / `set_mouse_cursor`**: se pueden llamar sin ventana sin reventar; la aserción es que la llamada vuelve (`void`) y que un `raylib.GetMousePosition` posterior sigue respondiendo un `Vector2` finito. Mutan estado de entrada, así que son lo más cerca que esta familia está de un efecto secundario, y el test lo registra.
- **`enable_gestures`**: un slice vacío es un no-op que no lee el elemento cero; un slice de dos elementos se acepta y `is_gesture_detected` sigue `false` porque no ha pasado nada.
- **`gamepad_axis_movement`**: devuelve `0.0` en ambos ejes de un mando ausente.
- **Sonda de solo compilación**: los dos retornos `maybe int` y el `maybe string` se comprueban además de tipos con una pequeña `input_api_probe` que referencia cada entrada envuelta, para que ninguna firma se deteriore sin que se note.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `GetMouseX`, `GetMouseY` | getter sin argumentos que no puede fallar; `GetMousePosition` ya da ambos (contrato §9, y `mouse_position` también se omite por el mismo motivo) |
| `GetMousePosition`, `GetMouseDelta` | getter sin argumentos que no puede fallar; la llamada al binding ya es clara (contrato §9 filas 1 y 417) |
| `GetMouseWheelMove`, `GetMouseWheelMoveV` | igual |
| `GetTouchX`, `GetTouchY`, `GetTouchPosition` | igual, y además `GetTouchPointCount` es una de las tres funciones que el contrato nombra explícitamente en §9 |
| `GetTouchPointCount` | nombrada en el contrato §9 como el getter canónico que no se envuelve |
| `GetGestureHoldDuration`, `GetGestureDragVector`, `GetGestureDragAngle`, `GetGesturePinchVector`, `GetGesturePinchAngle` | getters sin argumentos que no pueden fallar |
| `IsGamepadAvailable` | predicado que ya es `bool` y no recibe ningún enum (la ranura de mando es un `int` pelado); no hay nada que restaurar |
| `GetGamepadAxisCount` | consulta con argumento que no puede fallar y no lleva enum |
| `SetGamepadVibration` | setter que no cruza ninguna frontera de tipo y no tiene canal de fallo; sus cuatro argumentos sueltos ya son claros en el sitio de llamada |
| `SetExitKey` | plan maestro D14 (configuración global de un solo uso); ver la nota bajo D10 |

Auditoría de cobertura: de las 47 funciones de entrada y gestos, **28 se envuelven** (todas de módulo, sin enchantings) y **19 no**: 17 por el motivo de renombrado trivial de D3, `SetGamepadVibration` por el mismo motivo (tampoco cruza ninguna frontera) y `SetExitKey` por D10. La biblioteca instalada exporta todos los símbolos envueltos.
