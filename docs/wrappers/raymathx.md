> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# raymathx

> Source: `pengu/raymathx.pengu`

Layer-2 wrapper over the `raymath` binding: Pengunic methods for vectors, quaternions and matrices.

The wrapper adds no storage and no types of its own beyond two small result `rune`s
(`AxisAngle`, `MatrixParts`). Every method lowers to one direct call into
`pengu/raymath.d.pengu`; the types (`Vector2`, `Vector3`, `Vector4`, `Quaternion`,
`Matrix`) are declared in `pengu/raylib.d.pengu` and are only extended here with
`enchanting`.

`Quaternion` is an alias of `Vector4`, so both names share one method table. All the
arithmetic lives on `raylib.Vector4`; `raylib.Quaternion` adds only the operations that
are meaningful for a rotation (`mul`, `slerp_to`, `nlerp_to`, `cubic_hermite_to`,
`to_matrix`, `to_euler`, `to_axis_angle`). Never declare the same method name in both
blocks: the compiler would emit one C function twice and the C build would fail.

## Memory
No allocation, no ownership, nothing to release: raymath is by-value arithmetic. There is
no `banish` and no `std.ffi` in this module.

## Example
```pengu
import raylib
import raymathx

weave main into int:
    var v as raylib.Vector3 is calling Vector3.new with 3.0, 4.0, 0.0
    calling v.normalize
    var n as f32 is calling v.length
    return 0
```

---

### `AxisAngle`

> **rune** struct

The rotation axis and angle extracted from a quaternion.
Invariants
- `axis` is normalized.
- `angle` is in radians.

**Fields:**

- `axis` : Vector3
- `angle` : f32


### `MatrixParts`

> **rune** struct

The translation, rotation and scale decomposed from a transform matrix.
Invariants
- `rotation` is a unit quaternion.
- Any shear present in the source matrix is removed during decomposition.

**Fields:**

- `translation` : Vector3
- `rotation` : Vector4
- `scale` : Vector3


### `clamp`

> **clamp**(value: f32, lo: f32, hi: f32) -> f32

Clamps a scalar between `lo` and `hi`.
Parameters
- `value`: the value to clamp.
- `lo`: lower bound.
- `hi`: upper bound.
Returns
`lo` if `value` is below it, `hi` if above, otherwise `value`.
Example
```pengu
var c as f32 is calling clamp with 5.0, 0.0, 1.0   # 1.0
```


### `lerp`

> **lerp**(start: f32, end: f32, t: f32) -> f32

Linearly interpolates between two scalars.
Parameters
- `start`: value at `t = 0`.
- `end`: value at `t = 1`.
- `t`: blend factor.
Returns
The interpolated value.
Example
```pengu
var m as f32 is calling lerp with 0.0, 10.0, 0.5   # 5.0
```


### `normalize_in`

> **normalize_in**(value: f32, start: f32, end: f32) -> f32

Normalizes a value within a range, remapping it to `[0, 1]`.
Parameters
- `value`: the value to normalize.
- `start`: start of the input range.
- `end`: end of the input range.
Returns
The normalized value.
Example
```pengu
var n as f32 is calling normalize_in with 5.0, 0.0, 10.0   # 0.5
```


### `remap`

> **remap**(value: f32, in_start: f32, in_end: f32, out_start: f32, out_end: f32) -> f32

Remaps a value from one range to another.
Parameters
- `value`: the value to remap.
- `in_start`, `in_end`: the input range.
- `out_start`, `out_end`: the output range.
Returns
The remapped value.
Example
```pengu
var r as f32 is calling remap with 5.0, 0.0, 10.0, 0.0, 100.0   # 50.0
```


### `wrap`

> **wrap**(value: f32, lo: f32, hi: f32) -> f32

Wraps a value into the `[lo, hi]` range.
Parameters
- `value`: the value to wrap.
- `lo`: lower bound.
- `hi`: upper bound.
Returns
The wrapped value.
Example
```pengu
var w as f32 is calling wrap with 370.0, 0.0, 360.0   # 10.0
```


### `approx_eq`

> **approx_eq**(a: f32, b: f32) -> bool

Compares two scalars approximately, using raymath's `EPSILON`.
Parameters
- `a`, `b`: the values to compare.
Returns
`true` when the values are closer than `EPSILON`.
Example
```pengu
var same as bool is calling approx_eq with 0.1 + 0.2, 0.3   # true
```


### `quaternion_identity`

> **quaternion_identity**() -> Vector4

Returns the identity quaternion.
Returns
A unit quaternion with `w = 1`, representing no rotation.
Example
```pengu
var q as raylib.Quaternion is calling quaternion_identity
```


### `quaternion_from_axis_angle`

> **quaternion_from_axis_angle**(axis: Vector3, angle: f32) -> Vector4

Builds a quaternion from a rotation axis and an angle.
Parameters
- `axis`: the rotation axis. It does not need to be normalized.
- `angle`: the rotation in radians.
Returns
The rotation quaternion.
Example
```pengu
var q as raylib.Quaternion is calling quaternion_from_axis_angle with (calling Vector3.new with 0.0, 1.0, 0.0), 1.5707963
```


### `quaternion_from_euler`

> **quaternion_from_euler**(pitch: f32, yaw: f32, roll: f32) -> Vector4

Builds a quaternion from Euler angles.
Parameters
- `pitch`, `yaw`, `roll`: the angles in radians, applied in ZYX order.
Returns
The rotation quaternion.
Example
```pengu
var q as raylib.Quaternion is calling quaternion_from_euler with 0.1, 0.2, 0.3
```


### `quaternion_from_matrix`

> **quaternion_from_matrix**(mat: Matrix) -> Vector4

Builds a quaternion from a rotation matrix.
Parameters
- `mat`: the rotation matrix.
Returns
The rotation quaternion.
Example
```pengu
var q as raylib.Quaternion is calling quaternion_from_matrix with (calling Matrix.identity)
```


### `quaternion_from_vector_to_vector`

> **quaternion_from_vector_to_vector**(from: Vector3, to: Vector3) -> Vector4

Builds the quaternion that rotates one vector onto another.
Parameters
- `from`: the source direction.
- `to`: the destination direction.
Returns
The rotation quaternion.
Example
```pengu
var q as raylib.Quaternion is calling quaternion_from_vector_to_vector with (calling Vector3.new with 1.0, 0.0, 0.0), (calling Vector3.new with 0.0, 1.0, 0.0)
```

