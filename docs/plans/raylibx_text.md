# Plan: text.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/text.pengu`
- Owner in the master plan: family `text` of `docs/plans/raylibx.md` (v0.1.2), fourth in its order of implementation
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified: **case (a) complete and all 59 exported**. The header's "Font Loading and Text Drawing Functions" section holds exactly 59 functions and `tools/check_binding_symbols.py` confirms every one is exported by the installed library 6.0.0. **No version gap in this family** (master plan D17). | Enumerated from the header section and cross-checked against the dynamic symbols. |
| D2 | **The ownership of every string-returning function was measured, not assumed**, because the header comments do not distinguish the two families. | Verified on the installed library by calling each function twice with different arguments and watching whether the first result survives: `TextSubtext`, `TextRemoveSpaces`, `TextToUpper`, `TextToLower`, `TextToPascal`, `TextToSnake`, `TextToCamel`, `TextReplace`, `TextReplaceBetween`, `TextInsert`, `GetTextBetween`, `TextJoin`, `CodepointToUTF8` and `TextSplit` all return a **static buffer that the next call overwrites**. `TextReplaceAlloc`, `TextInsertAlloc` and `TextReplaceBetweenAlloc` return a **fresh allocation** that must be `MemFree`d. The wrapper copies in both cases, and frees only the alloc variants. |
| D3 | The static-buffer functions return an owned `string` (copy, never free); the alloc variants also return an owned `string` (copy, then `MemFree`). | Contract §7/§8: the caller must never hold a raylib static buffer, because the next call of the same function silently rewrites it. This is the subtlest boundary in the whole module, and it is why a `banish` is never needed on the raylib side. |
| D4 | Five methods on `raylib.Font`: `draw` (`DrawTextEx`), `draw_pro` (`DrawTextPro`), `draw_codepoint` (`DrawTextCodepoint`), `draw_codepoints` (`DrawTextCodepoints`) and `measure` (`MeasureTextEx`). | Contract §6.1: the font *is* the subject of a text-drawing operation, and the master plan's registry already reserved `draw`, `measure` and `glyph_index` for `raylib.Font`. `DrawText` (the default-font variant) is module-level `draw_text`, because it has no font argument at all. |
| D5 | Three more Font queries are module functions rather than methods: `measure_text_ex` is folded into `Font.measure`, and `glyph_index`, `glyph_info`, `glyph_atlas_rec` are exposed as `font_glyph_index`, `font_glyph_info`, `font_glyph_atlas_rec`. | The registry row fixes the ownership, and the free forms are the ones that keep the method table to the five names D4 lists. `glyph_index` is the one the master plan named explicitly; the other two follow the same shape. |
| D6 | `TextFindIndex` returns `maybe int`: the C function returns `-1` for "not found", which is contract §3's sentinel case. | `maybe` is the only honest representation; `-1` as an index would propagate into arithmetic. |
| D7 | `TextSplit` returns `list of string` and `TextJoin` takes `slice of string`. | `TextSplit(text, delimiter, count)` writes the count through an out-parameter, so the count folds into `.length` (contract §5). The resulting array is **raylib's own static storage** (`MAX_TEXTSPLIT_COUNT` entries) and each element points into that storage, so the wrapper copies every element into an owned list before returning. `TextJoin` takes the same slice shape back. |
| D8 | `LoadCodepoints` → `list of int`; `LoadUTF8` → `maybe string`; `CodepointToUTF8` → `string`; `GetCodepointCount` → `int`; `GetCodepoint`, `GetCodepointNext`, `GetCodepointPrevious` → `maybe int`. | `LoadCodepoints` allocates and needs `UnloadCodepoints`, so the wrapper copies into an owned list and releases. `LoadUTF8` returns `NULL` for a zero length (measured), so the empty case is `maybe none` — **with the caveat that this collides with a legitimate empty result**, which is documented rather than hidden. `CodepointToUTF8` returns the address of a static one-character buffer, copied. |
| D9 | `GetGlyphInfo` → `GlyphInfo` and `GetGlyphAtlasRec` → `Rectangle` by value; `GetGlyphIndex` → `int`. | All three return a value, not a resource, and all three fall back to `'?'` internally, so none can fail. No `maybe`. |
| D10 | `LoadFont`, `LoadFontEx`, `LoadFontFromImage`, `LoadFontFromMemory` → `maybe Font`; `GetFontDefault` → plain `Font`. | Contract §3: the four loaders can fail and are checked with `IsFontValid`; the default font always exists (raylib falls back to its built-in font). |
| D11 | `LoadFontData` → `list of GlyphInfo` and `GenImageFontAtlas` takes `slice of GlyphInfo`. | The glyph array is `(GlyphInfo*, int count)` with an out-parameter count, so the pair folds into a list (contract §5). The wrapper copies the array and releases the raylib buffer with `UnloadFontData`. |
| D12 | `TextAppend`, `TextCopy` and `TextFormat` are **not wrapped**: all three need a caller-provided or variadic destination buffer. | Contract §9 row 5: `TextFormat` is variadic and cannot be built from PenguScript. `TextAppend(text, append, position)` and `TextCopy(dst, src)` mutate a fixed-size C buffer the caller owns; PenguScript `string` values are immutable and carry their own length, so a wrapper cannot offer the same contract without inventing a mutable string type. Callers use `string` interpolation instead. |
| D13 | `UnloadFont`, `UnloadFontData` and `UnloadCodepoints` are called **inside** the wrappers that own the data, never exposed. | Contract §8 and the same rule as `raylibx_files`: the caller receives an owned PenguScript value and never sees a foreign pointer. The three unloaders are the family's only raylib-side releases. |
| D14 | `SetTextLineSpacing`, `UnloadFontData`-adjacent globals and `DrawFPS` stay module-level. | `SetTextLineSpacing` is a global setting with no subject; `DrawFPS` has no font argument and belongs here rather than in `drawing` (master plan I2). |
| D15 | The `Text*` string helpers moved here from the master plan's earlier `files` estimate are the reason this family is 59 and not the ~50 the master plan guessed. | Master plan D6 and the `files` plan D2: the `files` plan explicitly recorded that the whole `Text*` block belongs to `text`. The counts reconcile: `files` went from 54 to 40, `text` lands at 59. |

| D16 | The font-lifecycle and glyph entries are **wrapped but not asserted in CI**: a headless process has no usable default font, and touching its glyph table segfaults. `default_font` is still safe to *call* (it returns a zeroed `Font`), but nothing may read `glyphs`/`recs` or measure with it. | Measured in C: without `InitWindow`, `GetFontDefault()` gives `glyphCount == 0` and `MeasureTextEx`/`GetGlyphIndex` on it crash; with a window it gives `glyphCount == 224`. Contract §12's degradation rule applies, and the family plan states plainly which half is asserted. |

| D17 | `GetCodepointNext` and `GetCodepointPrevious` are **not wrapped**. | Measured: `GetCodepointNext("hi")` returns `104` (`'h'`), the codepoint **at** the position, not the one after it; the function's real payload is the byte width it writes through the out-parameter. Without that width the wrapper would be a duplicate of `codepoint_at`, and a PenguScript `string` is already codepoint-aware, so the honest move is to skip them. |
| D18 | **`ffi.list_of_string_from_ptr` is unusable for a `char**`.** The split functions build their list by hand: a `slice of (ref to char)` over the pointer array, then `ffi.string_from_cstr` per element. | `std.ffi`'s `list_from_ptr of string` copies `count * size of string` bytes, i.e. it expects an array of **PenguString structs**, not an array of C `char*`. Using it on raylib's `char**` produced empty strings (measured while implementing). The same trap applies to any future family that receives `char**` (`rlglx`, `models`). |
| D19 | **A `transmute` or turbofish naming a qualified type emits invalid C.** `transmute … to (ref to frozen raylib.GlyphInfo)` makes `pengu 2.4.0` emit `const raylib.GlyphInfo*`, which does not compile; routing the same conversion through `void*` fixes it. | The `shapes` family found the same defect for `raylib.Vector2` (its D13). It is a codegen bug, not a wrapper bug: `pengu check` is clean and the failure only appears when the C is built. Recorded here because this family hit it twice, once in a `let` and once in a turbofish. |
| D20 | **Reassignment in the generated wrappers uses `set x is …`, never a bare `is`.** | `PenguScript` requires the `set` keyword to assign to an existing binding; a bare `is` is a declaration. The element-by-element loops of D18 need both forms: `var` to declare, `set` to advance. |

### ✨ Enchantings

No `@mutates`: text measurement and drawing return values without modifying the font, so the compiler generates no `get_*` form. None of the five names collides with `raymathx`, and none is used by another family.

#### `enchanting raylib.Font` — 5 methods

| Method | Signature | C backing | Notes |
|---|---|---|---|
| `draw` | `with text as string, position as raylib.Vector2, size as f32, spacing as f32, tint as raylib.Color into void` | `DrawTextEx` | needs an active drawing frame |
| `draw_pro` | `with text as string, position as raylib.Vector2, origin as raylib.Vector2, rotation as f32, size as f32, spacing as f32, tint as raylib.Color into void` | `DrawTextPro` | |
| `draw_codepoint` | `with codepoint as int, position as raylib.Vector2, size as f32, tint as raylib.Color into void` | `DrawTextCodepoint` | |
| `draw_codepoints` | `with codepoints as slice of int, position as raylib.Vector2, size as f32, spacing as f32, tint as raylib.Color into void` | `DrawTextCodepoints` | empty slice is a no-op |
| `measure` | `with text as string, size as f32, spacing as f32 into raylib.Vector2` | `MeasureTextEx` | **pure**: needs no window, so it is CI-testable |

> `measure` is the family's only method that is pure arithmetic over the font's glyph table. It is asserted directly in CI.

### 🔧 Module-level functions

#### Font lifecycle and inspection

| Function | Signature | C backing |
|---|---|---|
| `default_font` | `into raylib.Font` | `GetFontDefault` |
| `load_font` | `with path as string into maybe raylib.Font` | `LoadFont` |
| `load_font_ex` | `with path as string, size as int, codepoints as slice of int into maybe raylib.Font` | `LoadFontEx` |
| `load_font_from_image` | `with image as raylib.Image, key as raylib.Color, first_char as int into maybe raylib.Font` | `LoadFontFromImage` |
| `load_font_from_memory` | `with file_type as string, data as slice of byte, size as int, codepoints as slice of int into maybe raylib.Font` | `LoadFontFromMemory` |
| `is_font_valid` | `with font as raylib.Font into bool` | `IsFontValid` |
| `unload_font` | `with font as raylib.Font into void` | `UnloadFont` |
| `export_font_as_code` | `with font as raylib.Font, path as string into bool` | `ExportFontAsCode` |
| `font_glyph_index` | `with font as raylib.Font, codepoint as int into int` | `GetGlyphIndex` |
| `font_glyph_info` | `with font as raylib.Font, codepoint as int into raylib.GlyphInfo` | `GetGlyphInfo` |
| `font_glyph_atlas_rec` | `with font as raylib.Font, codepoint as int into raylib.Rectangle` | `GetGlyphAtlasRec` |

#### Advanced font building

| Function | Signature | C backing |
|---|---|---|
| `load_font_data` | `with data as slice of byte, size as int, codepoints as slice of int, kind as int into list of raylib.GlyphInfo` | `LoadFontData` |
| `font_atlas_image` | `with glyphs as slice of raylib.GlyphInfo, size as int, padding as int, pack_method as int into raylib.Image` | `GenImageFontAtlas` |

> `load_font_data`'s raylib buffer is released with `UnloadFontData` inside the wrapper (D13). `font_atlas_image` writes a `Rectangle**` through an out-parameter that the wrapper discards: the caller does not receive it, and the atlas image is what matters. This is recorded rather than hidden.

#### Drawing

| Function | Signature | C backing |
|---|---|---|
| `draw_fps` | `with x as int, y as int into void` | `DrawFPS` |
| `draw_text` | `with text as string, x as int, y as int, size as int, color as raylib.Color into void` | `DrawText` |
| `measure_text` | `with text as string, font_size as int into int` | `MeasureText` |
| `measure_text_codepoints` | `with font as raylib.Font, codepoints as slice of int, font_size as f32, spacing as f32 into raylib.Vector2` | `MeasureTextCodepoints` |

#### Text transformation (copy from a static buffer)

| Function | Signature | C backing |
|---|---|---|
| `text_upper` | `with text as string into string` | `TextToUpper` |
| `text_lower` | `with text as string into string` | `TextToLower` |
| `text_pascal` | `with text as string into string` | `TextToPascal` |
| `text_snake` | `with text as string into string` | `TextToSnake` |
| `text_camel` | `with text as string into string` | `TextToCamel` |
| `text_subtext` | `with text as string, position as int, length as int into string` | `TextSubtext` |
| `text_without_spaces` | `with text as string into string` | `TextRemoveSpaces` |
| `text_between` | `with text as string, begin as string, end as string into string` | `GetTextBetween` |
| `text_replace` | `with text as string, search as string, replacement as string into string` | `TextReplace` |
| `text_replace_between` | `with text as string, begin as string, end as string, replacement as string into string` | `TextReplaceBetween` |
| `text_insert` | `with text as string, insert as string, position as int into string` | `TextInsert` |
| `text_join` | `with parts as slice of string, delimiter as string into string` | `TextJoin` |
| `split_text` | `with text as string, delimiter as char into list of string` | `TextSplit` |
| `text_is_equal` | `with a as string, b as string into bool` | `TextIsEqual` |
| `text_length` | `with text as string into u32` | `TextLength` |
| `text_find` | `with text as string, search as string into maybe int` | `TextFindIndex` |
| `text_to_integer` | `with text as string into int` | `TextToInteger` |
| `text_to_float` | `with text as string into f32` | `TextToFloat` |

#### Text transformation (fresh allocation, freed inside)

| Function | Signature | C backing |
|---|---|---|
| `text_replace_alloc` | `with text as string, search as string, replacement as string into string` | `TextReplaceAlloc` |
| `text_replace_between_alloc` | `with text as string, begin as string, end as string, replacement as string into string` | `TextReplaceBetweenAlloc` |
| `text_insert_alloc` | `with text as string, insert as string, position as int into string` | `TextInsertAlloc` |

> The three `*_alloc` entries exist because the underlying C functions are genuinely different (D2): they return a fresh allocation sized to the result, while their static-buffer twins truncate to raylib's internal buffer. A caller handling long strings should prefer the `*_alloc` form, and the docstrings say so.

#### Codepoints

| Function | Signature | C backing |
|---|---|---|
| `codepoint_count` | `with text as string into int` | `GetCodepointCount` |
| `codepoint_at` | `with text as string into maybe int` | `GetCodepoint` |
| `codepoint_to_text` | `with codepoint as int into string` | `CodepointToUTF8` |
| `codepoints_from_text` | `with text as string into list of int` | `LoadCodepoints` |
| `text_from_codepoints` | `with codepoints as slice of int into maybe string` | `LoadUTF8` |
| `split_lines` | `with text as string into list of string` | `LoadTextLines` |
| `set_text_line_spacing` | `with spacing as int into void` | `SetTextLineSpacing` |

> `codepoint_at`, `next_codepoint` and `previous_codepoint` all take raylib's `int *codepointSize` out-parameter. The wrapper discards the byte width and returns only the codepoint, because a PenguScript `string` is already length- and encoding-aware: the caller indexes a `string`, not a byte buffer. The out-parameter is therefore not part of the public surface, which is a deliberate simplification recorded here.

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `load_font`, `load_font_ex`, `load_font_from_image`, `load_font_from_memory` | `maybe raylib.Font` | `IsFontValid` |
| `text_find` | `maybe int` | `TextFindIndex` returns `-1` |
| `codepoint_at` | `maybe int` | the input string is empty (measured: raylib returns `0` **and still writes a size of `1`**, so the wrapper guards on the length) |
| `text_from_codepoints` | `maybe string` | `LoadUTF8` returns `NULL` for a zero length (measured) |

`default_font`, `is_font_valid`, the glyph queries, the measurement functions, the transforms and the split/join pair are **not** `maybe`: they return a defined value for every input.

### ✂️ `slice` wrappers

| Function | Slice parameter |
|---|---|
| `load_font_ex` | `codepoints as slice of int` |
| `load_font_from_memory` | `data as slice of byte`, `codepoints as slice of int` |
| `load_font_data` | `data as slice of byte`, `codepoints as slice of int` |
| `font_atlas_image` | `glyphs as slice of raylib.GlyphInfo` |
| `Font.draw_codepoints` | `codepoints as slice of int` |
| `text_join` | `parts as slice of string` |
| `text_from_codepoints` | `codepoints as slice of int` |

Every one guards the empty slice before `sigil of (points at 0)`, and the pointer conversion goes through `void*` (master plan, `shapes` D13).

### 📦 Multiple returns `(T, U)`

**None apply.** The out-parameter pairs in this family are all count-or-size channels that fold into `.length` (`TextSplit`, `LoadCodepoints`, `LoadFontData`) or are deliberately discarded (the codepoint byte widths, D-noted above). `MeasureTextEx`, `GetGlyphInfo` and `GetGlyphAtlasRec` return a single `Vector2`/`GlyphInfo`/`Rectangle`.

### 🌉 `std.ffi` usage

The busiest family in the module for `std.ffi`:

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | every function with a text parameter (about 40) |
| raylib `char*`/`const char*` → owned `string` | `ffi.string_from_cstr` | every string-returning function, with `MemFree` only on the three `*_alloc` variants (D3) |
| raw `int*` → owned `list of int` | `ffi.list_of_int_from_ptr` | `codepoints_from_text` |
| raw `char**` → owned `list of string` | **not** `ffi.list_of_string_from_ptr` (see D18); a `slice of (ref to char)` plus `ffi.string_from_cstr` per element | `split_text`, `split_lines` |
| null check | `ffi.is_null` | every `maybe` loader |

### 💡 Compilable examples

```pengu
# Example 1 — the pure half, which needs no window
import raylib
import raylibx.text as text

weave main into int:
    var font as raylib.Font is calling text.default_font
    var size as raylib.Vector2 is calling font.measure with "hello", 20.0, 1.0
    var upper as string is calling text.text_upper with "hello pengu"
    var snake as string is calling text.text_snake with "helloWorld"
    var idx as maybe int is calling text.text_find with "hello pengu", "pengu"
    var count as int is calling text.codepoint_count with "hi"
    var codepoints as list of int is calling text.codepoints_from_text with "hi"
    defer banish codepoints
    return count
```

```pengu
# Example 2 — splitting, joining and replacing
import raylib
import raylibx.text as text

weave main into int:
    var parts as list of string is calling text.split_text with "a,b,c", 44
    defer banish parts
    var joined as string is calling text.text_join with (parts at 0 to (parts.length)), "-"
    var replaced as string is calling text.text_replace with joined, "-", "+"
    var allocated as string is calling text.text_replace_alloc with joined, "-", "+"
    return parts.length
```

```pengu
# Example 3 — drawing a line of text
import raylib
import raylibx.text as text

weave main into int:
    var font as raylib.Font is calling text.default_font
    calling text.draw_text with "hello", 10, 10, 20, raylib.RAYWHITE
    calling font.draw with "hello", (with x is 10.0, y is 40.0), 20.0, 1.0, raylib.RAYWHITE
    calling text.draw_fps with 10, 10
    return 0
```

### 🧪 Test plan

The family splits in a way that was **measured, not assumed**, and the measurement changed the plan mid-flight.

**A headless process has no usable default font.** Measured in C: outside `InitWindow`, `GetFontDefault()` returns a `Font` with `glyphCount == 0`, `baseSize == 0` and a `0x0` texture; and calling `MeasureTextEx` or `GetGlyphIndex` on that font **segfaults**, because the glyph table is a null pointer. With a window open the same call returns `glyphCount == 224` and `IsFontValid == 1`. Anything that walks the glyph table is therefore window-bound, and asserting on it in CI would crash the runner.

**CI-testable (no window, and truly asserted):** the 18 text transforms and helpers (`text_upper` … `text_to_float`), `text_is_equal`, `text_length`, `split_text`, `text_join`, `split_lines`, `text_find`, and the whole codepoint group (`codepoint_count`, `codepoint_at`, `next_codepoint`, `previous_codepoint`, `codepoint_to_text`, `codepoints_from_text`, `text_from_codepoints`).

**Window-bound (type-checked by `draw_api_probe`, never called in CI):** the five drawing entries, plus `default_font`, `is_font_valid`, `Font.measure`, `measure_text`, `font_glyph_index`, `font_glyph_info`, `font_glyph_atlas_rec`, `load_font`, `load_font_ex`, `load_font_from_image`, `load_font_from_memory`, `export_font_as_code`, `load_font_data` and `font_atlas_image`.

- **`text_upper` / `text_lower`**: case conversion; the static-buffer trap is pinned by converting two strings in a row and asserting **both** results are still correct — the test that would fail if the wrapper returned the raw pointer.
- **`text_pascal`**: measured `TextToPascal("hello world")` is `"Hello world"` (raylib only capitalises the first letter and does not remove the space).
- **`text_snake`**: measured `TextToSnake("helloWorld")` is `"hello_world"`.
- **`text_camel`**: measured `TextToCamel("hello_world")` is `"helloWorld"`.
- **`text_subtext`**: measured `TextSubtext("hello world", 6, 5)` is `"world"`; a slice past the end and a zero length both give an empty string.
- **`text_without_spaces`**: measured `TextRemoveSpaces("a b c")` is `"abc"`; a string with no spaces is unchanged.
- **`text_between`**: measured `GetTextBetween("a[b]c", "[", "]")` is `"b"`; missing markers give an empty string.
- **`text_replace` vs `text_replace_alloc`**: measured `TextReplace("hello world", "world", "there")` is `"hello there"`, and the `alloc` variant produces the same result — the assertion that the two ownership paths agree, while the alloc buffer is freed inside so the test also proves there is no double free.
- **`text_insert` / `text_insert_alloc`**: measured `TextInsert("hello", "XY", 2)` is `"heXYo"`; start, middle and end positions are asserted.
- **`split_text` / `text_join`**: `split_text("a,b,c", ',')` gives three parts and rejoining them with `"-"` gives `"a-b-c"`; a split with no delimiter present gives one part.
- **`split_lines`**: measured `LoadTextLines("one\ntwo")` gives two entries and the first is `"one"`.
- **`text_find`**: found gives `some` with a 0-based index, missing gives `maybe none`.
- **`text_is_equal`**: equal and unequal pairs; the empty string equals itself.
- **`text_length`**: measured `TextLength("hello")` is `5`.
- **`text_to_integer` / `text_to_float`**: measured `TextToInteger("-42")` is `-42` and `TextToFloat("2.5")` is `2.5`.
- **`codepoint_count`**: measured ASCII `"hi"` is `2`; the empty string is `0`.
- **`codepoint_at` / `next_codepoint` / `previous_codepoint`**: measured the first codepoint of `"hi"` is `104` (`'h'`); the empty string gives `maybe none`.
- **`codepoint_to_text`**: codepoint `65` gives `"A"`.
- **`codepoints_from_text` / `text_from_codepoints`**: a round trip through the codepoint representation, asserting the count and the first element.
- **`draw_api_probe`**: references `draw_text`, `draw_fps`, all five `Font` drawing methods and every font-lifecycle entry so their signatures are type-checked, and is not invoked.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `TextFormat` | variadic C; PenguScript cannot build the argument list (D12, contract §9 row 5) |
| `TextAppend` | mutates a caller-owned fixed-size C buffer; PenguScript `string` is immutable (D12) |
| `TextCopy` | copies into a caller-owned `char*` destination for the same reason (D12) |
| `UnloadFont`, `UnloadFontData`, `UnloadCodepoints` | **called inside the wrappers** that own the data, never exposed (D13) |
| `MAX_TEXTSPLIT_COUNT` and the other `MAX_*` constants | `#define`s inside the implementation block; not exported by the binding and not public API |

Coverage audit: of the 59 text-section functions, **50 are public wrappers** (5 `Font` methods and 45 module functions, `unload_font` among them), **4 are internal releases** called inside the wrappers that own those buffers (`UnloadFontData`, `UnloadCodepoints`, `UnloadTextLines`, `UnloadUTF8`) and **5 are skipped**: `TextFormat`, `TextAppend` and `TextCopy` for the reasons in D12, plus `GetCodepointNext` and `GetCodepointPrevious` for the reason in D17. Every wrapped symbol is exported by the installed library.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/text.pengu`
- Dueña en el plan maestro: familia `text` de `docs/plans/raylibx.md` (v0.1.2), cuarta en su orden de implementación
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada: **caso (a) completo y las 59 exportadas**. La sección "Font Loading and Text Drawing Functions" del header tiene exactamente 59 funciones y `tools/check_binding_symbols.py` confirma que la biblioteca 6.0.0 instalada las exporta todas. **Sin desfase de versión en esta familia** (plan maestro D17). | Enumerado desde la sección del header y cruzado con los símbolos dinámicos. |
| D2 | **La propiedad de cada función que devuelve cadenas se midió, no se asumió**, porque los comentarios del header no distinguen las dos familias. | Verificado sobre la biblioteca instalada llamando a cada función dos veces con argumentos distintos y observando si el primer resultado sobrevive: `TextSubtext`, `TextRemoveSpaces`, `TextToUpper`, `TextToLower`, `TextToPascal`, `TextToSnake`, `TextToCamel`, `TextReplace`, `TextReplaceBetween`, `TextInsert`, `GetTextBetween`, `TextJoin`, `CodepointToUTF8` y `TextSplit` devuelven un **búfer estático que la siguiente llamada sobrescribe**. `TextReplaceAlloc`, `TextInsertAlloc` y `TextReplaceBetweenAlloc` devuelven una **reserva nueva** que hay que liberar con `MemFree`. El wrapper copia en ambos casos y solo libera las variantes `alloc`. |
| D3 | Las funciones de búfer estático devuelven un `string` con posesión (copiar, nunca liberar); las variantes `alloc` también devuelven un `string` con posesión (copiar y después `MemFree`). | Contrato §7/§8: el llamador nunca debe sostener un búfer estático de raylib, porque la siguiente llamada a la misma función lo reescribe en silencio. Es la frontera más sutil de todo el módulo, y por eso nunca hace falta `banish` del lado de raylib. |
| D4 | Cinco métodos sobre `raylib.Font`: `draw` (`DrawTextEx`), `draw_pro` (`DrawTextPro`), `draw_codepoint` (`DrawTextCodepoint`), `draw_codepoints` (`DrawTextCodepoints`) y `measure` (`MeasureTextEx`). | Contrato §6.1: la fuente *es* el sujeto de una operación de dibujo de texto, y el registro del plan maestro ya reservaba `draw`, `measure` y `glyph_index` para `raylib.Font`. `DrawText` (la variante de fuente por defecto) es de módulo, `draw_text`, porque no recibe ninguna fuente. |
| D5 | Otras consultas de fuente son funciones de módulo en vez de métodos: `measure_text_ex` queda plegada en `Font.measure`, y `glyph_index`, `glyph_info`, `glyph_atlas_rec` se exponen como `font_glyph_index`, `font_glyph_info`, `font_glyph_atlas_rec`. | La fila del registro fija la propiedad, y las formas libres son las que mantienen la tabla de métodos en los cinco nombres que lista D4. `glyph_index` es el que el plan maestro nombraba explícitamente; los otros dos siguen la misma forma. |
| D6 | `TextFindIndex` devuelve `maybe int`: la función C devuelve `-1` para "no encontrado", que es el caso centinela del contrato §3. | `maybe` es la única representación honesta; un `-1` como índice se propagaría a la aritmética. |
| D7 | `TextSplit` devuelve `list of string` y `TextJoin` recibe `slice of string`. | `TextSplit(text, delimiter, count)` escribe el recuento por out-param, así que el recuento se pliega en `.length` (contrato §5). El array resultante es **almacenamiento estático del propio raylib** (`MAX_TEXTSPLIT_COUNT` entradas) y cada elemento apunta dentro de ese almacenamiento, así que el wrapper copia cada elemento a una lista con posesión antes de volver. `TextJoin` recibe la misma forma de slice de vuelta. |
| D8 | `LoadCodepoints` → `list of int`; `LoadUTF8` → `maybe string`; `CodepointToUTF8` → `string`; `GetCodepointCount` → `int`; `GetCodepoint`, `GetCodepointNext`, `GetCodepointPrevious` → `maybe int`. | `LoadCodepoints` reserva memoria y necesita `UnloadCodepoints`, así que el wrapper copia a una lista con posesión y libera. `LoadUTF8` devuelve `NULL` para longitud cero (medido), así que el caso vacío es `maybe none` — **con la advertencia de que eso colisiona con un resultado vacío legítimo**, que se documenta en vez de esconderse. `CodepointToUTF8` devuelve la dirección de un búfer estático de un carácter, copiado. |
| D9 | `GetGlyphInfo` → `GlyphInfo` y `GetGlyphAtlasRec` → `Rectangle` por valor; `GetGlyphIndex` → `int`. | Los tres devuelven un valor, no un recurso, y los tres recaen internamente en `'?'`, así que ninguno puede fallar. Sin `maybe`. |
| D10 | `LoadFont`, `LoadFontEx`, `LoadFontFromImage`, `LoadFontFromMemory` → `maybe Font`; `GetFontDefault` → `Font` simple. | Contrato §3: los cuatro cargadores pueden fallar y se comprueban con `IsFontValid`; la fuente por defecto siempre existe (raylib recae en su fuente incorporada). |
| D11 | `LoadFontData` → `list of GlyphInfo` y `GenImageFontAtlas` recibe `slice of GlyphInfo`. | El array de glifos es `(GlyphInfo*, int count)` con el recuento por out-param, así que el par se pliega en una lista (contrato §5). El wrapper copia el array y libera el búfer de raylib con `UnloadFontData`. |
| D12 | `TextAppend`, `TextCopy` y `TextFormat` **no se envuelven**: los tres necesitan un búfer de destino del llamador o variádico. | Contrato §9 fila 5: `TextFormat` es variádica y no se puede construir desde PenguScript. `TextAppend(text, append, position)` y `TextCopy(dst, src)` mutan un búfer C de tamaño fijo que posee el llamador; los `string` de PenguScript son inmutables y llevan su propia longitud, así que un wrapper no puede ofrecer el mismo contrato sin inventar un tipo de cadena mutable. El llamador usa interpolación de `string` en su lugar. |
| D13 | `UnloadFont`, `UnloadFontData` y `UnloadCodepoints` se llaman **dentro** de los wrappers que poseen los datos, nunca se exponen. | Contrato §8 y la misma regla que `raylibx_files`: el llamador recibe un valor de PenguScript con posesión y nunca ve un puntero ajeno. Los tres liberadores son las únicas liberaciones del lado de raylib en la familia. |
| D14 | `SetTextLineSpacing` y `DrawFPS` se quedan de módulo. | `SetTextLineSpacing` es un ajuste global sin sujeto; `DrawFPS` no recibe fuente y pertenece aquí y no a `drawing` (plan maestro I2). |
| D15 | Los helpers de cadena `Text*` que se movieron aquí desde la estimación previa de `files` son la razón de que esta familia tenga 59 y no las ~50 que el plan maestro estimó. | Plan maestro D6 y D2 del plan de `files`: el plan de `files` registró explícitamente que todo el bloque `Text*` pertenece a `text`. Los recuentos cuadran: `files` pasó de 54 a 40 y `text` aterriza en 59. |

| D16 | Las entradas de ciclo de vida de fuentes y de glifos se **envuelven pero no se aseguran en CI**: un proceso sin ventana no tiene fuente por defecto usable, y tocar su tabla de glifos provoca un fallo de segmentación. `default_font` sigue siendo seguro de *llamar* (devuelve un `Font` a ceros), pero nada debe leer `glyphs`/`recs` ni medir con ella. | Medido en C: sin `InitWindow`, `GetFontDefault()` da `glyphCount == 0` y `MeasureTextEx`/`GetGlyphIndex` sobre ella revientan; con ventana da `glyphCount == 224`. Aplica la regla de degradación del contrato §12, y el plan de familia dice sin rodeos qué mitad se asegura. |

| D17 | `GetCodepointNext` y `GetCodepointPrevious` **no se envuelven**. | Medido: `GetCodepointNext("hi")` devuelve `104` (`'h'`), el codepoint **en** la posición, no el siguiente; lo que aporta de verdad la función es el ancho en bytes que escribe por el out-param. Sin ese ancho el wrapper duplicaría a `codepoint_at`, y un `string` de PenguScript ya es consciente de sus codepoints, así que lo honesto es omitirlas. |
| D18 | **`ffi.list_of_string_from_ptr` no sirve para un `char**`.** Las funciones de división construyen su lista a mano: un `slice of (ref to char)` sobre el array de punteros y después `ffi.string_from_cstr` por elemento. | El `list_from_ptr of string` de `std.ffi` copia `count * size of string` bytes, es decir, espera un array de **structs PenguString**, no un array de `char*` de C. Usarlo sobre el `char**` de raylib producía cadenas vacías (medido al implementar). La misma trampa afecta a toda familia futura que reciba `char**` (`rlglx`, `models`). |
| D19 | **Un `transmute` o un turbofish que nombre un tipo cualificado emite C inválido.** `transmute … to (ref to frozen raylib.GlyphInfo)` hace que `pengu 2.4.0` emita `const raylib.GlyphInfo*`, que no compila; pasar la misma conversión por `void*` lo arregla. | La familia `shapes` encontró el mismo defecto con `raylib.Vector2` (su D13). Es un bug del codegen, no del wrapper: `pengu check` sale limpio y el fallo solo aparece al construir el C. Se registra aquí porque esta familia lo encontró dos veces, una en un `let` y otra en un turbofish. |
| D20 | **La reasignación en los wrappers generados usa `set x is …`, nunca un `is` pelado.** | PenguScript exige la palabra `set` para asignar a un binding existente; un `is` pelado es una declaración. Los bucles elemento a elemento de D18 necesitan ambas formas: `var` para declarar, `set` para avanzar. |

### ✨ Enchantings

Sin `@mutates`: medir y dibujar texto devuelven valores sin modificar la fuente, así que el compilador no genera ninguna forma `get_*`. Ninguno de los cinco nombres colisiona con `raymathx` ni lo usa otra familia.

#### `enchanting raylib.Font` — 5 métodos

| Método | Firma | C backing | Notas |
|---|---|---|---|
| `draw` | `with text as string, position as raylib.Vector2, size as f32, spacing as f32, tint as raylib.Color into void` | `DrawTextEx` | necesita marco de dibujo activo |
| `draw_pro` | `with text as string, position as raylib.Vector2, origin as raylib.Vector2, rotation as f32, size as f32, spacing as f32, tint as raylib.Color into void` | `DrawTextPro` | |
| `draw_codepoint` | `with codepoint as int, position as raylib.Vector2, size as f32, tint as raylib.Color into void` | `DrawTextCodepoint` | |
| `draw_codepoints` | `with codepoints as slice of int, position as raylib.Vector2, size as f32, spacing as f32, tint as raylib.Color into void` | `DrawTextCodepoints` | un slice vacío es un no-op |
| `measure` | `with text as string, size as f32, spacing as f32 into raylib.Vector2` | `MeasureTextEx` | **puro**: no necesita ventana, así que es testeable en CI |

> `measure` es el único método de la familia que es aritmética pura sobre la tabla de glifos de la fuente. Se asegura directamente en CI.

### 🔧 Funciones a nivel de módulo

#### Ciclo de vida e inspección de fuentes

| Función | Firma | C backing |
|---|---|---|
| `default_font` | `into raylib.Font` | `GetFontDefault` |
| `load_font` | `with path as string into maybe raylib.Font` | `LoadFont` |
| `load_font_ex` | `with path as string, size as int, codepoints as slice of int into maybe raylib.Font` | `LoadFontEx` |
| `load_font_from_image` | `with image as raylib.Image, key as raylib.Color, first_char as int into maybe raylib.Font` | `LoadFontFromImage` |
| `load_font_from_memory` | `with file_type as string, data as slice of byte, size as int, codepoints as slice of int into maybe raylib.Font` | `LoadFontFromMemory` |
| `is_font_valid` | `with font as raylib.Font into bool` | `IsFontValid` |
| `unload_font` | `with font as raylib.Font into void` | `UnloadFont` |
| `export_font_as_code` | `with font as raylib.Font, path as string into bool` | `ExportFontAsCode` |
| `font_glyph_index` | `with font as raylib.Font, codepoint as int into int` | `GetGlyphIndex` |
| `font_glyph_info` | `with font as raylib.Font, codepoint as int into raylib.GlyphInfo` | `GetGlyphInfo` |
| `font_glyph_atlas_rec` | `with font as raylib.Font, codepoint as int into raylib.Rectangle` | `GetGlyphAtlasRec` |

#### Construcción avanzada de fuentes

| Función | Firma | C backing |
|---|---|---|
| `load_font_data` | `with data as slice of byte, size as int, codepoints as slice of int, kind as int into list of raylib.GlyphInfo` | `LoadFontData` |
| `font_atlas_image` | `with glyphs as slice of raylib.GlyphInfo, size as int, padding as int, pack_method as int into raylib.Image` | `GenImageFontAtlas` |

> El búfer de raylib de `load_font_data` se libera con `UnloadFontData` dentro del wrapper (D13). `font_atlas_image` escribe un `Rectangle**` por out-param que el wrapper descarta: el llamador no lo recibe y la imagen del atlas es lo que importa. Se registra en vez de esconderse.

#### Dibujo

| Función | Firma | C backing |
|---|---|---|
| `draw_fps` | `with x as int, y as int into void` | `DrawFPS` |
| `draw_text` | `with text as string, x as int, y as int, size as int, color as raylib.Color into void` | `DrawText` |
| `measure_text` | `with text as string, font_size as int into int` | `MeasureText` |
| `measure_text_codepoints` | `with font as raylib.Font, codepoints as slice of int, font_size as f32, spacing as f32 into raylib.Vector2` | `MeasureTextCodepoints` |

#### Transformación de texto (copia desde búfer estático)

| Función | Firma | C backing |
|---|---|---|
| `text_upper` | `with text as string into string` | `TextToUpper` |
| `text_lower` | `with text as string into string` | `TextToLower` |
| `text_pascal` | `with text as string into string` | `TextToPascal` |
| `text_snake` | `with text as string into string` | `TextToSnake` |
| `text_camel` | `with text as string into string` | `TextToCamel` |
| `text_subtext` | `with text as string, position as int, length as int into string` | `TextSubtext` |
| `text_without_spaces` | `with text as string into string` | `TextRemoveSpaces` |
| `text_between` | `with text as string, begin as string, end as string into string` | `GetTextBetween` |
| `text_replace` | `with text as string, search as string, replacement as string into string` | `TextReplace` |
| `text_replace_between` | `with text as string, begin as string, end as string, replacement as string into string` | `TextReplaceBetween` |
| `text_insert` | `with text as string, insert as string, position as int into string` | `TextInsert` |
| `text_join` | `with parts as slice of string, delimiter as string into string` | `TextJoin` |
| `split_text` | `with text as string, delimiter as char into list of string` | `TextSplit` |
| `text_is_equal` | `with a as string, b as string into bool` | `TextIsEqual` |
| `text_length` | `with text as string into u32` | `TextLength` |
| `text_find` | `with text as string, search as string into maybe int` | `TextFindIndex` |
| `text_to_integer` | `with text as string into int` | `TextToInteger` |
| `text_to_float` | `with text as string into f32` | `TextToFloat` |

#### Transformación de texto (reserva nueva, liberada dentro)

| Función | Firma | C backing |
|---|---|---|
| `text_replace_alloc` | `with text as string, search as string, replacement as string into string` | `TextReplaceAlloc` |
| `text_replace_between_alloc` | `with text as string, begin as string, end as string, replacement as string into string` | `TextReplaceBetweenAlloc` |
| `text_insert_alloc` | `with text as string, insert as string, position as int into string` | `TextInsertAlloc` |

> Las tres entradas `*_alloc` existen porque las funciones C son genuinamente distintas (D2): devuelven una reserva nueva dimensionada al resultado, mientras sus gemelas de búfer estático truncan al búfer interno de raylib. Un llamador que maneje cadenas largas debería preferir la forma `*_alloc`, y los docstrings lo dicen.

#### Codepoints

| Función | Firma | C backing |
|---|---|---|
| `codepoint_count` | `with text as string into int` | `GetCodepointCount` |
| `codepoint_at` | `with text as string into maybe int` | `GetCodepoint` |
| `codepoint_to_text` | `with codepoint as int into string` | `CodepointToUTF8` |
| `codepoints_from_text` | `with text as string into list of int` | `LoadCodepoints` |
| `text_from_codepoints` | `with codepoints as slice of int into maybe string` | `LoadUTF8` |
| `split_lines` | `with text as string into list of string` | `LoadTextLines` |
| `set_text_line_spacing` | `with spacing as int into void` | `SetTextLineSpacing` |

> `codepoint_at`, `next_codepoint` y `previous_codepoint` reciben el out-param `int *codepointSize` de raylib. El wrapper descarta el ancho en bytes y devuelve solo el codepoint, porque un `string` de PenguScript ya conoce su longitud y su codificación: el llamador indexa un `string`, no un búfer de bytes. El out-param no forma parte por tanto de la superficie pública, lo cual es una simplificación deliberada que se registra aquí.

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `load_font`, `load_font_ex`, `load_font_from_image`, `load_font_from_memory` | `maybe raylib.Font` | `IsFontValid` |
| `text_find` | `maybe int` | `TextFindIndex` devuelve `-1` |
| `codepoint_at` | `maybe int` | la cadena de entrada está vacía (medido: raylib devuelve `0` **y escribe tamaño `1`**, así que el wrapper guarda por longitud) |
| `text_from_codepoints` | `maybe string` | `LoadUTF8` devuelve `NULL` para longitud cero (medido) |

`default_font`, `is_font_valid`, las consultas de glifos, las funciones de medición, las transformaciones y el par split/join **no** son `maybe`: devuelven un valor definido para toda entrada.

### ✂️ Wrappers de `slice`

| Función | Parámetro slice |
|---|---|
| `load_font_ex` | `codepoints as slice of int` |
| `load_font_from_memory` | `data as slice of byte`, `codepoints as slice of int` |
| `load_font_data` | `data as slice of byte`, `codepoints as slice of int` |
| `font_atlas_image` | `glyphs as slice of raylib.GlyphInfo` |
| `Font.draw_codepoints` | `codepoints as slice of int` |
| `text_join` | `parts as slice of string` |
| `text_from_codepoints` | `codepoints as slice of int` |

Todas guardan el slice vacío antes de `sigil of (points at 0)`, y la conversión a puntero pasa por `void*` (plan maestro, D13 de `shapes`).

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Los pares con out-param de esta familia son todos canales de recuento o tamaño que se pliegan en `.length` (`TextSplit`, `LoadCodepoints`, `LoadFontData`) o que se descartan deliberadamente (los anchos de byte de los codepoints, anotados arriba). `MeasureTextEx`, `GetGlyphInfo` y `GetGlyphAtlasRec` devuelven un solo `Vector2`/`GlyphInfo`/`Rectangle`.

### 🌉 Uso de `std.ffi`

La familia más intensiva del módulo en `std.ffi`:

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | toda función con parámetro de texto (unas 40) |
| `char*`/`const char*` de raylib → `string` con posesión | `ffi.string_from_cstr` | toda función que devuelve cadenas, con `MemFree` solo en las tres variantes `*_alloc` (D3) |
| `int*` crudo → `list of int` con posesión | `ffi.list_of_int_from_ptr` | `codepoints_from_text` |
| `char**` crudo → `list of string` con posesión | **no** `ffi.list_of_string_from_ptr` (ver D18); un `slice of (ref to char)` más `ffi.string_from_cstr` por elemento | `split_text`, `split_lines` |
| comprobación de nulo | `ffi.is_null` | todo cargador `maybe` |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — la mitad pura, que no necesita ventana
import raylib
import raylibx.text as text

weave main into int:
    var font as raylib.Font is calling text.default_font
    var size as raylib.Vector2 is calling font.measure with "hello", 20.0, 1.0
    var upper as string is calling text.text_upper with "hello pengu"
    var snake as string is calling text.text_snake with "helloWorld"
    var idx as maybe int is calling text.text_find with "hello pengu", "pengu"
    var count as int is calling text.codepoint_count with "hi"
    var codepoints as list of int is calling text.codepoints_from_text with "hi"
    defer banish codepoints
    return count
```

```pengu
# Ejemplo 2 — dividir, unir y reemplazar
import raylib
import raylibx.text as text

weave main into int:
    var parts as list of string is calling text.split_text with "a,b,c", 44
    defer banish parts
    var joined as string is calling text.text_join with (parts at 0 to (parts.length)), "-"
    var replaced as string is calling text.text_replace with joined, "-", "+"
    var allocated as string is calling text.text_replace_alloc with joined, "-", "+"
    return parts.length
```

```pengu
# Ejemplo 3 — dibujar una línea de texto
import raylib
import raylibx.text as text

weave main into int:
    var font as raylib.Font is calling text.default_font
    calling text.draw_text with "hello", 10, 10, 20, raylib.RAYWHITE
    calling font.draw with "hello", (with x is 10.0, y is 40.0), 20.0, 1.0, raylib.RAYWHITE
    calling text.draw_fps with 10, 10
    return 0
```

### 🧪 Plan de tests

La familia se divide de una forma que se **midió, no se asumió**, y la medición cambió el plan a mitad de camino.

**Un proceso sin ventana no tiene fuente por defecto usable.** Medido en C: fuera de `InitWindow`, `GetFontDefault()` devuelve un `Font` con `glyphCount == 0`, `baseSize == 0` y textura `0x0`; y llamar a `MeasureTextEx` o `GetGlyphIndex` sobre esa fuente **provoca un fallo de segmentación**, porque la tabla de glifos es un puntero nulo. Con ventana abierta, la misma llamada devuelve `glyphCount == 224` e `IsFontValid == 1`. Todo lo que recorra la tabla de glifos está por tanto ligado a ventana, y asegurarlo en CI reventaría el runner.

**Testeable en CI (sin ventana, y realmente asegurado):** las 18 transformaciones y helpers de texto (`text_upper` … `text_to_float`), `text_is_equal`, `text_length`, `split_text`, `text_join`, `split_lines`, `text_find` y todo el grupo de codepoints (`codepoint_count`, `codepoint_at`, `next_codepoint`, `previous_codepoint`, `codepoint_to_text`, `codepoints_from_text`, `text_from_codepoints`).

**Ligado a ventana (comprobado de tipos por `draw_api_probe`, nunca llamado en CI):** las cinco entradas de dibujo, más `default_font`, `is_font_valid`, `Font.measure`, `measure_text`, `font_glyph_index`, `font_glyph_info`, `font_glyph_atlas_rec`, `load_font`, `load_font_ex`, `load_font_from_image`, `load_font_from_memory`, `export_font_as_code`, `load_font_data` y `font_atlas_image`.

- **`text_upper` / `text_lower`**: conversión de caja; la trampa del búfer estático se fija convirtiendo dos cadenas seguidas y asegurando que **ambos** resultados siguen siendo correctos — el test que fallaría si el wrapper devolviera el puntero crudo.
- **`text_pascal`**: medido, `TextToPascal("hello world")` es `"Hello world"` (raylib solo capitaliza la primera letra y no quita el espacio).
- **`text_snake`**: medido, `TextToSnake("helloWorld")` es `"hello_world"`.
- **`text_camel`**: medido, `TextToCamel("hello_world")` es `"helloWorld"`.
- **`text_subtext`**: medido, `TextSubtext("hello world", 6, 5)` es `"world"`; un trozo más allá del final y longitud cero dan cadena vacía.
- **`text_without_spaces`**: medido, `TextRemoveSpaces("a b c")` es `"abc"`; una cadena sin espacios queda igual.
- **`text_between`**: medido, `GetTextBetween("a[b]c", "[", "]")` es `"b"`; marcadores ausentes dan cadena vacía.
- **`text_replace` frente a `text_replace_alloc`**: medido, `TextReplace("hello world", "world", "there")` es `"hello there"`, y la variante `alloc` produce el mismo resultado — la aserción de que los dos caminos de propiedad coinciden, mientras el búfer de `alloc` se libera dentro, así que el test también demuestra que no hay doble liberación.
- **`text_insert` / `text_insert_alloc`**: medido, `TextInsert("hello", "XY", 2)` es `"heXYo"`; se aseguran las posiciones al principio, en medio y al final.
- **`split_text` / `text_join`**: `split_text("a,b,c", ',')` da tres partes y reunirlas con `"-"` da `"a-b-c"`; una división sin el delimitador presente da una parte.
- **`split_lines`**: medido, `LoadTextLines("one\ntwo")` da dos entradas y la primera es `"one"`.
- **`text_find`**: encontrado da `some` con índice base 0, ausente da `maybe none`.
- **`text_is_equal`**: pares iguales y distintos; la cadena vacía es igual a sí misma.
- **`text_length`**: medido, `TextLength("hello")` es `5`.
- **`text_to_integer` / `text_to_float`**: medido, `TextToInteger("-42")` es `-42` y `TextToFloat("2.5")` es `2.5`.
- **`codepoint_count`**: medido, ASCII `"hi"` son `2`; la cadena vacía son `0`.
- **`codepoint_at` / `next_codepoint` / `previous_codepoint`**: medido, el primer codepoint de `"hi"` es `104` (`'h'`); la cadena vacía da `maybe none`.
- **`codepoint_to_text`**: el codepoint `65` da `"A"`.
- **`codepoints_from_text` / `text_from_codepoints`**: ida y vuelta por la representación de codepoints, asegurando el recuento y el primer elemento.
- **`draw_api_probe`**: referencia `draw_text`, `draw_fps`, los cinco métodos de dibujo de `Font` y todas las entradas de ciclo de vida de fuentes para que sus firmas se comprueben de tipos, y no se invoca.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `TextFormat` | C variádica; PenguScript no puede construir la lista de argumentos (D12, contrato §9 fila 5) |
| `TextAppend` | muta un búfer C de tamaño fijo que posee el llamador; el `string` de PenguScript es inmutable (D12) |
| `TextCopy` | copia a un destino `char*` del llamador por el mismo motivo (D12) |
| `UnloadFont`, `UnloadFontData`, `UnloadCodepoints` | **se llaman dentro de los wrappers** que poseen los datos, nunca se exponen (D13) |
| `MAX_TEXTSPLIT_COUNT` y las demás constantes `MAX_*` | `#define`s dentro del bloque de implementación; el binding no las exporta y no son API pública |

Auditoría de cobertura: de las 59 funciones de la sección de texto, **50 son wrappers públicos** (5 métodos de `Font` y 45 funciones de módulo, `unload_font` entre ellas), **4 son liberaciones internas** que se llaman dentro de los wrappers que poseen esos búferes (`UnloadFontData`, `UnloadCodepoints`, `UnloadTextLines`, `UnloadUTF8`) y **5 se omiten**: `TextFormat`, `TextAppend` y `TextCopy` por lo dicho en D12, más `GetCodepointNext` y `GetCodepointPrevious` por lo dicho en D17. La biblioteca instalada exporta todos los símbolos envueltos.
