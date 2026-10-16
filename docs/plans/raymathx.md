# Plan: raymathx.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raymath.d.pengu`
- Wrapper target: `pengu/raymathx.pengu`
- Dependencies: `import raylib`, `import raymath`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete**. 146 `declare`, exact 1:1 set match against the 146 `RMAPI` functions of `include/raymath.h`. Nothing missing. | Symmetric diff of header `RMAPI` names vs binding `declare` names is empty. |
| D2 | Enchanting targets are `raylib.Vector2`, `raylib.Vector3`, `raylib.Vector4`, `raylib.Quaternion`, `raylib.Matrix`; the types live in `raylib.d.pengu`. `ritual` call sites use the **bare** type name (`calling Vector2.new with …`). | Contract §1/§4; `enchanting raymath.Vector2:` and three-segment `raylib.Vector2.new` are both `E0004`. |
| D3 | `raylib.Quaternion` is `alias Quaternion as Vector4`, so both names denote **one** C type: two `enchanting` blocks are legal, but a method name may appear in **only one**. Quaternion operations go on `raylib.Quaternion:`, plain 4D vector operations on `raylib.Vector4:`. | Verified on `pengu 2.4.0`: `weave length` in both blocks emits `float Vector4_length` twice and both call sites bind to the first body (duplicate C symbol = broken bundle). Distinct names (`Quaternion.mul` vs `Vector4.multiply`) keep distinct bodies. |
| D4 | `ritual new`, `splat`, `identity` are used with the **bare** type name at the call site (`calling Vector2.new with …`). | Contract §1: `raylib.Vector2.new` (three segments) is `E0004`. |
| D5 | Pure methods returning a derived value carry **no** `@mutates`: `length`, `length_sq`, `dot`, `distance`, `angle`, `cross`, `perpendicular`, `min_with`, `max_with`, `reflect_in`, `refract_through`, `determinant`, `trace`, conversions. Conversely, a C function returning `void` while writing through a receiver pointer is exposed as `weave … into void`, never `@mutates`. | Contract §4, style guide §6.7: `@mutates` needs the receiver's own type as return type (`E0067` otherwise); raymath has only one such by-pointer mutator. |
| D6 | `decompose` returns a new wrapper `rune MatrixParts` (three named fields) instead of three out-parameters. | Contract §6, style guide §17.1: named domain values are a `rune`, not out-params. |
| D7 | The 14 wrapped matrix constructors (`identity`, `zero`, `from_translation`, `from_scale`, `rotation`, `rotation_x/y/z`, `rotation_xyz/zyx`, `frustum`, `perspective`, `ortho`, `look_at`, `compose`) are `ritual`, not methods. | No receiver to transform; style guide §2.5 (`from_*`, `identity`). |
| D8 | Scalar helpers (`Clamp`, `Lerp`, `Normalize`, `Remap`, `Wrap`, `FloatEquals`) are **module-level** functions, not methods on `f32`, and NaN-producing conversions (`QuaternionToEuler`) are **not** `maybe`: `maybe` models absence, not `NaN`. | Contract §6.1 gives `no` to "is the first argument the subject?"; module-level also avoids providing `(f32, clamp)` twice alongside `std.numerus` (`E0047`). Contract §3 for the `NaN` case. |
| D9 | The infix operators are **not** bound: no `bind raylib.Vector2 with Par`, no arithmetic-operator concepts. | raymath exposes no C operators. `Par` would need `Vector2Equals`: `int` `0`/`1` with approximate comparison — wrong semantics for an equality contract. |
| D10 | `angle_line_to` is the chosen name for `Vector2LineAngle` (not `line_angle`). | Reads as a method and stays distinct from `Vector2Angle` → `angle_to`. |
| D11 | **Quaternion construction is module-level, not `ritual`**: `raymathx.quaternion_identity()`, `quaternion_from_axis_angle()`, `quaternion_from_euler()`, `quaternion_from_matrix()`, `quaternion_from_vector_to_vector()`. Only `Vector4.identity` stays a `ritual`. | Verified on `pengu 2.4.0`: a `ritual` declared inside `enchanting raylib.Quaternion:` is **not** reachable — `calling Quaternion.identity` / `Quaternion.from_axis_angle` both give `E0004` (`Type 'Quaternion' has no ritual method …`), including with unique names (`identityq`, `new_quat`). The alias shares `Vector4`'s ritual table, so the quaternion factories live at module level and the `rune`-literal form (`with x is …, w is …`) covers inline construction. |

| D12 | Phase-2 findings applied to the wrapper: (a) `Vector3.cubic_hermite_to` is `@mutates` (D6 listed it as such, its own table said pure) and exposes `get_cubic_hermite_to`; (b) `clamp_magnitude` leaves the zero vector unchanged, because `Vector2/3ClampValue` guard on `length > 0`; (c) `raymathx.quaternion_*` factories are called **unqualified** from inside `raymathx.pengu` (a module cannot qualify itself, contract §12). | Verified while writing and testing `pengu/raymathx.pengu` on `pengu 2.4.0`. |
### ✨ Enchantings

`Quaternion` and `Vector4` share one method table (D3), so the quaternion block declares only what is meaningful for a rotation. `add`, `add_scalar`, `subtract`, `subtract_scalar`, `scale`, `divide`, `negate`, `normalize`, `invert`, `length`, `length_sq`, `dot`, `distance_to`, `distance_sq_to`, `lerp_to`, `move_towards`, `multiply`, `min_with`, `max_with` and every constructor come from the `Vector4` block above and apply to a `Quaternion` value unchanged.

`get_<name>` is **not** declared: the compiler generates it from `@mutates weave <name>` (contract §4, `E0068` if declared by hand). The column below documents the generated form only.

#### `enchanting raylib.Vector2`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `new` / `splat` | ritual | `new with x, y` · `splat with value` | (inline) | struct literal; `splat` fills both lanes |
| `zero` / `one` | ritual | `into raylib.Vector2` | `Vector2Zero` / `Vector2One` | constantes del tipo |
| `add` / `add_scalar` | @mutates | `add with other` · `add_scalar with add as f32` | `Vector2Add` / `Vector2AddValue` | `get_add` generated |
| `subtract` / `subtract_scalar` | @mutates | `subtract with other` · `subtract_scalar with sub as f32` | `Vector2Subtract` / `Vector2SubtractValue` | `get_subtract` generated |
| `multiply` | @mutates | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Multiply` | component-wise |
| `scale` | @mutates | `with factor as f32 into raylib.Vector2` | `Vector2Scale` | `get_scale` generated |
| `divide` | @mutates | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Divide` | |
| `negate` | @mutates | `into raylib.Vector2` | `Vector2Negate` | |
| `invert` | @mutates | `into raylib.Vector2` | `Vector2Invert` | `1/x`, `1/y` |
| `normalize` | @mutates | `into raylib.Vector2` | `Vector2Normalize` | zero vector maps to zero |
| `clamp` | @mutates | `with lo as raylib.Vector2, hi as raylib.Vector2 into raylib.Vector2` | `Vector2Clamp` | component-wise |
| `clamp_magnitude` | @mutates | `with lo as f32, hi as f32 into raylib.Vector2` | `Vector2ClampValue` | clamps the magnitude |
| `lerp_to` | @mutates | `with other as raylib.Vector2, t as f32 into raylib.Vector2` | `Vector2Lerp` | `get_lerp_to` generated |
| `move_towards` | @mutates | `with target as raylib.Vector2, max_distance as f32 into raylib.Vector2` | `Vector2MoveTowards` | |
| `rotate_by` | @mutates | `with angle as f32 into raylib.Vector2` | `Vector2Rotate` | radians |
| `length` | pure | `into f32` | `Vector2Length` | |
| `length_sq` | pure | `into f32` | `Vector2LengthSqr` | cheaper than `length` |
| `dot` | pure | `with other as raylib.Vector2 into f32` | `Vector2DotProduct` | |
| `cross` | pure | `with other as raylib.Vector2 into f32` | `Vector2CrossProduct` | 2D cross = scalar |
| `distance_to` | pure | `with other as raylib.Vector2 into f32` | `Vector2Distance` | |
| `distance_sq_to` | pure | `with other as raylib.Vector2 into f32` | `Vector2DistanceSqr` | |
| `angle_to` | pure | `with other as raylib.Vector2 into f32` | `Vector2Angle` | signed, y-down convention |
| `angle_line_to` | pure | `with other as raylib.Vector2 into f32` | `Vector2LineAngle` | inputs should be normalized |
| `min_with` | pure | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Min` | component-wise |
| `max_with` | pure | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Max` | component-wise |
| `reflect_in` | pure | `with normal as raylib.Vector2 into raylib.Vector2` | `Vector2Reflect` | `normal` must be normalized |
| `refract_through` | pure | `with normal as raylib.Vector2, ratio as f32 into raylib.Vector2` | `Vector2Refract` | both normalized |
| `transform_by` | pure | `with mat as raylib.Matrix into raylib.Vector2` | `Vector2Transform` | |

#### `enchanting raylib.Vector3`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `new` / `splat` | ritual | `new with x, y, z` · `splat with value` | (inline) | `splat` fills all three lanes |
| `zero` / `one` | ritual | `into raylib.Vector3` | `Vector3Zero` / `Vector3One` | constantes del tipo |
| `radians_to_degrees` | ritual | `with radians as f32 into raylib.Vector3` | (inline) | `x = y = z = radians * RAD2DEG` |
| `degrees_to_radians` | ritual | `with degrees as f32 into raylib.Vector3` | (inline) | `x = y = z = degrees * DEG2RAD` |
| `add` / `add_scalar` | @mutates | `add with other` · `add_scalar with add as f32` | `Vector3Add` / `Vector3AddValue` | |
| `subtract` / `subtract_scalar` | @mutates | `subtract with other` · `subtract_scalar with sub as f32` | `Vector3Subtract` / `Vector3SubtractValue` | |
| `multiply` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Multiply` | component-wise |
| `scale` | @mutates | `with factor as f32 into raylib.Vector3` | `Vector3Scale` | |
| `divide` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Divide` | |
| `negate` | @mutates | `into raylib.Vector3` | `Vector3Negate` | |
| `invert` | @mutates | `into raylib.Vector3` | `Vector3Invert` | |
| `normalize` | @mutates | `into raylib.Vector3` | `Vector3Normalize` | zero vector maps to zero |
| `clamp` | @mutates | `with lo as raylib.Vector3, hi as raylib.Vector3 into raylib.Vector3` | `Vector3Clamp` | component-wise |
| `clamp_magnitude` | @mutates | `with lo as f32, hi as f32 into raylib.Vector3` | `Vector3ClampValue` | a zero vector cannot be lengthened: C guards on `length > 0` |
| `lerp_to` | @mutates | `with other as raylib.Vector3, t as f32 into raylib.Vector3` | `Vector3Lerp` | |
| `move_towards` | @mutates | `with target as raylib.Vector3, max_distance as f32 into raylib.Vector3` | `Vector3MoveTowards` | |
| `cross_with` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3CrossProduct` | **mutates**: `v = v × w` |
| `project_onto` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Project` | `v = proj(v, w)` |
| `reject_from` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Reject` | `v = v - proj(v, w)` |
| `rotate_by_quaternion` | @mutates | `with rotation as raylib.Quaternion into raylib.Vector3` | `Vector3RotateByQuaternion` | `v = q·v` |
| `length` | pure | `into f32` | `Vector3Length` | binding takes `frozen Vector3` |
| `length_sq` | pure | `into f32` | `Vector3LengthSqr` | |
| `dot` | pure | `with other as raylib.Vector3 into f32` | `Vector3DotProduct` | |
| `distance_to` | pure | `with other as raylib.Vector3 into f32` | `Vector3Distance` | |
| `distance_sq_to` | pure | `with other as raylib.Vector3 into f32` | `Vector3DistanceSqr` | |
| `angle_to` | pure | `with other as raylib.Vector3 into f32` | `Vector3Angle` | |
| `perpendicular` | pure | `into raylib.Vector3` | `Vector3Perpendicular` | |
| `min_with` | pure | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Min` | |
| `max_with` | pure | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Max` | |
| `reflect_in` | pure | `with normal as raylib.Vector3 into raylib.Vector3` | `Vector3Reflect` | |
| `refract_through` | pure | `with normal as raylib.Vector3, ratio as f32 into raylib.Vector3` | `Vector3Refract` | |
| `cubic_hermite_to` | @mutates | `with t1 as raylib.Vector3, other as raylib.Vector3, t2 as raylib.Vector3, t as f32 into raylib.Vector3` | `Vector3CubicHermite` | GLTF 2.0 §interpolation-cubic; `get_cubic_hermite_to` generated |
| `rotate_by_axis` | pure | `with axis as raylib.Vector3, angle as f32 into raylib.Vector3` | `Vector3RotateByAxisAngle` | |
| `transform_by` | pure | `with mat as raylib.Matrix into raylib.Vector3` | `Vector3Transform` | |
| `barycentric_in` | pure | `with a as raylib.Vector3, b as raylib.Vector3, c as raylib.Vector3 into raylib.Vector3` | `Vector3Barycenter` | `self` is the point |
| `unproject` | pure | `with projection as raylib.Matrix, view as raylib.Matrix into raylib.Vector3` | `Vector3Unproject` | screen → object space |

#### `enchanting raylib.Vector4`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `new` / `splat` | ritual | `new with x, y, z, w` · `splat with value` | (inline) | `splat` fills all four lanes |
| `zero` / `one` / `identity` | ritual | `into raylib.Vector4` | `Vector4Zero` / `Vector4One` / `QuaternionIdentity` | `identity` is shared with `Quaternion` because the alias exposes one method table (D3) |
| `add` / `add_scalar` | @mutates | `add with other` · `add_scalar with add as f32` | `Vector4Add` / `Vector4AddValue` | |
| `subtract` / `subtract_scalar` | @mutates | `subtract with other` · `subtract_scalar with sub as f32` | `Vector4Subtract` / `Vector4SubtractValue` | |
| `multiply` | @mutates | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Multiply` | component-wise |
| `scale` | @mutates | `with factor as f32 into raylib.Vector4` | `Vector4Scale` | |
| `divide` | @mutates | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Divide` | |
| `negate` | @mutates | `into raylib.Vector4` | `Vector4Negate` | |
| `invert` | @mutates | `into raylib.Vector4` | `Vector4Invert` | |
| `normalize` | @mutates | `into raylib.Vector4` | `Vector4Normalize` | |
| `lerp_to` | @mutates | `with other as raylib.Vector4, t as f32 into raylib.Vector4` | `Vector4Lerp` | |
| `move_towards` | @mutates | `with target as raylib.Vector4, max_distance as f32 into raylib.Vector4` | `Vector4MoveTowards` | |
| `length` | pure | `into f32` | `Vector4Length` | |
| `length_sq` | pure | `into f32` | `Vector4LengthSqr` | |
| `dot` | pure | `with other as raylib.Vector4 into f32` | `Vector4DotProduct` | |
| `distance_to` | pure | `with other as raylib.Vector4 into f32` | `Vector4Distance` | |
| `distance_sq_to` | pure | `with other as raylib.Vector4 into f32` | `Vector4DistanceSqr` | |
| `min_with` | pure | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Min` | |
| `max_with` | pure | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Max` | |

`Vector4` has no `Clamp` counterpart in `raymath.h`, so it exposes no `clamp`; use `min_with`/`max_with`.

#### `enchanting raylib.Quaternion`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `mul` | @mutates | `with other as raylib.Quaternion into raylib.Quaternion` | `QuaternionMultiply` | distinct name avoids `Vector4.multiply` (D3, D4) |
| `slerp_to` | @mutates | `with other as raylib.Quaternion, t as f32 into raylib.Quaternion` | `QuaternionSlerp` | |
| `nlerp_to` | @mutates | `with other as raylib.Quaternion, t as f32 into raylib.Quaternion` | `QuaternionNlerp` | |
| `cubic_hermite_to` | @mutates | `with t1 as raylib.Quaternion, other as raylib.Quaternion, t2 as raylib.Quaternion, t as f32 into raylib.Quaternion` | `QuaternionCubicHermiteSpline` | |
| `to_matrix` | pure | `into raylib.Matrix` | `QuaternionToMatrix` | |
| `to_euler` | pure | `into raylib.Vector3` | `QuaternionToEuler` | radians; ZYX order; `NaN` on degenerate input (D11) |
| `to_axis_angle` | pure | `into AxisAngle` | `QuaternionToAxisAngle` | wrapper `rune` (D8); C writes two out-params |

#### `enchanting raylib.Matrix`

| Method | Kind | Signature | C backing | Notes |
|---|---|---|---|---|
| `identity` | ritual | `into raylib.Matrix` | `MatrixIdentity` | |
| `zero` | ritual | `into raylib.Matrix` | (inline) | all-zero matrix |
| `from_translation` | ritual | `with x as f32, y as f32, z as f32 into raylib.Matrix` | `MatrixTranslate` | |
| `from_scale` | ritual | `with x as f32, y as f32, z as f32 into raylib.Matrix` | `MatrixScale` | |
| `rotation` | ritual | `with axis as raylib.Vector3, angle as f32 into raylib.Matrix` | `MatrixRotate` | radians |
| `rotation_x` | ritual | `with angle as f32 into raylib.Matrix` | `MatrixRotateX` | |
| `rotation_y` | ritual | `with angle as f32 into raylib.Matrix` | `MatrixRotateY` | |
| `rotation_z` | ritual | `with angle as f32 into raylib.Matrix` | `MatrixRotateZ` | |
| `rotation_xyz` | ritual | `with angle as raylib.Vector3 into raylib.Matrix` | `MatrixRotateXYZ` | |
| `rotation_zyx` | ritual | `with angle as raylib.Vector3 into raylib.Matrix` | `MatrixRotateZYX` | |
| `frustum` | ritual | `with left as f64, right as f64, bottom as f64, top as f64, near_plane as f64, far_plane as f64 into raylib.Matrix` | `MatrixFrustum` | |
| `perspective` | ritual | `with fov_y as f64, aspect as f64, near_plane as f64, far_plane as f64 into raylib.Matrix` | `MatrixPerspective` | radians |
| `ortho` | ritual | `with left as f64, right as f64, bottom as f64, top as f64, near_plane as f64, far_plane as f64 into raylib.Matrix` | `MatrixOrtho` | |
| `look_at` | ritual | `with eye as raylib.Vector3, target as raylib.Vector3, up as raylib.Vector3 into raylib.Matrix` | `MatrixLookAt` | |
| `compose` | ritual | `with translation as raylib.Vector3, rotation as raylib.Quaternion, scale as raylib.Vector3 into raylib.Matrix` | `MatrixCompose` | |
| `add` | @mutates | `with right as raylib.Matrix into raylib.Matrix` | `MatrixAdd` | |
| `subtract` | @mutates | `with right as raylib.Matrix into raylib.Matrix` | `MatrixSubtract` | |
| `multiply` | @mutates | `with right as raylib.Matrix into raylib.Matrix` | `MatrixMultiply` | order matters |
| `multiply_scalar` | @mutates | `with value as f32 into raylib.Matrix` | `MatrixMultiplyValue` | |
| `transpose` | @mutates | `into raylib.Matrix` | `MatrixTranspose` | |
| `invert` | @mutates | `into raylib.Matrix` | `MatrixInvert` | no failure channel: singular matrices yield garbage |
| `determinant` | pure | `into f32` | `MatrixDeterminant` | |
| `trace` | pure | `into f32` | `MatrixTrace` | |
| `parts` | pure | `into MatrixParts` | `MatrixDecompose` | wrapper `rune` (D8); writes 3 out-params |

#### Wrapper `rune` declarations

| Rune | Fields | Why |
|---|---|---|
| `AxisAngle` | `axis as raylib.Vector3`, `angle as f32` | `QuaternionToAxisAngle` writes two out-params; two independently-named values ⇒ `rune` |
| `MatrixParts` | `translation as raylib.Vector3`, `rotation as raylib.Quaternion`, `scale as raylib.Vector3` | `MatrixDecompose` writes three out-params |

### 🔧 Module-level functions

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `clamp` | `with value as f32, lo as f32, hi as f32 into f32` | `Clamp` | |
| `lerp` | `with start as f32, end as f32, t as f32 into f32` | `Lerp` | |
| `normalize_in` | `with value as f32, start as f32, end as f32 into f32` | `Normalize` | renamed: `normalize` alone collides with the vector methods |
| `remap` | `with value as f32, in_start as f32, in_end as f32, out_start as f32, out_end as f32 into f32` | `Remap` | |
| `wrap` | `with value as f32, lo as f32, hi as f32 into f32` | `Wrap` | |
| `approx_eq` | `with a as f32, b as f32 into bool` | `FloatEquals` | binding returns `int`; wrapper converts with `!= 0` |
| `quaternion_identity` | `into raylib.Quaternion` | `QuaternionIdentity` | D11: aliases cannot declare `ritual`s |
| `quaternion_from_axis_angle` | `with axis as raylib.Vector3, angle as f32 into raylib.Quaternion` | `QuaternionFromAxisAngle` | D11 |
| `quaternion_from_euler` | `with pitch as f32, yaw as f32, roll as f32 into raylib.Quaternion` | `QuaternionFromEuler` | D11; ZYX order |
| `quaternion_from_matrix` | `with mat as raylib.Matrix into raylib.Quaternion` | `QuaternionFromMatrix` | D11 |
| `quaternion_from_vector_to_vector` | `with from as raylib.Vector3, to as raylib.Vector3 into raylib.Quaternion` | `QuaternionFromVector3ToVector3` | D11 |

### 🎁 `maybe T` wrappers

**None apply.** raymath is pure by-value mathematics: no external resource (file, GPU, audio device) can cause a failure, so there is no absence to model. `MatrixInvert` on a singular matrix and `QuaternionToEuler` on a degenerate quaternion produce garbage or `NaN`, which are *wrong values*, not *absent values* (contract §3 and D11).

### ✂️ `slice` wrappers

**None apply.** raymath takes no `(T* ptr, int count)` pair and handles no arrays; every function is by-value scalar/vector/matrix arithmetic.

### 📦 Multiple returns `(T, U)`

**None apply as tuples.** The two C functions that write several values through pointers (`QuaternionToAxisAngle`, `MatrixDecompose`) are modelled with named `rune`s per contract §6 and `PenguScriptGuideSpanish.md` §17.1. No wrapper returns `(T, U)`.

### 🌉 `std.ffi` usage

**None apply, reason: raymath never crosses the string or pointer boundary.** All 146 functions take and return by-value numerics, vectors or matrices — except three that take `ref to T`, and those receivers are already the right shape for `essence of self` / `sigil of local` (no conversion needed). `import std.ffi` is therefore **not** in the wrapper's dependency list.

### 💡 Compilable examples

All three verified with `pengu check` and `pengu expand` on `pengu 2.4.0`.

```pengu
# Example 1 — construction with rituals
import raylib
import raymathx

weave main into int:
    var v as raylib.Vector2 is calling Vector2.new with 3.0, 4.0
    var s as raylib.Vector2 is calling Vector2.splat with 1.0
    var v2 as raylib.Vector2 is calling v.get_add with s
    var n as f32 is calling v2.length
    var q as raylib.Quaternion is with x is 0.0, y is 0.0, z is 0.0, w is 1.0
    var m as raylib.Matrix is calling Matrix.identity
    var t as raylib.Matrix is calling Matrix.from_translation with 1.0, 2.0, 3.0
    return 0
```

```pengu
# Example 2 — @mutates and its generated pure form
import raylib
import raymathx

weave main into int:
    var v as raylib.Vector3 is calling Vector3.new with 1.0, 2.0, 3.0
    var w as raylib.Vector3 is calling Vector3.splat with 2.0
    calling v.add with w                       # v is now (3, 4, 5)
    calling v.normalize                        # v is now unit length
    calling v.add_scalar with 0.5              # v = v + 0.5 per component
    var pure as raylib.Vector3 is calling v.get_add with w   # v unchanged
    var cl as raylib.Vector3 is calling v.get_clamp_magnitude with 0.0, 100.0
    return 0
```

```pengu
# Example 3 — chaining pure forms and quaternion factories
import raylib
import raymathx

weave main into int:
    var a as raylib.Vector3 is calling Vector3.new with 1.0, 2.0, 3.0
    var b as raylib.Vector3 is calling Vector3.new with 0.5, 0.5, 0.5
    var d as f32 is calling a.distance_to with b
    var added as raylib.Vector3 is calling a.get_add with b
    var len as f32 is calling added.length
    var axis as raylib.Vector3 is calling Vector3.new with 0.0, 1.0, 0.0
    var q as raylib.Quaternion is calling raymathx.quaternion_from_axis_angle with axis, 1.5707963
    var rotated as raylib.Vector3 is calling a.get_rotate_by_quaternion with q
    var euler as raylib.Vector3 is calling q.to_euler
    return 0
```

### 🧪 Test plan

Every public method gets ≥3 inline tests (contract §12). raymath is pure by-value mathematics, so **all** of these run in CI with no GPU, window or disk. Location: same `pengu/raymathx.pengu`, under `# --- Tests ---`, using `std.ward`.

Representative set (the full list is produced in Phase 2, three per method — happy path, edge case, documented caveat):

- **Vector2**: `new` stores both components; `get_add` sums component-wise; `get_scale` by zero gives the zero vector; `get_normalize` of the zero vector stays zero; `length` of a 3-4-5 triangle is 5; `get_lerp_to` at `t=0` returns the receiver and at `t=1` the target; `get_clamp_magnitude` keeps a short vector unchanged.
- **Vector3**: `get_cross_with` is anticommutative and zero for parallel vectors; `dot` of orthogonal vectors is zero; `get_normalize` yields unit length; `barycentric_in` at a vertex returns that vertex.
- **Vector4**: `get_add` is component-wise; `splat` fills all four lanes.
- **Quaternion**: `identity` round-trips through `get_mul`; `get_slerp_to` at `t=0` returns the receiver; `get_invert` of a unit quaternion is its conjugate; `to_axis_angle` round-trips `raymathx.quaternion_from_axis_angle`; `to_euler` of `identity` is the zero vector.
- **Matrix**: `identity.get_multiply` leaves a matrix unchanged; `identity.get_transpose` and `identity.get_invert` are the identity; `from_translation` stores the offset in `m12..m14`; `determinant` of the identity is 1; `trace` of the identity is 4; `parts` of a translation matrix recovers it.
- **Module-level**: `raymathx.clamp` below the range returns `lo`; `raymathx.lerp` at `t=0.5` is the midpoint; `raymathx.approx_eq` is true within epsilon.

CI note: all of the above are pure by-value maths, so they run in CI with no GPU, window or disk.

### 🚫 Not wrapped (with reason)

Group 1 — binding is complete (case (a), D1); nothing is missing. Group 2 — present in the binding but deliberately skipped:

| C symbol | Reason |
|---|---|
| `Vector2Equals`, `Vector3Equals`, `Vector4Equals`, `QuaternionEquals` | Contract §9 no. 13: equality predicates returning `int` (`0`/`1`) with **approximate** comparison (`EPSILON`). `bind … with Par` would make equality inexact (D9); a method adds nothing over the binding. |
| `Vector3OrthoNormalize` | `(v1 as ref to Vector3, v2 as ref to Vector3) into void` mutates **two** vectors and returns neither: no single natural receiver and `@mutates` is impossible (`E0067`). Any method spelling mutates only the receiver, because the second parameter is by value. Skipped rather than shipped with misleading semantics; use the binding. |
| `Vector3ToFloatV`, `MatrixToFloatV` | Return the binding-internal lane types `float3` / `float16`, each a single `v as f32` lane — an artefact of `pengu bind`'s array flattening, not a usable 3/16-element view. The wrapper must not surface a type that cannot carry the data. |
| `QuaternionTransform` | Transforms a quaternion as if it were a plain 4D vector (`QuaternionTransform with q as Quaternion, mat as Matrix`). That is almost never the intended rotation operation: use `to_matrix` plus `Vector3.transform_by` for rotation, and call the binding directly for the raw lane transform. |
| `Vector4Clamp`, `Vector4ClampValue` | **Do not exist** in `raymath.h` (there is no `RMAPI Vector4 Vector4Clamp`). `Vector4` therefore exposes no `clamp` / `clamp_magnitude`; `min_with` and `max_with` cover the need. |

Not listed as skipped because they **are** wrapped, recorded here to prevent naming confusion: `Vector2/3/4Invert` → `@mutates invert` (component-wise `1/x`, *not* a normalisation); `Vector2LineAngle` → `angle_line_to` (D10); `Vector3Project`/`Vector3Reject` → `@mutates project_onto`/`reject_from`; `MatrixFrustum`/`MatrixPerspective`/`MatrixOrtho` → `ritual`s taking `f64` (D9); all the zero/identity constructors → zero-argument `ritual`s.

Coverage audit over the 146 binding functions: **128 are called** and **18 are not**. Not called, with reason: `Vector2/3/4Equals` and `QuaternionEquals` (approximate equality, D9); `Vector3OrthoNormalize` (mutates two vectors, no single receiver); `Vector3ToFloatV` and `MatrixToFloatV` (flattened lane types); `QuaternionTransform` (transforms a quaternion as a plain 4D vector, almost never the intended rotation operation); and the seven quaternion arithmetic routines that the `Vector4` block already covers under the alias — `QuaternionAdd`, `QuaternionAddValue`, `QuaternionSubtract`, `QuaternionSubtractValue`, `QuaternionScale`, `QuaternionDivide`, `QuaternionNormalize`, `QuaternionInvert`, `QuaternionLength`, `QuaternionLerp` — of which only `Vector4Add`/`Vector4Subtract`/`…`/`QuaternionIdentity` are needed. The wrapper declares 138 public entries: 32 on `Vector2`, 40 on `Vector3`, 24 on `Vector4`, 7 on `Quaternion`, 24 on `Matrix` and 11 module-level functions.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raymath.d.pengu`
- Wrapper destino: `pengu/raymathx.pengu`
- Dependencias: `import raylib`, `import raymath`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo**. 146 `declare`, coincidencia exacta 1:1 contra las 146 funciones `RMAPI` de `include/raymath.h`. No falta ninguna. | La diferencia simétrica entre los nombres `RMAPI` del header y los `declare` del binding está vacía. |
| D2 | Los objetivos de `enchanting` son `raylib.Vector2`, `raylib.Vector3`, `raylib.Vector4`, `raylib.Quaternion`, `raylib.Matrix`; los tipos viven en `raylib.d.pengu`. Las invocaciones de `ritual` usan el nombre **desnudo** del tipo (`calling Vector2.new with …`). | Contrato §1/§4; `enchanting raymath.Vector2:` y `raylib.Vector2.new` de tres segmentos son ambos `E0004`. |
| D3 | `raylib.Quaternion` es `alias Quaternion as Vector4`, así que ambos nombres designan **un** tipo de C: dos bloques `enchanting` son legales, pero un nombre de método solo puede aparecer en **uno**. Las operaciones de quaternion van en `raylib.Quaternion:` y las de vector 4D puro en `raylib.Vector4:`. | Verificado en `pengu 2.4.0`: `weave length` en ambos bloques emite `float Vector4_length` dos veces y ambas llamadas caen en el primer cuerpo (símbolo C duplicado = bundle roto). Nombres distintos (`Quaternion.mul` vs `Vector4.multiply`) conservan cuerpos distintos. |
| D4 | `ritual new`, `splat` e `identity` se invocan con el nombre **desnudo** del tipo (`calling Vector2.new with …`). | Contrato §1: `raylib.Vector2.new` (tres segmentos) es `E0004`. |
| D5 | Los métodos puros que devuelven un valor derivado **no** llevan `@mutates`: `length`, `length_sq`, `dot`, `distance`, `angle`, `cross`, `perpendicular`, `min_with`, `max_with`, `reflect_in`, `refract_through`, `determinant`, `trace`, conversiones. A la inversa, una función C que devuelve `void` escribiendo por un puntero del receptor se expone como `weave … into void`, nunca `@mutates`. | Contrato §4, guía §6.7: `@mutates` exige el tipo del receptor como retorno (`E0067` en otro caso); raymath solo tiene un mutador de ese tipo. |
| D6 | `decompose` devuelve un `rune MatrixParts` nuevo (tres campos con nombre) en lugar de tres out-params. | Contrato §6, guía §17.1: los valores con nombre propio son un `rune`, no out-params. |
| D7 | Los 14 constructores de matriz envueltos (`identity`, `zero`, `from_translation`, `from_scale`, `rotation`, `rotation_x/y/z`, `rotation_xyz/zyx`, `frustum`, `perspective`, `ortho`, `look_at`, `compose`) son `ritual`, no métodos. | No hay receptor que transformar; guía §2.5 (`from_*`, `identity`). |
| D8 | Los helpers escalares (`Clamp`, `Lerp`, `Normalize`, `Remap`, `Wrap`, `FloatEquals`) son funciones **de módulo**, no métodos sobre `f32`, y las conversiones que producen `NaN` (`QuaternionToEuler`) **no** son `maybe`: `maybe` modela ausencia, no `NaN`. | El contrato §6.1 da `no` a "¿es el primer argumento el sujeto?"; a nivel de módulo además evita proveer `(f32, clamp)` dos veces junto a `std.numerus` (`E0047`). Contrato §3 para el caso `NaN`. |
| D9 | Los operadores infijos **no** se bindean: ni `bind raylib.Vector2 with Par` ni conceptos aritméticos. | raymath no expone operadores en C. `Par` necesitaría `Vector2Equals`: `int` `0`/`1` con comparación aproximada, semántica incorrecta para igualdad. |
| D10 | `angle_line_to` es el nombre elegido para `Vector2LineAngle` (no `line_angle`). | Se lee como método y queda distinto de `Vector2Angle` → `angle_to`. |
| D11 | **La construcción de quaternions es de módulo, no `ritual`**: `raymathx.quaternion_identity()`, `quaternion_from_axis_angle()`, `quaternion_from_euler()`, `quaternion_from_matrix()`, `quaternion_from_vector_to_vector()`. Solo `Vector4.identity` sigue siendo `ritual`. | Verificado en `pengu 2.4.0`: un `ritual` declarado dentro de `enchanting raylib.Quaternion:` **no** es alcanzable — `calling Quaternion.identity` y `Quaternion.from_axis_angle` dan `E0004` (`Type 'Quaternion' has no ritual method …`), incluso con nombres únicos (`identityq`, `new_quat`). El alias comparte la tabla de rituales de `Vector4`, así que las factorías de quaternion viven a nivel de módulo y el literal de `rune` (`with x is …, w is …`) cubre la construcción en línea. |

| D12 | Hallazgos de Fase 2 aplicados al wrapper: (a) `Vector3.cubic_hermite_to` es `@mutates` (D6 lo listaba así y su propia fila decía puro) y expone `get_cubic_hermite_to`; (b) `clamp_magnitude` deja intacto el vector cero, porque `Vector2/3ClampValue` comprueban `length > 0`; (c) las factorías `raymathx.quaternion_*` se invocan **sin cualificar** desde dentro de `raymathx.pengu` (un módulo no puede cualificarse a sí mismo, contrato §12). | Verificado al escribir y probar `pengu/raymathx.pengu` en `pengu 2.4.0`. |
### ✨ Enchantings

`Quaternion` y `Vector4` comparten una sola tabla de métodos (D3), así que el bloque de quaternion declara solo lo que tiene sentido para una rotación. `add`, `add_scalar`, `subtract`, `subtract_scalar`, `scale`, `divide`, `negate`, `normalize`, `invert`, `length`, `length_sq`, `dot`, `distance_to`, `distance_sq_to`, `lerp_to`, `move_towards`, `multiply`, `min_with`, `max_with` y todos los constructores vienen del bloque `Vector4` de arriba y se aplican sin cambios a un valor `Quaternion`.

`get_<nombre>` **no** se declara: el compilador lo genera a partir de `@mutates weave <nombre>` (contrato §4, `E0068` si se declara a mano). La columna de abajo documenta solo la forma generada.

#### `enchanting raylib.Vector2`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `new` / `splat` | ritual | `new with x, y` · `splat with value` | (inline) | literal de struct; `splat` rellena ambos carriles |
| `zero` / `one` | ritual | `into raylib.Vector2` | `Vector2Zero` / `Vector2One` | constantes del tipo |
| `add` / `add_scalar` | @mutates | `add with other` · `add_scalar with add as f32` | `Vector2Add` / `Vector2AddValue` | `get_add` generado |
| `subtract` / `subtract_scalar` | @mutates | `subtract with other` · `subtract_scalar with sub as f32` | `Vector2Subtract` / `Vector2SubtractValue` | `get_subtract` generado |
| `multiply` | @mutates | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Multiply` | componente a componente |
| `scale` | @mutates | `with factor as f32 into raylib.Vector2` | `Vector2Scale` | `get_scale` generado |
| `divide` | @mutates | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Divide` | |
| `negate` | @mutates | `into raylib.Vector2` | `Vector2Negate` | |
| `invert` | @mutates | `into raylib.Vector2` | `Vector2Invert` | `1/x`, `1/y` |
| `normalize` | @mutates | `into raylib.Vector2` | `Vector2Normalize` | el vector cero se queda en cero |
| `clamp` | @mutates | `with lo as raylib.Vector2, hi as raylib.Vector2 into raylib.Vector2` | `Vector2Clamp` | componente a componente |
| `clamp_magnitude` | @mutates | `with lo as f32, hi as f32 into raylib.Vector2` | `Vector2ClampValue` | clamps the magnitude; a zero vector is returned unchanged |
| `lerp_to` | @mutates | `with other as raylib.Vector2, t as f32 into raylib.Vector2` | `Vector2Lerp` | `get_lerp_to` generado |
| `move_towards` | @mutates | `with target as raylib.Vector2, max_distance as f32 into raylib.Vector2` | `Vector2MoveTowards` | |
| `rotate_by` | @mutates | `with angle as f32 into raylib.Vector2` | `Vector2Rotate` | radianes |
| `length` | puro | `into f32` | `Vector2Length` | |
| `length_sq` | puro | `into f32` | `Vector2LengthSqr` | más barato que `length` |
| `dot` | puro | `with other as raylib.Vector2 into f32` | `Vector2DotProduct` | |
| `cross` | puro | `with other as raylib.Vector2 into f32` | `Vector2CrossProduct` | el producto cruzado 2D es escalar |
| `distance_to` | puro | `with other as raylib.Vector2 into f32` | `Vector2Distance` | |
| `distance_sq_to` | puro | `with other as raylib.Vector2 into f32` | `Vector2DistanceSqr` | |
| `angle_to` | puro | `with other as raylib.Vector2 into f32` | `Vector2Angle` | con signo, convención Y hacia abajo |
| `angle_line_to` | puro | `with other as raylib.Vector2 into f32` | `Vector2LineAngle` | las entradas deberían estar normalizadas |
| `min_with` | puro | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Min` | componente a componente |
| `max_with` | puro | `with other as raylib.Vector2 into raylib.Vector2` | `Vector2Max` | componente a componente |
| `reflect_in` | puro | `with normal as raylib.Vector2 into raylib.Vector2` | `Vector2Reflect` | `normal` debe estar normalizada |
| `refract_through` | puro | `with normal as raylib.Vector2, ratio as f32 into raylib.Vector2` | `Vector2Refract` | ambas normalizadas |
| `transform_by` | puro | `with mat as raylib.Matrix into raylib.Vector2` | `Vector2Transform` | |

#### `enchanting raylib.Vector3`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `new` / `splat` | ritual | `new with x, y, z` · `splat with value` | (inline) | `splat` rellena los tres carriles |
| `zero` / `one` | ritual | `into raylib.Vector3` | `Vector3Zero` / `Vector3One` | constantes del tipo |
| `radians_to_degrees` | ritual | `with radians as f32 into raylib.Vector3` | (inline) | `x = y = z = radians * RAD2DEG` |
| `degrees_to_radians` | ritual | `with degrees as f32 into raylib.Vector3` | (inline) | `x = y = z = degrees * DEG2RAD` |
| `add` / `add_scalar` | @mutates | `add with other` · `add_scalar with add as f32` | `Vector3Add` / `Vector3AddValue` | |
| `subtract` / `subtract_scalar` | @mutates | `subtract with other` · `subtract_scalar with sub as f32` | `Vector3Subtract` / `Vector3SubtractValue` | |
| `multiply` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Multiply` | componente a componente |
| `scale` | @mutates | `with factor as f32 into raylib.Vector3` | `Vector3Scale` | |
| `divide` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Divide` | |
| `negate` | @mutates | `into raylib.Vector3` | `Vector3Negate` | |
| `invert` | @mutates | `into raylib.Vector3` | `Vector3Invert` | |
| `normalize` | @mutates | `into raylib.Vector3` | `Vector3Normalize` | el vector cero se queda en cero |
| `clamp` | @mutates | `with lo as raylib.Vector3, hi as raylib.Vector3 into raylib.Vector3` | `Vector3Clamp` | componente a componente |
| `clamp_magnitude` | @mutates | `with lo as f32, hi as f32 into raylib.Vector3` | `Vector3ClampValue` | |
| `lerp_to` | @mutates | `with other as raylib.Vector3, t as f32 into raylib.Vector3` | `Vector3Lerp` | |
| `move_towards` | @mutates | `with target as raylib.Vector3, max_distance as f32 into raylib.Vector3` | `Vector3MoveTowards` | |
| `cross_with` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3CrossProduct` | **muta**: `v = v × w` |
| `project_onto` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Project` | `v = proj(v, w)` |
| `reject_from` | @mutates | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Reject` | `v = v - proj(v, w)` |
| `rotate_by_quaternion` | @mutates | `with rotation as raylib.Quaternion into raylib.Vector3` | `Vector3RotateByQuaternion` | `v = q·v` |
| `length` | puro | `into f32` | `Vector3Length` | el binding recibe `frozen Vector3` |
| `length_sq` | puro | `into f32` | `Vector3LengthSqr` | |
| `dot` | puro | `with other as raylib.Vector3 into f32` | `Vector3DotProduct` | |
| `distance_to` | puro | `with other as raylib.Vector3 into f32` | `Vector3Distance` | |
| `distance_sq_to` | puro | `with other as raylib.Vector3 into f32` | `Vector3DistanceSqr` | |
| `angle_to` | puro | `with other as raylib.Vector3 into f32` | `Vector3Angle` | |
| `perpendicular` | puro | `into raylib.Vector3` | `Vector3Perpendicular` | |
| `min_with` | puro | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Min` | |
| `max_with` | puro | `with other as raylib.Vector3 into raylib.Vector3` | `Vector3Max` | |
| `reflect_in` | puro | `with normal as raylib.Vector3 into raylib.Vector3` | `Vector3Reflect` | |
| `refract_through` | puro | `with normal as raylib.Vector3, ratio as f32 into raylib.Vector3` | `Vector3Refract` | |
| `cubic_hermite_to` | puro | `with t1 as raylib.Vector3, other as raylib.Vector3, t2 as raylib.Vector3, t as f32 into raylib.Vector3` | `Vector3CubicHermite` | GLTF 2.0 §interpolation-cubic |
| `rotate_by_axis` | puro | `with axis as raylib.Vector3, angle as f32 into raylib.Vector3` | `Vector3RotateByAxisAngle` | |
| `transform_by` | puro | `with mat as raylib.Matrix into raylib.Vector3` | `Vector3Transform` | |
| `barycentric_in` | puro | `with a as raylib.Vector3, b as raylib.Vector3, c as raylib.Vector3 into raylib.Vector3` | `Vector3Barycenter` | `self` es el punto |
| `unproject` | puro | `with projection as raylib.Matrix, view as raylib.Matrix into raylib.Vector3` | `Vector3Unproject` | de pantalla a espacio de objeto |

#### `enchanting raylib.Vector4`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `new` / `splat` | ritual | `new with x, y, z, w` · `splat with value` | (inline) | `splat` rellena los cuatro carriles |
| `zero` / `one` / `identity` | ritual | `into raylib.Vector4` | `Vector4Zero` / `Vector4One` / `QuaternionIdentity` | `identity` se comparte con `Quaternion` porque el alias expone una sola tabla de métodos (D3) |
| `add` / `add_scalar` | @mutates | `add with other` · `add_scalar with add as f32` | `Vector4Add` / `Vector4AddValue` | |
| `subtract` / `subtract_scalar` | @mutates | `subtract with other` · `subtract_scalar with sub as f32` | `Vector4Subtract` / `Vector4SubtractValue` | |
| `multiply` | @mutates | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Multiply` | componente a componente |
| `scale` | @mutates | `with factor as f32 into raylib.Vector4` | `Vector4Scale` | |
| `divide` | @mutates | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Divide` | |
| `negate` | @mutates | `into raylib.Vector4` | `Vector4Negate` | |
| `invert` | @mutates | `into raylib.Vector4` | `Vector4Invert` | |
| `normalize` | @mutates | `into raylib.Vector4` | `Vector4Normalize` | |
| `lerp_to` | @mutates | `with other as raylib.Vector4, t as f32 into raylib.Vector4` | `Vector4Lerp` | |
| `move_towards` | @mutates | `with target as raylib.Vector4, max_distance as f32 into raylib.Vector4` | `Vector4MoveTowards` | |
| `length` | puro | `into f32` | `Vector4Length` | |
| `length_sq` | puro | `into f32` | `Vector4LengthSqr` | |
| `dot` | puro | `with other as raylib.Vector4 into f32` | `Vector4DotProduct` | |
| `distance_to` | puro | `with other as raylib.Vector4 into f32` | `Vector4Distance` | |
| `distance_sq_to` | puro | `with other as raylib.Vector4 into f32` | `Vector4DistanceSqr` | |
| `min_with` | puro | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Min` | |
| `max_with` | puro | `with other as raylib.Vector4 into raylib.Vector4` | `Vector4Max` | |

`Vector4` no tiene `Clamp` ni `ClampValue` en el binding: no se envuelve ninguno (véase "NO se envuelve").

#### `enchanting raylib.Quaternion`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `mul` | @mutates | `with other as raylib.Quaternion into raylib.Quaternion` | `QuaternionMultiply` | nombre distinto para no chocar con `Vector4.multiply` (D3, D4) |
| `slerp_to` | @mutates | `with other as raylib.Quaternion, t as f32 into raylib.Quaternion` | `QuaternionSlerp` | |
| `nlerp_to` | @mutates | `with other as raylib.Quaternion, t as f32 into raylib.Quaternion` | `QuaternionNlerp` | |
| `cubic_hermite_to` | @mutates | `with t1 as raylib.Quaternion, other as raylib.Quaternion, t2 as raylib.Quaternion, t as f32 into raylib.Quaternion` | `QuaternionCubicHermiteSpline` | |
| `to_matrix` | puro | `into raylib.Matrix` | `QuaternionToMatrix` | |
| `to_euler` | puro | `into raylib.Vector3` | `QuaternionToEuler` | radianes; orden ZYX; `NaN` con entradas degeneradas (D11) |
| `to_axis_angle` | puro | `into AxisAngle` | `QuaternionToAxisAngle` | `rune` del wrapper (D8); C escribe dos out-params |

#### `enchanting raylib.Matrix`

| Método | Tipo | Firma | C backing | Notas |
|---|---|---|---|---|
| `identity` | ritual | `into raylib.Matrix` | `MatrixIdentity` | |
| `zero` | ritual | `into raylib.Matrix` | (inline) | matriz de ceros |
| `from_translation` | ritual | `with x as f32, y as f32, z as f32 into raylib.Matrix` | `MatrixTranslate` | |
| `from_scale` | ritual | `with x as f32, y as f32, z as f32 into raylib.Matrix` | `MatrixScale` | |
| `rotation` | ritual | `with axis as raylib.Vector3, angle as f32 into raylib.Matrix` | `MatrixRotate` | radianes |
| `rotation_x` | ritual | `with angle as f32 into raylib.Matrix` | `MatrixRotateX` | |
| `rotation_y` | ritual | `with angle as f32 into raylib.Matrix` | `MatrixRotateY` | |
| `rotation_z` | ritual | `with angle as f32 into raylib.Matrix` | `MatrixRotateZ` | |
| `rotation_xyz` | ritual | `with angle as raylib.Vector3 into raylib.Matrix` | `MatrixRotateXYZ` | |
| `rotation_zyx` | ritual | `with angle as raylib.Vector3 into raylib.Matrix` | `MatrixRotateZYX` | |
| `frustum` | ritual | `with left as f64, right as f64, bottom as f64, top as f64, near_plane as f64, far_plane as f64 into raylib.Matrix` | `MatrixFrustum` | |
| `perspective` | ritual | `with fov_y as f64, aspect as f64, near_plane as f64, far_plane as f64 into raylib.Matrix` | `MatrixPerspective` | radianes |
| `ortho` | ritual | `with left as f64, right as f64, bottom as f64, top as f64, near_plane as f64, far_plane as f64 into raylib.Matrix` | `MatrixOrtho` | |
| `look_at` | ritual | `with eye as raylib.Vector3, target as raylib.Vector3, up as raylib.Vector3 into raylib.Matrix` | `MatrixLookAt` | |
| `compose` | ritual | `with translation as raylib.Vector3, rotation as raylib.Quaternion, scale as raylib.Vector3 into raylib.Matrix` | `MatrixCompose` | |
| `add` | @mutates | `with right as raylib.Matrix into raylib.Matrix` | `MatrixAdd` | |
| `subtract` | @mutates | `with right as raylib.Matrix into raylib.Matrix` | `MatrixSubtract` | |
| `multiply` | @mutates | `with right as raylib.Matrix into raylib.Matrix` | `MatrixMultiply` | el orden importa |
| `multiply_scalar` | @mutates | `with value as f32 into raylib.Matrix` | `MatrixMultiplyValue` | |
| `transpose` | @mutates | `into raylib.Matrix` | `MatrixTranspose` | |
| `invert` | @mutates | `into raylib.Matrix` | `MatrixInvert` | sin canal de fallo: una matriz singular da basura |
| `determinant` | puro | `into f32` | `MatrixDeterminant` | |
| `trace` | puro | `into f32` | `MatrixTrace` | |
| `parts` | puro | `into MatrixParts` | `MatrixDecompose` | `rune` del wrapper (D8); escribe 3 out-params |

#### `rune` del wrapper

| Rune | Campos | Motivo |
|---|---|---|
| `AxisAngle` | `axis as raylib.Vector3`, `angle as f32` | `QuaternionToAxisAngle` escribe dos out-params; dos valores con nombre propio ⇒ `rune` |
| `MatrixParts` | `translation as raylib.Vector3`, `rotation as raylib.Quaternion`, `scale as raylib.Vector3` | `MatrixDecompose` escribe tres out-params |

### 🔧 Funciones a nivel de módulo

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `clamp` | `with value as f32, lo as f32, hi as f32 into f32` | `Clamp` | |
| `lerp` | `with start as f32, end as f32, t as f32 into f32` | `Lerp` | |
| `normalize_in` | `with value as f32, start as f32, end as f32 into f32` | `Normalize` | renombrado: `normalize` a secas choca con los métodos de vector |
| `remap` | `with value as f32, in_start as f32, in_end as f32, out_start as f32, out_end as f32 into f32` | `Remap` | |
| `wrap` | `with value as f32, lo as f32, hi as f32 into f32` | `Wrap` | |
| `approx_eq` | `with a as f32, b as f32 into bool` | `FloatEquals` | el binding devuelve `int`; el wrapper convierte con `!= 0` |
| `quaternion_identity` | `into raylib.Quaternion` | `QuaternionIdentity` | D11: los alias no pueden declarar `ritual` |
| `quaternion_from_axis_angle` | `with axis as raylib.Vector3, angle as f32 into raylib.Quaternion` | `QuaternionFromAxisAngle` | D11 |
| `quaternion_from_euler` | `with pitch as f32, yaw as f32, roll as f32 into raylib.Quaternion` | `QuaternionFromEuler` | D11; orden ZYX |
| `quaternion_from_matrix` | `with mat as raylib.Matrix into raylib.Quaternion` | `QuaternionFromMatrix` | D11 |
| `quaternion_from_vector_to_vector` | `with from as raylib.Vector3, to as raylib.Vector3 into raylib.Quaternion` | `QuaternionFromVector3ToVector3` | D11 |

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** raymath es matemática pura por valor: ningún recurso externo (fichero, GPU, dispositivo de audio) puede provocar un fallo, así que no hay ausencia que modelar. `MatrixInvert` sobre una matriz singular y `QuaternionToEuler` sobre un quaternion degenerado producen basura o `NaN`, que son *valores incorrectos*, no *valores ausentes* (contrato §3 y D11).

### ✂️ Wrappers de `slice`

**Ninguno aplica.** raymath no recibe ningún par `(T* ptr, int count)` ni maneja arrays; todas sus funciones son aritmética por valor de escalares, vectores y matrices.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica como tupla.** Las dos funciones C que escriben varios valores por puntero (`QuaternionToAxisAngle`, `MatrixDecompose`) se modelan con `rune`s con nombre propio según el contrato §6 y `PenguScriptGuideSpanish.md` §17.1. Ningún wrapper devuelve `(T, U)`.

### 🌉 Uso de `std.ffi`

**Ninguno aplica, motivo: raymath no cruza nunca la frontera de cadenas ni de punteros.** Las 146 funciones reciben y devuelven numéricos, vectores o matrices por valor, salvo tres que reciben `ref to T`, y esos receptores ya tienen la forma correcta para `essence of self` / `sigil of local` (sin conversión). Por tanto `import std.ffi` **no** figura en las dependencias del wrapper.

### 💡 Ejemplos compilables

Los tres verificados con `pengu check` y `pengu expand` sobre `pengu 2.4.0`.

```pengu
# Ejemplo 1 — construcción con rituales
import raylib
import raymathx

weave main into int:
    var v as raylib.Vector2 is calling Vector2.new with 3.0, 4.0
    var s as raylib.Vector2 is calling Vector2.splat with 1.0
    var v2 as raylib.Vector2 is calling v.get_add with s
    var n as f32 is calling v2.length
    var q as raylib.Quaternion is with x is 0.0, y is 0.0, z is 0.0, w is 1.0
    var m as raylib.Matrix is calling Matrix.identity
    var t as raylib.Matrix is calling Matrix.from_translation with 1.0, 2.0, 3.0
    return 0
```

```pengu
# Ejemplo 2 — @mutates y su forma pura generada
import raylib
import raymathx

weave main into int:
    var v as raylib.Vector3 is calling Vector3.new with 1.0, 2.0, 3.0
    var w as raylib.Vector3 is calling Vector3.splat with 2.0
    calling v.add with w                       # v ahora es (3, 4, 5)
    calling v.normalize                        # v pasa a longitud unitaria
    calling v.add_scalar with 0.5              # v = v + 0.5 por componente
    var pure as raylib.Vector3 is calling v.get_add with w   # v no cambia
    var cl as raylib.Vector3 is calling v.get_clamp_magnitude with 0.0, 100.0
    return 0
```

```pengu
# Ejemplo 3 — encadenamiento de formas puras y factorías de quaternion
import raylib
import raymathx

weave main into int:
    var a as raylib.Vector3 is calling Vector3.new with 1.0, 2.0, 3.0
    var b as raylib.Vector3 is calling Vector3.new with 0.5, 0.5, 0.5
    var d as f32 is calling a.distance_to with b
    var added as raylib.Vector3 is calling a.get_add with b
    var len as f32 is calling added.length
    var axis as raylib.Vector3 is calling Vector3.new with 0.0, 1.0, 0.0
    var q as raylib.Quaternion is calling raymathx.quaternion_from_axis_angle with axis, 1.5707963
    var rotated as raylib.Vector3 is calling a.get_rotate_by_quaternion with q
    var euler as raylib.Vector3 is calling q.to_euler
    return 0
```

### 🧪 Plan de tests

Cada método público lleva ≥3 tests inline (contrato §12). raymath es matemática pura por valor, así que **todos** se ejecutan en CI sin GPU, ventana ni disco. Ubicación: el mismo `pengu/raymathx.pengu`, bajo `# --- Tests ---`, con `std.ward`.

Conjunto representativo (la lista completa se produce en Fase 2, tres por método — caso feliz, caso borde y advertencia documentada):

- **Vector2**: `new` guarda ambos componentes; `get_add` suma componente a componente; `get_scale` por cero da el vector cero; `get_normalize` del vector cero sigue siendo cero; `length` de un triángulo 3-4-5 es 5; `get_lerp_to` con `t=0` devuelve el receptor y con `t=1` el objetivo; `get_clamp_magnitude` deja intacto un vector corto.
- **Vector3**: `get_cross_with` es anticonmutativo y cero para vectores paralelos; `dot` de vectores ortogonales es cero; `get_normalize` da longitud unitaria; `barycentric_in` en un vértice devuelve ese vértice.
- **Vector4**: `get_add` es componente a componente; `splat` rellena los cuatro carriles.
- **Quaternion**: `identity` va y vuelve por `get_mul`; `get_slerp_to` con `t=0` devuelve el receptor; `get_invert` de un quaternion unitario es su conjugado; `to_axis_angle` va y vuelve por `raymathx.quaternion_from_axis_angle`; `to_euler` de `identity` es el vector cero.
- **Matrix**: `identity.get_multiply` deja la matriz intacta; `identity.get_transpose` e `identity.get_invert` son la identidad; `from_translation` guarda el desplazamiento en `m12..m14`; `determinant` de la identidad es 1; `trace` de la identidad es 4; `parts` de una matriz de traslación la recupera.
- **Nivel de módulo**: `raymathx.clamp` por debajo del rango devuelve `lo`; `raymathx.lerp` con `t=0.5` es el punto medio; `raymathx.approx_eq` es verdadero dentro del epsilon.

Nota de CI: todo lo anterior es matemática pura por valor, así que se ejecuta en CI sin GPU, ventana ni disco.

### 🚫 NO se envuelve (con motivo)

Grupo 1 — el binding está completo (caso (a), D1); no falta nada. Grupo 2 — presente en el binding pero descartado a propósito:

| Símbolo C | Motivo |
|---|---|
| `Vector2Equals`, `Vector3Equals`, `Vector4Equals`, `QuaternionEquals` | Contrato §9 nº 13: predicados de igualdad que devuelven `int` (`0`/`1`) con comparación **aproximada** (`EPSILON`). `bind … with Par` haría la igualdad inexacta (D9); un método no aporta nada sobre el binding. |
| `Vector3OrthoNormalize` | `(v1 as ref to Vector3, v2 as ref to Vector3) into void` muta **dos** vectores y no devuelve ninguno: no hay receptor natural único y `@mutates` es imposible (`E0067`). Cualquier método mutaría solo el receptor, porque el segundo parámetro va por valor. Se omite en vez de publicarlo con semántica engañosa; usa el binding. |
| `Vector3ToFloatV`, `MatrixToFloatV` | Devuelven los tipos de carril internos `float3` / `float16`, cada uno un único carril `v as f32`: un artefacto del aplanado de arrays de `pengu bind`, no una vista usable de 3/16 elementos. El wrapper no debe exponer un tipo incapaz de transportar el dato. |
| `QuaternionTransform` | Transforma un quaternion como si fuera un vector 4D plano (`QuaternionTransform with q as Quaternion, mat as Matrix`). Casi nunca es la operación de rotación buscada: usa `to_matrix` más `Vector3.transform_by` para rotar, y llama al binding directamente para la transformación cruda de carriles. |
| `Vector4Clamp`, `Vector4ClampValue` | **No existen** en `raymath.h` (no hay `RMAPI Vector4 Vector4Clamp`). Por eso `Vector4` no expone `clamp` ni `clamp_magnitude`; `min_with` y `max_with` cubren la necesidad. |

No figuran como omitidos porque **sí** se envuelven; se registran aquí para evitar confusiones de nombre: `Vector2/3/4Invert` → `@mutates invert` (`1/x` componente a componente, *no* una normalización); `Vector2LineAngle` → `angle_line_to` (D10); `Vector3Project`/`Vector3Reject` → `@mutates project_onto`/`reject_from`; `MatrixFrustum`/`MatrixPerspective`/`MatrixOrtho` → `ritual` que reciben `f64` (D9); todos los constructores zero/identity → `ritual` sin argumentos.

Auditoría de cobertura sobre las 146 funciones del binding: **128 se invocan** y **18 no**. No invocadas, con motivo: `Vector2/3/4Equals` y `QuaternionEquals` (igualdad aproximada, D9); `Vector3OrthoNormalize` (muta dos vectores, sin receptor único); `Vector3ToFloatV` y `MatrixToFloatV` (tipos de carril aplanados); `QuaternionTransform` (transforma un quaternion como vector 4D, casi nunca es la operación de rotación buscada); y las siete rutinas aritméticas de quaternion que el bloque `Vector4` ya cubre por el alias — `QuaternionAdd`, `QuaternionAddValue`, `QuaternionSubtract`, `QuaternionSubtractValue`, `QuaternionScale`, `QuaternionDivide`, `QuaternionNormalize`, `QuaternionInvert`, `QuaternionLength`, `QuaternionLerp`. El wrapper declara 138 entradas públicas: 32 en `Vector2`, 40 en `Vector3`, 24 en `Vector4`, 7 en `Quaternion`, 24 en `Matrix` y 11 funciones de módulo.
