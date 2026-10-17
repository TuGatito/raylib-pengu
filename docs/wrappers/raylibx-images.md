> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# images

> Source: `pengu/raylibx/images.pengu`

Layer-2 wrapper over the 74 image functions of the `raylib` binding: the biggest family
of the module, and the one where the wrapper becomes a type.

The image *is* the subject of almost everything here, so the family is dominated by
methods on `raylib.Image`: `img.crop with rect`, `img.resize with 128, 128`,
`img.draw_circle with 8, 8, 4, raylib.RED`. What stays module-level is what has no
receiver worth naming: the loaders, the exporters and the nine `gen_image_*` factories.

Every mutator returns `void` and changes the image in place. raylib owns the pixel buffer,
so an image that comes from a loader or a factory must be released with `unload_image`,
and so must the ones that `copy`, `region` and `channel` hand back.

This is family `images` of `raylibx`; see `docs/wrappers/raylibx-images.md`.

## Most of it is testable without a window
The `gen_image_*` factories, the transforms, the drawing methods and the pixel readers are
pure CPU work over a heap buffer -- measured, not assumed -- so they are asserted directly
in CI. Only three entries need a graphics context: `load_image_from_texture`
(a GPU read-back), `load_image_from_screen`, and the two text renderers, which walk the
default font's glyph table (null before `InitWindow`; the `text` family measured the
segfault).

## Memory
The wrapper never leaks and never frees twice. `colors` and `palette` copy raylib's array
into an owned PenguScript list and release it with `UnloadImageColors`/`UnloadImagePalette`;
`export_image_to_memory` copies and then `MemFree`s, because the header says the buffer
belongs to the caller.

## Example
```pengu
import raylib
import raylibx_images

weave main into int:
    var img as raylib.Image is calling raylibx_images.gen_image_color with 32, 32, raylib.RED
    defer calling raylibx_images.unload_image with img
    calling img.draw_circle with 16, 16, 8, raylib.WHITE
    calling img.resize with 64, 64
    var pixel as raylib.Color is calling img.color_at with 20, 20
    return 0
```

---

### `is_image_valid`

> **is_image_valid**(image: Image) -> bool

_Undocumented function._


### `unload_image`

> **unload_image**(image: Image) -> void

_Undocumented function._


### `load_image`

> **load_image**(path: string) -> maybe Image

_Undocumented function._


### `load_image_raw`

> **load_image_raw**(path: string, width: int, height: int, format: PixelFormat, header_size: int) -> maybe Image

_Undocumented function._


### `load_image_from_memory`

> **load_image_from_memory**(file_type: string, data: slice of byte) -> maybe Image

_Undocumented function._


### `load_image_from_texture`

> **load_image_from_texture**(texture: Texture) -> maybe Image

_Undocumented function._


### `load_image_from_screen`

> **load_image_from_screen**() -> maybe Image

_Undocumented function._


### `export_image`

> **export_image**(image: Image, path: string) -> bool

_Undocumented function._


### `export_image_to_memory`

> **export_image_to_memory**(image: Image, file_type: string) -> maybe list of byte

_Undocumented function._


### `export_image_as_code`

> **export_image_as_code**(image: Image, path: string) -> bool

_Undocumented function._


### `gen_image_color`

> **gen_image_color**(width: int, height: int, color: Color) -> Image

_Undocumented function._


### `gen_image_gradient_linear`

> **gen_image_gradient_linear**(width: int, height: int, direction: int, start: Color, end: Color) -> Image

_Undocumented function._


### `gen_image_gradient_radial`

> **gen_image_gradient_radial**(width: int, height: int, density: f32, inner: Color, outer: Color) -> Image

_Undocumented function._


### `gen_image_gradient_square`

> **gen_image_gradient_square**(width: int, height: int, density: f32, inner: Color, outer: Color) -> Image

_Undocumented function._


### `gen_image_checked`

> **gen_image_checked**(width: int, height: int, checks_x: int, checks_y: int, col1: Color, col2: Color) -> Image

_Undocumented function._


### `gen_image_white_noise`

> **gen_image_white_noise**(width: int, height: int, factor: f32) -> Image

_Undocumented function._


### `gen_image_perlin_noise`

> **gen_image_perlin_noise**(width: int, height: int, offset_x: int, offset_y: int, scale: f32) -> Image

_Undocumented function._


### `gen_image_cellular`

> **gen_image_cellular**(width: int, height: int, tile_size: int) -> Image

_Undocumented function._


### `gen_image_text`

> **gen_image_text**(width: int, height: int, text: string) -> Image

_Undocumented function._


### `image_from_text`

> **image_from_text**(text: string, font_size: int, color: Color) -> Image

_Undocumented function._


### `image_from_text_ex`

> **image_from_text_ex**(font: Font, text: string, font_size: f32, spacing: f32, tint: Color) -> Image

_Undocumented function._


### `pixel_data_size`

> **pixel_data_size**(width: int, height: int, format: PixelFormat) -> int

_Undocumented function._


### `images_api_probe`

> **images_api_probe**(tex: Texture, font: Font) -> void

The window-bound surface is not called in CI: a GPU read-back, a framebuffer capture and
the two text renderers, which walk the default font's glyph table (null before
InitWindow; the text family measured the segfault). This probe type-checks them.

