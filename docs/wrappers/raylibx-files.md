> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# files

> Source: `pengu/raylibx/files.pengu`

Layer-2 wrapper over the file-system, raw-data, compression and hashing surface of
the `raylib` binding.

Every entry is a free function: this family has no `enchanting`, because no raylib
type has a path or a buffer as its natural subject. What the wrapper adds is the
boundary: paths become `string`, lengths fold into `.length`, foreign buffers become
owned PenguScript values and every raylib allocation is released before returning.

    calling raylib.LoadFileText with cstr                     # binding
    calling raylibx_files.file_text with "notes.txt"          # wrapper

This is family `files` of `docs/README.md`; see `docs/wrappers/raylibx-files.md`.

## Ownership
Three rules, all enforced here:
- A raylib buffer that the caller must free is copied into an owned `list of byte` or
  `string` and then released with its `Unload*`/`MemFree` counterpart **before** the
  wrapper returns. The caller never sees a foreign pointer.
- A `const char*` that raylib owns (the path helpers) is copied with
  `ffi.string_from_cstr` and **not** freed.
- The digest functions (`md5`, `sha1`, `sha256`) return `slice of u32`, which is a
  **view into a raylib static buffer**. Do not `banish` it and do not keep it past the
  next call that uses the same buffer; copy it if it must outlive the expression.

## Memory
No `banish` in the wrapper itself: everything returned is either an owned PenguScript
value (the caller decides when to `banish`) or a documented view. `std.ffi` is used for
the string conversion, the byte/string list copies and the null checks.

## Example
```pengu
import raylib
import raylibx_files

weave main into int:
    var saved as bool is calling raylibx_files.save_file_text with "/tmp/notes.txt", "hello"
    var text as maybe string is calling raylibx_files.file_text with "/tmp/notes.txt"
    var names as list of string is calling raylibx_files.load_directory with "/tmp"
    defer banish names
    return 0
```

---

### `file_exists`

> **file_exists**(path: string) -> bool

_Undocumented function._


### `directory_exists`

> **directory_exists**(path: string) -> bool

_Undocumented function._


### `is_file_extension`

> **is_file_extension**(path: string, ext: string) -> bool

_Undocumented function._


### `is_path_file`

> **is_path_file**(path: string) -> bool

_Undocumented function._


### `is_file_name_valid`

> **is_file_name_valid**(name: string) -> bool

_Undocumented function._


### `file_length`

> **file_length**(path: string) -> int

_Undocumented function._


### `file_mod_time`

> **file_mod_time**(path: string) -> int

_Undocumented function._


### `file_extension`

> **file_extension**(path: string) -> string

_Undocumented function._


### `file_name`

> **file_name**(path: string) -> string

_Undocumented function._


### `file_name_without_extension`

> **file_name_without_extension**(path: string) -> string

_Undocumented function._


### `directory_path`

> **directory_path**(path: string) -> string

_Undocumented function._


### `previous_directory`

> **previous_directory**(path: string) -> string

_Undocumented function._


### `working_directory`

> **working_directory**() -> string

_Undocumented function._


### `application_directory`

> **application_directory**() -> string

_Undocumented function._


### `remove_file`

> **remove_file**(path: string) -> int

_Undocumented function._


### `rename_file`

> **rename_file**(path: string, new_path: string) -> int

_Undocumented function._


### `make_directory`

> **make_directory**(path: string) -> int

_Undocumented function._


### `change_directory`

> **change_directory**(path: string) -> int

_Undocumented function._


### `load_directory`

> **load_directory**(path: string) -> list of string

_Undocumented function._


### `load_directory_filtered`

> **load_directory_filtered**(base: string, filter: string, scan_subdirs: bool) -> list of string

_Undocumented function._


### `dropped_files`

> **dropped_files**() -> list of string

_Undocumented function._


### `file_bytes`

> **file_bytes**(path: string) -> maybe list of byte

_Undocumented function._


### `save_file_bytes`

> **save_file_bytes**(path: string, data: slice of byte) -> bool

_Undocumented function._


### `file_text`

> **file_text**(path: string) -> maybe string

_Undocumented function._


### `save_file_text`

> **save_file_text**(path: string, text: string) -> bool

_Undocumented function._


### `export_bytes_as_code`

> **export_bytes_as_code**(data: slice of byte, path: string) -> bool

_Undocumented function._


### `text_from_codepoints`

> **text_from_codepoints**(codepoints: slice of int) -> maybe string

_Undocumented function._


### `text_lines`

> **text_lines**(text: string) -> maybe list of string

_Undocumented function._


### `compress`

> **compress**(data: slice of byte) -> maybe list of byte

_Undocumented function._


### `decompress`

> **decompress**(data: slice of byte) -> maybe list of byte

_Undocumented function._


### `encode_base64`

> **encode_base64**(data: slice of byte) -> maybe string

_Undocumented function._


### `decode_base64`

> **decode_base64**(text: string) -> maybe list of byte

_Undocumented function._


### `crc32`

> **crc32**(data: slice of byte) -> u32

_Undocumented function._


### `md5`

> **md5**(data: slice of byte) -> slice of u32

_Undocumented function._


### `sha1`

> **sha1**(data: slice of byte) -> slice of u32

_Undocumented function._


### `sha256`

> **sha256**(data: slice of byte) -> slice of u32

_Undocumented function._

