> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# shaders

> Source: `pengu/raylibx/shaders.pengu`

Layer-2 wrapper over the 10 shader functions of the `raylib` binding, which become 15
wrappers: the shader is the subject of all of them, so they are methods on the nominal
`raylib.Shader`, plus the three module-level lifecycle entries.

The family's reason to exist is that **one C function covers every uniform type through a
`void*` and an enum**:

    float v = 0.5f;
    SetShaderValue(shader, loc, &v, SHADER_UNIFORM_FLOAT);          # binding
    calling shader.set_float with loc, 0.5                          # wrapper

`SetShaderValue` therefore appears seven times, once per uniform type, each typed. That is
contract section 2's "one C function may become several wrappers when the type is what
varies", and it is what removes both the `void*` and the enum from the call site.

This is family `shaders` of `raylibx`; see `docs/wrappers/raylibx-shaders.md`.

## The silent fallback, and what the wrapper does about it
Measured: raylib **never fails to return a shader**. A missing file and empty source both
yield the *default* shader with `IsShaderValid() == true`, so there is no sentinel to fold
and the caller would silently get the wrong program. Only a source that is non-empty and
fails to compile reports `false`.

The wrapper therefore checks the precondition first: `load_shader` requires both paths to
be files, and `load_shader_from_memory` requires both sources to be non-empty. After that,
`maybe none` means "your shader did not load", covering both the precondition and a
compile failure. To detect a *fallback* for any other reason, ask for one of your own
uniforms: `location` returns `maybe none` when the shader has fallen back to the default.

## Needs a window
Measured: loading a shader compiles GLSL, so it needs a graphics context, and this
environment has one. Unlike the earlier families, **every wrapped function here is
asserted against a live window**, including a real GLSL 330 compile.

## Memory
A shader is a GPU program: `unload_shader` releases it, and the wrapper never copies or
frees anything else. The temporary C strings for names and paths are released by `std.ffi`.

## Example
```pengu
import raylib
import raylibx_shaders

weave main into int:
    var shader as maybe raylib.Shader is calling raylibx_shaders.load_shader_from_memory with vs, fs
    if shader is present:
        var prog as raylib.Shader is calling shader.unwrap
        defer calling raylibx_shaders.unload_shader with prog
        var loc as maybe int is calling prog.location with "u_time"
        if loc is present:
            calling prog.set_float with (calling loc.unwrap), 1.5
    return 0
```

---

### `load_shader`

> **load_shader**(vs_path: string, fs_path: string) -> maybe Shader

_Undocumented function._


### `load_shader_from_memory`

> **load_shader_from_memory**(vs_code: string, fs_code: string) -> maybe Shader

_Undocumented function._


### `unload_shader`

> **unload_shader**(shader: Shader) -> void

_Undocumented function._


### `vertex_source`

> **vertex_source**() -> string

The sources are raw triple-quoted strings: raw because GLSL is full of braces, which a
normal literal would read as interpolation, and triple-quoted because GLSL is line-oriented
and `#version` must be followed by a real newline. The language guide names shaders as the
motivating case for raw literals.


### `fragment_source`

> **fragment_source**() -> string

_Undocumented function._


### `must_location`

> **must_location**(prog: Shader, name: string) -> int

A helper so the setters test reads as a sequence of uploads rather than a pile of unwraps.

