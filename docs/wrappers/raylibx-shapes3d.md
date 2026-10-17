> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# shapes3d

> Source: `pengu/raylibx/shapes3d.pengu`

Layer-2 wrapper over the 21 primitive 3D shape functions of the `raylib` binding.

The family splits by the anchor rule of `docs/NOTES.md` D9, extended to 3D:
raylib marks the functions whose first argument *is* the anchor with a `V` in the name.

- **4 methods on `raylib.Vector3`**: `draw_point`, `draw_cube`, `draw_cube_wires`,
  `draw_plane`. Each drops the binding's `_v` suffix, so `pos.draw_cube with extent, color`
  reads as "at `pos`, draw a cube of `size`".
- **17 module-level functions**: everything else, with the binding's exact names. The
  sphere and cylinder families take a `Vector3` centre but carry no `V`, so they stay
  here; making them methods would invent names that no longer say which C function runs.

This is family `shapes3d` of `raylibx`; see `docs/wrappers/raylibx-shapes3d.md`.

## Drawing needs a 3D mode
Every entry issues a raylib drawing command and is only meaningful between `BeginMode3D`
and `EndMode3D`. The tests assert only the empty-slice guard of `draw_triangle_strip_3d`;
the rest of the surface is type-checked by `draw_api_probe` and not called in CI.

## Memory
No allocation and nothing to release. The only FFI boundary is `slice of Vector3` ->
`ref to void` in `draw_triangle_strip_3d`, which guards the empty slice before taking
the address of element zero.

## Example
```pengu
import raylib
import raylibx_shapes3d

weave main into int:
    var center as raylib.Vector3 is with x is 0.0, y is 1.0, z is 0.0
    calling center.draw_cube with (with x is 1.0, y is 1.0, z is 1.0), raylib.GREEN
    calling draw_grid with 10, 1.0
    return 0
```

---

### `draw_line_3d`

> **draw_line_3d**(start: Vector3, end: Vector3, color: Color) -> void

_Undocumented function._


### `draw_circle_3d`

> **draw_circle_3d**(center: Vector3, radius: f32, rotation_axis: Vector3, rotation_angle: f32, color: Color) -> void

_Undocumented function._


### `draw_triangle_3d`

> **draw_triangle_3d**(v1: Vector3, v2: Vector3, v3: Vector3, color: Color) -> void

_Undocumented function._


### `draw_triangle_strip_3d`

> **draw_triangle_strip_3d**(points: slice of Vector3, color: Color) -> void

_Undocumented function._


### `draw_cube`

> **draw_cube**(position: Vector3, width: f32, height: f32, length: f32, color: Color) -> void

_Undocumented function._


### `draw_cube_wires`

> **draw_cube_wires**(position: Vector3, width: f32, height: f32, length: f32, color: Color) -> void

_Undocumented function._


### `draw_sphere`

> **draw_sphere**(center: Vector3, radius: f32, color: Color) -> void

_Undocumented function._


### `draw_sphere_ex`

> **draw_sphere_ex**(center: Vector3, radius: f32, rings: int, slices: int, color: Color) -> void

_Undocumented function._


### `draw_sphere_wires`

> **draw_sphere_wires**(center: Vector3, radius: f32, rings: int, slices: int, color: Color) -> void

_Undocumented function._


### `draw_cylinder`

> **draw_cylinder**(position: Vector3, radius_top: f32, radius_bottom: f32, height: f32, sides: int, color: Color) -> void

_Undocumented function._


### `draw_cylinder_ex`

> **draw_cylinder_ex**(start: Vector3, end: Vector3, start_radius: f32, end_radius: f32, sides: int, color: Color) -> void

_Undocumented function._


### `draw_cylinder_wires`

> **draw_cylinder_wires**(position: Vector3, radius_top: f32, radius_bottom: f32, height: f32, sides: int, color: Color) -> void

_Undocumented function._


### `draw_cylinder_wires_ex`

> **draw_cylinder_wires_ex**(start: Vector3, end: Vector3, start_radius: f32, end_radius: f32, sides: int, color: Color) -> void

_Undocumented function._


### `draw_capsule`

> **draw_capsule**(start: Vector3, end: Vector3, radius: f32, rings: int, slices: int, color: Color) -> void

_Undocumented function._


### `draw_capsule_wires`

> **draw_capsule_wires**(start: Vector3, end: Vector3, radius: f32, rings: int, slices: int, color: Color) -> void

_Undocumented function._


### `draw_ray`

> **draw_ray**(ray: Ray, color: Color) -> void

_Undocumented function._


### `draw_grid`

> **draw_grid**(slices: int, spacing: f32) -> void

_Undocumented function._


### `draw_api_probe`

> **draw_api_probe**() -> void

The whole family is window-bound: every entry below issues a raylib drawing command
that is only meaningful between BeginMode3D and EndMode3D, so none of it is asserted
in CI. This probe exists so that every public signature is type-checked at build time.

