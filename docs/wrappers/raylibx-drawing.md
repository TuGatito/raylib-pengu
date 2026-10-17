> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# drawing

> Source: `pengu/raylibx/drawing.pengu`

Layer-2 wrapper over the 15 frame-state functions of the `raylib` binding: the seven
`Begin`/`End` pairs and `ClearBackground`.

This is the family that names the frame's state machine:

    calling raylib.BeginMode3D with camera        # binding
    calling raylibx_drawing.begin_mode_3d with camera   # wrapper

## Balancing the pairs
The wrapper cannot enforce the pairing, and it deliberately does not try: the obvious
design -- a helper that takes the frame body as a lambda and closes it for you -- is
**not possible in PenguScript**, because lambdas do not capture locals and a drawing body
always needs the caller's camera and scene state. See the family plan, D3.

The idiomatic mechanism is `defer`, which runs at scope exit:

```pengu
calling raylibx_drawing.begin_drawing
defer calling raylibx_drawing.end_drawing
```

---

### `begin_drawing`

> **begin_drawing**() -> void

Opens a drawing frame.
Returns
Nothing; the frame state is changed.
Notes
This must be the first call of the frame and `end_drawing` must close it; everything drawn in between lands on the screen.
Pair it with `defer calling raylibx_drawing.end_drawing` right after, so the frame still closes if something returns early.
**Requires a window.** Measured: calling it without one crashes rather than being ignored.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_drawing
defer calling raylibx_drawing.end_drawing
```


### `end_drawing`

> **end_drawing**() -> void

Closes the drawing frame opened by `begin_drawing`.
Returns
Nothing; the frame state is changed.
Notes
This is where raylib presents the frame and advances the timing, so no drawing is visible until it runs.
Never call it without a matching `begin_drawing`: the frame stack is not checked.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_drawing
```


### `begin_mode_2d`

> **begin_mode_2d**(camera: Camera2D) -> void

Switches drawing into a 2D camera's coordinate space.
Parameters
- `c`: the camera whose 2D space drawing switches to
Returns
Nothing; the frame state is changed.
Notes
Everything drawn until `end_mode_2d` is transformed by the camera's offset, target, rotation and zoom.
Pair it with `defer calling raylibx_drawing.end_mode_2d`.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_mode_2d with camera
```


### `end_mode_2d`

> **end_mode_2d**() -> void

Leaves the 2D camera space opened by `begin_mode_2d`.
Returns
Nothing; the frame state is changed.
Notes
It takes no camera argument: raylib keeps the mode as stack state, so this closes whichever `begin_mode_2d` is innermost.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_mode_2d
```


### `begin_mode_3d`

> **begin_mode_3d**(camera: Camera3D) -> void

Switches drawing into a 3D camera's coordinate space.
Parameters
- `c`: the camera whose 3D space drawing switches to
Returns
Nothing; the frame state is changed.
Notes
Everything drawn until `end_mode_3d` uses the camera's view and projection matrices.
This is the switch that makes the `raylibx_shapes3d` primitives appear in perspective.
Pair it with `defer calling raylibx_drawing.end_mode_3d`.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_mode_3d with camera
```


### `end_mode_3d`

> **end_mode_3d**() -> void

Leaves the 3D camera space opened by `begin_mode_3d`.
Returns
Nothing; the frame state is changed.
Notes
The `raylibx_shapes3d` primitives drawn after this are back in screen space and will look wrong: it is the most common symptom of a missing pair.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_mode_3d
```


### `begin_texture_mode`

> **begin_texture_mode**(target: RenderTexture) -> void

Redirects drawing into a render target instead of the screen.
Parameters
- `t`: the render target that receives the drawing
Returns
Nothing; the frame state is changed.
Notes
The target's texture can then be drawn like any other texture, which is how you build post-processing and off-screen passes.
Rendering to a texture flips the vertical axis in OpenGL, so the result usually needs a negative source height when it is drawn back.
Pair it with `defer calling raylibx_drawing.end_texture_mode`.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_texture_mode with target
```


### `end_texture_mode`

> **end_texture_mode**() -> void

Returns drawing to the screen after `begin_texture_mode`.
Returns
Nothing; the frame state is changed.
Notes
raylib keeps the render target as stack state; this closes the innermost one.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_texture_mode
```


### `begin_shader_mode`

> **begin_shader_mode**(shader: Shader) -> void

Applies a shader to every draw call that follows.
Parameters
- `s`: the shader applied to everything drawn until the matching end
Returns
Nothing; the frame state is changed.
Notes
The shader's uniforms must be set before this call, because raylib binds it here.
Measured: this pair is the one piece of the family that is safe to call without a window, and repeating it five times does not crash, which is why the test can assert it.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_shader_mode with shader
```


### `end_shader_mode`

> **end_shader_mode**() -> void

Stops applying the shader bound by `begin_shader_mode`.
Returns
Nothing; the frame state is changed.
Notes
Shaders nest, so each `begin_shader_mode` needs its own end and the innermost wins.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_shader_mode
```


### `begin_blend_mode`

> **begin_blend_mode**(mode: BlendMode) -> void

Sets the blending equation used by the draw calls that follow.
Parameters
- `m`: the blending equation applied to everything drawn until the matching end
Returns
Nothing; the frame state is changed.
Notes
`raylib.BLEND_ALPHA` is the default; additive is the one that makes glows and particles work.
Measured: one pair is safe without a window but a second one crashes, so the test suite does not call this at all.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_blend_mode with raylib.BLEND_ALPHA
```


### `end_blend_mode`

> **end_blend_mode**() -> void

Restores the blending equation that was active before `begin_blend_mode`.
Returns
Nothing; the frame state is changed.
Notes
Blend modes do not nest the way shaders do: raylib stores one previous mode, so an unbalanced pair loses the original.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_blend_mode
```


### `begin_scissor_mode`

> **begin_scissor_mode**(x: int, y: int, width: int, height: int) -> void

Clips drawing to a rectangle.
Parameters
- `x`: the clip rectangle's left edge
- `y`: the clip rectangle's top edge
- `w`: the clip rectangle's width
- `h`: the clip rectangle's height
Returns
Nothing; the frame state is changed.
Notes
Everything drawn until `end_scissor_mode` is discarded outside the rectangle, which is how scrolling lists and masked panels are built.
The coordinates are in the current target's space, so inside a 2D camera they follow the camera.
Measured: both halves of this pair crash without a window.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.begin_scissor_mode with 0, 0, 128, 128
```


### `end_scissor_mode`

> **end_scissor_mode**() -> void

Removes the clip rectangle set by `begin_scissor_mode`.
Returns
Nothing; the frame state is changed.
Notes
raylib keeps one scissor rectangle, not a stack, so nesting loses the outer clip.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.end_scissor_mode
```


### `clear_background`

> **clear_background**(color: Color) -> void

Fills the current drawing target with a colour.
Parameters
- `c`: the colour the current target is filled with
Returns
Nothing; the frame state is changed.
Notes
It clears whatever target is active, so inside `begin_texture_mode` it clears the render texture and not the screen.
**Requires an open frame and a window.** Measured: calling it without one crashes.
This is `Image.clear`'s twin in `raylibx_images`: same idea, different target.
Memory
No allocation and nothing to release.
Example
```pengu
calling raylibx_drawing.clear_background with raylib.RAYWHITE
```


### `drawing_api_probe`

> **drawing_api_probe**(camera2: Camera2D, camera3: Camera3D, target: RenderTexture, shader: Shader) -> void

The rest of the surface is type-checked here and never called: every entry needs a window,
and the measured failure mode is a crash rather than a silent no-op.

