> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# models

> Source: `pengu/raylibx/models.pengu`

Layer-2 wrapper over the 37 model functions of the `raylib` binding, out of the 52 in the
3D-models section: 11 mesh generators are excluded by the contract's skip table and 3
billboards are reassigned to the camera family.

The family spans four types, and each entry goes where its subject is:

    calling raylib.GenMeshCube with 1.0, 1.0, 1.0        # a generator: not wrapped
    calling raylibx_models.load_model with "ship.glb"    # a loader: module level
    calling model.draw_ex with pos, axis, 45.0, scale, raylib.WHITE

## Two things here are subtle, and both were measured
**`LoadModelFromMesh` does not validate.** A zeroed mesh produces a model that reports
`is_valid` as `true`, so that loader cannot fail loudly and does not return a `maybe`.

**`LoadModelAnimations` returns a view, not a copy.** Its array and every keyframe inside
it are one allocation raylib owns, and `UnloadModelAnimations` frees the keyframes and then
the array. Copying the structs into a list would make `unload_animations` free a foreign
pointer, so `load_animations` returns `slice of raylib.ModelAnimation` — a view whose
lifetime is the pair `load_animations` / `unload_animations`.

This is family `models` of `raylibx`; see `docs/wrappers/raylibx-models.md`.

## What is testable, and what is not
The **eight collision functions and the bounding boxes are pure CPU arithmetic**, so they
are asserted against exact measured values without a window. Mesh generation, model
loading, mesh export and the draw calls are asserted against a live window, and the
animation loader's success path is **not** asserted because no animated model file is
available in this repository; only its failure path is.

## Memory
Models own their meshes (`unload_model`), generated meshes are released with `unload_mesh`,
and the two `slice` returns are **views** into raylib's own arrays with their releases
documented on each.

## Example
```pengu
import raylib
import raylibx_models

weave main into int:
    var mesh as raylib.Mesh is calling raylib.GenMeshCube with 1.0, 1.0, 1.0
    var model as raylib.Model is calling raylibx_models.load_model_from_mesh with mesh
    defer calling raylibx_models.unload_model with model
    var box as raylib.BoundingBox is calling model.bounding_box
    return 0
```

---

### `load_model`

> **load_model**(path: string) -> maybe Model

_Undocumented function._


### `load_model_from_mesh`

> **load_model_from_mesh**(mesh: Mesh) -> Model

_Undocumented function._


### `unload_model`

> **unload_model**(model: Model) -> void

_Undocumented function._


### `unload_mesh`

> **unload_mesh**(mesh: Mesh) -> void

_Undocumented function._


### `load_material_default`

> **load_material_default**() -> Material

_Undocumented function._


### `is_material_valid`

> **is_material_valid**(material: Material) -> bool

_Undocumented function._


### `unload_material`

> **unload_material**(material: Material) -> void

_Undocumented function._


### `load_animations`

> **load_animations**(path: string) -> maybe slice of ModelAnimation

_Undocumented function._


### `unload_animations`

> **unload_animations**(animations: slice of ModelAnimation) -> void

_Undocumented function._


### `draw_bounding_box`

> **draw_bounding_box**(box: BoundingBox, color: Color) -> void

_Undocumented function._


### `spheres_collide`

> **spheres_collide**(center1: Vector3, radius1: f32, center2: Vector3, radius2: f32) -> bool

_Undocumented function._


### `boxes_collide`

> **boxes_collide**(box1: BoundingBox, box2: BoundingBox) -> bool

_Undocumented function._


### `box_sphere_collide`

> **box_sphere_collide**(box: BoundingBox, center: Vector3, radius: f32) -> bool

_Undocumented function._


### `ray_sphere_hit`

> **ray_sphere_hit**(ray: Ray, center: Vector3, radius: f32) -> RayCollision

_Undocumented function._


### `ray_box_hit`

> **ray_box_hit**(ray: Ray, box: BoundingBox) -> RayCollision

_Undocumented function._


### `ray_mesh_hit`

> **ray_mesh_hit**(ray: Ray, mesh: Mesh, transform: Matrix) -> RayCollision

_Undocumented function._


### `ray_triangle_hit`

> **ray_triangle_hit**(ray: Ray, p1: Vector3, p2: Vector3, p3: Vector3) -> RayCollision

_Undocumented function._


### `ray_quad_hit`

> **ray_quad_hit**(ray: Ray, p1: Vector3, p2: Vector3, p3: Vector3, p4: Vector3) -> RayCollision

_Undocumented function._


### `unit_ray`

> **unit_ray**() -> Ray

_Undocumented function._


### `identity`

> **identity**() -> Matrix

_Undocumented function._

