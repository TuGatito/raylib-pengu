# Plan: models.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/models.pengu`
- Owner in the master plan: family `models` of `docs/plans/raylibx.md` (v0.1.2)
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: the models section holds **52** C functions, all exported by the installed library. **37 are wrapped** (19 methods and 18 module functions), **11 are skipped** (§9 row 11, the mesh generators) and **3 are reassigned** (the billboards, D12). | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`; a script asserts that all 52 land in exactly one bucket. This time the ratio is **1:1**: no single C function fans out into several wrappers, unlike `shaders` and `images`. |
| D2 | The surface is split by subject: **`raylib.Mesh`** takes the mesh operations (`upload`, `update_buffer`, `draw`, `draw_instanced`, `bounding_box`, `generate_tangents`, `export`, `export_as_code`), **`raylib.Material`** takes `set_texture`, **`raylib.Model`** takes the model operations, and the constructors, destructors and free functions stay module-level. | Contract §6.1, the same rule as every other family: the receiver decides. Note that the receiver form follows the C signature exactly — `ref to Mesh` methods take `self` while by-value ones need `(essence of self)` — which is the detail that broke the first build of this family. |
| D3 | **`LoadModelFromMesh` does not validate, so it returns a plain `raylib.Model`, not a `maybe`.** | Measured: a **zeroed mesh** produces a model that reports `IsModelValid() == true`. There is no sentinel to fold, so a `maybe` would be a lie in the one case it mattered. The docstring says so and points the caller at the generators or `load_model` for meshes that are known good. |
| D4 | **`load_animations` returns a *view* (`slice of raylib.ModelAnimation`) and `unload_animations` is its matching release.** | `LoadModelAnimations` returns one array that raylib owns, and `UnloadModelAnimations` frees each keyframe's poses, each bone array **and then the array itself**. Copying the structs into a `list` would make the release free a foreign pointer — heap corruption. `ffi.slice_from_ptr of raylib.ModelAnimation` produces a view instead, so the release receives the original pointer. This is the contract's view-lifetime case, and both halves document the pairing. |
| D5 | `load_animations` returns `maybe`, because the array pointer **is** a sentinel: measured, a missing file yields a null pointer with a count of `0`. | Unlike D3, here the failure is detectable, so the wrapper folds it. |
| D6 | `LoadMaterials` is **skipped**, and it is the only skip in the section that is not a generator. | raylib gives that array no release: the elements' maps are freed by `UnloadMaterial` while the array itself needs `MemFree`. A wrapper would have to ship a **composite release with no C backing** — the only such entry in the whole module — for an MTL path that `load_model` already handles internally. Contract §9 criterion 1 also fails: the binding call is not shortened. Recorded rather than invented. |
| D7 | The 11 mesh generators (`GenMeshPoly`, `GenMeshPlane`, `GenMeshCube`, `GenMeshSphere`, `GenMeshHemiSphere`, `GenMeshCylinder`, `GenMeshCone`, `GenMeshTorus`, `GenMeshKnot`, `GenMeshHeightmap`, `GenMeshCubicmap`) are **not wrapped**. | Contract §9 row 11 names them: "Geometría de mallas generada … ya devuelven un valor puro; a lo sumo un `ritual from_*` en el tipo, nunca un método con otro nombre". Criterion 1 fails too — `raylib.GenMeshCube with 1.0, 1.0, 1.0` is already a clear call — so even the optional `ritual` form is not worth its surface. The tests call them through the binding. |
| D8 | The **eight collision functions are renamed with a Pengunic verb** and stay module-level: `spheres_collide`, `boxes_collide`, `box_sphere_collide`, `ray_sphere_hit`, `ray_box_hit`, `ray_mesh_hit`, `ray_triangle_hit`, `ray_quad_hit`. | Contract §9 criterion 2's second branch: they rename a `Check*`/`Get*` with a Pengunic verb, which is what earns a module-level wrapper its place when there is no receiver. The collision tests are also the family's best CI surface (D10), because they are pure arithmetic with exact, measured answers. |
| D9 | `update_animation` takes `frame as f32`, not `int`. | The binding's signature says `f32`, which is not what a reader expects from a "frame". Rather than hiding it, the docstring states it and explains the consequence: interpolation between keyframes is the caller's choice. |
| D10 | **The measurements drive the tests**: the collision functions and the bounding boxes are asserted against exact values measured in C, and no test needs a window for the arithmetic. But **anything that owns GPU memory needs a window — including `unload_mesh`**. | Measured: `GetMeshBoundingBox(GenMeshCube(2, 4, 6))` is `(-1, -2, -3)` to `(1, 2, 3)` with 24 vertices and 12 triangles; a unit ray at the origin along `+x` hits a unit sphere at `(5, 0, 0)` at distance `4.0` and point `(4, 0, 0)`, a box spanning `x ∈ [4, 6]` at `4.0`, a triangle and a quad in the plane `x = 5` at `5.0`, and a cube mesh at all. The first build of the suite **segfaulted** because a bounding-box test released its mesh without a context, which is why D10 is a decision and not a footnote. |
| D11 | `is_animation_valid` is validated by bone count, and the docstring records the measured edge: a zeroed animation against a **boneless** model reports `true`, because `0 == 0`. | Measured. It is a footgun that reads as a guard, so the documentation carries it. |
| D12 | The three billboards (`DrawBillboard`, `DrawBillboardRec`, `DrawBillboardPro`) are **reassigned to the camera family**, not wrapped here. | Their first parameter is the camera, so the natural receiver is the camera (`camera.draw_billboard with texture, position, scale, tint`), and the camera types are owned by `rcamerax`. Same reasoning as the projection helpers of `raylibx_shaders` D13, and the same open addendum. |
| D13 | `unload_material` is wrapped but `load_materials` is not (D6), and the docstring states that it does **not** free the struct or raylib's default shader and textures. | The release that exists is worth exposing for a material the caller built; the release that does not exist is worth naming, which is what D6 is for. |

### ✨ Enchantings

#### `enchanting raylib.Mesh` — 8 methods

| Method | Signature |
|---|---|
| `upload` | `with dynamic as bool into void` |
| `update_buffer` | `with index as int, data as slice of byte, offset as int into void` |
| `draw` | `with material as raylib.Material, transform as raylib.Matrix into void` |
| `draw_instanced` | `with material as raylib.Material, transforms as slice of raylib.Matrix into void` |
| `bounding_box` | `into raylib.BoundingBox` |
| `generate_tangents` | `into void` |
| `export` | `with path as string into bool` |
| `export_as_code` | `with path as string into bool` |

#### `enchanting raylib.Material` — 1 method

| Method | Signature |
|---|---|
| `set_texture` | `with map_type as raylib.MaterialMapIndex, texture as raylib.Texture2D into void` |

#### `enchanting raylib.Model` — 10 methods

| Method | Signature |
|---|---|
| `is_valid` | `into bool` |
| `bounding_box` | `into raylib.BoundingBox` |
| `draw` | `with position as raylib.Vector3, scale as f32, tint as raylib.Color into void` |
| `draw_ex` | `with position as raylib.Vector3, rotation_axis as raylib.Vector3, rotation_angle as f32, scale as raylib.Vector3, tint as raylib.Color into void` |
| `draw_wires` | `with position as raylib.Vector3, scale as f32, tint as raylib.Color into void` |
| `draw_wires_ex` | `with position as raylib.Vector3, rotation_axis as raylib.Vector3, rotation_angle as f32, scale as raylib.Vector3, tint as raylib.Color into void` |
| `set_mesh_material` | `with mesh_id as int, material_id as int into void` |
| `update_animation` | `with animation as raylib.ModelAnimation, frame as f32 into void` |
| `update_animation_ex` | `with first as raylib.ModelAnimation, first_frame as f32, second as raylib.ModelAnimation, second_frame as f32, blend as f32 into void` |
| `is_animation_valid` | `with animation as raylib.ModelAnimation into bool` |

### 🔧 Module-level functions (18)

| Function | Signature |
|---|---|
| `load_model` | `with path as string into maybe raylib.Model` |
| `load_model_from_mesh` | `with mesh as raylib.Mesh into raylib.Model` |
| `unload_model` | `with model as raylib.Model into void` |
| `unload_mesh` | `with mesh as raylib.Mesh into void` |
| `load_material_default` | `into raylib.Material` |
| `is_material_valid` | `with material as raylib.Material into bool` |
| `unload_material` | `with material as raylib.Material into void` |
| `load_animations` | `with path as string into maybe (slice of raylib.ModelAnimation)` |
| `unload_animations` | `with animations as slice of raylib.ModelAnimation into void` |
| `draw_bounding_box` | `with box as raylib.BoundingBox, color as raylib.Color into void` |
| `spheres_collide` | `with center1 as raylib.Vector3, radius1 as f32, center2 as raylib.Vector3, radius2 as f32 into bool` |
| `boxes_collide` | `with box1 as raylib.BoundingBox, box2 as raylib.BoundingBox into bool` |
| `box_sphere_collide` | `with box as raylib.BoundingBox, center as raylib.Vector3, radius as f32 into bool` |
| `ray_sphere_hit` | `with ray as raylib.Ray, center as raylib.Vector3, radius as f32 into raylib.RayCollision` |
| `ray_box_hit` | `with ray as raylib.Ray, box as raylib.BoundingBox into raylib.RayCollision` |
| `ray_mesh_hit` | `with ray as raylib.Ray, mesh as raylib.Mesh, transform as raylib.Matrix into raylib.RayCollision` |
| `ray_triangle_hit` | `with ray as raylib.Ray, p1 as raylib.Vector3, p2 as raylib.Vector3, p3 as raylib.Vector3 into raylib.RayCollision` |
| `ray_quad_hit` | `with ray as raylib.Ray, p1 as raylib.Vector3, p2 as raylib.Vector3, p3 as raylib.Vector3, p4 as raylib.Vector3 into raylib.RayCollision` |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `load_model` | `maybe raylib.Model` | `IsModelValid` after the call (measured: a missing file is invalid) |
| `load_animations` | `maybe (slice of raylib.ModelAnimation)` | a null array pointer (measured) |

> Only two, and `load_model_from_mesh` is deliberately **not** one of them (D3).

### ✂️ `slice` wrappers

| Function | Slice parameter | Kind |
|---|---|---|
| `Mesh.update_buffer` | `data as slice of byte` | input; empty is a no-op |
| `Mesh.draw_instanced` | `transforms as slice of raylib.Matrix` | input; empty draws nothing |
| `unload_animations` | `animations as slice of raylib.ModelAnimation` | **view**; empty is a no-op |

The two input slices are routed through typed locals rather than a cast to a qualified type, which is the master plan's D20.

### 📦 Multiple returns `(T, U)`

**None apply.** `LoadModelAnimations` folds its `(pointer, count)` pair into the view's length (D4), and everything else returns one value.

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | `load_model`, `load_animations`, `Mesh.export`, `Mesh.export_as_code` |
| null check | `ffi.is_null` | `load_animations` |
| pointer → **view** | `ffi.slice_from_ptr of raylib.ModelAnimation` | `load_animations` |
| value → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | `update_buffer`, `draw_instanced`, `unload_animations` |

### 💡 Compilable examples

```pengu
# Example 1 — build a model from a generated mesh and draw it
import raylib
import raylibx.models as models

weave main into int:
    var mesh as raylib.Mesh is calling raylib.GenMeshCube with 2.0, 4.0, 6.0
    var model as raylib.Model is calling models.load_model_from_mesh with mesh
    defer calling models.unload_model with model
    var position as raylib.Vector3 is with x is 0.0, y is 0.0, z is 0.0
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    calling model.draw with position, 1.0, raylib.WHITE
    calling raylib.EndDrawing
    return 0
```

```pengu
# Example 2 — the collision surface, which needs no window
import raylib
import raylibx.models as models

weave main into int:
    var ray as raylib.Ray is with position is (with x is 0.0, y is 0.0, z is 0.0), direction is (with x is 1.0, y is 0.0, z is 0.0)
    var center as raylib.Vector3 is with x is 5.0, y is 0.0, z is 0.0
    var hit as raylib.RayCollision is calling models.ray_sphere_hit with ray, center, 1.0
    if hit.hit:
        var box as raylib.BoundingBox is with min is (with x is 4.0, y is -1.0, z is -1.0), max is (with x is 6.0, y is 1.0, z is 1.0)
        var also as bool is calling models.box_sphere_collide with box, center, 0.5
    return 0
```

```pengu
# Example 3 — a mesh that is uploaded, rewritten and exported
import raylib
import raylibx.models as models

weave main into int:
    var mesh as raylib.Mesh is calling raylib.GenMeshCube with 1.0, 1.0, 1.0
    defer calling models.unload_mesh with mesh
    calling mesh.upload with false
    var box as raylib.BoundingBox is calling mesh.bounding_box
    var ok as bool is calling mesh.export with "/tmp/cube.obj"
    return 0
```

### 🧪 Test plan

**Fourteen tests.** Eight of them are pure arithmetic with no window; the rest open one, because anything that owns GPU memory needs a context — a distinction the suite learned the hard way (D10).

- **The generated cube's numbers**: 24 vertices, 12 triangles, and a bounding box of `(-1, -2, -3)` to `(1, 2, 3)` for `GenMeshCube(2, 4, 6)`.
- **`spheres_collide`, `boxes_collide`, `box_sphere_collide`**: true when they overlap or contain, false when apart, with the exact geometries measured in C.
- **The four ray tests with exact distances**: sphere `4.0` (and the hit point `(4, 0, 0)`), box `4.0`, triangle `5.0`, quad `5.0`, plus `ray_mesh_hit` against a cube.
- **A model built from a mesh**: valid, one mesh, and the model box matching the mesh box.
- **Both failure paths**: `load_model` and `load_animations` are `maybe none` for a missing file; `unload_animations` on an empty slice is a no-op.
- **`upload` and `update_buffer`** on a real mesh, including the empty-slice no-op.
- **`export` and `export_as_code`** write files to unique temporary paths that `defer` removes, asserted with `FileExists`.
- **Every draw entry point** is called inside one frame with a real model and a real material: `draw`, `draw_ex`, `draw_wires`, `draw_wires_ex`, `DrawMesh`, `draw_instanced` (twice, once with an empty slice) and `draw_bounding_box`.
- **A material**: `load_material_default` is valid, `set_texture` accepts a real texture, `unload_material` is callable.

**Not asserted:** the animation loader's success path, because **no animated model file exists in this repository**; only its failure path is covered. The draw calls are asserted as callable, not as pixels, because this environment cannot read the framebuffer back (`raylibx_shaders` D9).

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `GenMeshPoly`, `GenMeshPlane`, `GenMeshCube`, `GenMeshSphere`, `GenMeshHemiSphere`, `GenMeshCylinder`, `GenMeshCone`, `GenMeshTorus`, `GenMeshKnot`, `GenMeshHeightmap`, `GenMeshCubicmap` | contract §9 row 11: generated mesh geometry already returns a pure value; at most a `ritual from_*`, and criterion 1 fails (D7) |
| `LoadMaterials` | raylib gives its array no release: the maps need `UnloadMaterial` and the array needs `MemFree`, so a wrapper would ship a composite release with no C backing (D6) |

| Out of scope | Reason |
|---|---|
| `DrawBillboard`, `DrawBillboardRec`, `DrawBillboardPro` | **reassigned to `rcamerax`**: the camera is the first parameter and therefore the receiver (D12) |
| `UnloadModelKeepMeshes` | not present in this raylib version: absent from the header, the binding and the installed library (checked) |
| The 3D shape primitives of this module banner (`DrawCube`, `DrawSphere`, …) | already wrapped by `raylibx_shapes3d` |

Coverage audit: **52 C functions, 37 wrapped, 11 skipped, 3 reassigned, no leftovers and no duplicates.** The method registry gains the 19 `Mesh`/`Material`/`Model` names; `ModelAnimation` gains **no methods**, because every animation operation takes the model as its subject.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/models.pengu`
- Dueña en el plan maestro: familia `models` de `docs/plans/raylibx.md` (v0.1.2)
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: la sección de modelos tiene **52** funciones C, todas exportadas por la biblioteca instalada. **37 se envuelven** (19 métodos y 18 funciones de módulo), **11 se omiten** (§9 fila 11, los generadores de mallas) y **3 se reasignan** (los billboards, D12). | Enumerado desde el binding y cruzado con `tools/check_binding_symbols.py`; un script comprueba que las 52 caen exactamente en un grupo. Esta vez la proporción es **1:1**: ninguna función C se despliega en varios wrappers, a diferencia de `shaders` e `images`. |
| D2 | La superficie se reparte por sujeto: **`raylib.Mesh`** se lleva las operaciones de malla (`upload`, `update_buffer`, `draw`, `draw_instanced`, `bounding_box`, `generate_tangents`, `export`, `export_as_code`), **`raylib.Material`** se lleva `set_texture`, **`raylib.Model`** se lleva las operaciones de modelo, y los constructores, destructores y funciones libres se quedan de módulo. | Contrato §6.1, la misma regla que en todas las familias: decide el receptor. Nótese que la forma del receptor sigue exactamente la firma C — los métodos con `ref to Mesh` reciben `self` y los de por valor necesitan `(essence of self)` —, que es el detalle que rompió la primera construcción de esta familia. |
| D3 | **`LoadModelFromMesh` no valida, así que devuelve un `raylib.Model` simple, no un `maybe`.** | Medido: una **malla a ceros** produce un modelo que informa `IsModelValid() == true`. No hay centinela que plegar, así que un `maybe` sería una mentira justo en el caso que importaba. El docstring lo dice y remite al llamador a los generadores o a `load_model` para mallas que se sabe que son buenas. |
| D4 | **`load_animations` devuelve una *vista* (`slice of raylib.ModelAnimation`) y `unload_animations` es su liberación correspondiente.** | `LoadModelAnimations` devuelve un array que posee raylib, y `UnloadModelAnimations` libera las poses de cada fotograma clave, cada array de huesos **y después el array mismo**. Copiar los structs a una `list` haría que la liberación liberase un puntero ajeno: corrupción del montón. `ffi.slice_from_ptr of raylib.ModelAnimation` produce una vista, de modo que la liberación recibe el puntero original. Es el caso de tiempo de vida de vista del contrato, y ambas mitades documentan el emparejamiento. |
| D5 | `load_animations` devuelve `maybe`, porque el puntero del array **sí** es un centinela: medido, un fichero ausente da puntero nulo con recuento `0`. | A diferencia del D3, aquí el fallo es detectable, así que el wrapper lo pliega. |
| D6 | `LoadMaterials` se **omite**, y es la única omisión de la sección que no es un generador. | raylib no le da liberación a ese array: los mapas de los elementos los libera `UnloadMaterial` mientras que el array necesita `MemFree`. Un wrapper tendría que enviar una **liberación compuesta sin respaldo en C** — la única entrada así en todo el módulo — para una ruta de MTL que `load_model` ya cubre internamente. El criterio 1 del contrato §9 también falla: la llamada al binding no se acorta. Se registra en vez de inventarse. |
| D7 | Los 11 generadores de mallas (`GenMeshPoly`, `GenMeshPlane`, `GenMeshCube`, `GenMeshSphere`, `GenMeshHemiSphere`, `GenMeshCylinder`, `GenMeshCone`, `GenMeshTorus`, `GenMeshKnot`, `GenMeshHeightmap`, `GenMeshCubicmap`) **no se envuelven**. | El contrato §9 fila 11 los nombra: "Geometría de mallas generada … ya devuelven un valor puro; a lo sumo un `ritual from_*` en el tipo, nunca un método con otro nombre". El criterio 1 también falla — `raylib.GenMeshCube with 1.0, 1.0, 1.0` ya es una llamada clara —, así que ni siquiera la forma opcional de `ritual` merece su superficie. Los tests los llaman desde el binding. |
| D8 | Las **ocho funciones de colisión se renombran con un verbo Pengunic** y se quedan de módulo: `spheres_collide`, `boxes_collide`, `box_sphere_collide`, `ray_sphere_hit`, `ray_box_hit`, `ray_mesh_hit`, `ray_triangle_hit`, `ray_quad_hit`. | La segunda rama del criterio 2 del contrato §9: renombran un `Check*`/`Get*` con un verbo Pengunic, que es lo que gana el sitio de un wrapper de módulo cuando no hay receptor. Los tests de colisión son además la mejor superficie de CI de la familia (D10), porque son aritmética pura con respuestas exactas y medidas. |
| D9 | `update_animation` recibe `frame as f32`, no `int`. | La firma del binding dice `f32`, que no es lo que un lector espera de un "fotograma". En vez de esconderlo, el docstring lo declara y explica la consecuencia: la interpolación entre fotogramas clave es decisión del llamador. |
| D10 | **Las mediciones mandan en los tests**: las funciones de colisión y las cajas envolventes se aseguran contra valores exactos medidos en C, y ningún test necesita ventana para la aritmética. Pero **todo lo que posee memoria de GPU necesita ventana — incluido `unload_mesh`**. | Medido: `GetMeshBoundingBox(GenMeshCube(2, 4, 6))` es `(-1, -2, -3)` a `(1, 2, 3)` con 24 vértices y 12 triángulos; un rayo unitario en el origen según `+x` acierta a una esfera unitaria en `(5, 0, 0)` a distancia `4.0` y punto `(4, 0, 0)`, a una caja que abarca `x ∈ [4, 6]` a `4.0`, a un triángulo y a un quad en el plano `x = 5` a `5.0`, y a una malla de cubo. La primera construcción de la suite **reventó** porque un test de caja envolvente liberaba su malla sin contexto, y por eso el D10 es una decisión y no una nota al pie. |
| D11 | `is_animation_valid` valida por número de huesos, y el docstring registra el borde medido: una animación a ceros contra un modelo **sin esqueleto** informa `true`, porque `0 == 0`. | Medido. Es una trampa que se lee como guarda, así que la documentación la carga. |
| D12 | Los tres billboards (`DrawBillboard`, `DrawBillboardRec`, `DrawBillboardPro`) se **reasignan a la familia de cámara**, no se envuelven aquí. | Su primer parámetro es la cámara, así que el receptor natural es la cámara (`camera.draw_billboard with texture, position, scale, tint`), y los tipos de cámara los posee `rcamerax`. El mismo razonamiento que los helpers de proyección del D13 de `raylibx_shaders`, y el mismo apéndice abierto. |
| D13 | `unload_material` se envuelve pero `load_materials` no (D6), y el docstring declara que **no** libera el struct ni el shader y las texturas por defecto de raylib. | La liberación que existe merece exponerse para un material construido por el llamador; la liberación que no existe merece nombrarse, y para eso está el D6. |

### ✨ Enchantings

#### `enchanting raylib.Mesh` — 8 métodos

| Método | Firma |
|---|---|
| `upload` | `with dynamic as bool into void` |
| `update_buffer` | `with index as int, data as slice of byte, offset as int into void` |
| `draw` | `with material as raylib.Material, transform as raylib.Matrix into void` |
| `draw_instanced` | `with material as raylib.Material, transforms as slice of raylib.Matrix into void` |
| `bounding_box` | `into raylib.BoundingBox` |
| `generate_tangents` | `into void` |
| `export` | `with path as string into bool` |
| `export_as_code` | `with path as string into bool` |

#### `enchanting raylib.Material` — 1 método

| Método | Firma |
|---|---|
| `set_texture` | `with map_type as raylib.MaterialMapIndex, texture as raylib.Texture2D into void` |

#### `enchanting raylib.Model` — 10 métodos

| Método | Firma |
|---|---|
| `is_valid` | `into bool` |
| `bounding_box` | `into raylib.BoundingBox` |
| `draw` | `with position as raylib.Vector3, scale as f32, tint as raylib.Color into void` |
| `draw_ex` | `with position as raylib.Vector3, rotation_axis as raylib.Vector3, rotation_angle as f32, scale as raylib.Vector3, tint as raylib.Color into void` |
| `draw_wires` | `with position as raylib.Vector3, scale as f32, tint as raylib.Color into void` |
| `draw_wires_ex` | `with position as raylib.Vector3, rotation_axis as raylib.Vector3, rotation_angle as f32, scale as raylib.Vector3, tint as raylib.Color into void` |
| `set_mesh_material` | `with mesh_id as int, material_id as int into void` |
| `update_animation` | `with animation as raylib.ModelAnimation, frame as f32 into void` |
| `update_animation_ex` | `with first as raylib.ModelAnimation, first_frame as f32, second as raylib.ModelAnimation, second_frame as f32, blend as f32 into void` |
| `is_animation_valid` | `with animation as raylib.ModelAnimation into bool` |

### 🔧 Funciones a nivel de módulo (18)

| Función | Firma |
|---|---|
| `load_model` | `with path as string into maybe raylib.Model` |
| `load_model_from_mesh` | `with mesh as raylib.Mesh into raylib.Model` |
| `unload_model` | `with model as raylib.Model into void` |
| `unload_mesh` | `with mesh as raylib.Mesh into void` |
| `load_material_default` | `into raylib.Material` |
| `is_material_valid` | `with material as raylib.Material into bool` |
| `unload_material` | `with material as raylib.Material into void` |
| `load_animations` | `with path as string into maybe (slice of raylib.ModelAnimation)` |
| `unload_animations` | `with animations as slice of raylib.ModelAnimation into void` |
| `draw_bounding_box` | `with box as raylib.BoundingBox, color as raylib.Color into void` |
| `spheres_collide` | `with center1 as raylib.Vector3, radius1 as f32, center2 as raylib.Vector3, radius2 as f32 into bool` |
| `boxes_collide` | `with box1 as raylib.BoundingBox, box2 as raylib.BoundingBox into bool` |
| `box_sphere_collide` | `with box as raylib.BoundingBox, center as raylib.Vector3, radius as f32 into bool` |
| `ray_sphere_hit` | `with ray as raylib.Ray, center as raylib.Vector3, radius as f32 into raylib.RayCollision` |
| `ray_box_hit` | `with ray as raylib.Ray, box as raylib.BoundingBox into raylib.RayCollision` |
| `ray_mesh_hit` | `with ray as raylib.Ray, mesh as raylib.Mesh, transform as raylib.Matrix into raylib.RayCollision` |
| `ray_triangle_hit` | `with ray as raylib.Ray, p1 as raylib.Vector3, p2 as raylib.Vector3, p3 as raylib.Vector3 into raylib.RayCollision` |
| `ray_quad_hit` | `with ray as raylib.Ray, p1 as raylib.Vector3, p2 as raylib.Vector3, p3 as raylib.Vector3, p4 as raylib.Vector3 into raylib.RayCollision` |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `load_model` | `maybe raylib.Model` | `IsModelValid` tras la llamada (medido: un fichero ausente es inválido) |
| `load_animations` | `maybe (slice of raylib.ModelAnimation)` | puntero de array nulo (medido) |

> Solo dos, y `load_model_from_mesh` deliberadamente **no** es una de ellas (D3).

### ✂️ Wrappers de `slice`

| Función | Parámetro slice | Tipo |
|---|---|---|
| `Mesh.update_buffer` | `data as slice of byte` | entrada; vacío es no-op |
| `Mesh.draw_instanced` | `transforms as slice of raylib.Matrix` | entrada; vacío no dibuja nada |
| `unload_animations` | `animations as slice of raylib.ModelAnimation` | **vista**; vacío es no-op |

Los dos slices de entrada pasan por locales tipados en vez de por un cast a un tipo cualificado, que es el D20 del plan maestro.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** `LoadModelAnimations` pliega su par `(puntero, recuento)` en la longitud de la vista (D4), y todo lo demás devuelve un solo valor.

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | `load_model`, `load_animations`, `Mesh.export`, `Mesh.export_as_code` |
| comprobación de nulo | `ffi.is_null` | `load_animations` |
| puntero → **vista** | `ffi.slice_from_ptr of raylib.ModelAnimation` | `load_animations` |
| valor → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | `update_buffer`, `draw_instanced`, `unload_animations` |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — construir un modelo desde una malla generada y dibujarlo
import raylib
import raylibx.models as models

weave main into int:
    var mesh as raylib.Mesh is calling raylib.GenMeshCube with 2.0, 4.0, 6.0
    var model as raylib.Model is calling models.load_model_from_mesh with mesh
    defer calling models.unload_model with model
    var position as raylib.Vector3 is with x is 0.0, y is 0.0, z is 0.0
    calling raylib.BeginDrawing
    calling raylib.ClearBackground with raylib.RAYWHITE
    calling model.draw with position, 1.0, raylib.WHITE
    calling raylib.EndDrawing
    return 0
```

```pengu
# Ejemplo 2 — la superficie de colisión, que no necesita ventana
import raylib
import raylibx.models as models

weave main into int:
    var ray as raylib.Ray is with position is (with x is 0.0, y is 0.0, z is 0.0), direction is (with x is 1.0, y is 0.0, z is 0.0)
    var center as raylib.Vector3 is with x is 5.0, y is 0.0, z is 0.0
    var hit as raylib.RayCollision is calling models.ray_sphere_hit with ray, center, 1.0
    if hit.hit:
        var box as raylib.BoundingBox is with min is (with x is 4.0, y is -1.0, z is -1.0), max is (with x is 6.0, y is 1.0, z is 1.0)
        var also as bool is calling models.box_sphere_collide with box, center, 0.5
    return 0
```

```pengu
# Ejemplo 3 — una malla que se sube, se reescribe y se exporta
import raylib
import raylibx.models as models

weave main into int:
    var mesh as raylib.Mesh is calling raylib.GenMeshCube with 1.0, 1.0, 1.0
    defer calling models.unload_mesh with mesh
    calling mesh.upload with false
    var box as raylib.BoundingBox is calling mesh.bounding_box
    var ok as bool is calling mesh.export with "/tmp/cube.obj"
    return 0
```

### 🧪 Plan de tests

**Catorce tests.** Ocho son aritmética pura sin ventana; el resto abren una, porque todo lo que posee memoria de GPU necesita contexto: una distinción que la suite aprendió a golpes (D10).

- **Los números del cubo generado**: 24 vértices, 12 triángulos y una caja envolvente de `(-1, -2, -3)` a `(1, 2, 3)` para `GenMeshCube(2, 4, 6)`.
- **`spheres_collide`, `boxes_collide`, `box_sphere_collide`**: verdadero cuando se solapan o se contienen, falso cuando están separados, con las geometrías exactas medidas en C.
- **Los cuatro tests de rayo con distancias exactas**: esfera `4.0` (y el punto de impacto `(4, 0, 0)`), caja `4.0`, triángulo `5.0`, quad `5.0`, más `ray_mesh_hit` contra un cubo.
- **Un modelo construido desde una malla**: válido, con una malla, y la caja del modelo coincidiendo con la de la malla.
- **Las dos rutas de fallo**: `load_model` y `load_animations` son `maybe none` para un fichero ausente; `unload_animations` sobre un slice vacío es un no-op.
- **`upload` y `update_buffer`** sobre una malla real, incluido el no-op de slice vacío.
- **`export` y `export_as_code`** escriben ficheros en rutas temporales únicas que `defer` borra, aseguradas con `FileExists`.
- **Todas las entradas de dibujo** se llaman dentro de un fotograma con un modelo y un material reales: `draw`, `draw_ex`, `draw_wires`, `draw_wires_ex`, `DrawMesh`, `draw_instanced` (dos veces, una con slice vacío) y `draw_bounding_box`.
- **Un material**: `load_material_default` es válido, `set_texture` acepta una textura real y `unload_material` se puede llamar.

**No se asegura:** la ruta de éxito del cargador de animaciones, porque **no existe ningún fichero de modelo animado en este repositorio**; solo se cubre su ruta de fallo. Las llamadas de dibujo se aseguran como invocables, no como píxeles, porque este entorno no puede releer el framebuffer (D9 de `raylibx_shaders`).

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `GenMeshPoly`, `GenMeshPlane`, `GenMeshCube`, `GenMeshSphere`, `GenMeshHemiSphere`, `GenMeshCylinder`, `GenMeshCone`, `GenMeshTorus`, `GenMeshKnot`, `GenMeshHeightmap`, `GenMeshCubicmap` | contrato §9 fila 11: la geometría de malla generada ya devuelve un valor puro; a lo sumo un `ritual from_*`, y el criterio 1 falla (D7) |
| `LoadMaterials` | raylib no da liberación a su array: los mapas necesitan `UnloadMaterial` y el array necesita `MemFree`, así que un wrapper enviaría una liberación compuesta sin respaldo en C (D6) |

| Fuera de alcance | Motivo |
|---|---|
| `DrawBillboard`, `DrawBillboardRec`, `DrawBillboardPro` | **reasignadas a `rcamerax`**: la cámara es el primer parámetro y por tanto el receptor (D12) |
| `UnloadModelKeepMeshes` | no existe en esta versión de raylib: ausente del header, del binding y de la biblioteca instalada (comprobado) |
| Las primitivas de formas 3D de este banner del módulo (`DrawCube`, `DrawSphere`, …) | ya las envuelve `raylibx_shapes3d` |

Auditoría de cobertura: **52 funciones C, 37 envueltas, 11 omitidas, 3 reasignadas, sin restos y sin duplicados.** El registro de métodos gana los 19 nombres de `Mesh`/`Material`/`Model`; `ModelAnimation` **no gana métodos**, porque toda operación de animación tiene el modelo como sujeto.
