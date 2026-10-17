> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# colors

> Source: `pengu/raylibx/colors.pengu`

Layer-2 wrapper over the colour surface of the `raylib` binding.

The binding exposes fourteen free functions over `Color`. This wrapper turns the value
transforms into methods on `raylib.Color` and the constructors into `ritual`s, so a
colour computation reads as the operation instead of as a call into the binding:

    calling raylib.ColorAlpha with (sigil of c), 0.5      # binding
    calling c.with_alpha with 0.5                          # wrapper

The family is `colors` of `docs/README.md`; see `docs/wrappers/raylibx-colors.md`.

`SetPixelColor` and `GetPixelColor` are deliberately **not** wrapped: both operate on a
raw `void*` into foreign memory tagged with a `PixelFormat`, and a wrapper cannot make
that safer (see the family plan, D7).

## Memory
No allocation, no ownership, nothing to release. Every entry is arithmetic over four
bytes. There is no `banish`, no `std.ffi` and no `transmute` anywhere in this module:
`from_int` masks each byte and uses the checked `to byte` cast.

## Ranges
The C functions do **not** clamp their float parameters. `with_alpha` and `from_hsv`
expect `[0..1]` (hue `[0..360]`), `brighten_by` and `contrast_with` expect `[-1..1]`.
Out-of-range values are passed through to raylib unchanged, exactly as in C.

## Example
```pengu
import raylib
import raylibx_colors

weave main into int:
    var c as raylib.Color is calling Color.from_hex with 0xFF0000FF
    var soft as raylib.Color is calling c.with_alpha with 0.5
    var packed as int is calling c.to_int
    return 0
```

---

### `is_equal`

> **is_equal**(a: Color, b: Color) -> bool

_Undocumented function._


### `fade`

> **fade**(color: Color, alpha: f32) -> Color

_Undocumented function._

