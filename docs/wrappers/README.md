# Layer 2 — wrappers

One page per wrapper module. These are hand-written: `weave` and `enchanting` only, no binding
directives, and every page is generated from the module's `##` doc comments by `pengu doc`.

`raylibx.md` is the facade and the fourteen `raylibx-<family>.md` pages are its families;
`raymathx.md`, `rcamerax.md`, `rlglx.md` and `rayguix.md` wrap their own bindings and are not part
of the facade. The module name in code is the page name with the hyphen replaced by a dot:
`raylibx-shapes.md` documents `raylibx.shapes`, reached as `import raylibx.shapes as shapes`.

| Page | Source | Surface | Tests | What it covers |
|---|---|---|---|---|
<!-- generated:wrappers -->
| [`rayguix`](rayguix.md) | `pengu/rayguix.pengu` | 38 functions · 0 methods | 4 | raygui widgets: strings in, text fields out through a `ref to string` |
| [`raylibx`](raylibx.md) | `pengu/raylibx.pengu` | 0 functions · 0 methods | 0 | the facade: imports the fourteen families so the layer builds and tests in one process; re-exports nothing |
| [`raylibx-audio`](raylibx-audio.md) | `pengu/raylibx/audio.pengu` | 14 functions · 41 methods | 8 | waves, sounds, music and audio streams, over four receiver types |
| [`raylibx-colors`](raylibx-colors.md) | `pengu/raylibx/colors.pengu` | 2 functions · 14 methods | 46 | `Color` methods and the colour helpers |
| [`raylibx-drawing`](raylibx-drawing.md) | `pengu/raylibx/drawing.pengu` | 15 functions · 0 methods | 2 | the `Begin`/`End` frame-state pairs |
| [`raylibx-files`](raylibx-files.md) | `pengu/raylibx/files.pengu` | 36 functions · 0 methods | 39 | files, directories, paths and the dropped-files clipboard |
| [`raylibx-images`](raylibx-images.md) | `pengu/raylibx/images.pengu` | 22 functions · 52 methods | 43 | the image pipeline, with the most methods in the layer |
| [`raylibx-input`](raylibx-input.md) | `pengu/raylibx/input.pengu` | 28 functions · 0 methods | 16 | keyboard, mouse, gamepad, touch and gestures |
| [`raylibx-models`](raylibx-models.md) | `pengu/raylibx/models.pengu` | 18 functions · 19 methods | 14 | meshes, materials, models, animations and 3D collision |
| [`raylibx-random`](raylibx-random.md) | `pengu/raylibx/random.pengu` | 2 functions · 0 methods | 6 | `between` and `sequence`, plus the four measured traps of raylib's randomness |
| [`raylibx-shaders`](raylibx-shaders.md) | `pengu/raylibx/shaders.pengu` | 3 functions · 12 methods | 7 | shader loading and typed uniforms |
| [`raylibx-shapes`](raylibx-shapes.md) | `pengu/raylibx/shapes.pengu` | 41 functions · 27 methods | 37 | 2D shapes, split by anchor into `Vector2` and `Rectangle` methods and module functions |
| [`raylibx-shapes3d`](raylibx-shapes3d.md) | `pengu/raylibx/shapes3d.pengu` | 17 functions · 4 methods | 1 | 3D primitives, with `Vector3` methods for the `V`-anchored draws |
| [`raylibx-text`](raylibx-text.md) | `pengu/raylibx/text.pengu` | 45 functions · 5 methods | 33 | fonts and text, with `Font` methods |
| [`raylibx-textures`](raylibx-textures.md) | `pengu/raylibx/textures.pengu` | 6 functions · 13 methods | 8 | `Texture` and `RenderTexture` |
| [`raylibx-window`](raylibx-window.md) | `pengu/raylibx/window.pengu` | 11 functions · 0 methods | 7 | window state, monitors and the clipboard |
| [`raymathx`](raymathx.md) | `pengu/raymathx.pengu` | 11 functions · 127 methods | 416 | the raymath surface as methods on the vector, quaternion and matrix types |
| [`rcamerax`](rcamerax.md) | `pengu/rcamerax.pengu` | 0 functions · 22 methods | 42 | `Camera3D` and `Camera2D` methods, including the reassigned projection helpers and billboards |
| [`rlglx`](rlglx.md) | `pengu/rlglx.pengu` | 16 functions · 2 methods | 6 | the rlgl boundary crossings: strings, slices and the render batch; the rest stays at the binding |
<!-- /generated -->

A method in a page appears under the type it is enchanted onto, which is why the wrapper counts in
this table split into module-level functions and methods. Regenerate with
`python3 tools/gen_docs.py`; the table above is rewritten from the sources by that script.
