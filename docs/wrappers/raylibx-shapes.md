> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# shapes

> Source: `pengu/raylibx/shapes.pengu`

Layer-2 wrapper over the 2D shape surface of the `raylib` binding.

The 61 functions split three ways, following the master plan's subjecthood rule
(`docs/NOTES.md` D9):

- **18 methods on `raylib.Vector2`** — every `Draw*` whose C name ends in `V`, because
  then the first argument really is the shape's anchor: `center.draw_circle`, `a.draw_line_to`.
- **7 methods on `raylib.Rectangle`** — every function whose first argument is a rectangle:
  `rec.draw`, `rec.draw_rounded`, `rec.contains_point`.
- **36 module-level functions** — the integer-coordinate variants (`draw_pixel with x, y, color`),
  the slice-shaped draws (`draw_line_strip`, `draw_spline_*`) and the collision predicates.

This is family `shapes` of `raylibx`; see `docs/wrappers/raylibx-shapes.md`.

## Drawing needs a window
Every `Draw*` entry issues a raylib drawing command and is only meaningful between
`BeginDrawing` and `EndDrawing`. The tests in this file therefore assert the *pure*
half of the family (collision, containment, the shapes-texture getters) and the
empty-slice guard of the slice-shaped draws; the drawing calls themselves are
type-checked by `draw_api_probe` but not executed in CI.

## Memory
No allocation and nothing to release. The only FFI boundary is `slice of Vector2` ->
`ref to frozen Vector2` in the nine slice-shaped functions, each of which guards the
empty slice before taking the address of element zero.

## Example
```pengu
import raylib
import raylibx_shapes

weave main into int:
    var center as raylib.Vector2 is with x is 100.0, y is 100.0
    var rec as raylib.Rectangle is with x is 10.0, y is 10.0, width is 40.0, height is 20.0
    calling center.draw_circle with 20.0, raylib.RED
    calling rec.draw_rounded with 0.4, 8, raylib.WHITE
    return 0
```

---

### `draw_pixel`

> **draw_pixel**(x: int, y: int, color: Color) -> void

_Undocumented function._


### `draw_line`

> **draw_line**(x1: int, y1: int, x2: int, y2: int, color: Color) -> void

_Undocumented function._


### `draw_circle`

> **draw_circle**(center_x: int, center_y: int, radius: f32, color: Color) -> void

_Undocumented function._


### `draw_ellipse`

> **draw_ellipse**(center_x: int, center_y: int, radius_h: f32, radius_v: f32, color: Color) -> void

_Undocumented function._


### `draw_ellipse_lines`

> **draw_ellipse_lines**(center_x: int, center_y: int, radius_h: f32, radius_v: f32, color: Color) -> void

_Undocumented function._


### `draw_rectangle`

> **draw_rectangle**(x: int, y: int, width: int, height: int, color: Color) -> void

_Undocumented function._


### `draw_rectangle_lines`

> **draw_rectangle_lines**(x: int, y: int, width: int, height: int, color: Color) -> void

_Undocumented function._


### `draw_rectangle_gradient_v`

> **draw_rectangle_gradient_v**(x: int, y: int, width: int, height: int, top: Color, bottom: Color) -> void

_Undocumented function._


### `draw_rectangle_gradient_h`

> **draw_rectangle_gradient_h**(x: int, y: int, width: int, height: int, left: Color, right: Color) -> void

_Undocumented function._


### `draw_circle_lines`

> **draw_circle_lines**(center_x: int, center_y: int, radius: f32, color: Color) -> void

_Undocumented function._


### `draw_line_strip`

> **draw_line_strip**(points: slice of Vector2, color: Color) -> void

_Undocumented function._


### `draw_triangle_fan`

> **draw_triangle_fan**(points: slice of Vector2, color: Color) -> void

_Undocumented function._


### `draw_triangle_strip`

> **draw_triangle_strip**(points: slice of Vector2, color: Color) -> void

_Undocumented function._


### `draw_spline_linear`

> **draw_spline_linear**(points: slice of Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_basis`

> **draw_spline_basis**(points: slice of Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_catmull_rom`

> **draw_spline_catmull_rom**(points: slice of Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_bezier_quadratic`

> **draw_spline_bezier_quadratic**(points: slice of Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_bezier_cubic`

> **draw_spline_bezier_cubic**(points: slice of Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_segment_linear`

> **draw_spline_segment_linear**(p1: Vector2, p2: Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_segment_basis`

> **draw_spline_segment_basis**(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_segment_catmull_rom`

> **draw_spline_segment_catmull_rom**(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_segment_bezier_quadratic`

> **draw_spline_segment_bezier_quadratic**(p1: Vector2, c2: Vector2, p3: Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_spline_segment_bezier_cubic`

> **draw_spline_segment_bezier_cubic**(p1: Vector2, c2: Vector2, c3: Vector2, p4: Vector2, thick: f32, color: Color) -> void

_Undocumented function._


### `draw_rectangle_rounded_lines`

> **draw_rectangle_rounded_lines**(rec: Rectangle, roundness: f32, segments: int, color: Color) -> void

_Undocumented function._


### `spline_point_linear`

> **spline_point_linear**(start: Vector2, end: Vector2, t: f32) -> Vector2

_Undocumented function._


### `spline_point_basis`

> **spline_point_basis**(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2, t: f32) -> Vector2

_Undocumented function._


### `spline_point_catmull_rom`

> **spline_point_catmull_rom**(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2, t: f32) -> Vector2

_Undocumented function._


### `spline_point_bezier_cubic`

> **spline_point_bezier_cubic**(p1: Vector2, c2: Vector2, c3: Vector2, p4: Vector2, t: f32) -> Vector2

_Undocumented function._


### `set_shapes_texture`

> **set_shapes_texture**(texture: Texture, rec: Rectangle) -> void

_Undocumented function._


### `shapes_texture`

> **shapes_texture**() -> Texture

_Undocumented function._


### `shapes_texture_rectangle`

> **shapes_texture_rectangle**() -> Rectangle

_Undocumented function._


### `collision_recs`

> **collision_recs**(a: Rectangle, b: Rectangle) -> bool

_Undocumented function._


### `collision_rectangle`

> **collision_rectangle**(a: Rectangle, b: Rectangle) -> Rectangle

_Undocumented function._


### `collision_circles`

> **collision_circles**(c1: Vector2, r1: f32, c2: Vector2, r2: f32) -> bool

_Undocumented function._


### `collision_circle_rec`

> **collision_circle_rec**(center: Vector2, radius: f32, rec: Rectangle) -> bool

_Undocumented function._


### `collision_circle_line`

> **collision_circle_line**(center: Vector2, radius: f32, p1: Vector2, p2: Vector2) -> bool

_Undocumented function._


### `collision_point_circle`

> **collision_point_circle**(point: Vector2, center: Vector2, radius: f32) -> bool

_Undocumented function._


### `collision_point_triangle`

> **collision_point_triangle**(point: Vector2, p1: Vector2, p2: Vector2, p3: Vector2) -> bool

_Undocumented function._


### `collision_point_line`

> **collision_point_line**(point: Vector2, p1: Vector2, p2: Vector2, threshold: int) -> bool

_Undocumented function._


### `line_intersection`

> **line_intersection**(a1: Vector2, a2: Vector2, b1: Vector2, b2: Vector2) -> maybe Vector2

_Undocumented function._


### `collision_point_poly`

> **collision_point_poly**(point: Vector2, points: slice of Vector2) -> bool

_Undocumented function._


### `draw_api_probe`

> **draw_api_probe**() -> void

The window-bound drawing surface is not called in CI: every Draw* below needs an
active BeginDrawing/EndDrawing frame and a GPU. This probe exists so that every
public signature is type-checked by `pengu check`; the test that would run it is
deliberately absent.

