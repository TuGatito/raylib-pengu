> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# textures

> Source: `pengu/raylibx/textures.pengu`

Layer-2 wrapper over the 19 available texture functions of the `raylib` binding.

A texture is a GPU handle, and almost everything you do with one is an action on it, so
this family is mostly methods on the nominal types `raylib.Texture` and
`raylib.RenderTexture`:

    calling raylib.DrawTexturePro with tex, src, dst, origin, rot, tint   # binding
    calling tex.draw_pro with src, dst, origin, rot, tint                 # wrapper

`Texture2D` and `RenderTexture2D` are aliases of those two runes, so a caller that writes
`raylib.Texture2D` gets these methods too; the wrapper enchants the nominal names because
enchanting an alias pair emits duplicate C symbols (the `raymathx` lesson).

What stays module-level is the resource lifecycle: the four loaders and the two unloaders,
matching `unload_font` in `raylibx_text` and `unload_image` in `raylibx_images`.

This is family `textures` of `raylibx`; see `docs/wrappers/raylibx-textures.md`.

## This family needs a window
Measured: a texture cannot exist without a graphics context. The loaders fail *gracefully*
headless (they return an invalid zeroed texture, which the `maybe` catches), and
`is_valid`, `unload_texture`, `unload_render_texture` and `generate_mipmaps` are safe to
call on an invalid texture. Everything else -- the six draws, `set_filter`, `set_wrap`,
`update` and `update_rec` -- either does nothing meaningful or crashes without a context,
so it is type-checked by `textures_api_probe` and never called in CI.

## Memory
Nothing is copied and nothing is `MemFree`d: a texture is a handle, not a heap buffer.
The releases are `unload_texture` and `unload_render_texture`, which raylib itself makes
safe to call on an invalid texture.

## Example
```pengu
import raylib
import raylibx_textures

weave main into int:
    var tex as maybe raylib.Texture2D is calling raylibx_textures.load_texture with "sprite.png"
    if tex is present:
        var img as raylib.Texture2D is calling tex.unwrap
        calling img.set_filter with raylib.TEXTURE_FILTER_BILINEAR
        calling img.draw_at with (with x is 10.0, y is 10.0), raylib.WHITE
    return 0
```

---

### `load_texture`

> **load_texture**(path: string) -> maybe Texture

Loads a texture from an image file.
Parameters
- `path`: the image file to upload.
Returns
`some` with a valid texture, or `maybe none` when the file is missing or the upload fails.
Notes
The file is decoded on the CPU and then uploaded to the GPU, so this needs a graphics context for the second half; without one it reports `maybe none` rather than crashing.
Memory
The texture is a GPU resource: release it with `unload_texture`.
Example
```pengu
var tex as maybe raylib.Texture2D is calling raylibx_textures.load_texture with "sprite.png"
```


### `load_texture_from_image`

> **load_texture_from_image**(image: Image) -> maybe Texture

Uploads an existing image as a texture.
Parameters
- `image`: the source image; it is read, not consumed.
Returns
`some` with a valid texture, or `maybe none` when the upload fails.
Notes
The pair to `raylibx_images`: build or load an image on the CPU, then upload it once.
Memory
The image stays the caller's to unload; the returned texture is released with `unload_texture`.
Example
```pengu
var tex as maybe raylib.Texture2D is calling raylibx_textures.load_texture_from_image with img
```


### `load_texture_cubemap`

> **load_texture_cubemap**(image: Image, layout: int) -> maybe Texture

Uploads an image as a cubemap texture.
Parameters
- `image`: the source image holding the six faces.
- `layout`: how the faces are arranged; raylib fails when it cannot detect the layout.
Returns
`some` with a valid texture, or `maybe none` when raylib cannot read the layout or the upload fails.
Notes
Measured: raylib reports a failure for a layout it cannot detect instead of guessing, which the `maybe` surfaces.
Memory
Release the texture with `unload_texture`.
Example
```pengu
var sky as maybe raylib.TextureCubemap is calling raylibx_textures.load_texture_cubemap with img, 0
```


### `load_render_texture`

> **load_render_texture**(width: int, height: int) -> maybe RenderTexture

Creates a render target: a texture you can draw into.
Parameters
- `width`: the target width in pixels.
- `height`: the target height in pixels.
Returns
`some` with a valid render texture, or `maybe none` when the framebuffer cannot be created.
Notes
The target owns two GPU textures (colour and depth) plus a framebuffer. Draw into it by binding it as the drawing target, which the `drawing` family will expose as a method on this type.
Memory
Release it with `unload_render_texture`, which frees all three resources.
Example
```pengu
var target as maybe raylib.RenderTexture2D is calling raylibx_textures.load_render_texture with 256, 256
```


### `unload_texture`

> **unload_texture**(texture: Texture) -> void

Releases a texture's GPU resources.
Parameters
- `texture`: the texture to release.
Returns
Nothing.
Notes
Measured safe on an invalid texture, so a `maybe none` result can be passed straight in.
Do not use the texture after this call, and do not release a texture whose drawing is still queued.
Memory
This is the release for every texture this family hands back.
Example
```pengu
calling raylibx_textures.unload_texture with tex
```


### `unload_render_texture`

> **unload_render_texture**(target: RenderTexture) -> void

Releases a render target's GPU resources.
Parameters
- `target`: the render texture to release.
Returns
Nothing.
Notes
Frees both textures and the framebuffer in one call. Measured safe on an invalid target.
Memory
This is the release for every render texture this family hands back.
Example
```pengu
calling raylibx_textures.unload_render_texture with target
```


### `textures_api_probe`

> **textures_api_probe**(tex: Texture, patch: NPatchInfo, pixels: slice of byte) -> void

The window-bound surface: the six draws, set_filter, set_wrap, update and update_rec all
need a graphics context (measured: three of them crash outright on an invalid texture), so
this probe only type-checks them. It is not invoked by any test.

