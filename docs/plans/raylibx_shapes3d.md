# Plan: shapes3d.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/shapes3d.pengu`
- Owner in the master plan: family `shapes3d` of `docs/plans/raylibx.md` (v0.1.2), seventh in its order of implementation (brought forward)
- Dependencies: `import raylib`, `import std.ffi` (the one slice-shaped draw)
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete and all 21 exported**. The header's "Basic 3d Shapes Drawing Functions" section holds exactly 21 functions, no more and no fewer, and `python3 tools/check_binding_symbols.py` reports every one of them as exported by the installed `libraylib.so` 6.0.0. **Nothing is skipped in this family** — it is the first family with no 6.1-only functions (master plan D17). | Enumerated from the header section itself rather than from a name pattern, and cross-checked against the dynamic symbols. This is the check that the `shapes` family lacked (master plan D17). |
| D2 | The master plan's D9 subjecthood rule is extended to 3D with the same mechanical test: **the `V` in raylib's own name marks the functions whose first argument is the anchor**, so `DrawCubeV` and `DrawCubeWiresV` become methods on `raylib.Vector3`. | Master plan D9. The extension is stated explicitly because `DrawCube` is the trap: its first argument is a `Vector3 position` even though the name has no `V`, so the naive "first argument is a Vector3" test would wrongly make it a method. The `V` is the test, and the family plan records why. |
| D3 | **Exactly four** functions become methods on `Vector3`: `draw_cube` (`DrawCubeV`), `draw_cube_wires` (`DrawCubeWiresV`), `draw_plane` (`DrawPlane`) and `draw_point` (`DrawPoint3D`). The `_v` suffix is dropped for readability, so `pos.draw_cube with extent, color` reads as "at `pos`, draw a cube of `extent`". | The mechanical test of D2 applied to the real names: raylib's 6.x cylinder and sphere families have **no `V` variant** (there is no `DrawCylinderV`), and `DrawPoint3D`/`DrawPlane` are the two non-`V` names whose first argument is the subject. Everything else with a `Vector3` centre keeps the binding name and stays a module function (D4). |
| D4 | The other thirteen functions stay module-level with the binding's exact names: `draw_line_3d`, `draw_circle_3d`, `draw_triangle_3d`, `draw_triangle_strip_3d`, `draw_cube`, `draw_cube_wires`, `draw_sphere`, `draw_sphere_ex`, `draw_sphere_wires`, `draw_cylinder`, `draw_cylinder_ex`, `draw_cylinder_wires`, `draw_capsule`, `draw_capsule_wires`, `draw_ray`, `draw_grid`. | The master plan's D9 rule: names without a `V` are not methods. `DrawSphere` and `DrawSphereEx` take `centerPos as Vector3` too, but the name does not mark it, and renaming them into methods would silently change the C function the caller gets. |
| D5 | The three `Ex` variants that take two anchors (`DrawCylinderEx`, `DrawCylinderWiresEx`, `DrawCapsule`, `DrawCapsuleWires`) stay module-level even though their first argument is a `Vector3`. | Contract §6.1: with two equally good subjects (`startPos` **and** `endPos`) there is no natural receiver. A method would force the caller to remember which end became the receiver. |
| D6 | `DrawGrid(slices, spacing)` is wrapped as `draw_grid`, module-level. | Its arguments are neither a vector nor a colour, so it has no subject at all. It is also the only function in the family that takes no colour. |
| D7 | `DrawRay(ray as Ray, color as Color)` is wrapped as `draw_ray` taking a `raylib.Ray`, module-level. | `Ray` is a two-`Vector3` `rune` whose *first field* is the origin, so a method on `Ray` would be defensible — but `Ray` has no other wrapper methods anywhere in `raylibx` and the master plan's registry has no row for it, so introducing a one-method type would be a registry decision, not a family one. Recorded as a deliberate non-decision; the master plan's registry is the place to revisit it. |
| D8 | One slice-shaped function: `draw_triangle_strip_3d` takes `slice of raylib.Vector3` with the empty-slice guard, and the pointer conversion goes through `void*`. | Contract §5 for the slice, and master plan/D13 of `shapes` for the `void*` route: the typed `ref to frozen raylib.Vector3` form makes `pengu 2.4.0` emit `const raylib.Vector3*` into the C, which does not compile. |
| D9 | No `maybe` and no `std.ffi` string use. | Nothing in the family can fail, return a resource or take a path. The only FFI boundary is the one slice. |
| D10 | Models and meshes are **not** here. | `DrawModel`, `DrawMesh`, `DrawBoundingBox` and the `GenMesh*` constructors live in the `models` family (master plan D6). This family is only the primitive shapes. |

### ✨ Enchantings

No `@mutates`: a drawing call returns nothing and the receiver is read, not modified, so the compiler generates no `get_*` form. None of these names collides with `raymathx`, which owns the `Vector3` arithmetic, or with `raylibx_shapes`, which owns the 2D `Vector2`/`Rectangle` methods. The master plan's registry is extended with the eight names below.

#### `enchanting raylib.Vector3` — 4 methods

| Method | Signature | C backing | Notes |
|---|---|---|---|
| `draw_point` | `with color as raylib.Color into void` | `DrawPoint3D` | sets a single 3D point |
| `draw_cube` | `with extent as raylib.Vector3, color as raylib.Color into void` | `DrawCubeV` | this point is the **centre** |
| `draw_cube_wires` | `with extent as raylib.Vector3, color as raylib.Color into void` | `DrawCubeWiresV` | this point is the **centre** |
| `draw_plane` | `with extent as raylib.Vector2, color as raylib.Color into void` | `DrawPlane` | this point is the **centre**; `extent` is in `Vector2` world units |

> **Why the sphere and cylinder are not methods.** `DrawSphere`, `DrawSphereEx`, `DrawSphereWires`, `DrawCylinder`, `DrawCylinderWires` and `DrawCylinderEx` all take a `Vector3` centre or start point, so a method would be intuitive — but none of their names carries the `V` that D2 makes the test, and raylib 6.x has no `DrawSphereV`/`DrawCylinderV` to key on. Making them methods would also mean inventing names (`sphere`, `cylinder`) that no longer say which C function runs. They stay module-level with their binding names, and the caller writes `draw_sphere with center, radius, color`.

### 🔧 Module-level functions

| Function | Signature | C backing |
|---|---|---|
| `draw_line_3d` | `with start as raylib.Vector3, end as raylib.Vector3, color as raylib.Color into void` | `DrawLine3D` |
| `draw_circle_3d` | `with center as raylib.Vector3, radius as f32, rotation_axis as raylib.Vector3, rotation_angle as f32, color as raylib.Color into void` | `DrawCircle3D` |
| `draw_triangle_3d` | `with v1 as raylib.Vector3, v2 as raylib.Vector3, v3 as raylib.Vector3, color as raylib.Color into void` | `DrawTriangle3D` |
| `draw_triangle_strip_3d` | `with points as slice of raylib.Vector3, color as raylib.Color into void` | `DrawTriangleStrip3D` |
| `draw_cube` | `with position as raylib.Vector3, width as f32, height as f32, length as f32, color as raylib.Color into void` | `DrawCube` |
| `draw_cube_wires` | `with position as raylib.Vector3, width as f32, height as f32, length as f32, color as raylib.Color into void` | `DrawCubeWires` |
| `draw_sphere` | `with center as raylib.Vector3, radius as f32, color as raylib.Color into void` | `DrawSphere` |
| `draw_sphere_ex` | `with center as raylib.Vector3, radius as f32, rings as int, slices as int, color as raylib.Color into void` | `DrawSphereEx` |
| `draw_sphere_wires` | `with center as raylib.Vector3, radius as f32, rings as int, slices as int, color as raylib.Color into void` | `DrawSphereWires` |
| `draw_cylinder` | `with position as raylib.Vector3, radius_top as f32, radius_bottom as f32, height as f32, sides as int, color as raylib.Color into void` | `DrawCylinder` |
| `draw_cylinder_ex` | `with start as raylib.Vector3, end as raylib.Vector3, start_radius as f32, end_radius as f32, sides as int, color as raylib.Color into void` | `DrawCylinderEx` |
| `draw_cylinder_wires` | `with position as raylib.Vector3, radius_top as f32, radius_bottom as f32, height as f32, sides as int, color as raylib.Color into void` | `DrawCylinderWires` |
| `draw_cylinder_wires_ex` | `with start as raylib.Vector3, end as raylib.Vector3, start_radius as f32, end_radius as f32, sides as int, color as raylib.Color into void` | `DrawCylinderWiresEx` |
| `draw_capsule` | `with start as raylib.Vector3, end as raylib.Vector3, radius as f32, rings as int, slices as int, color as raylib.Color into void` | `DrawCapsule` |
| `draw_capsule_wires` | same as `draw_capsule`, wires variant | `DrawCapsuleWires` |
| `draw_ray` | `with ray as raylib.Ray, color as raylib.Color into void` | `DrawRay` |
| `draw_grid` | `with slices as int, spacing as f32 into void` | `DrawGrid` |

`draw_cube`, `draw_cube_wires`, `draw_sphere`, `draw_sphere_wires` and `draw_cylinder_wires` share a name with a `Vector3` method. That is deliberate and legal: module functions are emitted as `raylibx_shapes3d_<name>` and methods as `Vector3_<name>`, which the master plan's D4 verified.

### 🎁 `maybe T` wrappers

**None apply.** Drawing cannot fail: no return value, no failure channel, no resource.

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `draw_triangle_strip_3d` | `points as slice of raylib.Vector3` |

One guard: an empty slice is a no-op, because taking the address of element zero of an empty slice is out of bounds.

### 📦 Multiple returns `(T, U)`

**None apply.** Every function returns `void` or, in the method case, nothing.

### 🌉 `std.ffi` usage

Only `slice of Vector3` → `ref to void` through `transmute (sigil of (points at 0)) to (ref to void)` in the one slice-shaped function. No string, no allocation, no `banish`.

### 💡 Compilable examples

```pengu
# Example 1 — the anchor methods
import raylib
import raylibx.shapes3d as shapes3d

weave main into int:
    var center as raylib.Vector3 is with x is 0.0, y is 1.0, z is 0.0
    calling center.draw_point with raylib.RED
    calling center.draw_cube with (with x is 1.0, y is 1.0, z is 1.0), raylib.GREEN
    calling center.draw_cube_wires with (with x is 1.0, y is 1.0, z is 1.0), raylib.WHITE
    calling center.draw_plane with (with x is 10.0, y is 10.0), raylib.LIGHTGRAY
    calling shapes3d.draw_sphere with center, 0.5, raylib.BLUE
    return 0
```

```pengu
# Example 2 — the module-level shapes and the one slice
import raylib
import raylibx.shapes3d as shapes3d

weave main into int:
    calling shapes3d.draw_line_3d with (with x is 0.0, y is 0.0, z is 0.0), (with x is 1.0, y is 0.0, z is 0.0), raylib.RED
    calling shapes3d.draw_cube with (with x is 0.0, y is 1.0, z is 0.0), 1.0, 1.0, 1.0, raylib.GREEN
    calling shapes3d.draw_grid with 10, 1.0
    var points as list of raylib.Vector3 is list of raylib.Vector3
    defer banish points
    calling points.push with (with x is 0.0, y is 0.0, z is 0.0)
    calling points.push with (with x is 1.0, y is 0.0, z is 0.0)
    calling points.push with (with x is 1.0, y is 1.0, z is 0.0)
    calling shapes3d.draw_triangle_strip_3d with (points at 0 to 3), raylib.BLUE
    return 0
```

### 🧪 Test plan

This family has **no CI-testable behaviour at all**: all 21 functions issue a raylib drawing command and every one of them is only meaningful between `BeginMode3D` and `EndMode3D`. There is no pure arithmetic here, unlike `shapes` (which had the collision predicates and the spline evaluators).

The plan therefore does what `shapes` did for its window-bound half:

- **The empty-slice guard of `draw_triangle_strip_3d` is the only assertion**, and it is a real one: the call must return early without touching element zero. Verified that this is safe without a window, exactly as the nine slice draws of `shapes` were.
- **The full public surface is type-checked by a compile-only probe** (`draw_api_probe`) that references every method and every module function with the values they need. It is not invoked by any test.

That is the honest degradation: the family is a thin, faithful renaming layer over drawing calls, and its value is the call-site ergonomics, not testable logic.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| none | **Nothing is skipped.** All 21 functions in the section are wrapped and all 21 are exported by the installed library. |

Coverage audit: **21 of 21** functions wrapped — **4 as `Vector3` methods** and **17 as module-level functions**. Nothing is skipped, and every wrapped symbol is exported by the installed library.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/shapes3d.pengu`
- Dueña en el plan maestro: familia `shapes3d` de `docs/plans/raylibx.md` (v0.1.2), séptima en su orden de implementación (adelantada)
- Dependencias: `import raylib`, `import std.ffi` (el único dibujo con slice)
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo y las 21 exportadas**. La sección "Basic 3d Shapes Drawing Functions" del header tiene exactamente 21 funciones, ni una más ni una menos, y `python3 tools/check_binding_symbols.py` confirma que la `libraylib.so` 6.0.0 instalada exporta todas. **En esta familia no se omite nada**: es la primera sin funciones exclusivas de 6.1 (plan maestro D17). | Enumerado desde la propia sección del header, no desde un patrón de nombres, y cruzado con los símbolos dinámicos. Es la comprobación que le faltó a la familia `shapes` (plan maestro D17). |
| D2 | La regla de sujeción D9 del plan maestro se extiende a 3D con la misma prueba mecánica: **la `V` del nombre de raylib marca las funciones cuyo primer argumento es el ancla**, así que `DrawCubeV` y `DrawCubeWiresV` pasan a métodos de `raylib.Vector3`. | Plan maestro D9. La extensión se declara explícitamente porque `DrawCube` es la trampa: su primer argumento es un `Vector3 position` aunque el nombre no lleve `V`, así que la prueba ingenua "el primer argumento es un Vector3" lo convertiría en método por error. La prueba es la `V`, y el plan de familia registra por qué. |
| D3 | **Exactamente cuatro** funciones pasan a métodos de `Vector3`: `draw_cube` (`DrawCubeV`), `draw_cube_wires` (`DrawCubeWiresV`), `draw_plane` (`DrawPlane`) y `draw_point` (`DrawPoint3D`). Se elimina el sufijo `_v` por legibilidad, así que `pos.draw_cube with extent, color` se lee como "en `pos`, dibuja un cubo de `size`". | La prueba mecánica de D2 aplicada a los nombres reales: las familias de cilindro y esfera de raylib 6.x **no tienen variante `V`** (no existe `DrawCylinderV`), y `DrawPoint3D`/`DrawPlane` son los dos nombres sin `V` cuyo primer argumento es el sujeto. Todo lo demás con un centro `Vector3` conserva el nombre del binding y se queda de módulo (D4). |
| D4 | Las demás quedan como funciones de módulo con los nombres exactos del binding: `draw_line_3d`, `draw_circle_3d`, `draw_triangle_3d`, `draw_triangle_strip_3d`, `draw_sphere`, `draw_sphere_ex`, `draw_sphere_wires`, `draw_cylinder`, `draw_cylinder_ex`, `draw_cylinder_wires`, `draw_cylinder_wires_ex`, `draw_capsule`, `draw_capsule_wires`, `draw_ray`, `draw_grid`. | Regla D9 del plan maestro: los nombres sin `V` no son métodos. `DrawSphere` y `DrawSphereEx` reciben `centerPos as Vector3`, pero el nombre no lo marca, y renombrarlos a métodos cambiaría en silencio la función C que recibe el llamador. |
| D5 | Las variantes `Ex` con dos anclas (`DrawCylinderEx`, `DrawCylinderWiresEx`, `DrawCapsule`, `DrawCapsuleWires`) se quedan en módulo aunque su primer argumento sea un `Vector3`. | Contrato §6.1: con dos sujetos igual de buenos (`startPos` **y** `endPos`) no hay receptor natural. Un método obligaría al llamador a recordar qué extremo quedó como receptor. |
| D6 | `DrawGrid(slices, spacing)` se envuelve como `draw_grid`, de módulo. | Sus argumentos no son ni un vector ni un color, así que no tiene sujeto. Es además la única función de la familia que no recibe color. |
| D7 | `DrawRay(ray as Ray, color as Color)` se envuelve como `draw_ray` recibiendo un `raylib.Ray`, de módulo. | `Ray` es un `rune` de dos `Vector3` cuyo *primer campo* es el origen, así que un método sobre `Ray` sería defendible — pero `Ray` no tiene ningún otro método en `raylibx` y el registro del plan maestro no tiene fila para él, así que introducir un tipo con un solo método sería una decisión de registro, no de familia. Queda como no-decisión deliberada; el registro del plan maestro es el sitio para revisarlo. |
| D8 | Una función con slice: `draw_triangle_strip_3d` recibe `slice of raylib.Vector3` con la guarda de slice vacío, y la conversión a puntero pasa por `void*`. | Contrato §5 para el slice, y D13 de `shapes` del plan maestro para la ruta `void*`: la forma tipada `ref to frozen raylib.Vector3` hace que `pengu 2.4.0` emita `const raylib.Vector3*` en el C, que no compila. |
| D9 | Sin `maybe` y sin uso de cadenas de `std.ffi`. | Nada en la familia puede fallar, devolver un recurso ni recibir una ruta. La única frontera FFI es el slice. |
| D10 | Los modelos y las mallas **no** están aquí. | `DrawModel`, `DrawMesh`, `DrawBoundingBox` y los constructores `GenMesh*` viven en la familia `models` (plan maestro D6). Esta familia es solo las figuras primitivas. |

### ✨ Enchantings

Sin `@mutates`: una llamada de dibujo no devuelve nada y el receptor se lee, no se modifica, así que el compilador no genera ninguna forma `get_*`. Ninguno de estos nombres colisiona con `raymathx`, que posee la aritmética de `Vector3`, ni con `raylibx_shapes`, que posee los métodos 2D de `Vector2`/`Rectangle`. El registro del plan maestro se amplía con los nombres de abajo.

#### `enchanting raylib.Vector3` — 4 métodos

| Método | Firma | C backing | Notas |
|---|---|---|---|
| `draw_point` | `with color as raylib.Color into void` | `DrawPoint3D` | dibuja un punto 3D |
| `draw_cube` | `with size as raylib.Vector3, color as raylib.Color into void` | `DrawCubeV` | este punto es el **centro** |
| `draw_cube_wires` | `with size as raylib.Vector3, color as raylib.Color into void` | `DrawCubeWiresV` | este punto es el **centro** |
| `draw_plane` | `with extent as raylib.Vector2, color as raylib.Color into void` | `DrawPlane` | este punto es el **centro**; `extent` va en unidades de mundo `Vector2` |

> **Por qué la esfera y el cilindro no son métodos.** `DrawSphere`, `DrawSphereEx`, `DrawSphereWires`, `DrawCylinder`, `DrawCylinderWires` y `DrawCylinderEx` reciben todos un centro o un punto inicial `Vector3`, así que un método sería intuitivo — pero ninguno de sus nombres lleva la `V` que D2 usa como prueba, y raylib 6.x no tiene `DrawSphereV`/`DrawCylinderV` sobre los que anclar. Convertirlos en métodos obligaría además a inventar nombres (`sphere`, `cylinder`) que ya no dicen qué función C se ejecuta. Se quedan de módulo con sus nombres del binding, y el llamador escribe `draw_sphere with center, radius, color`.

### 🔧 Funciones a nivel de módulo

| Función | Firma | C backing |
|---|---|---|
| `draw_line_3d` | `with start as raylib.Vector3, end as raylib.Vector3, color as raylib.Color into void` | `DrawLine3D` |
| `draw_circle_3d` | `with center as raylib.Vector3, radius as f32, rotation_axis as raylib.Vector3, rotation_angle as f32, color as raylib.Color into void` | `DrawCircle3D` |
| `draw_triangle_3d` | `with v1 as raylib.Vector3, v2 as raylib.Vector3, v3 as raylib.Vector3, color as raylib.Color into void` | `DrawTriangle3D` |
| `draw_triangle_strip_3d` | `with points as slice of raylib.Vector3, color as raylib.Color into void` | `DrawTriangleStrip3D` |
| `draw_cube` | `with position as raylib.Vector3, width as f32, height as f32, length as f32, color as raylib.Color into void` | `DrawCube` |
| `draw_cube_wires` | `with position as raylib.Vector3, width as f32, height as f32, length as f32, color as raylib.Color into void` | `DrawCubeWires` |
| `draw_sphere` | `with center as raylib.Vector3, radius as f32, color as raylib.Color into void` | `DrawSphere` |
| `draw_sphere_ex` | `with center as raylib.Vector3, radius as f32, rings as int, slices as int, color as raylib.Color into void` | `DrawSphereEx` |
| `draw_sphere_wires` | `with center as raylib.Vector3, radius as f32, rings as int, slices as int, color as raylib.Color into void` | `DrawSphereWires` |
| `draw_cylinder` | `with position as raylib.Vector3, radius_top as f32, radius_bottom as f32, height as f32, sides as int, color as raylib.Color into void` | `DrawCylinder` |
| `draw_cylinder_ex` | `with start as raylib.Vector3, end as raylib.Vector3, start_radius as f32, end_radius as f32, sides as int, color as raylib.Color into void` | `DrawCylinderEx` |
| `draw_cylinder_wires` | `with position as raylib.Vector3, radius_top as f32, radius_bottom as f32, height as f32, sides as int, color as raylib.Color into void` | `DrawCylinderWires` |
| `draw_cylinder_wires_ex` | `with start as raylib.Vector3, end as raylib.Vector3, start_radius as f32, end_radius as f32, sides as int, color as raylib.Color into void` | `DrawCylinderWiresEx` |
| `draw_capsule` | `with start as raylib.Vector3, end as raylib.Vector3, radius as f32, rings as int, slices as int, color as raylib.Color into void` | `DrawCapsule` |
| `draw_capsule_wires` | igual que `draw_capsule`, variante de alambre | `DrawCapsuleWires` |
| `draw_ray` | `with ray as raylib.Ray, color as raylib.Color into void` | `DrawRay` |
| `draw_grid` | `with slices as int, spacing as f32 into void` | `DrawGrid` |

`draw_cube` y `draw_cube_wires` comparten nombre con un método de `Vector3`. Es deliberado y legal: las funciones de módulo se emiten como `raylibx_shapes3d_<nombre>` y los métodos como `Vector3_<nombre>`, lo que el D4 del plan maestro verificó.

### 🎁 Wrappers `maybe T`

**Ninguno aplica.** Dibujar no puede fallar: sin valor de retorno, sin canal de fallo, sin recurso.

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `draw_triangle_strip_3d` | `points as slice of raylib.Vector3` |

Una guarda: un slice vacío es un no-op, porque tomar la dirección del elemento cero de un slice vacío queda fuera de rango.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Todas las funciones devuelven `void` o, en el caso de los métodos, nada.

### 🌉 Uso de `std.ffi`

Solo `slice of Vector3` → `ref to void` mediante `transmute (sigil of (points at 0)) to (ref to void)` en la única función con slice. Sin cadenas, sin alojamiento, sin `banish`.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — los métodos de ancla
import raylib
import raylibx.shapes3d as shapes3d

weave main into int:
    var center as raylib.Vector3 is with x is 0.0, y is 1.0, z is 0.0
    calling center.draw_point with raylib.RED
    calling center.draw_cube with (with x is 1.0, y is 1.0, z is 1.0), raylib.GREEN
    calling center.draw_cube_wires with (with x is 1.0, y is 1.0, z is 1.0), raylib.WHITE
    calling center.draw_plane with (with x is 10.0, y is 10.0), raylib.LIGHTGRAY
    calling shapes3d.draw_sphere with center, 0.5, raylib.BLUE
    return 0
```

```pengu
# Ejemplo 2 — las figuras de módulo y el único slice
import raylib
import raylibx.shapes3d as shapes3d

weave main into int:
    calling shapes3d.draw_line_3d with (with x is 0.0, y is 0.0, z is 0.0), (with x is 1.0, y is 0.0, z is 0.0), raylib.RED
    calling shapes3d.draw_cube with (with x is 0.0, y is 1.0, z is 0.0), 1.0, 1.0, 1.0, raylib.GREEN
    calling shapes3d.draw_grid with 10, 1.0
    var points as list of raylib.Vector3 is list of raylib.Vector3
    defer banish points
    calling points.push with (with x is 0.0, y is 0.0, z is 0.0)
    calling points.push with (with x is 1.0, y is 0.0, z is 0.0)
    calling points.push with (with x is 1.0, y is 1.0, z is 0.0)
    calling shapes3d.draw_triangle_strip_3d with (points at 0 to 3), raylib.BLUE
    return 0
```

### 🧪 Plan de tests

Esta familia **no tiene nada testeable en CI**: las 21 funciones emiten un comando de dibujo de raylib y todas solo tienen sentido entre `BeginMode3D` y `EndMode3D`. Aquí no hay aritmética pura, a diferencia de `shapes` (que tenía los predicados de colisión y los evaluadores de spline).

El plan hace por tanto lo que `shapes` hizo con su mitad ligada a ventana:

- **La guarda de slice vacío de `draw_triangle_strip_3d` es la única aserción**, y es real: la llamada debe volver antes de tocar el elemento cero. Verificado que es segura sin ventana, exactamente como los nueve dibujos con slice de `shapes`.
- **Toda la superficie pública se comprueba de tipos con una sonda de solo compilación** (`draw_api_probe`) que referencia cada método y cada función de módulo con los valores que necesitan. No la invoca ningún test.

Es la degradación honesta: la familia es una capa fina y fiel de renombrado sobre llamadas de dibujo, y su valor es la ergonomía en el sitio de llamada, no lógica testeable.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| ninguno | **No se omite nada.** Las 21 funciones de la sección se envuelven y las 21 las exporta la biblioteca instalada. |

Auditoría de cobertura: **21 de 21** funciones envueltas — **4 como métodos de `Vector3`** y **17 como funciones de módulo**. No se omite nada y la biblioteca instalada exporta todos los símbolos envueltos.
