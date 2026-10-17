> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# rayguix

> Source: `pengu/rayguix.pengu`

Layer-2 wrapper over the 38 raygui functions worth wrapping, out of the 61 the binding declares.

## One deliberate omission worth knowing about
`GuiLoadStyleFromMemory` is **not** wrapped, even though it takes a slice. Measured: raygui
reads a `.rgs` buffer **without validating its length**, and a buffer whose first four bytes
are the valid magic `rGS ` but which is too short segfaults the process. A wrapper cannot
validate a style file, so this one stays at the binding, where the caller passes
`ref to frozen byte, dataSize` knowingly. `load_style`, which reads a file, **is** wrapped,
because it was measured to fail safely on a missing path.

raygui is a widget library, so almost everything here takes a `const char*` and returns
raygui's own state:

    var c_text as ref to frozen char is calling ffi.cstr_from_string with "Save"
    defer calling ffi.cstr_free with (transmute c_text to ref to char)
    var state as int is calling raygui.GuiButton with bounds, c_text    # binding

    var state as int is calling rayguix.button with bounds, "Save"      # wrapper

## Why the module can exist at all
raygui is a single-header library: its implementation only exists in a translation unit
that defines `RAYGUI_IMPLEMENTATION`. That is already handled by `c/raygui_impl.c`, which the
build compiles into the bundle, so no `antiquus`, no compiler change and no extra archive are
needed -- and measured, the `Gui*` symbols are absent from `libraylib.so`, which is why the
bridge is load-bearing rather than decorative. See `docs/wrappers/rayguix.md`.

## The out-parameter shape
Twenty-two widgets read **and write** a value the caller owns -- a toggle's flag, a slider's
number, a picker's colour. The wrapper keeps the binding's shape instead of inventing a
return value: the call site passes `sigil of enabled`, and the widget's own return stays what
raygui means by it, the drawing state.

## The three text fields
`text_box`, `value_box_float` and `text_input_box` edit a caller-owned C buffer in place, and
PenguScript strings are immutable. The wrapper therefore allocates the buffer, seeds it from
your string, calls raygui and copies the edited text back into the `ref to string` you
passed; `capacity` is the buffer's size, and typing past it truncates rather than overflows.
The copy is byte by byte because the language has no `memcpy`, no pointer arithmetic and no
assignable slice view.

## Needs a window
Every widget draws, so every test opens one. raygui keeps its state in globals that survive
`CloseWindow`, so the tests use the binding's own `GuiSetStyle`/`GuiGetStyle` to save and
restore anything they change.

## Memory
Nothing is leaked: the temporary C strings and the text-field buffers are released by the
wrapper, and the caller's values stay the caller's.

## Example
```pengu
import raylib
import rayguix

weave main into int:
    var volume as f32 is 0.5
    var bounds as raylib.Rectangle is with x is 20.0, y is 20.0, width is 200.0, height is 24.0
    var state as int is calling rayguix.slider with bounds, "0", "100", (sigil of volume), 0.0, 100.0
    return 0
```

---

### `_clear_buffer`

> **_clear_buffer**(buffer: slice of byte, capacity: int) -> void

Zeroes `capacity` bytes of a caller-owned buffer. Private to the module.
Parameters
- `buffer`: the byte view to clear.
- `capacity`: how many bytes to write.
Returns
Nothing.
Notes
raygui reads its text buffer as a C string, so a field that starts as `MemAlloc` garbage would
print whatever happened to be in the heap. This is why the buffer is cleared before seeding.
Memory
The buffer belongs to the caller.
Example
```pengu
calling _clear_buffer with buffer, capacity
```


### `_seed_buffer`

> **_seed_buffer**(buffer: slice of byte, text: string, capacity: int) -> void

Copies a PenguScript string into a caller-owned buffer and NUL-terminates it. Private.
Parameters
- `buffer`: the byte view to write into.
- `text`: the text to copy.
- `capacity`: the buffer's size in bytes.
Returns
Nothing.
Notes
The copy is byte by byte: the language has no `memcpy`, no pointer arithmetic and no
assignable slice view, so this loop is the only expressible route. It stops at the string's
length and leaves the rest of the buffer cleared, which is what raygui expects from an
editable field.
Memory
The buffer and the string both belong to the caller; the temporary C string of the source is
freed here.
Example
```pengu
calling _seed_buffer with buffer, "editable", capacity
```


### `_read_buffer`

> **_read_buffer**(buffer: slice of byte) -> string

Reads a NUL-terminated string out of a caller-owned buffer. Private.
Parameters
- `buffer`: the byte view to read from.
Returns
The text raygui left in the buffer, as an owned PenguScript string.
Notes
raygui edits the buffer in place, so this is how the edited text gets back into the caller's
`string`.
Memory
The returned string is owned by the caller of the wrapper; the buffer stays the wrapper's.
Example
```pengu
set essence of text is (calling _read_buffer with buffer)
```


### `load_style`

> **load_style**(path: string) -> void

_Undocumented function._


### `set_tooltip`

> **set_tooltip**(text: string) -> void

_Undocumented function._


### `text_width`

> **text_width**(text: string) -> int

_Undocumented function._


### `icon_text`

> **icon_text**(icon_id: int, text: string) -> string

_Undocumented function._


### `window_box`

> **window_box**(bounds: Rectangle, title: string) -> int

_Undocumented function._


### `group_box`

> **group_box**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `line`

> **line**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `panel`

> **panel**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `label`

> **label**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `button`

> **button**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `label_button`

> **label_button**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `status_bar`

> **status_bar**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `dummy_rec`

> **dummy_rec**(bounds: Rectangle, text: string) -> int

_Undocumented function._


### `toggle`

> **toggle**(bounds: Rectangle, text: string, active: ref to bool) -> int

_Undocumented function._


### `toggle_group`

> **toggle_group**(bounds: Rectangle, text: string, active: ref to int) -> int

_Undocumented function._


### `toggle_slider`

> **toggle_slider**(bounds: Rectangle, text: string, active: ref to int) -> int

_Undocumented function._


### `check_box`

> **check_box**(bounds: Rectangle, text: string, checked: ref to bool) -> int

_Undocumented function._


### `combo_box`

> **combo_box**(bounds: Rectangle, text: string, active: ref to int) -> int

_Undocumented function._


### `dropdown_box`

> **dropdown_box**(bounds: Rectangle, text: string, active: ref to int, edit_mode: bool) -> int

_Undocumented function._


### `spinner`

> **spinner**(bounds: Rectangle, text: string, value: ref to int, min_value: int, max_value: int, edit_mode: bool) -> int

_Undocumented function._


### `value_box`

> **value_box**(bounds: Rectangle, text: string, value: ref to int, min_value: int, max_value: int, edit_mode: bool) -> int

_Undocumented function._


### `slider`

> **slider**(bounds: Rectangle, text_left: string, text_right: string, value: ref to f32, min_value: f32, max_value: f32) -> int

_Undocumented function._


### `slider_bar`

> **slider_bar**(bounds: Rectangle, text_left: string, text_right: string, value: ref to f32, min_value: f32, max_value: f32) -> int

_Undocumented function._


### `progress_bar`

> **progress_bar**(bounds: Rectangle, text_left: string, text_right: string, value: ref to f32, min_value: f32, max_value: f32) -> int

_Undocumented function._


### `grid`

> **grid**(bounds: Rectangle, text: string, spacing: f32, subdivs: int, mouse_cell: ref to Vector2) -> int

_Undocumented function._


### `list_view`

> **list_view**(bounds: Rectangle, text: string, scroll_index: ref to int, active: ref to int) -> int

_Undocumented function._


### `tab_bar`

> **tab_bar**(bounds: Rectangle, text: string, h_scroll: ref to int, active: ref to int) -> int

_Undocumented function._


### `scroll_panel`

> **scroll_panel**(bounds: Rectangle, text: string, content: Rectangle, scroll: ref to Vector2, view: ref to Rectangle) -> int

_Undocumented function._


### `color_picker`

> **color_picker**(bounds: Rectangle, text: string, color: ref to Color) -> int

_Undocumented function._


### `color_panel`

> **color_panel**(bounds: Rectangle, text: string, color: ref to Color) -> int

_Undocumented function._


### `color_bar_alpha`

> **color_bar_alpha**(bounds: Rectangle, text: string, alpha: ref to f32) -> int

_Undocumented function._


### `color_bar_hue`

> **color_bar_hue**(bounds: Rectangle, text: string, value: ref to f32) -> int

_Undocumented function._


### `color_picker_hsv`

> **color_picker_hsv**(bounds: Rectangle, text: string, color_hsv: ref to Vector3) -> int

_Undocumented function._


### `color_panel_hsv`

> **color_panel_hsv**(bounds: Rectangle, text: string, color_hsv: ref to Vector3) -> int

_Undocumented function._


### `message_box`

> **message_box**(bounds: Rectangle, title: string, message: string, button_text: string, button_active: ref to int) -> int

_Undocumented function._


### `text_box`

> **text_box**(bounds: Rectangle, text: ref to string, capacity: int, edit_mode: bool) -> int

_Undocumented function._


### `value_box_float`

> **value_box_float**(bounds: Rectangle, label: string, text: ref to string, value: ref to f32, capacity: int, edit_mode: bool) -> int

_Undocumented function._


### `text_input_box`

> **text_input_box**(bounds: Rectangle, title: string, message: string, text: ref to string, capacity: int, button_text: string, button_active: ref to int, secret: ref to bool) -> int

_Undocumented function._

