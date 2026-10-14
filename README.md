# raylib-pengu - PenguScript binding

Binding to the `raylib-pengu` C library for PenguScript.

## Install

From any PenguScript project:

    pengu add <this-repo-url> --trust

`--trust` is required the first time because `build.py` compiles the native
part.

## Use

```pengu
import raylib-pengu

weave main into int:
  calling raylib-pengu.raylib_pengu_init with 800, 600, "Hello"
  var x as int is calling raylib-pengu.raylib_pengu_add with 1, 2
  calling raylib-pengu.raylib_pengu_close
  return x
```

## Regenerate the declarations

If you change `include/raylib-pengu.h`, regenerate the binding:

    pengu bind include/raylib-pengu.h --output pengu/raylib-pengu.d.pengu --links raylib-pengu

## Structure

```
raylib-pengu/
|-- pengu.toml
|-- build.py                 # fetches/compiles the native part into lib/
|-- pengu/
|   `-- raylib-pengu.d.pengu       # declarations (include/link/declare)
|-- include/
|   `-- raylib-pengu.h             # the real C header
|-- c/
|   `-- raylib-pengu.c             # optional glue code
`-- lib/                     # compiled native libraries (built by build.py)
```

The `link "raylib-pengu"` statement in `pengu/raylib-pengu.d.pengu` propagates to the
consumer's link line automatically. See the PenguScript docs/BINDINGS.md for
the full contract.
