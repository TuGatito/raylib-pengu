> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# raylib_pengu

> Source: `pengu/raylib_pengu.d.pengu`

raylib-pengu — facade module for the whole binding.

This file declares nothing itself: it re-exports every module of the binding
so a program can pull the entire raylib surface in with a single import.

    import raylib_pengu

The module name uses an underscore because an import path cannot contain a
hyphen (`import raylib-pengu` is a syntax error); the repository itself is
still called `raylib-pengu`.

Prefer importing only what you use (`import raylib`, `import raymath`, …):
the compiler's dead-code elimination already drops unused bindings, and a
narrower import keeps the dependency explicit.

The modules:
  raylib     raylib.h    core: window, input, shapes, textures, text, models, audio
  raymath    raymath.h   vector/quaternion/matrix maths (implemented in libraylib)
  rcamera    rcamera.h   the Camera3D helper system (implemented in libraylib)
  rgestures  rgestures.h touch/gesture detection (implemented in libraylib)
  rlgl       rlgl.h      the OpenGL abstraction layer raylib builds on
  raygui     raygui.h    immediate-mode GUI (compiled by c/raygui_impl.c)

Regenerate the individual bindings with the procedure in README.md; this
facade is hand-written and must be kept in step with `ls pengu/*.d.pengu`.

---

_No documented symbols in `raylib_pengu.d.pengu`._
