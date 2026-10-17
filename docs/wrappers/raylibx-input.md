> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# input

> Source: `pengu/raylibx/input.pengu`

pengu
Layer-2 wrapper over the 28 input and gesture functions of the `raylib` binding that
cross a boundary worth crossing.

The binding flattens **every** enum parameter to `int`. Restoring the real types is the
whole point of this family:

    calling raylib.IsKeyDown with (raylib.KEY_SPACE to int)   # binding
    calling is_key_down with raylib.KEY_SPACE   # wrapper

The other half of the family is the failure sentinels: `key_pressed`, `char_pressed`,
`gamepad_button_pressed`, `touch_point_id`, `detected_gesture` and `key_name` all
report "nothing happened" through a magic value, so they return `maybe`.

What is deliberately **absent** is as important: a zero-argument getter that cannot fail
(`GetMousePosition`, `GetMouseDelta`, `GetTouchX`, `GetGestureDragVector`, ...) is not
wrapped, because the binding call is already clear and a wrapper would only add a jump
(contract section 9). Read those through `raylib` directly.

This is family `input` of `raylibx`; see `docs/wrappers/raylibx-input.md`.

## No window needed
Every wrapped function is safe to call headless: with no input the predicates are
`false`, the sentinel wrappers are `maybe none` and the setters simply record state.
That is why this family has real CI tests rather than a compile-only probe.

## Memory
No allocation and nothing to release. `std.ffi` appears only in `key_name` and
`gamepad_name`, which copy a raylib-owned `const char*` and free nothing.

## Example
```pengu
import raylib
import raylibx_input

weave main into int:
    var jump as bool is calling is_key_pressed with raylib.KEY_SPACE
    var typed as maybe int is calling key_pressed
    var name as string is calling gamepad_name with 0
    return 0
```

---

### `is_key_pressed`

> **is_key_pressed**(key: KeyboardKey) -> bool

_Undocumented function._


### `is_key_pressed_repeat`

> **is_key_pressed_repeat**(key: KeyboardKey) -> bool

_Undocumented function._


### `is_key_down`

> **is_key_down**(key: KeyboardKey) -> bool

_Undocumented function._


### `is_key_released`

> **is_key_released**(key: KeyboardKey) -> bool

_Undocumented function._


### `is_key_up`

> **is_key_up**(key: KeyboardKey) -> bool

_Undocumented function._


### `key_pressed`

> **key_pressed**() -> maybe int

_Undocumented function._


### `char_pressed`

> **char_pressed**() -> maybe int

_Undocumented function._


### `key_name`

> **key_name**(key: KeyboardKey) -> maybe string

_Undocumented function._


### `is_gamepad_button_pressed`

> **is_gamepad_button_pressed**(gamepad: int, button: GamepadButton) -> bool

_Undocumented function._


### `is_gamepad_button_down`

> **is_gamepad_button_down**(gamepad: int, button: GamepadButton) -> bool

_Undocumented function._


### `is_gamepad_button_released`

> **is_gamepad_button_released**(gamepad: int, button: GamepadButton) -> bool

_Undocumented function._


### `is_gamepad_button_up`

> **is_gamepad_button_up**(gamepad: int, button: GamepadButton) -> bool

_Undocumented function._


### `gamepad_button_pressed`

> **gamepad_button_pressed**() -> maybe int

_Undocumented function._


### `gamepad_axis_movement`

> **gamepad_axis_movement**(gamepad: int, axis: GamepadAxis) -> f32

_Undocumented function._


### `gamepad_name`

> **gamepad_name**(gamepad: int) -> string

_Undocumented function._


### `set_gamepad_mappings`

> **set_gamepad_mappings**(mappings: string) -> int

_Undocumented function._


### `is_mouse_button_pressed`

> **is_mouse_button_pressed**(button: MouseButton) -> bool

_Undocumented function._


### `is_mouse_button_down`

> **is_mouse_button_down**(button: MouseButton) -> bool

_Undocumented function._


### `is_mouse_button_released`

> **is_mouse_button_released**(button: MouseButton) -> bool

_Undocumented function._


### `is_mouse_button_up`

> **is_mouse_button_up**(button: MouseButton) -> bool

_Undocumented function._


### `set_mouse_position`

> **set_mouse_position**(position: Vector2) -> void

_Undocumented function._


### `set_mouse_offset`

> **set_mouse_offset**(offset: Vector2) -> void

_Undocumented function._


### `set_mouse_scale`

> **set_mouse_scale**(scale: Vector2) -> void

_Undocumented function._


### `set_mouse_cursor`

> **set_mouse_cursor**(cursor: MouseCursor) -> void

_Undocumented function._


### `touch_point_id`

> **touch_point_id**(index: int) -> maybe int

_Undocumented function._


### `enable_gestures`

> **enable_gestures**(gestures: slice of Gesture) -> void

_Undocumented function._


### `is_gesture_detected`

> **is_gesture_detected**(gesture: Gesture) -> bool

_Undocumented function._


### `detected_gesture`

> **detected_gesture**() -> maybe int

_Undocumented function._


### `input_api_probe`

> **input_api_probe**() -> void

Every wrapped entry is referenced here so that no signature can rot unnoticed. The
probe is not invoked: the family is already asserted by the tests above, and this one
exists only for the type checker.

