> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# text

> Source: `pengu/raylibx/text.pengu`

pengu
Layer-2 wrapper over the 56 font and text functions of the `raylib` binding.

This is the busiest family for the string boundary, and the header does not make the
two ownership families obvious, so they were measured (see the family plan D2):

- `text_upper`, `text_lower`, `text_pascal`, `text_snake`, `text_camel`, `text_subtext`,
  `text_without_spaces`, `text_between`, `text_replace`, `text_replace_between`,
  `text_insert`, `text_join`, `split_text` and `codepoint_to_text` return a **static
  buffer that the next call to the same function overwrites**. The wrapper copies it into
  an owned `string` and frees nothing.
- `text_replace_alloc`, `text_replace_between_alloc` and `text_insert_alloc` return a
  **fresh allocation**. The wrapper copies it and frees it with `MemFree`.

Five methods live on `raylib.Font` (`draw`, `draw_pro`, `draw_codepoint`,
`draw_codepoints`, `measure`); everything else is a module-level function.

This is family `text` of `raylibx`; see `docs/wrappers/raylibx-text.md`.

## A headless process has no usable font
Outside `InitWindow`, `GetFontDefault()` returns a `Font` with `glyphCount == 0` and a
null glyph table, and measuring or querying a glyph on it **segfaults** (measured). Only
the pure text and codepoint groups are asserted in CI; the font lifecycle, the glyph
queries and the drawing entries are type-checked by `draw_api_probe` and not called.

## Memory
Nothing is leaked and nothing is freed twice: the three `*_alloc` results and the
`GenImageFontAtlas` rectangle array are `MemFree`d inside their wrappers, and
`UnloadFontData`/`UnloadCodepoints` are called inside the wrappers that own those
buffers. The caller always receives an owned PenguScript value.

## Example
```pengu
import raylib
import raylibx_text

weave main into int:
    var parts as list of string is calling split_text with "a,b,c", 44
    defer banish parts
    var joined as string is calling text_join with (parts at 0 to (parts.length)), "-"
    var shouty as string is calling text_upper with joined
    return parts.length
```

---

### `default_font`

> **default_font**() -> Font

_Undocumented function._


### `load_font`

> **load_font**(path: string) -> maybe Font

_Undocumented function._


### `load_font_ex`

> **load_font_ex**(path: string, font_size: int, codepoints: slice of int) -> maybe Font

_Undocumented function._


### `load_font_from_image`

> **load_font_from_image**(image: Image, key: Color, first_char: int) -> maybe Font

_Undocumented function._


### `load_font_from_memory`

> **load_font_from_memory**(file_type: string, data: slice of byte, font_size: int, codepoints: slice of int) -> maybe Font

_Undocumented function._


### `is_font_valid`

> **is_font_valid**(font: Font) -> bool

_Undocumented function._


### `unload_font`

> **unload_font**(font: Font) -> void

_Undocumented function._


### `export_font_as_code`

> **export_font_as_code**(font: Font, path: string) -> bool

_Undocumented function._


### `font_glyph_index`

> **font_glyph_index**(font: Font, codepoint: int) -> int

_Undocumented function._


### `font_glyph_info`

> **font_glyph_info**(font: Font, codepoint: int) -> GlyphInfo

_Undocumented function._


### `font_glyph_atlas_rec`

> **font_glyph_atlas_rec**(font: Font, codepoint: int) -> Rectangle

_Undocumented function._


### `load_font_data`

> **load_font_data**(data: slice of byte, font_size: int, codepoints: slice of int, kind: int) -> list of GlyphInfo

_Undocumented function._


### `font_atlas_image`

> **font_atlas_image**(glyphs: slice of GlyphInfo, font_size: int, padding: int, pack_method: int) -> Image

_Undocumented function._


### `draw_fps`

> **draw_fps**(x: int, y: int) -> void

_Undocumented function._


### `draw_text`

> **draw_text**(text: string, x: int, y: int, font_size: int, color: Color) -> void

_Undocumented function._


### `measure_text`

> **measure_text**(text: string, font_size: int) -> int

_Undocumented function._


### `text_upper`

> **text_upper**(text: string) -> string

_Undocumented function._


### `text_lower`

> **text_lower**(text: string) -> string

_Undocumented function._


### `text_pascal`

> **text_pascal**(text: string) -> string

_Undocumented function._


### `text_snake`

> **text_snake**(text: string) -> string

_Undocumented function._


### `text_camel`

> **text_camel**(text: string) -> string

_Undocumented function._


### `text_without_spaces`

> **text_without_spaces**(text: string) -> string

_Undocumented function._


### `text_subtext`

> **text_subtext**(text: string, position: int, length: int) -> string

_Undocumented function._


### `text_between`

> **text_between**(text: string, begin: string, end: string) -> string

_Undocumented function._


### `text_replace`

> **text_replace**(text: string, search: string, replacement: string) -> string

_Undocumented function._


### `text_replace_between`

> **text_replace_between**(text: string, begin: string, end: string, replacement: string) -> string

_Undocumented function._


### `text_insert`

> **text_insert**(text: string, insert: string, position: int) -> string

_Undocumented function._


### `text_replace_alloc`

> **text_replace_alloc**(text: string, search: string, replacement: string) -> string

_Undocumented function._


### `text_replace_between_alloc`

> **text_replace_between_alloc**(text: string, begin: string, end: string, replacement: string) -> string

_Undocumented function._


### `text_insert_alloc`

> **text_insert_alloc**(text: string, insert: string, position: int) -> string

_Undocumented function._


### `text_join`

> **text_join**(parts: slice of string, delimiter: string) -> string

_Undocumented function._


### `split_text`

> **split_text**(text: string, delimiter: char) -> list of string

_Undocumented function._


### `split_lines`

> **split_lines**(text: string) -> list of string

_Undocumented function._


### `text_is_equal`

> **text_is_equal**(a: string, b: string) -> bool

_Undocumented function._


### `text_length`

> **text_length**(text: string) -> u32

_Undocumented function._


### `text_find`

> **text_find**(text: string, search: string) -> maybe int

_Undocumented function._


### `text_to_integer`

> **text_to_integer**(text: string) -> int

_Undocumented function._


### `text_to_float`

> **text_to_float**(text: string) -> f32

_Undocumented function._


### `codepoint_count`

> **codepoint_count**(text: string) -> int

_Undocumented function._


### `codepoint_at`

> **codepoint_at**(text: string) -> maybe int

_Undocumented function._


### `codepoint_to_text`

> **codepoint_to_text**(codepoint: int) -> string

_Undocumented function._


### `codepoints_from_text`

> **codepoints_from_text**(text: string) -> list of int

_Undocumented function._


### `text_from_codepoints`

> **text_from_codepoints**(codepoints: slice of int) -> maybe string

_Undocumented function._


### `set_text_line_spacing`

> **set_text_line_spacing**(spacing: int) -> void

_Undocumented function._


### `measure_text_codepoints`

> **measure_text_codepoints**(font: Font, codepoints: slice of int, font_size: f32, spacing: f32) -> Vector2

_Undocumented function._


### `text_api_probe`

> **text_api_probe**() -> void

The drawing and font-lifecycle surface is not called in CI: the drawing entries need an
active frame, and the font entries need InitWindow, because before it GetFontDefault()
has no glyph table and measuring or querying a glyph on it segfaults (family plan D16).
This probe exists so every public signature is type-checked at build time.

