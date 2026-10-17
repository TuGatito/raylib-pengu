> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# window

> Source: `pengu/raylibx/window.pengu`

Layer-2 wrapper over the 11 window functions of the `raylib` binding that cross a
boundary worth crossing, out of the 67 the family owns.

This is deliberately the smallest family in the module, and the reason is structural:
raylib has **no window type**, so there is no receiver to hang a method on, and almost
every window function is a zero-argument getter or a flat `int` setter whose binding call
is already a clear call. Contract section 9 rows 1 and 8 exclude exactly that shape, and
row 9 anticipates this outcome for `rlglx` too: wrapping almost nothing is a valid
deliverable. The family plan lists all 56 exclusions by rule.

What is left is the surface that genuinely converts or allocates:

    calling raylib.SetWindowTitle with c_title                 # binding
    calling raylibx_window.set_window_title with "Pengunic"    # wrapper

## The window lifecycle is not here
`InitWindow` and `CloseWindow` are **not** wrapped: contract section 9 row 8 names them
as one-shot global configuration, called once, where a wrapper only adds a hop. Open and
close the window through the binding:

```pengu
calling raylib.InitWindow with 800, 600, "Pengunic"
defer calling raylib.CloseWindow
```

## Needs a window
Every function here except `get_monitor_name` operates on a live window. Measured: a
window *can* be opened in this environment, so unlike the families planned before this
one, its tests run against a real window rather than a compile-only probe.

## Memory
Nothing is allocated and nothing is released. The strings raylib returns are copied into
owned PenguScript strings, so no raylib-owned pointer escapes the wrapper.

## Example
```pengu
import raylib
import raylibx_window

weave main into int:
    calling raylib.InitWindow with 800, 600, "Pengunic"
    defer calling raylib.CloseWindow
    calling raylibx_window.set_window_title with "Pengunic"
    var name as string is calling raylibx_window.get_monitor_name with 0
    return 0
```

---

### `is_window_state`

> **is_window_state**(flag: ConfigFlags) -> bool

Reports whether a window state flag is set.
Parameters
- `flag`: the flag to test, as a `raylib.ConfigFlags`.
Returns
`true` when **any** of the flag's bits is set in the window's current state.
Notes
**One flag only, and that is deliberate.** raylib computes `(current & flags) != 0`, so a slice here would mean "any of these" while reading as "all of these". A single flag has no such ambiguity; use `set_window_state` and `clear_window_state` for combinations.
Measured: with a live window, `raylib.FLAG_VSYNC_HINT` reports `false` and `FLAG_WINDOW_ALWAYS_RUN` reports `true` while it is set.
Memory
No allocation; a single direct C call.
Example
```pengu
if calling raylibx_window.is_window_state with raylib.FLAG_WINDOW_RESIZABLE:
return 0
```


### `set_window_state`

> **set_window_state**(states: slice of ConfigFlags) -> void

Adds window state flags.
Parameters
- `states`: the flags to add; an empty slice is a no-op.
Returns
Nothing; the window's state changes and takes effect on the platform.
Notes
The flags are ORed with `|`, never with `or`: `or` is boolean-only and rejects `u32` (`E0005`).
This **adds** to the current state; it does not replace it. Use `clear_window_state` to undo, which is why the two are named as a pair.
Memory
No allocation; a single direct C call.
Example
```pengu
calling raylibx_window.set_window_state with (states at 0 to (states.length))
```


### `clear_window_state`

> **clear_window_state**(states: slice of ConfigFlags) -> void

Removes window state flags.
Parameters
- `states`: the flags to remove; an empty slice is a no-op.
Returns
Nothing; the window's state changes and takes effect on the platform.
Notes
Only flags that are currently set are affected. Measured: setting `FLAG_WINDOW_ALWAYS_RUN` then clearing it returns the state to `false`.
Memory
No allocation; a single direct C call.
Example
```pengu
calling raylibx_window.clear_window_state with (states at 0 to (states.length))
```


### `set_window_title`

> **set_window_title**(title: string) -> void

Changes the window's title.
Parameters
- `title`: the new title text.
Returns
Nothing.
Notes
The title is copied into raylib's own buffer, so the PenguScript string does not need to outlive the call.
Requires a window; measured callable on a live one.
Memory
The temporary C string is released by the wrapper; raylib copies what it needs.
Example
```pengu
calling raylibx_window.set_window_title with "Pengunic - level 1"
```


### `set_window_icon`

> **set_window_icon**(icon: Image) -> void

Sets the window icon from an image.
Parameters
- `icon`: the image to use; raylib reads it, it does not take ownership.
Returns
Nothing.
Notes
The image should be square and small (raylib's own default is 32x32); the platform may scale it or ignore it.
Unload the image yourself when you are done with it: `raylib.SetWindowIcon` copies what it needs.
Memory
No allocation; the image stays the caller's to release.
Example
```pengu
calling raylibx_window.set_window_icon with icon
```


### `set_window_icons`

> **set_window_icons**(icons: slice of Image) -> void

Sets the window icon from several images, one per size.
Parameters
- `icons`: the images to use; an empty slice is a no-op.
Returns
Nothing.
Notes
Providing several sizes lets the platform pick the one it needs instead of scaling a single icon. The empty slice is guarded because raylib would otherwise read past a null pointer.
Memory
The images stay the caller's to release.
Example
```pengu
calling raylibx_window.set_window_icons with (icons at 0 to (icons.length))
```


### `get_monitor_name`

> **get_monitor_name**(monitor: int) -> string

Returns the name of a monitor.
Parameters
- `monitor`: the monitor index, `0` for the primary one.
Returns
The monitor's name, or an **empty string** for an index raylib does not know.
Notes
Measured: an out-of-range index returns an empty string, **not** `NULL`, so this is a plain `string` rather than a `maybe` — the same shape as `GetGamepadName` in `raylibx_input`.
Works without a window, because the monitor list comes from the platform rather than from the window.
Memory
raylib owns the returned `const char*`; the wrapper copies it into an owned PenguScript string and frees nothing.
Example
```pengu
var name as string is calling raylibx_window.get_monitor_name with 0
```


### `set_clipboard_text`

> **set_clipboard_text**(text: string) -> void

Puts text on the system clipboard.
Parameters
- `text`: the text to place on the clipboard.
Returns
Nothing.
Notes
Measured: `set_clipboard_text` followed by `get_clipboard_text` returns the exact text, so the round trip is usable as a test.
On X11 the clipboard belongs to the process: the text survives only while the program that set it is running and pumping events.
Memory
The temporary C string is released by the wrapper; the platform copies what it needs.
Example
```pengu
calling raylibx_window.set_clipboard_text with "copied from Pengunic"
```


### `get_clipboard_text`

> **get_clipboard_text**() -> maybe string

Reads text from the system clipboard.
Returns
`some` with the clipboard text, or `maybe none` when the clipboard holds no text.
Notes
Measured: a fresh clipboard returns `NULL`, which is the predicate. An empty clipboard and a clipboard holding an empty string are therefore indistinguishable, as they are in the binding.
On X11 this can block briefly while the selection owner responds.
Memory
raylib owns the returned `const char*`; the wrapper copies it and frees nothing.
Example
```pengu
var pasted as maybe string is calling raylibx_window.get_clipboard_text
```


### `get_clipboard_image`

> **get_clipboard_image**() -> maybe Image

Reads an image from the system clipboard.
Returns
`some` with the clipboard image, or `maybe none` when the clipboard holds no image.
Notes
**This call can block.** Measured: it hangs in this environment, because an X11 clipboard image needs a selection owner that is pumping events. Only call it when the clipboard is known to hold an image, and prefer `get_clipboard_text` when either would do.
The image is returned in raylib's default format and needs no window, but it does need a live platform connection.
Memory
The returned image owns its pixel buffer: release it with `raylib.UnloadImage` (or `raylibx_images.unload_image`).
Example
```pengu
var pasted as maybe raylib.Image is calling raylibx_window.get_clipboard_image
```


### `take_screenshot`

> **take_screenshot**(path: string) -> void

Saves a screenshot of the current frame to a file.
Parameters
- `path`: the destination file; the extension chooses the format.
Returns
Nothing. **raylib reports no failure**, so a bad path fails silently.
Notes
**The file appears when the frame advances.** Measured: raylib defers the write, so checking the file in the same frame reports `false`; after the next `EndDrawing` it exists (517 bytes for a 120x80 frame). Call it inside a frame and check the file after the frame has ended.
This is the only way to capture the screen through the wrapper; for a specific render target, read it back as an image instead.
Memory
raylib allocates and releases the temporary buffer; nothing is left to the caller.
Example
```pengu
calling raylibx_window.take_screenshot with "/tmp/pengunic.png"
```


### `window_api_probe`

> **window_api_probe**(icons: slice of Image, image: Image) -> void

The window-bound entries that are not asserted, either because they need a window state the
tests do not set up or because they are the ones measured to be unstable. This probe exists
so no signature can rot unnoticed; it is never invoked.

