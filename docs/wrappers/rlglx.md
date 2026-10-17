> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# rlglx

> Source: `pengu/rlglx.pengu`

Layer-2 wrapper over the 18 rlgl functions worth wrapping, out of the 163 the binding declares.

This is the smallest family in the module by design, and the plan that specifies it says so in
its first line: `rlgl` is the OpenGL escape hatch, and **145 of its 163 functions are used
through the binding directly**. `rlEnableDepthTest()`, `rlClearColor(…)` and the whole
`rlBegin`/`rlVertex2f`/`rlEnd` idiom already read perfectly; a Pengunic rename would add a hop
and nothing else (contract section 9 row 9 anticipates exactly this).

What is here is the part of `rlgl` that crosses a boundary and therefore reads badly:

    let c_vs as ref to frozen char is calling ffi.cstr_from_string with vs   # binding
    var program as u32 is calling rlgl.rlLoadShaderProgram with c_vs, c_fs

    var program as u32 is calling rlglx.load_shader_program with vs, fs     # wrapper

**Five string crossings and nine slice folds**, plus the `rlRenderBatch` type's two methods.
In all eighteen the wrapper's job is one of two things: copy a PenguScript string into a C
string (or back), or turn a slice into the pointer-and-size pair raylib wants — including the
byte count, which the caller would otherwise have to compute by hand.

## What is deliberately NOT here
The matrix stack, the immediate-mode vertex calls, the `rlEnable*`/`rlDisable*` state toggles,
the framebuffer and shader-buffer plumbing, and every function whose only difference from the
binding is an enum parameter. On that last point, measured: **a parameter typed as an `omen`
accepts any integer** (master plan D22), so typing an enum buys documentation and a shorter
call, never enforcement. `docs/wrappers/rlglx.md` lists every exclusion with its rule.

## Needs a window
Measured: `rlGetVersion` and `rlGetPixelFormatName` work with no context, but the matrix stack
**crashes** without one (`rlPushMatrix` was the probe that found it), because rlgl's state is
only initialised by `rlglInit` inside `InitWindow`. Everything else here needs a live context,
so the tests open a window; only the two string-free queries are asserted without one.

## Memory
Nothing is allocated by this module except the temporary C strings it frees itself. The GPU
handles it returns (`u32` buffer, texture and program ids) are released through the binding's
own `rlUnload*` calls, which are not wrapped because they take a bare id.

## Example
```pengu
import raylib
import rlgl
import rlglx

weave main with vs as string, fs as string into int:
    calling raylib.InitWindow with 320, 240, "rlglx"
    defer calling raylib.CloseWindow
    var program as u32 is calling rlglx.load_shader_program with vs, fs
    var location as maybe int is calling rlglx.uniform_location with program, "u_time"
    return 0
```

---

### `pixel_format_name`

> **pixel_format_name**(format: rlPixelFormat) -> string

Names a pixel format.
Parameters
- `format`: the format to name, as an `rlgl.rlPixelFormat`.
Returns
The format's name, or the string `"UNKNOWN"` for a value rlgl does not recognise.
Notes
**Measured never to return a null pointer**, which is why this is a plain `string` rather than
a `maybe`: `R8G8B8A8` for the common case and `"UNKNOWN"` for a bogus one.
Memory
raylib owns the returned `const char*`; the wrapper copies it into an owned PenguScript string
and frees nothing.
Example
```pengu
var name as string is calling rlglx.pixel_format_name with rlgl.RL_PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
```


### `load_shader`

> **load_shader**(code: string, shader_type: int) -> u32

Compiles one shader stage from source.
Parameters
- `code`: the GLSL source.
- `shader_type`: which stage to compile, as one of raylib's `RL_VERTEX_SHADER` /
`RL_FRAGMENT_SHADER` / `RL_COMPUTE_SHADER` constants. The binding types it as a plain `int`
because rlgl defines those as `#define`s rather than as an enum.
Returns
The OpenGL program id, or `0` when the shader fails to compile.
Notes
**`0` is the failure sentinel and the binding reports nothing else**, so check it. Unlike
`raylibx.shaders`, no fallback program is substituted: this is the raw layer.
Write the GLSL with **real newlines** (a raw triple-quoted string, or a normal literal with
escapes): `\n` inside a raw string is a literal backslash-n and the compile silently fails.
Memory
The program id is a GPU handle: release it with `rlgl.rlUnloadShader`.
Example
```pengu
var stage as u32 is calling rlglx.load_shader with source, (rlgl.RL_FRAGMENT_SHADER to int)
```


### `load_shader_program`

> **load_shader_program**(vs_code: string, fs_code: string) -> u32

Compiles and links a vertex and a fragment shader into one program.
Parameters
- `vs_code`: the vertex stage source.
- `fs_code`: the fragment stage source.
Returns
The OpenGL program id, or `0` when either stage fails to compile or the link fails.
Notes
This is the two-string crossing that justifies the module: the binding takes two
`const char*`, which costs two `ffi.cstr_from_string` calls at every site.
The sources need **real newlines**; see `load_shader`.
Memory
The program id is a GPU handle: release it with `rlgl.rlUnloadShaderProgram`.
Example
```pengu
var program as u32 is calling rlglx.load_shader_program with vs, fs
```


### `uniform_location`

> **uniform_location**(program: u32, name: string) -> maybe int

Returns the location a linked program assigned to a uniform.
Parameters
- `program`: the program id from `load_shader_program`.
- `name`: the uniform's name, exactly as it appears in the source.
Returns
`some` with the location, or `maybe none` when the program has no such uniform.
Notes
Measured: rlgl returns **`-1`** for a name the program does not declare, which is the
predicate. A location is a small integer, not a handle, and it stays valid for the program's
lifetime.
Memory
No allocation; a single direct C call.
Example
```pengu
var location as maybe int is calling rlglx.uniform_location with program, "u_time"
```


### `attrib_location`

> **attrib_location**(program: u32, name: string) -> maybe int

Returns the location a linked program assigned to a vertex attribute.
Parameters
- `program`: the program id from `load_shader_program`.
- `name`: the attribute's name, exactly as it appears in the source.
Returns
`some` with the location, or `maybe none` when the program has no such attribute.
Notes
It is the attribute counterpart of `uniform_location`, with the same measured `-1` sentinel.
Memory
No allocation; a single direct C call.
Example
```pengu
var location as maybe int is calling rlglx.attrib_location with program, "vertexPosition"
```


### `load_vertex_buffer`

> **load_vertex_buffer**(data: slice of byte, dynamic: bool) -> u32

Uploads a slice of bytes as a vertex buffer.
Parameters
- `data`: the vertex data, as raw bytes.
- `dynamic`: `true` when the buffer will be rewritten later with `update_vertex_buffer`.
Returns
The OpenGL buffer id, or `0` when rlgl cannot create it.
Notes
**The byte size is the slice's length**: the binding asks for it separately and would otherwise
make every caller compute it. An empty slice uploads nothing and rlgl still returns a valid
empty buffer.
Memory
The buffer id is a GPU handle: release it with `rlgl.rlUnloadVertexBuffer`.
Example
```pengu
var vbo as u32 is calling rlglx.load_vertex_buffer with (data at 0 to (data.length)), true
```


### `load_vertex_buffer_element`

> **load_vertex_buffer_element**(data: slice of byte, dynamic: bool) -> u32

Uploads a slice of bytes as an index buffer.
Parameters
- `data`: the index data, as raw bytes.
- `dynamic`: `true` when the buffer will be rewritten later.
Returns
The OpenGL buffer id, or `0` when rlgl cannot create it.
Notes
The element counterpart of `load_vertex_buffer`, with the same folded byte size. Indices are
bytes rather than a typed slice because rlgl accepts both 16- and 32-bit indices and the caller
is the one who knows which it built.
Memory
The buffer id is a GPU handle: release it with `rlgl.rlUnloadVertexBuffer`.
Example
```pengu
var ebo as u32 is calling rlglx.load_vertex_buffer_element with (indices at 0 to (indices.length)), false
```


### `update_vertex_buffer`

> **update_vertex_buffer**(id: u32, data: slice of byte, offset: int) -> void

Rewrites part of a vertex buffer.
Parameters
- `id`: the buffer id from `load_vertex_buffer`.
- `data`: the replacement bytes.
- `offset`: the byte offset to start writing at.
Returns
Nothing.
Notes
The buffer must have been created with `dynamic`, and the offset must land on a whole-vertex
boundary or the geometry becomes garbage. The byte size is the slice's length.
Memory
The buffer keeps belonging to the caller.
Example
```pengu
calling rlglx.update_vertex_buffer with vbo, (data at 0 to (data.length)), 0
```


### `update_vertex_buffer_elements`

> **update_vertex_buffer_elements**(id: u32, data: slice of byte, offset: int) -> void

Rewrites part of an index buffer.
Parameters
- `id`: the buffer id from `load_vertex_buffer_element`.
- `data`: the replacement bytes.
- `offset`: the byte offset to start writing at.
Returns
Nothing.
Notes
The element counterpart of `update_vertex_buffer`, with the same folded byte size.
Memory
The buffer keeps belonging to the caller.
Example
```pengu
calling rlglx.update_vertex_buffer_elements with ebo, (indices at 0 to (indices.length)), 0
```


### `set_uniform_floats`

> **set_uniform_floats**(location: int, values: slice of f32) -> void

Uploads a slice of floats as a `float` uniform array.
Parameters
- `location`: the location from `uniform_location`.
- `values`: the floats to upload; an empty slice uploads nothing.
Returns
Nothing.
Notes
**Only the float case is exposed.** raylib's element count depends on the uniform type — for a
`vec2` array the same parameter counts vectors, so the call would read `count * 2` floats — and
exposing that ambiguity is worse than leaving other uniform types to the binding
(`raylibx.shaders` D7 takes the same position). Here `count` is simply the slice's length.
Memory
No allocation beyond the temporary pointer; the GPU copies the values.
Example
```pengu
calling rlglx.set_uniform_floats with location, (values at 0 to (values.length))
```


### `set_uniform_matrices`

> **set_uniform_matrices**(location: int, matrices: slice of Matrix) -> void

Uploads a slice of matrices as a `mat4` uniform array.
Parameters
- `location`: the location from `uniform_location`.
- `matrices`: the matrices to upload; an empty slice is a no-op.
Returns
Nothing.
Notes
The count is the slice's length, and a `Matrix` is sixteen contiguous floats, so the layout is
exactly what rlgl expects. This is how a shader receives a whole skeleton or a set of
transforms in one call.
Memory
No allocation beyond the temporary pointer; the GPU copies the values.
Example
```pengu
calling rlglx.set_uniform_matrices with location, (bones at 0 to (bones.length))
```


### `load_texture`

> **load_texture**(pixels: slice of byte, width: int, height: int, format: rlPixelFormat, mipmap_count: int) -> u32

Uploads a slice of bytes as a texture.
Parameters
- `pixels`: the pixel data in `format`, or an **empty slice** to allocate without uploading.
- `width`: the texture width in pixels.
- `height`: the texture height in pixels.
- `format`: the pixel format, as an `rlgl.rlPixelFormat`.
- `mipmap_count`: how many mipmap levels to allocate, `1` for none.
Returns
The OpenGL texture id, or `0` when rlgl cannot create it.
Notes
**An empty slice is a valid input, not a no-op**: rlgl accepts a null data pointer to create an
uninitialised texture, which is what a render target or a streamed texture starts as. This is
the opposite of the other families' empty-slice guards, and it is deliberate.
Memory
The texture id is a GPU handle: release it with `rlgl.rlUnloadTexture`.
Example
```pengu
var texture as u32 is calling rlglx.load_texture with (pixels at 0 to (pixels.length)), 256, 256, rlgl.RL_PIXELFORMAT_UNCOMPRESSED_R8G8B8A8, 1
```


### `update_texture`

> **update_texture**(id: u32, x: int, y: int, width: int, height: int, format: rlPixelFormat, pixels: slice of byte) -> void

Rewrites a rectangle of an existing texture.
Parameters
- `id`: the texture id from `load_texture`.
- `x`: the left edge of the region to rewrite.
- `y`: the top edge of the region to rewrite.
- `width`: the region width in pixels.
- `height`: the region height in pixels.
- `format`: the pixel format of `pixels`, as an `rlgl.rlPixelFormat`.
- `pixels`: the bytes to upload, which must hold `width * height` pixels in `format`.
Returns
Nothing.
Notes
The size comes from `width`/`height` rather than from the slice, because that is what rlgl reads:
a slice shorter than the region would read past its end, so the docstring states the contract.
Memory
The texture keeps belonging to the caller.
Example
```pengu
calling rlglx.update_texture with texture, 0, 0, 16, 16, rlgl.RL_PIXELFORMAT_UNCOMPRESSED_R8G8B8A8, (pixels at 0 to (pixels.length))
```


### `draw_vertex_array_elements`

> **draw_vertex_array_elements**(offset: int, indices: slice of u32) -> void

Draws indexed vertices from an index buffer.
Parameters
- `offset`: how many indices to skip.
- `indices`: the index data as 32-bit values; an empty slice is a no-op.
Returns
Nothing; the geometry is queued into the current batch.
Notes
The count is the slice's length, and this is the one `rlDrawVertexArray*` call whose element type
is unambiguous in practice, which is why it is typed as `slice of u32` rather than bytes. It is
the indexed counterpart of the binding's own `rlDrawVertexArray`.
Memory
No allocation; the indices are only read during the call.
Example
```pengu
calling rlglx.draw_vertex_array_elements with 0, (indices at 0 to (indices.length))
```


### `load_render_batch`

> **load_render_batch**(num_buffers: int, buffer_elements: int) -> rlRenderBatch

Creates a render batch: a set of vertex buffers with their own draw-call queue.
Parameters
- `num_buffers`: how many vertex buffers the batch owns; `1` is the usual value.
- `buffer_elements`: how many elements each buffer holds.
Returns
The batch, ready to be made active with `set_active`.
Notes
This is raylib's own batching machinery exposed. Custom batches are for renderers that need more
than the single default one, which is why the type gets methods and the other 145 functions do
not.
Memory
The batch owns its buffers: release it with `unload_render_batch`.
Example
```pengu
var batch as rlgl.rlRenderBatch is calling rlglx.load_render_batch with 1, 8192
```


### `unload_render_batch`

> **unload_render_batch**(batch: rlRenderBatch) -> void

Releases a render batch and its buffers.
Parameters
- `batch`: the batch to release.
Returns
Nothing.
Notes
Do not release the batch raylib is currently recording into; make another one active first.
Memory
This is the release for `load_render_batch`.
Example
```pengu
calling rlglx.unload_render_batch with batch
```


### `vertex_source`

> **vertex_source**() -> string

_Undocumented function._


### `fragment_source`

> **fragment_source**() -> string

_Undocumented function._

