> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# rcamerax

> Source: `pengu/rcamerax.pengu`

Layer-2 wrapper over the `rcamera` binding: a Pengunic `Camera3D` controller.

The binding exposes twelve free functions that all take `Camera *` as their first
parameter. This wrapper turns each of them into a method on `raylib.Camera3D`, so the
`(sigil of cam)` that the FFI boundary requires disappears from the call site:

    calling rcamera.CameraMoveForward with (sigil of cam), 0.1, true   # binding
    calling cam.move_forward with 0.1, true                            # wrapper

`UpdateCamera` and `UpdateCameraPro` are **not** here: they are already declared in
`pengu/raylib.d.pengu` and remain reachable as `raylib.UpdateCamera` /
`raylib.UpdateCameraPro`. This module covers custom camera controllers built by hand.

Note that `rcamera.h` only supports `Camera3D`; it has no helper for `Camera2D`.

## Cost
Every method lowers to exactly one call into the binding. Verified with `pengu expand`:
the seven mutators emit `Camera3D_move_* / yaw / pitch / roll(&cam, ...)` and the five getters
emit `Camera3D_forward(&cam)` and friends, with no temporaries and no `memcpy`. Keep that
invariant when editing: re-run `pengu expand` if a method name or body changes.

## Memory
No allocation, no ownership, nothing to release: every method is arithmetic over the
camera struct. There is no `banish`, no `std.ffi` and no `transmute` in this module.

## Example
```pengu
import raylib
import rcamerax

weave main into int:
    var cam as raylib.Camera3D is with position is (calling Vector3.new with 0.0, 10.0, 10.0), target is (calling Vector3.new with 0.0, 0.0, 0.0), up is (calling Vector3.new with 0.0, 1.0, 0.0), fovy is 45.0, projection is 0
    calling cam.move_forward with 0.1, true
    var forward as raylib.Vector3 is calling cam.forward
    return 0
```

---

_No documented symbols in `rcamerax.pengu`._
