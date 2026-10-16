# Plan: files.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-translative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/files.pengu`
- Owner in the master plan: family `files` of `docs/plans/raylibx.md` (v0.1.2), second in its order of implementation
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Binding completeness verified for this bucket: **case (a) complete**. 40 `declare`s match the files family. Of those, **36 are wrapped as public functions**, **8 are the resource releases called inside those wrappers** (`UnloadFileData`, `UnloadFileText`, `UnloadDirectoryFiles`, `UnloadDroppedFiles`, `UnloadUTF8`, `UnloadTextLines` and `MemFree`) and **3 are skipped** (D12). The remaining functions in the earlier estimate were `Text*` helpers, which belong to the `text` family (D2). | Enumerated against `pengu/raylib.d.pengu` (`:948-1180`) and `include/raylib.h` (`:1150-1195`). Nothing missing. |
| D2 | The scope is **file system + raw data + compression/encoding/hash**. The 23 `Text*` helpers (`TextToUpper`, `TextSplit`, `TextJoin`, `TextFindIndex`, …) are **not** here: they belong to the `text` family. | The master plan's own bucket split, and D6 of the master plan ("the family that owns the C function"). Leaving them here would put two owners on one symbol; the master plan's `text` row already claims them. This is why the bucket is 40, not the 54 estimated in the master plan's family table (C2 explicitly allows the exact recount to move). |
| D3 | Every path parameter is `string`, converted with `ffi.cstr_from_string`. | Contract §7. The whole point of the family: `file_exists with "notes.txt"` instead of `raylib.FileExists with (transmute (calling ffi.cstr_from_string with "notes.txt") to ref to frozen char)`. |
| D4 | The five path helpers (`GetFileExtension`, `GetFileName`, `GetFileNameWithoutExt`, `GetDirectoryPath`, `GetPrevDirectoryPath`, `GetWorkingDirectory`, `GetApplicationDirectory`) are wrapped as `string` returns. | They return `const char*` that **raylib owns** (the header says "uses static string" for most of them, and the rest point into the input), so the wrapper copies with `ffi.string_from_cstr` and frees nothing (contract §7, row "raylib owns it"). Verified in the probe: `GetFileExtension("/tmp/sample.txt")` → `".txt"`, no free. |
| D5 | `LoadFileData` → `maybe (list of byte)`. The raylib buffer is copied with `ffi.list_of_bytes_from_ptr` and then released with `UnloadFileData` **before** returning. | Contract §3 (null → `maybe none`) and §8 ("copy the raylib buffer, then the raylib free"). The returned `list of byte` is PenguScript-owned, so the caller can `banish` it or let it drop; it is never a foreign pointer. Verified end to end. |
| D6 | `LoadFileText` → `maybe string`, `LoadUTF8`/`LoadTextLines` → `maybe string` / `maybe (list of string)`. | Same copy-then-free rule, with `UnloadFileText`, `UnloadUTF8` and `UnloadTextLines` respectively. `maybe none` comes from the null pointer that raylib returns for a missing file. |
| D7 | `SaveFileData`, `SaveFileText`, `ExportDataAsCode` return `bool`. | The C functions already return a success channel; there is nothing to add, and a `result` wrapper would invent an error taxonomy raylib does not have (contract §3, the `bool` case). |
| D8 | `LoadDirectoryFiles`, `LoadDirectoryFilesEx` and `LoadDroppedFiles` → `list of string`. The `FilePathList` is copied with `ffi.list_of_string_from_ptr` and then released with `UnloadDirectoryFiles`/`UnloadDroppedFiles`. | Returning the `FilePathList` by value would expose a `ref to ref to char` **into raylib-owned memory** and force every caller onto the raw unloader; returning a `slice` would be worse, because the `FilePathList` is a local and the view would dangle on return (contract §8). An owned `list of string` is the only shape that is safe to return. Verified: `/tmp` lists, then `UnloadDirectoryFiles`. |
| D9 | `file_length` and `file_mod_time` return plain `int`/`int`, **not** `maybe`. | Measured in C: a missing file gives `0`, not `-1`, so there is no sentinel to turn into `maybe none` and no way to tell "empty file" from "no file" at this level. Documented as an ambiguity rather than papered over (contract §3). |
| D10 | `CompressData`/`DecompressData`/`EncodeDataBase64`/`DecodeDataBase64` return `maybe (list of byte)` / `maybe string`, taking `slice of byte` or `string` in. | All four take `(data, size)` and write the result size through an out-param, so they are the out-param plus pointer pair the contract folds into a slice (contract §5) and a null result is `maybe none`. |
| D11 | Hashes return `u32` (CRC32) and `slice of u32` (MD5, SHA1, SHA256). | `ComputeCRC32` returns a scalar; the other three return a pointer to a fixed-size array. `slice of u32` states the element count implicitly and needs no out-param (contract §5, "pointer + out-param folds into `.length`"). |
| D12 | **Skipped**: `IsFileDropped`, `OpenURL`, `GetFileNameLength`, plus the three `Text*` helpers that are file-adjacent. | `IsFileDropped` is a trivial `bool` getter that crosses no boundary (contract §9 row 8); `OpenURL` launches a browser, has no failure channel and is out of the 20 % that matters (contract §9 row 7); `GetFileNameLength` is a one-line predicate over a string the wrapper already handles as a `string` (the user has `.length`). |
| D13 | `MakeDirectory`/`ChangeDirectory` return `int` and **not** `bool`, matching the binding, with the header's "0 on success" documented. | Contract §3: converting to `bool` would invert the sense of the value silently. The docstring states `0` means success in both languages. |
| D15 | Two behaviours were measured that contradict the obvious reading, and both are encoded in the wrapper rather than hidden: **an empty file is `some` with an empty list** (`LoadFileData` returns a null pointer for a zero-byte file as well as for a missing one, so `file_bytes` disambiguates with `FileExists`), and **`ChangeDirectory` returns `1` on success, not `0`** despite its own header comment saying "returns 0 on success". | Both measured against `libraylib.so` while implementing (a plain C program, not a guess). `SaveFileData(NULL, 0)` also reports failure while still creating the file, so the empty write passes the address of a dummy byte. The plan records them because a future reader would otherwise "fix" the wrapper back to the wrong behaviour. |
| D14 | The three `GetFileExtension`-style helpers keep their binding names as `file_extension`, `file_name`, `file_name_without_extension`, `directory_path`, `previous_directory`, `working_directory`, `application_directory`. | Contract §2 naming: the wrapper is a direct mapping, so the shortest name that is unambiguous wins. `previous_directory` avoids the `directory_path`/`prev_directory_path` near-collision. |

### ✨ Enchantings

**None apply.** Every function in this family is a free function: it takes a path, a buffer or a scalar and returns a value. There is no raylib type whose first argument is the natural subject — `Image` and `Wave` are the loaders' *results*, not their receivers, and the `FilePathList` is a return shape (D8). This is the same shape as `rgesturesx`'s module-level functions, except here it is the whole family.

### 🔧 Module-level functions

#### File system

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `file_exists` | `with path as string into bool` | `FileExists` | |
| `directory_exists` | `with path as string into bool` | `DirectoryExists` | |
| `is_file_extension` | `with path as string, ext as string into bool` | `IsFileExtension` | case-insensitive; `ext` includes the dot (`.png`) |
| `is_path_file` | `with path as string into bool` | `IsPathFile` | |
| `is_file_name_valid` | `with name as string into bool` | `IsFileNameValid` | raylib accepts `""` and names with spaces; only the illegal set is rejected |
| `file_length` | `with path as string into int` | `GetFileLength` | `0` for a missing file (D9) |
| `file_mod_time` | `with path as string into int` | `GetFileModTime` | `0` for a missing file (D9) |
| `file_extension` | `with path as string into string` | `GetFileExtension` | includes the dot; raylib-owned pointer, copied (D4) |
| `file_name` | `with path as string into string` | `GetFileName` | |
| `file_name_without_extension` | `with path as string into string` | `GetFileNameWithoutExt` | raylib static buffer; copied |
| `directory_path` | `with path as string into string` | `GetDirectoryPath` | raylib static buffer; copied |
| `previous_directory` | `with path as string into string` | `GetPrevDirectoryPath` | raylib static buffer; copied |
| `working_directory` | `into string` | `GetWorkingDirectory` | raylib static buffer; copied |
| `application_directory` | `into string` | `GetApplicationDirectory` | raylib static buffer; copied |
| `remove_file` | `with path as string into int` | `FileRemove` | `0` on success (D13) |
| `rename_file` | `with path as string, new_path as string into int` | `FileRename` | `0` on success (D13) |
| `make_directory` | `with path as string into int` | `MakeDirectory` | `0` on success (D13) |
| `change_directory` | `with path as string into int` | `ChangeDirectory` | `0` on success (D13) |
| `load_directory` | `with path as string into list of string` | `LoadDirectoryFiles` | owned copy; raylib list released (D8) |
| `load_directory_filtered` | `with base as string, filter as string, scan_subdirs as bool into list of string` | `LoadDirectoryFilesEx` | |
| `dropped_files` | `into list of string` | `LoadDroppedFiles` | owned copy; raylib list released (D8) |

#### Raw data

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `file_bytes` | `with path as string into maybe (list of byte)` | `LoadFileData` | owned copy; raylib buffer released (D5) |
| `save_file_bytes` | `with path as string, data as slice of byte into bool` | `SaveFileData` | |
| `file_text` | `with path as string into maybe string` | `LoadFileText` | owned copy; raylib buffer released (D6) |
| `save_file_text` | `with path as string, text as string into bool` | `SaveFileText` | |
| `export_bytes_as_code` | `with data as slice of byte, path as string into bool` | `ExportDataAsCode` | writes a C source file |
| `text_from_codepoints` | `with codepoints as slice of int into maybe string` | `LoadUTF8` | owned copy; `UnloadUTF8` released (D6) |
| `text_lines` | `with text as string into maybe (list of string)` | `LoadTextLines` | splits on newlines (D6) |

#### Compression, encoding and hashes

| Function | Signature | C backing | Notes |
|---|---|---|---|
| `compress` | `with data as slice of byte into maybe (list of byte)` | `CompressData` | qoi/zlib; null → `maybe none` (D10) |
| `decompress` | `with data as slice of byte into maybe (list of byte)` | `DecompressData` | |
| `encode_base64` | `with data as slice of byte into maybe string` | `EncodeDataBase64` | |
| `decode_base64` | `with text as string into maybe (list of byte)` | `DecodeDataBase64` | |
| `crc32` | `with data as slice of byte into u32` | `ComputeCRC32` | |
| `md5` | `with data as slice of byte into slice of u32` | `ComputeMD5` | view into raylib's static buffer; **do not `banish`** (D11) |
| `sha1` | `with data as slice of byte into slice of u32` | `ComputeSHA1` | same |
| `sha256` | `with data as slice of byte into slice of u32` | `ComputeSHA256` | same |

> The three digest functions return `slice of u32`, which is a **view into a raylib static buffer**, not an owned copy. The docstrings say so, and the family plan records it in the §8 "lifetime" table. A caller that needs to keep a digest must copy it.

### 🎁 `maybe T` wrappers

| Function | Return | Predicate |
|---|---|---|
| `file_bytes` | `maybe (list of byte)` | `LoadFileData` returns `NULL` for a missing or unreadable file |
| `file_text` | `maybe string` | `LoadFileText` returns `NULL` |
| `text_from_codepoints` | `maybe string` | `LoadUTF8` returns `NULL` |
| `text_lines` | `maybe (list of string)` | `LoadTextLines` returns `NULL` or a zero count |
| `compress`, `decompress` | `maybe (list of byte)` | `NULL` result |
| `encode_base64` | `maybe string` | `NULL` result |
| `decode_base64` | `maybe (list of byte)` | `NULL` result |

`file_length`, `file_mod_time`, `make_directory`, `change_directory`, the four path predicates and the four hash/digest functions are **not** `maybe`: they return a value that is defined for every input (D9, D13).

### ✂️ `slice` wrappers

| Function | Slice parameter | Reason |
|---|---|---|
| `save_file_bytes` | `data as slice of byte` | `SaveFileData(const char*, void*, int)`; the length folds into `.length` |
| `export_bytes_as_code` | `data as slice of byte` | same shape |
| `text_from_codepoints` | `codepoints as slice of int` | `LoadUTF8(const int*, int)` |
| `compress`, `decompress` | `data as slice of byte` | `(data, size)` pair |
| `encode_base64` | `data as slice of byte` | same |
| `crc32`, `md5`, `sha1`, `sha256` | `data as slice of byte` | same |

Every one of them guards the empty slice before `sigil of (data at 0)`, because taking the address of element 0 of an empty slice is out of bounds (contract §5). The empty case is defined per function: `compress`/`decompress`/`encode_base64`/`crc32` treat it as "no data" and return `0` or `maybe none`; the savers return `false`.

### 📦 Multiple returns `(T, U)`

**None apply.** The three digest functions are the only candidates (a pointer plus a fixed length), and `slice of u32` already carries the length in `.length` (D11). `file_length` and `file_mod_time` are single scalars. No tuple is invented.

### 🌉 `std.ffi` usage

`std.ffi` is used for exactly four things:

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | every function with a path parameter |
| raylib `const char*` → owned `string` | `ffi.string_from_cstr` | the seven path helpers, `encode_base64` |
| raw buffer → owned `list of byte` | `ffi.list_of_bytes_from_ptr` | `file_bytes`, `decompress`, `decode_base64` |
| null check | `ffi.is_null` | every `maybe` loader |

Plus `sigil of` for the out-parameters (`LoadFileData`, `CompressData`, `DecompressData`, `EncodeDataBase64`, `DecodeDataBase64`) and `transmute` for the `ref to byte` → `ref to void` widening that `ffi.is_null` requires.

> **Reserved-word traps found while implementing.** `size` is a reserved word (it belongs to the `size of` operator), so an out-parameter may not be named `size` — `sigil of size` fails to parse. `bytes` is reserved too (`bytes of`). The wrapper uses `n` and `blob` for those locals. Recorded here because every future family plan that wraps an out-parameter will hit the same wall.

### 💡 Compilable examples

```pengu
# Example 1 — reading, writing and inspecting a text file
import raylib
import raylibx.files as files

weave main into int:
    var saved as bool is calling files.save_file_text with "/tmp/notes.txt", "hello pengu"
    var have as bool is calling files.file_exists with "/tmp/notes.txt"
    var text as maybe string is calling files.file_text with "/tmp/notes.txt"
    var missing as maybe string is calling files.file_text with "/tmp/not_here.txt"
    var ext as string is calling files.file_extension with "/tmp/notes.txt"
    return 0
```

```pengu
# Example 2 — bytes, hashing and compression
import raylib
import raylibx.files as files

weave main into int:
    var raw as maybe (list of byte) is calling files.file_bytes with "/tmp/notes.txt"
    var data as list of byte is list of byte
    defer banish data
    calling data.push with 1
    calling data.push with 2
    var digest as u32 is calling files.crc32 with (data at 0 to 2)
    var packed as maybe (list of byte) is calling files.compress with (data at 0 to 2)
    return 0
```

```pengu
# Example 3 — enumerating a directory into an owned list
import raylib
import raylibx.files as files

weave main into int:
    var names as list of string is calling files.load_directory with "/tmp"
    defer banish names
    var count as int is names.length
    return count
```

### 🧪 Test plan

The family is CI-testable because raylib's file API touches the real disk: **every test that writes uses a unique path under the system temporary directory and removes it afterwards**, so the suite leaves the workspace and the temporary directory exactly as it found them. Verified: after a full run, `/tmp/raylibx_files_*.txt` does not exist.

The tests use `GetRandomValue` once per run to build a collision-free file name; the cleanup is `defer calling raylib.FileDelete with ...` so a failing assertion still tidies up.

- **`save_file_text` / `file_text`**: a round trip returns the same content; a missing path gives `maybe none`; overwriting changes the content.
- **`save_file_bytes` / `file_bytes`**: a round trip preserves the bytes; a missing path gives `maybe none`; an empty payload round-trips as an empty list.
- **`file_exists` / `directory_exists`**: true for a path just written, false for an absent one; a file is not a directory and `/tmp` is not a file.
- **`is_file_extension`**: `.txt` matches `notes.txt`, `.png` does not; the case-insensitive behaviour is asserted.
- **`is_path_file`**: `/tmp` is false and a regular file is true.
- **`is_file_name_valid`**: a plain name is valid and the empty string is accepted by raylib (asserted, not assumed).
- **`file_length`**: the length of a known payload; `0` for a missing file (the documented ambiguity).
- **`file_mod_time`**: non-zero for a file just written; `0` for a missing file.
- **`file_extension` / `file_name` / `file_name_without_extension` / `directory_path`**: each asserted on `/tmp/sample.txt` against the measured values (`.txt`, `sample.txt`, `sample`, `/tmp`).
- **`working_directory` / `application_directory`**: non-empty; the working directory contains the repository root when the runner starts there.
- **`make_directory` / `change_directory`**: `0` on success for an existing directory; a non-zero code for an impossible path (asserted as "not zero", since the exact errno value is platform-specific).
- **`load_directory`**: listing `/tmp` gives a non-empty list and every entry is a non-empty string.
- **`load_directory_filtered`**: filtering `/tmp` by `.txt` returns only paths ending in `.txt`.
- **`crc32`**: a known payload gives a non-zero value, the same payload gives the same value twice, and a different payload differs.
- **`md5` / `sha1` / `sha256`**: each returns a four-element slice, the three differ from each other on the same input, and the same input is stable across calls.
- **`compress` / `decompress`**: decompressing a compressed payload returns the original bytes; compressing an empty slice is handled without touching element zero.
- **`encode_base64` / `decode_base64`**: a round trip returns the original bytes; the encoded form is a non-empty string; an invalid base64 string gives `maybe none` or an empty result (asserted as "does not panic").
- **`text_lines`**: a two-line string gives two entries; a single line gives one.
- **`text_from_codepoints`**: the codepoints of `"hi"` give back `"hi"`.
- **`export_bytes_as_code`**: writing to a temporary `.c` path returns true and the file exists afterwards (then is removed).
- **`dropped_files`**: callable without a window; the list may be empty, so the assertion is only that the call returns a list (no window means no drops).

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `IsFileDropped` | trivial `bool` getter that crosses no boundary; the predicate *is* the value (D12, contract §9 row 8) |
| `OpenURL` | launches the system browser; no failure channel and outside the 20 % that matters (D12, contract §9 row 7) |
| `GetFileNameLength` | a one-line length query the caller already has as `string.length` (D12) |
| `TextSplit`, `TextJoin`, `TextInsert`, `TextInsertAlloc`, `TextReplace`, `TextReplaceAlloc`, `TextReplaceBetween`, `TextReplaceBetweenAlloc`, `TextAppend`, `TextFindIndex`, `TextToUpper`, `TextToLower`, `TextToPascal`, `TextToInteger`, `TextToFloat`, `TextLength`, `TextSubtext`, `GetTextBetween` | **not this family**: the `text` family owns the whole `Text*` block (D2, master plan D6) |
| `LoadFileData`/`file_bytes`'s raw pointer form, `LoadFileText`/`file_text`'s raw pointer form | not exposed wrapped: the wrapper always returns the owned copy, never the foreign `ref` (D5/D6) |

Coverage audit: of the 40 files-family `declare`s, **36 are public wrappers** and **8 are internal releases** (the `Unload*`/`MemFree` calls the wrappers make before returning), and **3 are skipped** (`IsFileDropped`, `OpenURL`, `GetFileNameLength`). Every release is used: `UnloadFileData` once, `UnloadFileText` once, `UnloadDirectoryFiles` twice, `UnloadDroppedFiles` once, `UnloadUTF8` once, `UnloadTextLines` once and `MemFree` four times. The method registry gains **no** entry from this family, which is expected: it has no enchantings.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/files.pengu`
- Dueña en el plan maestro: familia `files` de `docs/plans/raylibx.md` (v0.1.2), segunda en su orden de implementación
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Completitud del binding verificada para este grupo: **caso (a) completo**. 40 `declare` corresponden a la familia files. De ellos, **36 se envuelven como funciones públicas**, **8 son las liberaciones de recurso que se llaman dentro de esos wrappers** (`UnloadFileData`, `UnloadFileText`, `UnloadDirectoryFiles`, `UnloadDroppedFiles`, `UnloadUTF8`, `UnloadTextLines` y `MemFree`) y **3 se omiten** (D12). El resto de la estimación anterior eran helpers `Text*`, que pertenecen a la familia `text` (D2). | Enumerado contra `pengu/raylib.d.pengu` (`:948-1180`) y `include/raylib.h` (`:1150-1195`). No falta ninguno. |
| D2 | El alcance es **sistema de ficheros + datos crudos + compresión/codificación/hash**. Los 23 helpers `Text*` (`TextToUpper`, `TextSplit`, `TextJoin`, `TextFindIndex`, …) **no** están aquí: pertenecen a la familia `text`. | El propio reparto del plan maestro y su D6 ("la familia dueña de la función C"). Dejarlos aquí pondría dos dueños sobre un símbolo; la fila `text` del plan maestro ya los reclama. Por eso el grupo es 40 y no los 54 estimados en la tabla de familias (C2 permite explícitamente que el recuento exacto se mueva). |
| D3 | Todo parámetro de ruta es `string`, convertido con `ffi.cstr_from_string`. | Contrato §7. Es el objetivo de la familia: `file_exists with "notes.txt"` en vez de `raylib.FileExists with (transmute (calling ffi.cstr_from_string with "notes.txt") to ref to frozen char)`. |
| D4 | Los siete helpers de ruta (`GetFileExtension`, `GetFileName`, `GetFileNameWithoutExt`, `GetDirectoryPath`, `GetPrevDirectoryPath`, `GetWorkingDirectory`, `GetApplicationDirectory`) se envuelven devolviendo `string`. | Devuelven `const char*` que **posee raylib** (el header dice "uses static string" en la mayoría, y el resto apuntan dentro de la entrada), así que el wrapper copia con `ffi.string_from_cstr` y no libera nada (contrato §7, fila "lo posee raylib"). Verificado en la sonda: `GetFileExtension("/tmp/sample.txt")` → `".txt"`, sin liberar. |
| D5 | `LoadFileData` → `maybe (list of byte)`. El búfer de raylib se copia con `ffi.list_of_bytes_from_ptr` y luego se libera con `UnloadFileData` **antes** de devolver. | Contrato §3 (nulo → `maybe none`) y §8 ("copiar el búfer de raylib y después el free de raylib"). El `list of byte` devuelto es propiedad de PenguScript, así que el llamador puede hacer `banish` o dejarlo caer; nunca es un puntero ajeno. Verificado de extremo a extremo. |
| D6 | `LoadFileText` → `maybe string`, `LoadUTF8`/`LoadTextLines` → `maybe string` / `maybe (list of string)`. | La misma regla de copiar-y-liberar, con `UnloadFileText`, `UnloadUTF8` y `UnloadTextLines` respectivamente. El `maybe none` viene del puntero nulo que raylib devuelve para un fichero ausente. |
| D7 | `SaveFileData`, `SaveFileText`, `ExportDataAsCode` devuelven `bool`. | Las funciones C ya devuelven un canal de éxito; no hay nada que añadir, y un `result` inventaría una taxonomía de error que raylib no tiene (contrato §3, el caso `bool`). |
| D8 | `LoadDirectoryFiles`, `LoadDirectoryFilesEx` y `LoadDroppedFiles` → `list of string`. El `FilePathList` se copia con `ffi.list_of_string_from_ptr` y luego se libera con `UnloadDirectoryFiles`/`UnloadDroppedFiles`. | Devolver el `FilePathList` por valor expondría un `ref to ref to char` **dentro de memoria de raylib** y obligaría a cada llamador al liberador crudo; devolver un `slice` sería peor, porque el `FilePathList` es un local y la vista quedaría colgando al volver (contrato §8). Un `list of string` con posesión es la única forma segura de devolverlo. Verificado: `/tmp` se lista y después se libera. |
| D9 | `file_length` y `file_mod_time` devuelven `int`/`int` simple, **no** `maybe`. | Medido en C: un fichero ausente da `0`, no `-1`, así que no hay centinela que convertir en `maybe none` ni forma de distinguir "fichero vacío" de "no hay fichero" a este nivel. Se documenta la ambigüedad en vez de disimularla (contrato §3). |
| D10 | `CompressData`/`DecompressData`/`EncodeDataBase64`/`DecodeDataBase64` devuelven `maybe (list of byte)` / `maybe string`, recibiendo `slice of byte` o `string`. | Las cuatro reciben `(data, size)` y escriben el tamaño de salida por out-param, así que son el par puntero + out-param que el contrato pliega en un slice (contrato §5) y un resultado nulo es `maybe none`. |
| D11 | Los hashes devuelven `u32` (CRC32) y `slice of u32` (MD5, SHA1, SHA256). | `ComputeCRC32` devuelve un escalar; los otros tres devuelven un puntero a un array de tamaño fijo. `slice of u32` declara el número de elementos implícitamente y no necesita out-param (contrato §5, "puntero + out-param se pliega en `.length`"). |
| D12 | **Se omiten**: `IsFileDropped`, `OpenURL`, `GetFileNameLength`, más los tres helpers `Text*` adyacentes a ficheros. | `IsFileDropped` es un getter `bool` trivial que no cruza ninguna frontera (contrato §9 fila 8); `OpenURL` lanza el navegador, no tiene canal de fallo y queda fuera del 20 % que importa (contrato §9 fila 7); `GetFileNameLength` es una consulta de longitud de una línea que el llamador ya tiene como `string.length` (D12). |
| D13 | `MakeDirectory`/`ChangeDirectory` devuelven `int` y **no** `bool`, igual que el binding, con el "0 en éxito" del header documentado. | Contrato §3: convertirlo a `bool` invertiría el sentido del valor en silencio. El docstring declara que `0` significa éxito en ambos idiomas. |
| D15 | Se midieron dos comportamientos que contradicen la lectura obvia, y ambos quedan codificados en el wrapper en vez de escondidos: **un fichero vacío es `some` con lista vacía** (`LoadFileData` devuelve puntero nulo tanto para un fichero de cero bytes como para uno ausente, así que `file_bytes` desambigua con `FileExists`), y **`ChangeDirectory` devuelve `1` en éxito, no `0`**, pese a que su propio comentario en el header dice "returns 0 on success". | Ambos medidos contra `libraylib.so` al implementar (con un programa C, no a ojo). `SaveFileData(NULL, 0)` además reporta fallo aunque cree el fichero, así que la escritura vacía pasa la dirección de un byte dummy. El plan los registra porque, si no, un lector futuro "arreglaría" el wrapper de vuelta al comportamiento equivocado. |
| D14 | Los tres helpers estilo `GetFileExtension` conservan los nombres del binding como `file_extension`, `file_name`, `file_name_without_extension`, `directory_path`, `previous_directory`, `working_directory`, `application_directory`. | Nomenclatura del contrato §2: el wrapper es un mapeo directo, así que gana el nombre más corto que no sea ambiguo. `previous_directory` evita la casi-colisión con `directory_path`. |

### ✨ Enchantings

**Ninguno aplica.** Todas las funciones de esta familia son libres: reciben una ruta, un búfer o un escalar y devuelven un valor. No hay ningún tipo de raylib cuyo primer argumento sea el sujeto natural: `Image` y `Wave` son el *resultado* de los cargadores, no sus receptores, y `FilePathList` es una forma de retorno (D8). Es la misma forma que las funciones de módulo de `rgesturesx`, salvo que aquí es toda la familia.

### 🔧 Funciones a nivel de módulo

#### Sistema de ficheros

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `file_exists` | `with path as string into bool` | `FileExists` | |
| `directory_exists` | `with path as string into bool` | `DirectoryExists` | |
| `is_file_extension` | `with path as string, ext as string into bool` | `IsFileExtension` | insensible a mayúsculas; `ext` incluye el punto (`.png`) |
| `is_path_file` | `with path as string into bool` | `IsPathFile` | |
| `is_file_name_valid` | `with name as string into bool` | `IsFileNameValid` | raylib acepta `""` y nombres con espacios; solo rechaza el conjunto ilegal |
| `file_length` | `with path as string into int` | `GetFileLength` | `0` para un fichero ausente (D9) |
| `file_mod_time` | `with path as string into int` | `GetFileModTime` | `0` para un fichero ausente (D9) |
| `file_extension` | `with path as string into string` | `GetFileExtension` | incluye el punto; puntero de raylib, copiado (D4) |
| `file_name` | `with path as string into string` | `GetFileName` | |
| `file_name_without_extension` | `with path as string into string` | `GetFileNameWithoutExt` | búfer estático de raylib; copiado |
| `directory_path` | `with path as string into string` | `GetDirectoryPath` | búfer estático de raylib; copiado |
| `previous_directory` | `with path as string into string` | `GetPrevDirectoryPath` | búfer estático de raylib; copiado |
| `working_directory` | `into string` | `GetWorkingDirectory` | búfer estático de raylib; copiado |
| `application_directory` | `into string` | `GetApplicationDirectory` | búfer estático de raylib; copiado |
| `remove_file` | `with path as string into int` | `FileRemove` | `0` en éxito (D13) |
| `rename_file` | `with path as string, new_path as string into int` | `FileRename` | `0` en éxito (D13) |
| `make_directory` | `with path as string into int` | `MakeDirectory` | `0` en éxito (D13) |
| `change_directory` | `with path as string into int` | `ChangeDirectory` | `0` en éxito (D13) |
| `load_directory` | `with path as string into list of string` | `LoadDirectoryFiles` | copia con posesión; lista de raylib liberada (D8) |
| `load_directory_filtered` | `with base as string, filter as string, scan_subdirs as bool into list of string` | `LoadDirectoryFilesEx` | |
| `dropped_files` | `into list of string` | `LoadDroppedFiles` | copia con posesión; lista de raylib liberada (D8) |

#### Datos crudos

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `file_bytes` | `with path as string into maybe (list of byte)` | `LoadFileData` | copia con posesión; búfer de raylib liberado (D5) |
| `save_file_bytes` | `with path as string, data as slice of byte into bool` | `SaveFileData` | |
| `file_text` | `with path as string into maybe string` | `LoadFileText` | copia con posesión; búfer de raylib liberado (D6) |
| `save_file_text` | `with path as string, text as string into bool` | `SaveFileText` | |
| `export_bytes_as_code` | `with data as slice of byte, path as string into bool` | `ExportDataAsCode` | escribe un fichero fuente C |
| `text_from_codepoints` | `with codepoints as slice of int into maybe string` | `LoadUTF8` | copia con posesión; `UnloadUTF8` liberado (D6) |
| `text_lines` | `with text as string into maybe (list of string)` | `LoadTextLines` | divide por saltos de línea (D6) |

#### Compresión, codificación y hashes

| Función | Firma | C backing | Notas |
|---|---|---|---|
| `compress` | `with data as slice of byte into maybe (list of byte)` | `CompressData` | qoi/zlib; nulo → `maybe none` (D10) |
| `decompress` | `with data as slice of byte into maybe (list of byte)` | `DecompressData` | |
| `encode_base64` | `with data as slice of byte into maybe string` | `EncodeDataBase64` | |
| `decode_base64` | `with text as string into maybe (list of byte)` | `DecodeDataBase64` | |
| `crc32` | `with data as slice of byte into u32` | `ComputeCRC32` | |
| `md5` | `with data as slice of byte into slice of u32` | `ComputeMD5` | vista dentro del búfer estático de raylib; **no `banish`** (D11) |
| `sha1` | `with data as slice of byte into slice of u32` | `ComputeSHA1` | igual |
| `sha256` | `with data as slice of byte into slice of u32` | `ComputeSHA256` | igual |

> Las tres funciones de digest devuelven `slice of u32`, que es una **vista dentro de un búfer estático de raylib**, no una copia con posesión. Los docstrings lo dicen y el plan de familia lo registra en la tabla de "lifetime" del §8. Un llamador que necesite conservar un digest debe copiarlo.

### 🎁 Wrappers `maybe T`

| Función | Retorno | Predicado |
|---|---|---|
| `file_bytes` | `maybe (list of byte)` | `LoadFileData` devuelve `NULL` para un fichero ausente o ilegible |
| `file_text` | `maybe string` | `LoadFileText` devuelve `NULL` |
| `text_from_codepoints` | `maybe string` | `LoadUTF8` devuelve `NULL` |
| `text_lines` | `maybe (list of string)` | `LoadTextLines` devuelve `NULL` o un recuento cero |
| `compress`, `decompress` | `maybe (list of byte)` | resultado `NULL` |
| `encode_base64` | `maybe string` | resultado `NULL` |
| `decode_base64` | `maybe (list of byte)` | resultado `NULL` |

`file_length`, `file_mod_time`, `make_directory`, `change_directory`, los cuatro predicados de ruta y las cuatro funciones de hash/digest **no** son `maybe`: devuelven un valor definido para toda entrada (D9, D13).

### ✂️ Wrappers de `slice`

| Función | Parámetro slice | Motivo |
|---|---|---|
| `save_file_bytes` | `data as slice of byte` | `SaveFileData(const char*, void*, int)`; la longitud se pliega en `.length` |
| `export_bytes_as_code` | `data as slice of byte` | misma forma |
| `text_from_codepoints` | `codepoints as slice of int` | `LoadUTF8(const int*, int)` |
| `compress`, `decompress` | `data as slice of byte` | par `(data, size)` |
| `encode_base64` | `data as slice of byte` | igual |
| `crc32`, `md5`, `sha1`, `sha256` | `data as slice of byte` | igual |

Todas guardan el slice vacío antes de `sigil of (data at 0)`, porque tomar la dirección del elemento 0 de un slice vacío queda fuera de rango (contrato §5). El caso vacío se define por función: `compress`/`decompress`/`encode_base64`/`crc32` lo tratan como "sin datos" y devuelven `0` o `maybe none`; los que guardan devuelven `false`.

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** Las tres funciones de digest son los únicos candidatos (un puntero más una longitud fija), y `slice of u32` ya lleva la longitud en `.length` (D11). `file_length` y `file_mod_time` son escalares sueltos. No se inventa ninguna tupla.

### 🌉 Uso de `std.ffi`

`std.ffi` se usa exactamente para cuatro cosas:

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | toda función con parámetro de ruta |
| `const char*` de raylib → `string` con posesión | `ffi.string_from_cstr` | los siete helpers de ruta, `encode_base64` |
| búfer crudo → `list of byte` con posesión | `ffi.list_of_bytes_from_ptr` | `file_bytes`, `decompress`, `decode_base64` |
| comprobación de nulo | `ffi.is_null` | todo cargador `maybe` |

Más `sigil of` para los out-params (`LoadFileData`, `CompressData`, `DecompressData`, `EncodeDataBase64`, `DecodeDataBase64`) y `transmute` para el ensanchamiento `ref to byte` → `ref to void` que exige `ffi.is_null`.

> **Trampas de palabras reservadas encontradas al implementar.** `size` es palabra reservada (pertenece al operador `size of`), así que un out-param no puede llamarse `size`: `sigil of size` no parsea. `bytes` también es reservada (`bytes of`). El wrapper usa `n` y `blob` para esos locales. Se registra aquí porque todo plan de familia futuro que envuelva un out-param chocará con el mismo muro.

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — leer, escribir e inspeccionar un fichero de texto
import raylib
import raylibx.files as files

weave main into int:
    var saved as bool is calling files.save_file_text with "/tmp/notes.txt", "hello pengu"
    var have as bool is calling files.file_exists with "/tmp/notes.txt"
    var text as maybe string is calling files.file_text with "/tmp/notes.txt"
    var missing as maybe string is calling files.file_text with "/tmp/not_here.txt"
    var ext as string is calling files.file_extension with "/tmp/notes.txt"
    return 0
```

```pengu
# Ejemplo 2 — bytes, hashing y compresión
import raylib
import raylibx.files as files

weave main into int:
    var raw as maybe (list of byte) is calling files.file_bytes with "/tmp/notes.txt"
    var data as list of byte is list of byte
    defer banish data
    calling data.push with 1
    calling data.push with 2
    var digest as u32 is calling files.crc32 with (data at 0 to 2)
    var packed as maybe (list of byte) is calling files.compress with (data at 0 to 2)
    return 0
```

```pengu
# Ejemplo 3 — enumerar un directorio en una lista con posesión
import raylib
import raylibx.files as files

weave main into int:
    var names as list of string is calling files.load_directory with "/tmp"
    defer banish names
    var count as int is names.length
    return count
```

### 🧪 Plan de tests

La familia es testeable en CI porque la API de ficheros de raylib toca el disco real: **todo test que escribe usa una ruta única bajo el directorio temporal del sistema y la borra después**, así que la suite deja el workspace y el directorio temporal exactamente como los encontró. Verificado: tras una ejecución completa, `/tmp/raylibx_files_*.txt` no existe.

Los tests usan `GetRandomValue` una vez por ejecución para construir un nombre de fichero sin colisiones; la limpieza es `defer calling raylib.FileDelete with ...` para que una aserción fallida también ordene.

- **`save_file_text` / `file_text`**: la ida y vuelta devuelve el mismo contenido; una ruta ausente da `maybe none`; sobrescribir cambia el contenido.
- **`save_file_bytes` / `file_bytes`**: la ida y vuelta conserva los bytes; una ruta ausente da `maybe none`; una carga vacía vuelve como lista vacía.
- **`file_exists` / `directory_exists`**: verdadero para una ruta recién escrita, falso para una ausente; un fichero no es un directorio y `/tmp` no es un fichero.
- **`is_file_extension`**: `.txt` coincide con `notes.txt`, `.png` no; se asegura el comportamiento insensible a mayúsculas.
- **`is_path_file`**: `/tmp` es falso y un fichero regular es verdadero.
- **`is_file_name_valid`**: un nombre simple es válido y la cadena vacía la acepta raylib (se asegura, no se asume).
- **`file_length`**: la longitud de una carga conocida; `0` para un fichero ausente (la ambigüedad documentada).
- **`file_mod_time`**: distinto de cero para un fichero recién escrito; `0` para uno ausente.
- **`file_extension` / `file_name` / `file_name_without_extension` / `directory_path`**: cada uno asegurado sobre `/tmp/sample.txt` contra los valores medidos (`.txt`, `sample.txt`, `sample`, `/tmp`).
- **`working_directory` / `application_directory`**: no vacíos; el directorio de trabajo contiene la raíz del repositorio cuando el runner arranca ahí.
- **`make_directory` / `change_directory`**: `0` en éxito para un directorio existente; un código distinto de cero para una ruta imposible (se asegura "distinto de cero", porque el valor exacto de errno depende de la plataforma).
- **`load_directory`**: listar `/tmp` da una lista no vacía y cada entrada es una cadena no vacía.
- **`load_directory_filtered`**: filtrar `/tmp` por `.txt` devuelve solo rutas que terminan en `.txt`.
- **`crc32`**: una carga conocida da un valor distinto de cero, la misma carga da el mismo valor dos veces y una carga distinta difiere.
- **`md5` / `sha1` / `sha256`**: cada uno devuelve un slice de cuatro elementos, los tres difieren entre sí sobre la misma entrada y la misma entrada es estable entre llamadas.
- **`compress` / `decompress`**: descomprimir una carga comprimida devuelve los bytes originales; comprimir un slice vacío se maneja sin tocar el elemento cero.
- **`encode_base64` / `decode_base64`**: la ida y vuelta devuelve los bytes originales; la forma codificada es una cadena no vacía; una cadena base64 inválida da `maybe none` o un resultado vacío (se asegura "no entra en pánico").
- **`text_lines`**: una cadena de dos líneas da dos entradas; una sola línea da una.
- **`text_from_codepoints`**: los codepoints de `"hi"` devuelven `"hi"`.
- **`export_bytes_as_code`**: escribir en una ruta temporal `.c` devuelve verdadero y el fichero existe después (y luego se borra).
- **`dropped_files`**: se puede llamar sin ventana; la lista puede estar vacía, así que la única aserción es que la llamada devuelve una lista (sin ventana no hay drops).

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `IsFileDropped` | getter `bool` trivial que no cruza ninguna frontera; el predicado *es* el valor (D12, contrato §9 fila 8) |
| `OpenURL` | lanza el navegador del sistema; sin canal de fallo y fuera del 20 % que importa (D12, contrato §9 fila 7) |
| `GetFileNameLength` | consulta de longitud de una línea que el llamador ya tiene como `string.length` (D12) |
| `TextSplit`, `TextJoin`, `TextInsert`, `TextInsertAlloc`, `TextReplace`, `TextReplaceAlloc`, `TextReplaceBetween`, `TextReplaceBetweenAlloc`, `TextAppend`, `TextFindIndex`, `TextToUpper`, `TextToLower`, `TextToPascal`, `TextToInteger`, `TextToFloat`, `TextLength`, `TextSubtext`, `GetTextBetween` | **no son de esta familia**: la familia `text` posee todo el bloque `Text*` (D2, plan maestro D6) |
| La forma de puntero crudo de `LoadFileData`/`file_bytes` y de `LoadFileText`/`file_text` | no se expone envuelta: el wrapper devuelve siempre la copia con posesión, nunca el `ref` ajeno (D5/D6) |

Auditoría de cobertura: de los 40 `declare` de la familia files, **36 son wrappers públicos** y **8 son liberaciones internas** (las llamadas `Unload*`/`MemFree` que los wrappers hacen antes de volver), y **3 se omiten** (`IsFileDropped`, `OpenURL`, `GetFileNameLength`). Todas las liberaciones se usan: `UnloadFileData` una vez, `UnloadFileText` una, `UnloadDirectoryFiles` dos, `UnloadDroppedFiles` una, `UnloadUTF8` una, `UnloadTextLines` una y `MemFree` cuatro. El registro de métodos no gana **ninguna** entrada con esta familia, lo cual es esperable: no tiene enchantings.
