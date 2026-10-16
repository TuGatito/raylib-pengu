# Plan: raylibx/random.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`, raylib **6.1-dev** (measured against the installed **6.0.0**)
- Wrapper target: `pengu/raylibx/random.pengu` — the **fourteenth family**, imported by the `raylibx` facade
- Owner in the master plan: family 14 of `docs/plans/raylibx.md`, which had listed these four functions as "assigned to no family"
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### ✅ Verdict, first

**The azar appendix is feasible, needs no window, and only two of its four functions earn a wrapper — but it earns its place because it is where four measured traps get written down.**

| Question | Measured answer |
|---|---|
| How many functions does raylib's random banner have? | **Four**: `SetRandomSeed`, `GetRandomValue`, `LoadRandomSequence`, `UnloadRandomSequence`. |
| How many are wrapped? | **Two** (`between`, `sequence`); `SetRandomSeed` is excluded by §9 row 8 and `UnloadRandomSequence` by §9 row 4. |
| Does it need a window or a context? | **No.** The whole family is pure CPU state, so these are the first layer-2 tests that need neither a window nor a drawing frame. |
| Is there a 6.1/6.0 gap? | **No.** All four are exported by the installed library. |
| Is it the smallest family? | **Yes**, and by a wide margin: two wrappers, no receiver and no `insignia`. It still has six tests, because the traps are worth pinning. |

### 🔬 Measured behaviour (the evidence the decisions rest on)

Every row was measured on the installed raylib 6.0.0 with a C program before any of this was designed.

| # | Measurement | Result |
|---|---|---|
| M1 | Two separate runs, no seeding, drawing `GetRandomValue(1, 6)` six times | **The same sequence both times**: `6 3 6 1 4 3`. raylib's generator starts from a **fixed default seed**, so an unseeded program repeats itself for ever. |
| M2 | `SetRandomSeed(42)` twice | The same six values both times: seeding is reproducible, which is what makes exact assertions in tests possible. |
| M3 | `GetRandomValue(10, 1)` | Values inside `[1, 10]`: **inverted bounds are swapped silently**. |
| M4 | `GetRandomValue(5, 5)` | Always `5`. |
| M5 | `LoadRandomSequence(5, 1, 5)` with seed 7 | `5 4 3 1 2`: **values never repeat**, and the exact values are deterministic. |
| M6 | `LoadRandomSequence(6, 1, 5)` | **A null pointer.** Asking for more values than the range holds is impossible, not truncated. |
| M7 | `LoadRandomSequence(3, 5, 1)` | `9 8 7` — **values outside both bounds**, and no null pointer: unlike `GetRandomValue`, this one does **not** swap. |
| M8 | `LoadRandomSequence(-1, 1, 5)` | A null pointer. |
| M9 | `LoadRandomSequence(0, 1, 5)` | A non-null pointer with no values — which is what `malloc(0)` happened to do here, and is not something a wrapper should depend on. |

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: raylib's random banner declares **4** functions. **2 are wrapped** and **2 are skipped**. | The census, with the contract's three-condition criterion (§9) applied one function at a time. |
| D2 | `GetRandomValue` is wrapped as **`between`**. | Criterion 2 is satisfied literally: it renames a `Get*` with a Pengunic noun. Criterion 1 is the debatable one — token counts tie — and it is settled by the project's own practice: the families already wrap **137** one-to-one renames (`begin_drawing`, `end_drawing`, `clear_background`, the audio loaders), so skipping this one would be the inconsistent choice. What the wrapper adds beyond the rename is that the three facts of M1, M3 and M4 live in the docstring where a user of randomness will look. |
| D3 | `LoadRandomSequence` is wrapped as **`sequence`**, returning an **owned `maybe list of int`**. | This is the family's real wrapper, and it folds three separate things: the NULL sentinel into `maybe` (§5), the C array into an owned PenguScript list through `ffi.list_of_int_from_ptr` — **measured to copy**, which is what makes releasing the source safe — and the `UnloadRandomSequence` call into the wrapper itself, so the caller can never leak. Without it, the caller's correct form is a `is_valid` check, a `transmute`, a `defer` and manual indexing. |
| D4 | `sequence` returns **`none`** for an inverted range instead of forwarding raylib's answer. | M7: raylib hands back values outside both bounds, silently. An inverted range is an impossible request, and the honest answer to an impossible request in this contract is `none`, not garbage. The guard is the same shape as `raylibx.shaders`' loader precondition, which exists because raylib substitutes the default shader silently. |
| D5 | `sequence` returns **`none`** for a negative count and for a count larger than the range holds, and **`some` with an empty list** for a count of zero. | M6 and M8 are raylib's own null pointer, so the fold is a sentinel fold. M9 is the exception that needed a guard rather than a fold: a zero count is a *valid* request for nothing, and raylib's answer depends on what `malloc(0)` does, so the wrapper answers it without calling raylib at all. |
| D6 | `SetRandomSeed` is **not** wrapped. | §9 row 8, one-shot global configuration, the same rule that excludes `InitWindow`, `CloseWindow` and `SetTraceLogLevel` in the `window` family, and the same reason: a rename does not reduce tokens. The module header points at `raylib.SetRandomSeed` explicitly, because M1 makes it the first thing a user of randomness has to know, and the family's tests use the binding to seed. |
| D7 | `UnloadRandomSequence` is **not** wrapped. | §9 row 4, the `Unload*` rule. Here it is stronger than the rule: `sequence` owns the array it allocates, so a module-level `unload_sequence` would be an invitation to double-free something the caller never received. |
| D8 | No `enchanting`, no `insignia`, no receiver. | raylib's random API has no type: it is four functions over a process-global generator. The natural call site form is `random.between with 1, 6`. |
| D9 | The family is deliberately the smallest in the layer, and the module header says so. | The alternative — padding the family with the two skipped setters so it looks bigger — would be exactly what §9 exists to prevent. A reader who lands in `raylibx.random` finds the traps of **all four** functions, wrapped or not. |
| D10 | The tests seed through the binding and then assert **exact values**. | M2 makes the generator reproducible, so a test can assert `5 4 3 1 2` rather than a range. A test that only asserts "inside the range" would pass with a broken generator. |
| D11 | The cross-run determinism of M1 is documented, not tested. | It is a property of two separate processes, and a single test process cannot express it. It is recorded here with the measurement instead, and the module header repeats it. |

### 🔧 Module-level functions (2)

| Function | Signature | C backing |
|---|---|---|
| `between` | `with min_value as int, max_value as int into int` | `GetRandomValue` |
| `sequence` | `with count as int, min_value as int, max_value as int into maybe list of int` | `LoadRandomSequence` |

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `sequence` | `maybe list of int` | raylib answers with a **null pointer** for a negative count (M8) and for a count larger than the range holds (M6); the wrapper adds the inverted range (M7), which raylib answers with values outside both bounds instead. A count of zero is **not** a `none`: it is `some` with an empty list (D5). |

### ✂️ `slice` wrappers

**None apply.** The family neither accepts nor returns a slice; the ownership fold of `sequence` is on the *return* side only, which is why the module needs no empty-slice policy.

### 📦 Multiple returns `(T, U)`

**None apply**, and one near miss is worth recording: `sequence` produces a list **and** can fail, which is exactly the case a tuple would handle and a `maybe` handles better — there is no second value to carry on failure.

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| pointer validity | `ffi.is_valid` | `sequence`, folding raylib's null pointer into `none` |
| pointer → owned list | `ffi.list_of_int_from_ptr` | `sequence`; measured to **copy**, which is what makes it safe to release the C array immediately afterwards |
| value → `ref to void` | `transmute … to ref to void` | the two calls above, since `is_valid` and the list constructor take an untyped pointer |

### 💡 Compilable examples

```pengu
# Example 1 — the trap first: seed, then draw
import raylib
import raylibx.random as random

weave main into int:
    # measured: without this line every run of this program repeats itself
    calling raylib.SetRandomSeed with 12345
    var damage as int is 0
    var i as int is 0
    while i < 4:
        set damage is calling random.between with 5, 10
        set i is i + 1
    return damage
```

```pengu
# Example 2 — a hand of distinct cards
import raylib
import raylibx.random as random

weave main into int:
    calling raylib.SetRandomSeed with (calling raylib.GetTime to u32)
    var hand as maybe list of int is calling random.sequence with 5, 1, 52
    if hand is present:
        var cards as list of int is calling hand.unwrap
        defer banish cards
        return cards.length
    return 0
```

### 🧪 Test plan

**Six tests, and none of them opens a window** — the first tests in layer 2 that need no graphics context at all, which is itself the family's clearest property.

- **`between` stays inside an inclusive range and reaches both ends** — 64 draws with a fixed seed, tracking the observed minimum and maximum, which must be exactly `1` and `6`.
- **`between` swaps silently** — 64 draws with an inverted range, each asserted to land in `[1, 10]`, pinning M3.
- **`between` with equal bounds** returns that bound, pinning M4.
- **`sequence` is deterministic once seeded, distinct and inside the range** — the exact values of M5 (`5 4 3 1 2`) with seed 7.
- **A longer sequence does not repeat** — 8 values from `[1, 100]`, each pair compared, because "the values never repeat" is the function's whole point.
- **The impossible requests come back as `none`, and zero as an empty list** — `count > distinct` (M6), a negative count (M8), an inverted range (M7) and a count of zero (M9) in one test, since they are the four edges of the same decision.

### 🚫 Not wrapped (with reason)

| Rule | Symbol | Reason |
|---|---|---|
| §9 row 8 — one-shot global configuration | `SetRandomSeed` | it is called once and a rename does not reduce tokens; the module header points at `raylib.SetRandomSeed` because of M1 |
| §9 row 4 — the `Unload*` rule | `UnloadRandomSequence` | `sequence` owns and releases the array, so exposing this would invite a double free of something the caller never received |

Coverage audit: **4 C functions, 2 wrapped, 2 skipped, no leftovers and no duplicates.** The family adds two module-level names and enchants nothing, so the method registry is untouched. The facade's import list grows from thirteen families to **fourteen**, and `docs/WRAPPER_CONVENTIONS.md` §15 still says "los trece `import`" — recorded here as a one-word documentation drift to correct, not corrected silently.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`, raylib **6.1-dev** (medido contra la **6.0.0** instalada)
- Wrapper destino: `pengu/raylibx/random.pengu` — la **decimocuarta familia**, importada por la fachada `raylibx`
- Dueña en el plan maestro: familia 14 de `docs/plans/raylibx.md`, que listaba estas cuatro funciones como "asignadas a ninguna familia"
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### ✅ Veredicto, lo primero

**El apéndice de azar es factible, no necesita ventana, y solo dos de sus cuatro funciones se ganan un wrapper — pero se gana su sitio porque es donde quedan escritas cuatro trampas medidas.**

| Pregunta | Respuesta medida |
|---|---|
| ¿Cuántas funciones tiene el cartel de azar de raylib? | **Cuatro**: `SetRandomSeed`, `GetRandomValue`, `LoadRandomSequence`, `UnloadRandomSequence`. |
| ¿Cuántas se envuelven? | **Dos** (`between`, `sequence`); `SetRandomSeed` queda excluida por la §9 fila 8 y `UnloadRandomSequence` por la fila 4. |
| ¿Necesita ventana o contexto? | **No.** Toda la familia es estado de CPU puro, así que son los primeros tests de capa 2 que no necesitan ni ventana ni fotograma de dibujo. |
| ¿Hay hueco 6.1/6.0? | **No.** Las cuatro las exporta la biblioteca instalada. |
| ¿Es la familia más pequeña? | **Sí**, y por mucho: dos envolturas, sin receptor y sin `insignia`. Aun así tiene seis tests, porque las trampas merecen fijarse. |

### 🔬 Comportamiento medido (la evidencia en la que se apoyan las decisiones)

Cada fila se midió sobre la raylib 6.0.0 instalada con un programa de C antes de diseñar nada de esto.

| # | Medición | Resultado |
|---|---|---|
| M1 | Dos ejecuciones separadas, sin sembrar, sacando `GetRandomValue(1, 6)` seis veces | **La misma secuencia en ambas**: `6 3 6 1 4 3`. El generador de raylib parte de una **semilla por defecto fija**, así que un programa sin sembrar se repite para siempre. |
| M2 | `SetRandomSeed(42)` dos veces | Los mismos seis valores en ambas: sembrar es reproducible, que es lo que permite aserciones exactas en los tests. |
| M3 | `GetRandomValue(10, 1)` | Valores dentro de `[1, 10]`: **los límites invertidos se intercambian en silencio**. |
| M4 | `GetRandomValue(5, 5)` | Siempre `5`. |
| M5 | `LoadRandomSequence(5, 1, 5)` con semilla 7 | `5 4 3 1 2`: **los valores nunca se repiten**, y los valores exactos son deterministas. |
| M6 | `LoadRandomSequence(6, 1, 5)` | **Un puntero nulo.** Pedir más valores de los que caben en el rango es imposible, no se trunca. |
| M7 | `LoadRandomSequence(3, 5, 1)` | `9 8 7` — **valores fuera de ambos límites**, y sin puntero nulo: a diferencia de `GetRandomValue`, esta **no** intercambia. |
| M8 | `LoadRandomSequence(-1, 1, 5)` | Un puntero nulo. |
| M9 | `LoadRandomSequence(0, 1, 5)` | Un puntero no nulo sin valores — que es lo que `malloc(0)` hizo aquí, y no es algo de lo que un wrapper deba depender. |

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: el cartel de azar de raylib declara **4** funciones. **2 se envuelven** y **2 se omiten**. | El censo, aplicando el criterio de tres condiciones del contrato (§9) función a función. |
| D2 | `GetRandomValue` se envuelve como **`between`**. | El criterio 2 se cumple literalmente: renombra un `Get*` con un sustantivo Pengunic. El criterio 1 es el discutible — el recuento de tokens empata — y lo resuelve la práctica del propio proyecto: las familias ya envuelven **137** renombrados uno a uno (`begin_drawing`, `end_drawing`, `clear_background`, los cargadores de audio), así que saltarse este sería lo inconsistente. Lo que el wrapper añade más allá del renombrado es que los tres hechos de M1, M3 y M4 vivan en el docstring, donde los mirará quien use azar. |
| D3 | `LoadRandomSequence` se envuelve como **`sequence`**, devolviendo un **`maybe list of int`** con posesión. | Es el wrapper real de la familia, y pliega tres cosas distintas: el centinela NULL en `maybe` (§5), el array de C en una lista de PenguScript con posesión mediante `ffi.list_of_int_from_ptr` — **medido que copia**, que es lo que hace seguro liberar la fuente — y la llamada a `UnloadRandomSequence` dentro del propio wrapper, para que el llamador no pueda filtrar nunca. Sin él, la forma correcta del llamador es una comprobación con `is_valid`, un `transmute`, un `defer` y indexación manual. |
| D4 | `sequence` devuelve **`none`** ante un rango invertido en vez de reenviar la respuesta de raylib. | M7: raylib devuelve valores fuera de ambos límites, en silencio. Un rango invertido es una petición imposible, y la respuesta honesta a una petición imposible en este contrato es `none`, no basura. La guarda tiene la misma forma que la precondición del cargador de `raylibx.shaders`, que existe porque raylib sustituye el shader por defecto en silencio. |
| D5 | `sequence` devuelve **`none`** para una cuenta negativa y para una cuenta mayor de lo que cabe en el rango, y **`some` con una lista vacía** para una cuenta de cero. | M6 y M8 son el propio puntero nulo de raylib, así que el pliegue es un pliegue de centinela. M9 es la excepción que necesitó una guarda en vez de un pliegue: una cuenta de cero es una petición *válida* de nada, y la respuesta de raylib depende de lo que haga `malloc(0)`, así que el wrapper la responde sin llamar a raylib. |
| D6 | `SetRandomSeed` **no** se envuelve. | §9 fila 8, configuración global de un solo uso, la misma regla que excluye `InitWindow`, `CloseWindow` y `SetTraceLogLevel` en la familia `window`, y por el mismo motivo: un renombrado no reduce tokens. La cabecera del módulo apunta explícitamente a `raylib.SetRandomSeed`, porque M1 lo convierte en lo primero que tiene que saber quien use azar, y los tests de la familia usan el binding para sembrar. |
| D7 | `UnloadRandomSequence` **no** se envuelve. | §9 fila 4, la regla de los `Unload*`. Aquí es más fuerte que la regla: `sequence` posee el array que reserva, así que un `unload_sequence` de módulo sería una invitación a liberar dos veces algo que el llamador nunca recibió. |
| D8 | Sin `enchanting`, sin `insignia`, sin receptor. | La API de azar de raylib no tiene tipo: son cuatro funciones sobre un generador global de proceso. La forma natural en el sitio de llamada es `random.between with 1, 6`. |
| D9 | La familia es deliberadamente la más pequeña de la capa, y la cabecera del módulo lo dice. | La alternativa — rellenar la familia con los dos setters omitidos para que parezca más grande — sería exactamente lo que la §9 existe para evitar. Quien aterrice en `raylibx.random` encuentra las trampas de **las cuatro** funciones, envueltas o no. |
| D10 | Los tests siembran por el binding y luego aseguran **valores exactos**. | M2 hace reproducible el generador, así que un test puede asegurar `5 4 3 1 2` en vez de un rango. Un test que solo asegurara "dentro del rango" pasaría con un generador roto. |
| D11 | El determinismo entre ejecuciones de M1 se documenta, no se testea. | Es una propiedad de dos procesos separados, y un único proceso de test no puede expresarla. Se registra aquí con la medición, y la cabecera del módulo la repite. |

### 🔧 Funciones a nivel de módulo (2)

| Función | Firma | C backing |
|---|---|---|
| `between` | `with min_value as int, max_value as int into int` | `GetRandomValue` |
| `sequence` | `with count as int, min_value as int, max_value as int into maybe list of int` | `LoadRandomSequence` |

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `sequence` | `maybe list of int` | raylib responde con un **puntero nulo** a una cuenta negativa (M8) y a una cuenta mayor de lo que cabe en el rango (M6); el wrapper añade el rango invertido (M7), que raylib responde con valores fuera de ambos límites. Una cuenta de cero **no** es `none`: es `some` con una lista vacía (D5). |

### ✂️ Wrappers de `slice`

**Ninguno aplica.** La familia ni recibe ni devuelve slices; el pliegue de propiedad de `sequence` está solo del lado del *retorno*, y por eso el módulo no necesita política de slice vacío.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica**, y hay un casi que merece registrarse: `sequence` produce una lista **y** puede fallar, que es justo el caso que una tupla resolvería y que un `maybe` resuelve mejor — no hay un segundo valor que llevar en el fallo.

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| validez de un puntero | `ffi.is_valid` | `sequence`, plegando el puntero nulo de raylib en `none` |
| puntero → lista con posesión | `ffi.list_of_int_from_ptr` | `sequence`; medido que **copia**, que es lo que hace seguro liberar el array de C justo después |
| valor → `ref to void` | `transmute … to ref to void` | las dos llamadas anteriores, porque `is_valid` y el constructor de lista reciben un puntero sin tipo |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — la trampa primero: sembrar y luego sacar
import raylib
import raylibx.random as random

weave main into int:
    # medido: sin esta línea cada ejecución de este programa se repite
    calling raylib.SetRandomSeed with 12345
    var damage as int is 0
    var i as int is 0
    while i < 4:
        set damage is calling random.between with 5, 10
        set i is i + 1
    return damage
```

```pengu
# Ejemplo 2 — una mano de cartas distintas
import raylib
import raylibx.random as random

weave main into int:
    calling raylib.SetRandomSeed with (calling raylib.GetTime to u32)
    var hand as maybe list of int is calling random.sequence with 5, 1, 52
    if hand is present:
        var cards as list of int is calling hand.unwrap
        defer banish cards
        return cards.length
    return 0
```

### 🧪 Plan de tests

**Seis tests, y ninguno abre ventana** — los primeros tests de capa 2 que no necesitan contexto gráfico alguno, que es en sí la propiedad más clara de la familia.

- **`between` se queda dentro de un rango inclusivo y alcanza ambos extremos** — 64 extracciones con semilla fija, siguiendo el mínimo y el máximo observados, que deben ser exactamente `1` y `6`.
- **`between` intercambia en silencio** — 64 extracciones con rango invertido, cada una asegurada dentro de `[1, 10]`, fijando M3.
- **`between` con límites iguales** devuelve ese límite, fijando M4.
- **`sequence` es determinista una vez sembrada, distinta y dentro del rango** — los valores exactos de M5 (`5 4 3 1 2`) con semilla 7.
- **Una secuencia más larga no repite** — 8 valores de `[1, 100]`, comparando cada pareja, porque "los valores nunca se repiten" es el sentido entero de la función.
- **Las peticiones imposibles vuelven como `none`, y el cero como lista vacía** — `count > distintos` (M6), cuenta negativa (M8), rango invertido (M7) y cuenta de cero (M9) en un solo test, porque son los cuatro bordes de la misma decisión.

### 🚫 NO se envuelve (con motivo)

| Regla | Símbolo | Motivo |
|---|---|---|
| §9 fila 8 — configuración global de un solo uso | `SetRandomSeed` | se llama una vez y un renombrado no reduce tokens; la cabecera del módulo apunta a `raylib.SetRandomSeed` por M1 |
| §9 fila 4 — la regla de los `Unload*` | `UnloadRandomSequence` | `sequence` posee y libera el array, así que exponer esto sería invitar a liberar dos veces algo que el llamador nunca recibió |

Auditoría de cobertura: **4 funciones C, 2 envueltas, 2 omitidas, sin restos y sin duplicados.** La familia añade dos nombres de nivel de módulo y no encanta nada, así que el registro de métodos queda intacto. La lista de import de la fachada pasa de trece familias a **catorce**, y `docs/WRAPPER_CONVENTIONS.md` §15 sigue diciendo "los trece `import`" — se registra aquí como un desliz de documentación de una palabra que hay que corregir, no corregido en silencio.
