> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# random

> Source: `pengu/raylibx/random.pengu`

The azar appendix: two wrappers over raylib's four random functions, and the traps of all four
in one place.

This is the smallest family in the layer, and deliberately so. raylib's random banner is four
functions and, measured against the contract's three-condition criterion (§9), only two of them
earn a wrapper:

    GetRandomValue        -> between     a Get* renamed to a Pengunic noun (criterion 2)
    LoadRandomSequence    -> sequence    folds a NULL sentinel AND an ownership (criteria 1, 2)
    SetRandomSeed         -> skipped     §9 row 8, one-shot global configuration
    UnloadRandomSequence  -> skipped     §9 row 4, `sequence` already owns the array

## Read this before using randomness at all
**Measured: raylib's generator has a fixed default seed, so an unseeded program produces the
same sequence on every run.** Two runs of the same C program printed `6 3 6 1 4 3` and nothing
else changed. Before anything varies, seed it through the binding:

    calling raylib.SetRandomSeed with 12345

`docs/wrappers/raylibx-random.md` records that measurement, and why `seed` itself is not wrapped.

## The other three measured traps
- `between` is **inclusive on both ends** and **silently swaps inverted bounds**: measured,
  `GetRandomValue(10, 1)` returns values in `[1, 10]`.
- `sequence` **does not swap**: measured, `LoadRandomSequence(3, 5, 1)` returns `9 8 7`, values
  outside both bounds. The wrapper turns that into `none` instead of passing garbage on.
- `sequence` cannot repeat a value, so asking for more than the range holds is impossible:
  measured, `LoadRandomSequence(6, 1, 5)` returns **NULL**, which the wrapper folds into `none`.

## Example
```pengu
import raylib
import raylibx.random as random

weave main into int:
    calling raylib.SetRandomSeed with 12345
    var damage as int is calling random.between with 5, 10
    var hand as maybe list of int is calling random.sequence with 5, 1, 5
    return damage
```

---

### `between`

> **between**(min_value: int, max_value: int) -> int

Draws a random integer inside an inclusive range.
Parameters
- `min_value`: the lowest value the result can take, inclusive.
- `max_value`: the highest value the result can take, inclusive.
Returns
A value in `[min_value, max_value]`.
Notes
**The range is inclusive on both ends**, so `between with 1, 6` is a die roll and not a
five-sided one. **Inverted bounds are swapped silently** rather than reported, which is measured
behaviour and not something the wrapper changes: `between with 10, 1` still answers inside
`[1, 10]`. If `min_value` equals `max_value` the result is that value.
**This needs a seed to vary between runs.** Measured, raylib starts from a fixed default seed,
so two runs of the same program return the same numbers until
`raylib.SetRandomSeed` is called; see the module header and `docs/wrappers/raylibx-random.md`.
Memory
No allocation; a single direct C call over raylib's own generator state.
Example
```pengu
var damage as int is calling between with 5, 10
```


### `sequence`

> **sequence**(count: int, min_value: int, max_value: int) -> maybe list of int

Draws a sequence of distinct random integers from a range.
Parameters
- `count`: how many values to draw.
- `min_value`: the lowest value the sequence may contain, inclusive.
- `max_value`: the highest value the sequence may contain, inclusive.
Returns
`some` with an owned list of `count` values in `[min_value, max_value]`, or `maybe none` when
the request cannot be satisfied.
Notes
**The values never repeat**, which is what makes this the way to shuffle a hand of cards or
place distinct spawn points — and what makes the impossible cases possible. `none` is returned
when the request cannot be answered at all:
- `count` is negative, or larger than the range holds — measured, asking for 6 values from
`[1, 5]` makes raylib return a null pointer rather than a short sequence;
- `min_value` is greater than `max_value` — measured, raylib does **not** swap these the way
`between` does, and returns values **outside both bounds** (asking for 3 from `[5, 1]` gave
`9 8 7`), so the wrapper refuses instead of forwarding garbage.
`count` of `0` is not an error: it returns `some` with an empty list, without calling raylib at
all, because raylib's answer for a zero count depends on what `malloc(0)` does.
The C array raylib allocates is copied into an owned list and released here, so the caller never
sees it and can never forget to free it.
**Seeding applies here too**: without `raylib.SetRandomSeed` the same sequence comes back on
every run.
Memory
The list returned is owned by the caller and freed by PenguScript; the C array raylib allocates
is freed by the wrapper, which is why `UnloadRandomSequence` is not wrapped.
Example
```pengu
var hand as maybe list of int is calling sequence with 5, 1, 5
if hand is present:
var first as int is ((calling hand.unwrap) at 0)
```

