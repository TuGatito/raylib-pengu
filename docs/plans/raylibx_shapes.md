# Plan: shapes.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/shapes.pengu`
- Owner in the master plan: family `shapes` of `docs/plans/raylibx.md` (v0.1.2), third in its order of implementation
- Dependencies: `import raylib`, `import std.ffi` (the slice-shaped draws)
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified for this bucket: **case (a) complete against the header, with a version caveat (D14)**. The shapes section of `include/raylib.h` holds **75** functions: 58 `Draw*`, 5 `GetSplinePoint*`, 3 shapes-texture, 9 collision **and `GetSplinePoint*`**. Of those, **69 are wrapped** (27 methods on `Vector2`/`Rectangle` and 42 module-level functions) and **6 are skipped as unavailable in the installed library** (D14). | Enumerated from the header section itself, not from a name-pattern guess: an earlier draft of this plan said 61 because a hand-written regex missed `DrawLineDashed`, the `*LinesEx` variants and the five `GetSplinePoint*`. The corrected enumeration is at `include/raylib.h` between the "Basic Shapes Drawing Functions" and "Texture Loading and Drawing Functions" markers. |
| D2 | **The `<Shape>V` rule of the master plan (D9) is applied literally.** A `Draw*` becomes a method on `Vector2` when raylib's own name ends in `V`, because then the first argument *is* the shape's anchor. It stays a module function when the name has no `V`, even if the first argument is a `Vector2`. | Master plan D9, with the mechanical test the reviewer asked for. `DrawCircleV` → `center.draw_circle`; `DrawCircle` → module `draw_circle`; `DrawPoly` → module `draw_poly` (the vector is a centre, but the function name does not say so). |
| D3 | The six functions whose first argument is a `Rectangle` **by value and by name** become methods on `Rectangle`: `draw_rec`, `draw_pro`, `draw_gradient`, `draw_outline`, `draw_rounded`, `draw_rounded_outline`. | Master plan D9 and the registry row for `Rectangle`. `DrawRectangleRec(rec, color)` transforms `rec`, and reading `rec.draw()` needs no argument order to remember. The module-level forms keep the binding's descriptive names for the parameterless-by-name variants. |
| D4 | `Rectangle.draw_outline` is `DrawRectangleLinesEx` and `Rectangle.draw_rounded` is `DrawRectangleRounded`, **not** the shorter `DrawRectangleLines`/`DrawRectangleRoundedLines`. | The binding has five near-identical functions (`Lines`, `LinesEx`, `Rounded`, `RoundedLines`, `RoundedLinesEx`). Naming the methods after the *capability* rather than the C suffix keeps `rec.draw_outline` and `rec.draw_rounded_outline` unambiguous while the module-level functions keep the literal spelling. |
| D5 | `CheckCollisionPointRec` → `Rectangle.contains_point`; `CheckCollisionRecs`/`Circles`/`CircleRec`/`CircleLine`/`PointCircle`/`PointTriangle`/`PointLine`/`PointPoly` stay **module-level free functions**. | A free predicate is symmetric or has two equally good subjects, so there is no natural receiver. `Rectangle.contains_point` is the exception the master plan's registry already anticipates: a rectangle is the container, so it *is* the subject. |
| D6 | `CheckCollisionLines` → `maybe raylib.Vector2`, folding the `bool` and the out-parameter into one value. | Contract §3: the C function returns a success flag plus writes a point through `collisionPoint as ref to Vector2`. `some point` means "they cross here" and `maybe none` means "they do not", so the `bool` disappears into the `maybe` instead of being returned twice. Measured: on a miss raylib leaves the output untouched, so the wrapper must not read it. |
| D7 | `GetCollisionRec` returns a plain `Rectangle`, **not** `maybe Rectangle`, and the empty-overlap case is documented. | Measured: `GetCollisionRec(a, empty)` and `GetCollisionRec` on non-overlapping rectangles both return `(0, 0, 0, 0)`, and `CheckCollisionRecs` already reports the failure, so callers who care check that first. A `maybe` would duplicate the predicate. |
| D8 | The integer-coordinate variants (`DrawPixel`, `DrawLine`, `DrawCircle`, `DrawRectangle`, `DrawRectangleLines`, `DrawRectangleGradientV/H`, `DrawEllipse`, `DrawEllipseLines`) are wrapped as module-level functions with their binding names, **and** the `V`/`Rec` forms are the ones that become methods. | Master plan D9: the rule keys on the name, so the integer forms having a `Vector2` sibling does not make them methods. This also keeps the wrapper honest: `draw_pixel with 4, 5, color` is the binding's own signature. |
| D9 | `SetShapesTexture` is **not wrapped with a guard**, and both it and the two getters are exposed. | The pair is a global: `SetShapesTexture` replaces the 1×1 white texture raylib uses to draw every shape, and `GetShapesTexture`/`GetShapesTextureRectangle` read it back. Wrapping them keeps the round trip available; a guard would need to restore the previous texture and that is the caller's decision. Measured: the default rectangle is `(0, 0, 1, 1)`. | **Measured, and it is a cross-family interaction:** before any window exists `shapes_texture_rectangle` returns `(0, 0, 1, 1)`, and once `InitWindow` has run it returns `(41, 46, 2, 8)`, because loading the default font calls `SetShapesTexture`; the change survives `CloseWindow` because it is process-global state. The suite learned this by running through the `raylibx` facade, which runs all thirteen families in one process.
| D10 | The 12 slice-shaped draws (`DrawLineStrip`, `DrawTriangleFan`, `DrawTriangleStrip`, the five `DrawSpline*`, `CheckCollisionPointPoly`) take `slice of raylib.Vector2` with the empty-slice guard. | Contract §5. `DrawSplineSegment*` take individual `Vector2`s and are **not** slices, so they stay scalar functions. |
| D11 | No `maybe` on any draw function. | Drawing cannot fail: it has no return value, no failure channel and no resource to acquire. The only `maybe` in the family is `line_intersection` (D6). |
| D12 | Nothing is skipped. | Unlike `colors` and `files`, every symbol in this bucket is a legitimate wrapper: the draws remove the `(sigil of …)`-free but still order-sensitive argument lists, and the collision functions are pure and CI-testable. |

| D14 | **Six shapes functions are declared but not exported by the installed library**, so they are not wrapped: `DrawTriangleGradient`, `DrawTriangleLinesEx`, `DrawCircleLinesEx`, `DrawEllipseLinesEx`, `DrawRingLinesEx`, `DrawCircleSectorLinesEx` and `GetSplinePointBezierQuadratic`. | The repo header is raylib **6.1-dev** while `/usr/lib/libraylib.so` is **6.0.0**, and these seven are 6.1 additions. `pengu check` clean, `pengu build` clean, and the failure only appears at link time with `referencia a 'X' sin definir`. A cross-check of all 619 `declare`s against the library's dynamic symbols (`tools/check_binding_symbols.py`) found **22 such functions in `raylib.d.pengu`**; the other 16 belong to `files` (`IsFileHidden`, `IsPathDirectory`, `IsPathAbsolute`), `images` (`ImageDrawImage*`, `ImageDrawTextPro`, …) and `textures` (`LoadRenderTextureEx`). The wrapper cannot cover them until the library matches the header. |
| D13 | The slice-to-pointer conversion goes through **`void*`**, not through a typed `ref to frozen raylib.Vector2`: `let raw as ref to void is transmute (sigil of (points at 0)) to (ref to void)`. | A compiler defect found while implementing: writing the typed form makes `pengu 2.4.0` emit `const raylib.Vector2*` into the generated C, which is not valid C and fails to compile (`error: nombre de tipo 'raylib' desconocido`). `pengu check` does **not** catch it, because the C is only produced at build time. Routing through `void*` makes the emitted C a plain `void*` that converts implicitly to the `const Vector2 *` parameter, and that compiles. **Every future family that wraps a `(T*, int)` function hits this.** |

### ✨ Enchantings

No `@mutates`: no drawing function returns a value derived from its receiver, so the compiler generates no `get_*` form. All method names are collision-free against `raymathx` (which owns `Vector2` arithmetic) — the master plan's registry note for `Vector2` is respected: `raylibx` only adds draw-side names.

#### `enchanting raylib.Vector2` — 18 draw methods

| Method | Signature | C backing |
|---|---|---|
| `draw_pixel` | `with color as raylib.Color into void` | `DrawPixelV` |
| `draw_line_to` | `with end as raylib.Vector2, color as raylib.Color into void` | `DrawLineV` |
| `draw_line_ex` | `with end as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawLineEx` |
| `draw_line_bezier` | `with end as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawLineBezier` |
| `draw_circle` | `with radius as f32, color as raylib.Color into void` | `DrawCircleV` |
| `draw_circle_gradient` | `with radius as f32, inner as raylib.Color, outer as raylib.Color into void` | `DrawCircleGradient` |
| `draw_circle_sector` | `with radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawCircleSector` |
| `draw_circle_sector_lines` | `with radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawCircleSectorLines` |
| `draw_ellipse` | `with radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipseV` |
| `draw_ellipse_lines` | `with radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipseLinesV` |
| `draw_ring` | `with inner_radius as f32, outer_radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawRing` |
| `draw_ring_lines` | `with inner_radius as f32, outer_radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawRingLines` |
| `draw_poly` | `with sides as int, radius as f32, rotation as f32, color as raylib.Color into void` | `DrawPoly` |
| `draw_poly_lines` | `with sides as int, radius as f32, rotation as f32, color as raylib.Color into void` | `DrawPolyLines` |
| `draw_poly_lines_ex` | `with sides as int, radius as f32, rotation as f32, thick as f32, color as raylib.Color into void` | `DrawPolyLinesEx` |
| `draw_rectangle` | `with size as raylib.Vector2, color as raylib.Color into void` | `DrawRectangleV` |
| `draw_triangle` | `with v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `DrawTriangle` |
| `draw_triangle_lines` | `with v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `DrawTriangleLines` |
| `draw_line_dashed` | `with end as raylib.Vector2, dash_size as int, space_size as int, color as raylib.Color into void` | `DrawLineDashed` |
| `draw_circle_lines` | `with radius as f32, color as raylib.Color into void` | `DrawCircleLinesV` |
| `draw_triangle_gradient` | — | **omitido**: solo 6.1 (D14) |
| `draw_triangle_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_circle_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_ellipse_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_ring_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_circle_sector_lines_ex` | — | **omitido**: solo 6.1 (D14) |

> The `Rectangle.draw_*` family and the `Vector2` methods share no name with `raymathx`, which owns `add`, `scale`, `length`, `lerp_to`, `dot`, `cross`, `distance_to`, `negate`, `normalize` and the rest of the arithmetic. No collision.

#### `enchanting raylib.Rectangle` — 6 methods

| Method | Signature | C backing |
|---|---|---|
| `draw` | `with color as raylib.Color into void` | `DrawRectangleRec` |
| `draw_pro` | `with origin as raylib.Vector2, rotation as f32, color as raylib.Color into void` | `DrawRectanglePro` |
| `draw_gradient` | `with c1 as raylib.Color, c2 as raylib.Color, c3 as raylib.Color, c4 as raylib.Color into void` | `DrawRectangleGradientEx` |
| `draw_outline` | `with thick as f32, color as raylib.Color into void` | `DrawRectangleLinesEx` |
| `draw_rounded` | `with roundness as f32, segments as int, color as raylib.Color into void` | `DrawRectangleRounded` |
| `draw_rounded_outline` | `with roundness as f32, segments as int, thick as f32, color as raylib.Color into void` | `DrawRectangleRoundedLinesEx` |
| `contains_point` | `with point as raylib.Vector2 into bool` | `CheckCollisionPointRec` |

### 🔧 Module-level functions

#### Draws with integer coordinates

| Function | Signature | C backing |
|---|---|---|
| `draw_pixel` | `with x as int, y as int, color as raylib.Color into void` | `DrawPixel` |
| `draw_line` | `with x1 as int, y1 as int, x2 as int, y2 as int, color as raylib.Color into void` | `DrawLine` |
| `draw_circle` | `with center_x as int, center_y as int, radius as f32, color as raylib.Color into void` | `DrawCircle` |
| `draw_ellipse` | `with center_x as int, center_y as int, radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipse` |
| `draw_ellipse_lines` | `with center_x as int, center_y as int, radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipseLines` |
| `draw_rectangle` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `DrawRectangle` |
| `draw_rectangle_lines` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `DrawRectangleLines` |
| `draw_rectangle_gradient_v` | `with x as int, y as int, width as int, height as int, top as raylib.Color, bottom as raylib.Color into void` | `DrawRectangleGradientV` |
| `draw_rectangle_gradient_h` | `with x as int, y as int, width as int, height as int, left as raylib.Color, right as raylib.Color into void` | `DrawRectangleGradientH` |
| `draw_circle_lines` | `with center_x as int, center_y as int, radius as f32, color as raylib.Color into void` | `DrawCircleLines` |
| `draw_rectangle_rounded_lines` | `with rec as raylib.Rectangle, roundness as f32, segments as int, color as raylib.Color into void` | `DrawRectangleRoundedLines` |

> `draw_pixel`, `draw_circle`, `draw_ellipse`, `draw_rectangle` and `draw_rectangle_lines` share their names with the `Vector2`/`Rectangle` methods. That is intentional and legal: module-level functions and methods live in different namespaces (`raylibx_shapes_draw_circle` versus `Vector2_draw_circle`), which the master plan's D4 verified.

#### Slice-shaped draws

| Function | Signature | C backing |
|---|---|---|
| `draw_line_strip` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `DrawLineStrip` |
| `draw_triangle_fan` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `DrawTriangleFan` |
| `draw_triangle_strip` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `DrawTriangleStrip` |
| `draw_spline_linear` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineLinear` |
| `draw_spline_basis` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineBasis` |
| `draw_spline_catmull_rom` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineCatmullRom` |
| `draw_spline_bezier_quadratic` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineBezierQuadratic` |
| `draw_spline_bezier_cubic` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineBezierCubic` |
| `collision_point_poly` | `with point as raylib.Vector2, points as slice of raylib.Vector2 into bool` | `CheckCollisionPointPoly` |

Every one guards `points.length == 0` before taking `sigil of (points at 0)`, and a draw with no points is a no-op rather than an error.

#### Spline segments (scalar points)

| Function | Signature | C backing |
|---|---|---|
| `draw_spline_segment_linear` | `with p1 as raylib.Vector2, p2 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentLinear` |
| `draw_spline_segment_basis` | `with p1 as raylib.Vector2, p2 as raylib.Vector2, p3 as raylib.Vector2, p4 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentBasis` |
| `draw_spline_segment_catmull_rom` | same as `basis` | `DrawSplineSegmentCatmullRom` |
| `draw_spline_segment_bezier_quadratic` | `with p1 as raylib.Vector2, c2 as raylib.Vector2, p3 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentBezierQuadratic` |
| `draw_spline_segment_bezier_cubic` | `with p1 as raylib.Vector2, c2 as raylib.Vector2, c3 as raylib.Vector2, p4 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentBezierCubic` |

#### Spline point evaluation (pure; no window needed)

| Function | Signature | C backing |
|---|---|---|
| `spline_point_linear` | `with start as raylib.Vector2, end as raylib.Vector2, t as f32 into raylib.Vector2` | `GetSplinePointLinear` |
| `spline_point_basis` | `with p1 as raylib.Vector2, p2 as raylib.Vector2, p3 as raylib.Vector2, p4 as raylib.Vector2, t as f32 into raylib.Vector2` | `GetSplinePointBasis` |
| `spline_point_catmull_rom` | same as `basis` | `GetSplinePointCatmullRom` |
| `spline_point_bezier_cubic` | `with p1 as raylib.Vector2, c2 as raylib.Vector2, c3 as raylib.Vector2, p4 as raylib.Vector2, t as f32 into raylib.Vector2` | `GetSplinePointBezierCubic` |
| `spline_point_bezier_quadratic` | — | **skipped**: 6.1 only (D14) |

These five are pure arithmetic and need no window, so unlike the `Draw*` half they **are** asserted directly in CI.

#### Shapes texture (global)

| Function | Signature | C backing |
|---|---|---|
| `set_shapes_texture` | `with texture as raylib.Texture2D, rec as raylib.Rectangle into void` | `SetShapesTexture` |
| `shapes_texture` | `into raylib.Texture2D` | `GetShapesTexture` |
| `shapes_texture_rectangle` | `into raylib.Rectangle` | `GetShapesTextureRectangle` |

#### Collision predicates

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `collision_recs` | `with a as raylib.Rectangle, b as raylib.Rectangle into bool` | `CheckCollisionRecs` | `false` when either rectangle is empty |
| `collision_circles` | `with c1 as raylib.Vector2, r1 as f32, c2 as raylib.Vector2, r2 as f32 into bool` | `CheckCollisionCircles` | |
| `collision_circle_rec` | `with center as raylib.Vector2, radius as f32, rec as raylib.Rectangle into bool` | `CheckCollisionCircleRec` | |
| `collision_circle_line` | `with center as raylib.Vector2, radius as f32, p1 as raylib.Vector2, p2 as raylib.Vector2 into bool` | `CheckCollisionCircleLine` | |
| `collision_point_circle` | `with point as raylib.Vector2, center as raylib.Vector2, radius as f32 into bool` | `CheckCollisionPointCircle` | |
| `collision_point_triangle` | `with point as raylib.Vector2, p1 as raylib.Vector2, p2 as raylib.Vector2, p3 as raylib.Vector2 into bool` | `CheckCollisionPointTriangle` | |
| `collision_point_line` | `with point as raylib.Vector2, p1 as raylib.Vector2, p2 as raylib.Vector2, threshold as int into bool` | `CheckCollisionPointLine` | `threshold` is in pixels |
| `line_intersection` | `with a1 as raylib.Vector2, a2 as raylib.Vector2, b1 as raylib.Vector2, b2 as raylib.Vector2 into maybe raylib.Vector2` | `CheckCollisionLines` | D6 |
| `collision_rectangle` | `with a as raylib.Rectangle, b as raylib.Rectangle into raylib.Rectangle` | `GetCollisionRec` | zero rect when there is no overlap (D7) |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `line_intersection` | `maybe raylib.Vector2` | `CheckCollisionLines` returns `false` and leaves the out-parameter untouched, so the wrapper must not read it (D6) |

**Nine draws are `maybe none`-free by construction** and the rest of the family has no failure channel (D11).

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `draw_line_strip`, `draw_triangle_fan`, `draw_triangle_strip` | `points as slice of raylib.Vector2` |
| `draw_spline_linear`, `draw_spline_basis`, `draw_spline_catmull_rom`, `draw_spline_bezier_quadratic`, `draw_spline_bezier_cubic` | `points as slice of raylib.Vector2` |
| `collision_point_poly` | `points as slice of raylib.Vector2` |

Nine functions, one guard shape: an empty slice is a no-op for the drawers and `false` for the predicate.

### 📦 Multiple returns `(T, U)`

**None apply.** The one function that returns two things (`CheckCollisionLines`, a flag plus a point) folds into `maybe` (D6). `GetCollisionRec` returns a single `Rectangle`.

### 🌉 `std.ffi` usage

Only `slice of Vector2` → `ref to frozen Vector2` through `transmute (sigil of (points at 0))`, in the nine slice-shaped functions, plus `import std.ffi` for nothing else. There is no string in this family: no path is drawn, only colours and coordinates.

### 💡 Compilable examples

```pengu
# Example 1 — the method shapes and the module-level ones side by side
import raylib
import raylibx.shapes as shapes

weave main into int:
    var center as raylib.Vector2 is with x is 100.0, y is 100.0
    var rec as raylib.Rectangle is with x is 10.0, y is 10.0, width is 40.0, height is 20.0
    calling center.draw_circle with 20.0, raylib.RED
    calling center.draw_line_to with (with x is 200.0, y is 100.0), raylib.BLUE
    calling rec.draw with raylib.GREEN
    calling rec.draw_rounded with 0.4, 8, raylib.WHITE
    calling shapes.draw_circle with 300, 300, 25.0, raylib.YELLOW
    calling shapes.draw_rectangle with 0, 0, 50, 50, raylib.PURPLE
    return 0
```

```pengu
# Example 2 — slices and a splash of collision
import raylib
import raylibx.shapes as shapes

weave main into int:
    var points as list of raylib.Vector2 is list of raylib.Vector2
    defer banish points
    calling points.push with (with x is 0.0, y is 0.0)
    calling points.push with (with x is 50.0, y is 50.0)
    calling points.push with (with x is 100.0, y is 0.0)
    var strip as slice of raylib.Vector2 is points at 0 to 3
    calling shapes.draw_line_strip with strip, raylib.RED
    calling shapes.draw_spline_catmull_rom with strip, 2.0, raylib.WHITE
    var inside as bool is calling shapes.collision_point_poly with (with x is 50.0, y is 20.0), strip
    return 0
```

```pengu
# Example 3 — collision queries that need no window
import raylib
import raylibx.shapes as shapes

weave main into int:
    var a as raylib.Rectangle is with x is 0.0, y is 0.0, width is 10.0, height is 10.0
    var b as raylib.Rectangle is with x is 5.0, y is 5.0, width is 10.0, height is 10.0
    var hit as bool is calling shapes.collision_recs with a, b
    var overlap as raylib.Rectangle is calling shapes.collision_rectangle with a, b
    var point as raylib.Vector2 is with x is 3.0, y is 3.0
    var inside as bool is calling a.contains_point with point
    var cross as maybe raylib.Vector2 is calling shapes.line_intersection with (with x is 0.0, y is 0.0), (with x is 10.0, y is 0.0), (with x is 5.0, y is -5.0), (with x is 5.0, y is 5.0)
    return 0
```

### 🧪 Test plan

The split in this family is sharp and worth stating plainly.

**CI-testable (no window):** the nine collision functions, `Rectangle.contains_point`, the three shapes-texture getters, and the *guard paths* of the nine slice-shaped draws.

**Not CI-testable (needs a window and a GPU):** the 49 `Draw*` calls themselves. raylib's drawing commands outside a `BeginDrawing`/`EndDrawing` pair are undefined; calling them headless would either abort or silently rely on uninitialised GL state. Those functions are therefore covered by a **compiled-but-not-called** test: a function that references each one so that the signature is type-checked at `pengu check` time, with a comment saying the call is not executed in CI. That is the honest degradation the family plan records, and it is the same one `rcamerax` used for its window-bound paths.

- **`collision_recs`**: two overlapping rectangles are `true`; disjoint rectangles are `false`; an empty rectangle (zero width) collides with nothing, including itself (measured).
- **`collision_rectangle`**: the overlap of `(0,0,10,10)` and `(5,5,10,10)` is `(5,5,5,5)`; a disjoint pair gives `(0,0,0,0)`; the result never exceeds either input.
- **`collision_circles`**: identical circles collide; circles exactly `r1 + r2` apart are `false` (the C uses a strict compare); far-apart circles are `false`.
- **`collision_circle_rec`**: a circle centred inside the rectangle is `true`; one centred outside and further than the radius is `false`.
- **`collision_circle_line`**: a circle centred on the segment is `true`; one far from it is `false`.
- **`collision_point_circle`**: the centre is inside; a point at exactly `radius` is the boundary case the test pins; a point outside is `false`.
- **`collision_point_triangle`**: a point inside a triangle is `true`; a point outside is `false`.
- **`collision_point_line`**: measured — a point on the segment with `threshold = 1` is `true`, and a point 9 pixels off is `false`.
- **`collision_point_poly`**: a point inside a triangle is `true`; a point outside is `false`; an empty slice gives `false` without touching element zero.
- **`line_intersection`**: measured — the crossing pair `(0,0)-(10,0)` and `(5,-5)-(5,5)` gives `some (5, 0)`; the parallel pair gives `maybe none`; the returned point is on both segments.
- **`Rectangle.contains_point`**: a point inside is `true`; a point outside is `false`; the corner is the boundary case pinned by measurement.
- **`shapes_texture_rectangle`**: measured default `(0, 0, 1, 1)`; `shapes_texture` returns a texture whose `width`/`height` are the same 1×1 placeholder before any `SetShapesTexture`.
- **`set_shapes_texture`**: not called in CI (it mutates global GL state); the round trip `set` → `shapes_texture` is documented instead.
- **The nine slice-shaped draws**: each is called with an **empty** slice and must be a no-op that does not read element zero. That is the one assertion that is both meaningful and CI-safe, and it is exactly the guard the wrapper adds.
- **The 49 window-bound draws**: not called. The test file contains a `weave draw_api_probe` that takes the values each one needs and calls them, so the whole public surface is type-checked at compile time; the test itself records that it is not invoked in CI.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `DrawTextureNPatch` and the other `DrawTexture*` | **not this family**: they are `textures` (master plan D6), and the registry already assigns them there |
| `ImageDraw*` (`ImageDrawLine`, `ImageDrawCircle`, …) | **not this family**: they are `Image` methods and belong to `raylibx_images` |
| `DrawRectangleGradientEx`'s 4-colour `DrawRectangleGradientV/H` siblings | **wrapped**, as module-level functions with their integer signatures (D8) |

Coverage audit: of the 75 shapes-section functions, **69 are wrapped** — 20 `Vector2` methods, 7 `Rectangle` methods (6 draws plus `contains_point`) and 36 module-level functions, one of which (`line_intersection`) is the family's only `maybe`. Nothing is skipped. The method registry gains these entries for `raylib.Vector2` and `raylib.Rectangle`; **no other family may add a method to either type**.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/shapes.pengu`
- Dueña en el plan maestro: familia `shapes` de `docs/plans/raylibx.md` (v0.1.2), tercera en su orden de implementación
- Dependencias: `import raylib`, `import std.ffi` (los dibujos con slice)
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada para este grupo: **caso (a) completo**. 61 `declare`: 49 `Draw*`, 3 de textura de formas, 9 de colisión. De ellos, **69 se envuelven**: 25 como métodos (20 en `Vector2`, 7 en `Rectangle`) y 36 como funciones de módulo. | Enumerado contra `pengu/raylib.d.pengu`. No falta ninguno ni hay nada que omitir. |
| D2 | **La regla `<Shape>V` del plan maestro (D9) se aplica al pie de la letra.** Un `Draw*` pasa a método de `Vector2` cuando el nombre que le da raylib termina en `V`, porque entonces el primer argumento *es* el ancla de la figura. Se queda como función de módulo cuando el nombre no tiene `V`, aunque el primer argumento sea un `Vector2`. | Plan maestro D9, con la prueba mecánica que pidió la revisión. `DrawCircleV` → `center.draw_circle`; `DrawCircle` → módulo `draw_circle`; `DrawPoly` → módulo `draw_poly` (el vector es un centro, pero el nombre de la función no lo dice). |
| D3 | Las seis funciones cuyo primer argumento es un `Rectangle` **por valor y por nombre** pasan a métodos de `Rectangle`: `draw_rec`, `draw_pro`, `draw_gradient`, `draw_outline`, `draw_rounded`, `draw_rounded_outline`. | Plan maestro D9 y la fila del registro para `Rectangle`. `DrawRectangleRec(rec, color)` transforma `rec`, y leer `rec.draw()` no obliga a recordar ningún orden de argumentos. Las formas de módulo conservan los nombres descriptivos del binding para las variantes sin `Rec`. |
| D4 | `Rectangle.draw_outline` es `DrawRectangleLinesEx` y `Rectangle.draw_rounded` es `DrawRectangleRounded`, **no** las más cortas `DrawRectangleLines`/`DrawRectangleRoundedLines`. | El binding tiene cinco funciones casi idénticas (`Lines`, `LinesEx`, `Rounded`, `RoundedLines`, `RoundedLinesEx`). Nombrar los métodos por la *capacidad* y no por el sufijo C mantiene `rec.draw_outline` y `rec.draw_rounded_outline` sin ambigüedad, mientras las funciones de módulo conservan la grafía literal. |
| D5 | `CheckCollisionPointRec` → `Rectangle.contains_point`; `CheckCollisionRecs`/`Circles`/`CircleRec`/`CircleLine`/`PointCircle`/`PointTriangle`/`PointLine`/`PointPoly` se quedan como **funciones libres de módulo**. | Un predicado libre es simétrico o tiene dos sujetos igual de buenos, así que no hay receptor natural. `Rectangle.contains_point` es la excepción que el registro del plan maestro ya anticipa: el rectángulo es el contenedor, así que *sí* es el sujeto. |
| D6 | `CheckCollisionLines` → `maybe raylib.Vector2`, plegando el `bool` y el out-param en un solo valor. | Contrato §3: la función C devuelve un indicador de éxito y además escribe un punto por `collisionPoint as ref to Vector2`. `some point` significa "se cruzan aquí" y `maybe none` significa "no se cruzan", así que el `bool` desaparece dentro del `maybe` en vez de devolverse dos veces. Medido: en un fallo raylib deja la salida intacta, así que el wrapper no debe leerla. |
| D7 | `GetCollisionRec` devuelve un `Rectangle` simple, **no** `maybe Rectangle`, y el caso de solapamiento vacío queda documentado. | Medido: `GetCollisionRec(a, empty)` y `GetCollisionRec` sobre rectángulos que no se solapan devuelven ambos `(0, 0, 0, 0)`, y `CheckCollisionRecs` ya informa del fallo, así que quien se preocupe por ello lo consulta antes. Un `maybe` duplicaría el predicado. |
| D8 | Las variantes de coordenadas enteras (`DrawPixel`, `DrawLine`, `DrawCircle`, `DrawRectangle`, `DrawRectangleLines`, `DrawRectangleGradientV/H`, `DrawEllipse`, `DrawEllipseLines`) se envuelven como funciones de módulo con sus nombres del binding, **y** las formas `V`/`Rec` son las que pasan a métodos. | Plan maestro D9: la regla depende del nombre, así que que las formas enteras tengan un hermano con `Vector2` no las convierte en métodos. Esto además mantiene honesto el wrapper: `draw_pixel with 4, 5, color` es la firma del propio binding. |
| D9 | `SetShapesTexture` **no se envuelve con guarda**, y tanto ella como los dos getters quedan expuestas. | El trío es global: `SetShapesTexture` reemplaza la textura blanca de 1×1 que raylib usa para dibujar toda figura, y `GetShapesTexture`/`GetShapesTextureRectangle` la leen. Envolverlas mantiene disponible la ida y vuelta; una guarda tendría que restaurar la textura anterior y eso es decisión del llamador. Medido: el rectángulo por defecto es `(0, 0, 1, 1)`. | **Medido, y es una interacción entre familias:** antes de que exista ninguna ventana `shapes_texture_rectangle` devuelve `(0, 0, 1, 1)`, y una vez que `InitWindow` ha corrido devuelve `(41, 46, 2, 8)`, porque cargar la fuente por defecto llama a `SetShapesTexture`; el cambio sobrevive a `CloseWindow` porque es estado global del proceso. La suite lo aprendió al ejecutarse a través de la fachada `raylibx`, que corre las trece familias en un proceso.
| D10 | Los 12 dibujos con slice (`DrawLineStrip`, `DrawTriangleFan`, `DrawTriangleStrip`, los cinco `DrawSpline*`, `CheckCollisionPointPoly`) reciben `slice of raylib.Vector2` con la guarda de slice vacío. | Contrato §5. Los `DrawSplineSegment*` reciben `Vector2` sueltos y **no** son slices, así que se quedan como funciones escalares. |
| D11 | Ningún `maybe` en las funciones de dibujo. | Dibujar no puede fallar: no devuelve valor, no tiene canal de fallo ni recurso que adquirir. El único `maybe` de la familia es `line_intersection` (D6). |
| D12 | No se omite nada. | A diferencia de `colors` y `files`, cada símbolo de este grupo es un wrapper legítimo: los dibujos quitan listas de argumentos sensibles al orden, y las funciones de colisión son puras y testeables en CI. |

| D14 | **Seis funciones de shapes están declaradas pero la biblioteca instalada no las exporta**, así que no se envuelven: `DrawTriangleGradient`, `DrawTriangleLinesEx`, `DrawCircleLinesEx`, `DrawEllipseLinesEx`, `DrawRingLinesEx`, `DrawCircleSectorLinesEx` y `GetSplinePointBezierQuadratic`. | El header del repo es raylib **6.1-dev** y `/usr/lib/libraylib.so` es **6.0.0**; estas siete son añadidos de 6.1. `pengu check` sale limpio, `pengu build` sale limpio, y el fallo solo aparece al enlazar con `referencia a 'X' sin definir`. Una comprobación de los 619 `declare` contra los símbolos dinámicos de la biblioteca (`tools/check_binding_symbols.py`) encontró **22 funciones así en `raylib.d.pengu`**; las otras 16 son de `files` (`IsFileHidden`, `IsPathDirectory`, `IsPathAbsolute`), `images` (`ImageDrawImage*`, `ImageDrawTextPro`, …) y `textures` (`LoadRenderTextureEx`). El wrapper no puede cubrirlas hasta que la biblioteca coincida con el header. |
| D13 | La conversión de slice a puntero pasa por **`void*`**, no por un `ref to frozen raylib.Vector2` tipado: `let raw as ref to void is transmute (sigil of (points at 0)) to (ref to void)`. | Defecto del compilador encontrado al implementar: escribir la forma tipada hace que `pengu 2.4.0` emita `const raylib.Vector2*` en el C generado, que no es C válido y no compila (`error: nombre de tipo 'raylib' desconocido`). `pengu check` **no** lo detecta, porque el C solo se produce al construir. Pasar por `void*` hace que el C emitido sea un `void*` que convierte implícitamente al parámetro `const Vector2 *`, y eso sí compila. **Toda familia futura que envuelva una función `(T*, int)` se topa con esto.** |

### ✨ Enchantings

Sin `@mutates`: ninguna función de dibujo devuelve un valor derivado de su receptor, así que el compilador no genera ninguna forma `get_*`. Todos los nombres de método están libres de colisión con `raymathx` (que posee la aritmética de `Vector2`) — se respeta la nota del registro del plan maestro para `Vector2`: `raylibx` solo añade nombres del lado del dibujo.

#### `enchanting raylib.Vector2` — 18 métodos de dibujo

| Método | Firma | C backing |
|---|---|---|
| `draw_pixel` | `with color as raylib.Color into void` | `DrawPixelV` |
| `draw_line_to` | `with end as raylib.Vector2, color as raylib.Color into void` | `DrawLineV` |
| `draw_line_ex` | `with end as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawLineEx` |
| `draw_line_bezier` | `with end as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawLineBezier` |
| `draw_circle` | `with radius as f32, color as raylib.Color into void` | `DrawCircleV` |
| `draw_circle_gradient` | `with radius as f32, inner as raylib.Color, outer as raylib.Color into void` | `DrawCircleGradient` |
| `draw_circle_sector` | `with radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawCircleSector` |
| `draw_circle_sector_lines` | `with radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawCircleSectorLines` |
| `draw_ellipse` | `with radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipseV` |
| `draw_ellipse_lines` | `with radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipseLinesV` |
| `draw_ring` | `with inner_radius as f32, outer_radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawRing` |
| `draw_ring_lines` | `with inner_radius as f32, outer_radius as f32, start_angle as f32, end_angle as f32, segments as int, color as raylib.Color into void` | `DrawRingLines` |
| `draw_poly` | `with sides as int, radius as f32, rotation as f32, color as raylib.Color into void` | `DrawPoly` |
| `draw_poly_lines` | `with sides as int, radius as f32, rotation as f32, color as raylib.Color into void` | `DrawPolyLines` |
| `draw_poly_lines_ex` | `with sides as int, radius as f32, rotation as f32, thick as f32, color as raylib.Color into void` | `DrawPolyLinesEx` |
| `draw_rectangle` | `with size as raylib.Vector2, color as raylib.Color into void` | `DrawRectangleV` |
| `draw_triangle` | `with v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `DrawTriangle` |
| `draw_triangle_lines` | `with v2 as raylib.Vector2, v3 as raylib.Vector2, color as raylib.Color into void` | `DrawTriangleLines` |
| `draw_line_dashed` | `with end as raylib.Vector2, dash_size as int, space_size as int, color as raylib.Color into void` | `DrawLineDashed` |
| `draw_circle_lines` | `with radius as f32, color as raylib.Color into void` | `DrawCircleLinesV` |
| `draw_triangle_gradient` | — | **omitido**: solo 6.1 (D14) |
| `draw_triangle_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_circle_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_ellipse_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_ring_lines_ex` | — | **omitido**: solo 6.1 (D14) |
| `draw_circle_sector_lines_ex` | — | **omitido**: solo 6.1 (D14)

> La familia `Rectangle.draw_*` y los métodos de `Vector2` no comparten ningún nombre con `raymathx`, que posee `add`, `scale`, `length`, `lerp_to`, `dot`, `cross`, `distance_to`, `negate`, `normalize` y el resto de la aritmética. Sin colisión.

#### `enchanting raylib.Rectangle` — 6 métodos

| Método | Firma | C backing |
|---|---|---|
| `draw` | `with color as raylib.Color into void` | `DrawRectangleRec` |
| `draw_pro` | `with origin as raylib.Vector2, rotation as f32, color as raylib.Color into void` | `DrawRectanglePro` |
| `draw_gradient` | `with c1 as raylib.Color, c2 as raylib.Color, c3 as raylib.Color, c4 as raylib.Color into void` | `DrawRectangleGradientEx` |
| `draw_outline` | `with thick as f32, color as raylib.Color into void` | `DrawRectangleLinesEx` |
| `draw_rounded` | `with roundness as f32, segments as int, color as raylib.Color into void` | `DrawRectangleRounded` |
| `draw_rounded_outline` | `with roundness as f32, segments as int, thick as f32, color as raylib.Color into void` | `DrawRectangleRoundedLinesEx` |
| `contains_point` | `with point as raylib.Vector2 into bool` | `CheckCollisionPointRec` |

### 🔧 Funciones a nivel de módulo

#### Dibujos con coordenadas enteras

| Función | Firma | C backing |
|---|---|---|
| `draw_pixel` | `with x as int, y as int, color as raylib.Color into void` | `DrawPixel` |
| `draw_line` | `with x1 as int, y1 as int, x2 as int, y2 as int, color as raylib.Color into void` | `DrawLine` |
| `draw_circle` | `with center_x as int, center_y as int, radius as f32, color as raylib.Color into void` | `DrawCircle` |
| `draw_ellipse` | `with center_x as int, center_y as int, radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipse` |
| `draw_ellipse_lines` | `with center_x as int, center_y as int, radius_h as f32, radius_v as f32, color as raylib.Color into void` | `DrawEllipseLines` |
| `draw_rectangle` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `DrawRectangle` |
| `draw_rectangle_lines` | `with x as int, y as int, width as int, height as int, color as raylib.Color into void` | `DrawRectangleLines` |
| `draw_rectangle_gradient_v` | `with x as int, y as int, width as int, height as int, top as raylib.Color, bottom as raylib.Color into void` | `DrawRectangleGradientV` |
| `draw_rectangle_gradient_h` | `with x as int, y as int, width as int, height as int, left as raylib.Color, right as raylib.Color into void` | `DrawRectangleGradientH` |
| `draw_circle_lines` | `with center_x as int, center_y as int, radius as f32, color as raylib.Color into void` | `DrawCircleLines` |
| `draw_rectangle_rounded_lines` | `with rec as raylib.Rectangle, roundness as f32, segments as int, color as raylib.Color into void` | `DrawRectangleRoundedLines` |

> `draw_pixel`, `draw_circle`, `draw_ellipse`, `draw_rectangle` y `draw_rectangle_lines` comparten nombre con los métodos de `Vector2`/`Rectangle`. Es intencional y legal: las funciones de módulo y los métodos viven en espacios de nombres distintos (`raylibx_shapes_draw_circle` frente a `Vector2_draw_circle`), lo que el D4 del plan maestro verificó.

#### Dibujos con slice

| Función | Firma | C backing |
|---|---|---|
| `draw_line_strip` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `DrawLineStrip` |
| `draw_triangle_fan` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `DrawTriangleFan` |
| `draw_triangle_strip` | `with points as slice of raylib.Vector2, color as raylib.Color into void` | `DrawTriangleStrip` |
| `draw_spline_linear` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineLinear` |
| `draw_spline_basis` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineBasis` |
| `draw_spline_catmull_rom` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineCatmullRom` |
| `draw_spline_bezier_quadratic` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineBezierQuadratic` |
| `draw_spline_bezier_cubic` | `with points as slice of raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineBezierCubic` |
| `collision_point_poly` | `with point as raylib.Vector2, points as slice of raylib.Vector2 into bool` | `CheckCollisionPointPoly` |

Todas guardan `points.length == 0` antes de tomar `sigil of (points at 0)`, y un dibujo sin puntos es un no-op en vez de un error.

#### Segmentos de spline (puntos escalares)

| Función | Firma | C backing |
|---|---|---|
| `draw_spline_segment_linear` | `with p1 as raylib.Vector2, p2 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentLinear` |
| `draw_spline_segment_basis` | `with p1 as raylib.Vector2, p2 as raylib.Vector2, p3 as raylib.Vector2, p4 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentBasis` |
| `draw_spline_segment_catmull_rom` | igual que `basis` | `DrawSplineSegmentCatmullRom` |
| `draw_spline_segment_bezier_quadratic` | `with p1 as raylib.Vector2, c2 as raylib.Vector2, p3 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentBezierQuadratic` |
| `draw_spline_segment_bezier_cubic` | `with p1 as raylib.Vector2, c2 as raylib.Vector2, c3 as raylib.Vector2, p4 as raylib.Vector2, thick as f32, color as raylib.Color into void` | `DrawSplineSegmentBezierCubic` |

#### Evaluación de puntos de spline (pura; no necesita ventana)

| Función | Firma | C backing |
|---|---|---|
| `spline_point_linear` | `with start as raylib.Vector2, end as raylib.Vector2, t as f32 into raylib.Vector2` | `GetSplinePointLinear` |
| `spline_point_basis` | `with p1 as raylib.Vector2, p2 as raylib.Vector2, p3 as raylib.Vector2, p4 as raylib.Vector2, t as f32 into raylib.Vector2` | `GetSplinePointBasis` |
| `spline_point_catmull_rom` | igual que `basis` | `GetSplinePointCatmullRom` |
| `spline_point_bezier_cubic` | `with p1 as raylib.Vector2, c2 as raylib.Vector2, c3 as raylib.Vector2, p4 as raylib.Vector2, t as f32 into raylib.Vector2` | `GetSplinePointBezierCubic` |
| `spline_point_bezier_quadratic` | — | **omitido**: solo 6.1 (D14) |

Estas cinco son aritmética pura y no necesitan ventana, así que a diferencia de la mitad `Draw*` **sí** se aseguran directamente en CI.

#### Textura de formas (global)

| Función | Firma | C backing |
|---|---|---|
| `set_shapes_texture` | `with texture as raylib.Texture2D, rec as raylib.Rectangle into void` | `SetShapesTexture` |
| `shapes_texture` | `into raylib.Texture2D` | `GetShapesTexture` |
| `shapes_texture_rectangle` | `into raylib.Rectangle` | `GetShapesTextureRectangle` |

#### Predicados de colisión

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `collision_recs` | `with a as raylib.Rectangle, b as raylib.Rectangle into bool` | `CheckCollisionRecs` | `false` si algún rectángulo está vacío |
| `collision_circles` | `with c1 as raylib.Vector2, r1 as f32, c2 as raylib.Vector2, r2 as f32 into bool` | `CheckCollisionCircles` | |
| `collision_circle_rec` | `with center as raylib.Vector2, radius as f32, rec as raylib.Rectangle into bool` | `CheckCollisionCircleRec` | |
| `collision_circle_line` | `with center as raylib.Vector2, radius as f32, p1 as raylib.Vector2, p2 as raylib.Vector2 into bool` | `CheckCollisionCircleLine` | |
| `collision_point_circle` | `with point as raylib.Vector2, center as raylib.Vector2, radius as f32 into bool` | `CheckCollisionPointCircle` | |
| `collision_point_triangle` | `with point as raylib.Vector2, p1 as raylib.Vector2, p2 as raylib.Vector2, p3 as raylib.Vector2 into bool` | `CheckCollisionPointTriangle` | |
| `collision_point_line` | `with point as raylib.Vector2, p1 as raylib.Vector2, p2 as raylib.Vector2, threshold as int into bool` | `CheckCollisionPointLine` | `threshold` en píxeles |
| `line_intersection` | `with a1 as raylib.Vector2, a2 as raylib.Vector2, b1 as raylib.Vector2, b2 as raylib.Vector2 into maybe raylib.Vector2` | `CheckCollisionLines` | D6 |
| `collision_rectangle` | `with a as raylib.Rectangle, b as raylib.Rectangle into raylib.Rectangle` | `GetCollisionRec` | rectángulo cero si no hay solapamiento (D7) |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `line_intersection` | `maybe raylib.Vector2` | `CheckCollisionLines` devuelve `false` y deja el out-param intacto, así que el wrapper no debe leerlo (D6) |

**Ninguna función de dibujo devuelve `maybe none`** y el resto de la familia no tiene canal de fallo (D11).

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `draw_line_strip`, `draw_triangle_fan`, `draw_triangle_strip` | `points as slice of raylib.Vector2` |
| `draw_spline_linear`, `draw_spline_basis`, `draw_spline_catmull_rom`, `draw_spline_bezier_quadratic`, `draw_spline_bezier_cubic` | `points as slice of raylib.Vector2` |
| `collision_point_poly` | `points as slice of raylib.Vector2` |

Nueve funciones, una sola forma de guarda: un slice vacío es un no-op para los dibujos y `false` para el predicado.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** La única función que devuelve dos cosas (`CheckCollisionLines`, un indicador y un punto) se pliega en `maybe` (D6). `GetCollisionRec` devuelve un solo `Rectangle`.

### 🌉 Uso de `std.ffi`

Solo `slice of Vector2` → `ref to frozen Vector2` mediante `transmute (sigil of (points at 0))`, en las nueve funciones con slice, más `import std.ffi` para nada más. En esta familia no hay cadenas: no se dibuja ninguna ruta, solo colores y coordenadas.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — las figuras como métodos y las de módulo, lado a lado
import raylib
import raylibx.shapes as shapes

weave main into int:
    var center as raylib.Vector2 is with x is 100.0, y is 100.0
    var rec as raylib.Rectangle is with x is 10.0, y is 10.0, width is 40.0, height is 20.0
    calling center.draw_circle with 20.0, raylib.RED
    calling center.draw_line_to with (with x is 200.0, y is 100.0), raylib.BLUE
    calling rec.draw with raylib.GREEN
    calling rec.draw_rounded with 0.4, 8, raylib.WHITE
    calling shapes.draw_circle with 300, 300, 25.0, raylib.YELLOW
    calling shapes.draw_rectangle with 0, 0, 50, 50, raylib.PURPLE
    return 0
```

```pengu
# Ejemplo 2 — slices y una pizca de colisión
import raylib
import raylibx.shapes as shapes

weave main into int:
    var points as list of raylib.Vector2 is list of raylib.Vector2
    defer banish points
    calling points.push with (with x is 0.0, y is 0.0)
    calling points.push with (with x is 50.0, y is 50.0)
    calling points.push with (with x is 100.0, y is 0.0)
    var strip as slice of raylib.Vector2 is points at 0 to 3
    calling shapes.draw_line_strip with strip, raylib.RED
    calling shapes.draw_spline_catmull_rom with strip, 2.0, raylib.WHITE
    var inside as bool is calling shapes.collision_point_poly with (with x is 50.0, y is 20.0), strip
    return 0
```

```pengu
# Ejemplo 3 — consultas de colisión que no necesitan ventana
import raylib
import raylibx.shapes as shapes

weave main into int:
    var a as raylib.Rectangle is with x is 0.0, y is 0.0, width is 10.0, height is 10.0
    var b as raylib.Rectangle is with x is 5.0, y is 5.0, width is 10.0, height is 10.0
    var hit as bool is calling shapes.collision_recs with a, b
    var overlap as raylib.Rectangle is calling shapes.collision_rectangle with a, b
    var point as raylib.Vector2 is with x is 3.0, y is 3.0
    var inside as bool is calling a.contains_point with point
    var cross as maybe raylib.Vector2 is calling shapes.line_intersection with (with x is 0.0, y is 0.0), (with x is 10.0, y is 0.0), (with x is 5.0, y is -5.0), (with x is 5.0, y is 5.0)
    return 0
```

### 🧪 Plan de tests

La división en esta familia es tajante y merece decirse sin rodeos.

**Testeable en CI (sin ventana):** las nueve funciones de colisión, `Rectangle.contains_point`, los tres getters de la textura de formas y las *rutas de guarda* de los nueve dibujos con slice.

**No testeable en CI (necesita ventana y GPU):** las 49 llamadas `Draw*` en sí. Los comandos de dibujo de raylib fuera de un par `BeginDrawing`/`EndDrawing` son indefinidos; llamarlos sin display o abortaría o dependería en silencio de un estado GL sin inicializar. Por eso esas funciones se cubren con un test **compilado pero no invocado**: una función que referencia cada una para que la firma se compruebe de tipos en `pengu check`, con un comentario que dice que la llamada no se ejecuta en CI. Es la degradación honesta que registra el plan de familia, la misma que `rcamerax` usó para sus rutas ligadas a ventana.

- **`collision_recs`**: dos rectángulos solapados son `true`; rectángulos disjuntos son `false`; un rectángulo vacío (ancho cero) no colisiona con nada, ni consigo mismo (medido).
- **`collision_rectangle`**: el solapamiento de `(0,0,10,10)` y `(5,5,10,10)` es `(5,5,5,5)`; un par disjunto da `(0,0,0,0)`; el resultado nunca excede a ninguno de los dos.
- **`collision_circles`**: círculos idénticos colisionan; círculos separados exactamente `r1 + r2` dan `false` (el C compara estricto); círculos lejanos dan `false`.
- **`collision_circle_rec`**: un círculo centrado dentro del rectángulo es `true`; uno centrado fuera y a más distancia que el radio es `false`.
- **`collision_circle_line`**: un círculo centrado sobre el segmento es `true`; uno lejos de él es `false`.
- **`collision_point_circle`**: el centro está dentro; un punto exactamente en `radius` es el caso límite que el test fija; un punto fuera es `false`.
- **`collision_point_triangle`**: un punto dentro de un triángulo es `true`; uno fuera es `false`.
- **`collision_point_line`**: medido — un punto sobre el segmento con `threshold = 1` es `true`, y un punto a 9 píxeles es `false`.
- **`collision_point_poly`**: un punto dentro de un triángulo es `true`; uno fuera es `false`; un slice vacío da `false` sin tocar el elemento cero.
- **`line_intersection`**: medido — el par que se cruza `(0,0)-(10,0)` y `(5,-5)-(5,5)` da `some (5, 0)`; el par paralelo da `maybe none`; el punto devuelto está en ambos segmentos.
- **`Rectangle.contains_point`**: un punto dentro es `true`; uno fuera es `false`; la esquina es el caso límite que fija la medición.
- **`shapes_texture_rectangle`**: el valor por defecto medido es `(0, 0, 1, 1)`; `shapes_texture` devuelve una textura cuyos `width`/`height` son ese marcador de 1×1 antes de cualquier `SetShapesTexture`.
- **`set_shapes_texture`**: no se llama en CI (muta estado GL global); la ida y vuelta `set` → `shapes_texture` queda documentada en su lugar.
- **Los nueve dibujos con slice**: cada uno se llama con un slice **vacío** y debe ser un no-op que no lea el elemento cero. Es la única aserción que es a la vez significativa y segura en CI, y es exactamente la guarda que añade el wrapper.
- **Los 49 dibujos ligados a ventana**: no se llaman. El archivo de tests contiene un `weave draw_api_probe` que recibe los valores que cada uno necesita y los llama, de modo que toda la superficie pública se comprueba de tipos al compilar; el test en sí deja constancia de que no se invoca en CI.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `DrawTextureNPatch` y el resto de `DrawTexture*` | **no son de esta familia**: son de `textures` (plan maestro D6), y el registro ya las asigna allí |
| `ImageDraw*` (`ImageDrawLine`, `ImageDrawCircle`, …) | **no son de esta familia**: son métodos de `Image` y pertenecen a `raylibx_images` |
| `DrawRectangleGradientEx` y sus hermanos de 4 colores `DrawRectangleGradientV/H` | **envueltos**: `DrawRectangleGradientEx` como método `Rectangle.draw_gradient` y los otros dos como funciones de módulo con su firma entera (D8) |

Auditoría de cobertura: de las 75 funciones de la sección shapes, **69 se envuelven** — 20 métodos de `Vector2`, 6 métodos de `Rectangle` (incluido `contains_point`) y 36 funciones de módulo, una de las cuales (`line_intersection`) es el único `maybe` de la familia. No se omite nada. El registro de métodos gana estas entradas para `raylib.Vector2` y `raylib.Rectangle`; **ninguna otra familia puede añadir un método a ninguno de los dos tipos**.
