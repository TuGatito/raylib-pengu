# Plan: audio.pengu

> 🌐 Bilingual plan. English is canonical; the Spanish section below is a
> non-normative translation, kept in step section by section.
> Plan bilingüe. El inglés es canónico; la sección en español de abajo es una
> traducción no normativa, sincronizada sección a sección.

## 🇬🇧 English

### 📌 Metadata
- Source binding: `pengu/raylib.d.pengu`
- Wrapper target: `pengu/raylibx/audio.pengu`
- Owner in the master plan: family `audio` of `docs/plans/raylibx.md` (v0.1.2)
- Dependencies: `import raylib`, `import std.ffi`
- Conventions: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Module-specific decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Coverage: the audio section holds **66** C functions, all exported by the installed library. **55 are wrapped** (41 methods and 14 module functions), **5 are callbacks** and **6 are one-shot device or global configuration**, and neither group is wrapped. | Enumerated from the binding and cross-checked with `tools/check_binding_symbols.py`; a script asserts that all 66 land in exactly one bucket. |
| D2 | **The audio device is available, so this family is asserted for real.** Measured: `IsAudioDeviceReady()` is `1`, `SetMasterVolume`/`GetMasterVolume` round-trip, a handmade `Wave` turns into a playable `Sound`, and `IsSoundPlaying` goes from `false` to `true` across `play`. | The same "measure the new boundary before promising tests" step that `window` needed for the display. It is the reason this plan claims 8 tests instead of a compile-only probe. |
| D3 | **Four receiver types, so 41 of the 55 wrappers are methods**: 7 on `raylib.Wave`, 10 on `raylib.Sound`, 13 on `raylib.Music` and 11 on `raylib.AudioStream`. | Contract §6.1. The four types are genuinely different things — CPU sample data, a device-owned playback buffer, a streaming decoder, and a buffer you push samples into — and each one's operations belong on it. This is the widest method fan-out in the module after `images`. |
| D4 | `InitAudioDevice` and `CloseAudioDevice` are **not wrapped**, and they are the only entries excluded by the *shape* of §9 row 8 rather than by its literal text. | Row 8 names `InitWindow`/`CloseWindow` as one-shot global configuration; an audio device is exactly the same shape, so the same reasoning applies word for word. The tests open and close the device through the binding, and every docstring that needs a device says so. |
| D5 | `IsAudioDeviceReady`, `GetMasterVolume`, `SetMasterVolume` and `SetAudioStreamBufferSizeDefault` are **not wrapped** either: they are a zero-argument predicate, a zero-argument getter and two flat global setters with no receiver and no boundary. | Contract §9 rows 1 and 8 and criterion 2. `raylib.SetMasterVolume with 0.5` is already a clear call; a wrapper would rename without shortening. This is the same mechanical outcome as `window`'s 56 exclusions, and it is worth stating that the family is not inconsistent for wrapping `sound.set_volume` while skipping `SetMasterVolume`: the first has a receiver. |
| D6 | The **five callback entries** (`SetAudioStreamCallback`, `AttachAudioStreamProcessor`, `DetachAudioStreamProcessor`, `AttachAudioMixedProcessor`, `DetachAudioMixedProcessor`) are not wrapped. | §9 row 6: PenguScript lambdas have no closures, and `AudioCallback` is `ref to weave with bufferData as ref to void, frames as u32 into void`. A processor that needs the caller's state could not be written, which is the same finding as `drawing`'s D3 and the master plan's D19. |
| D7 | **Every one of the nine loaders returns `maybe`**: `load_wave`, `load_wave_from_memory`, `load_sound`, `load_sound_from_wave`, `load_sound_alias`, `load_music_stream`, `load_music_stream_from_memory`, `load_audio_stream`, and each is checked with its own type's predicate. | All measured: a missing file gives an invalid wave, sound and music; junk bytes and an empty buffer give an invalid wave; a **zeroed wave** gives an invalid sound; and **with no device at all** `LoadAudioStream` is invalid while `IsAudioDeviceReady()` is `false`. The `maybe` is not decorative in any of the nine. |
| D8 | **`Wave.samples` returns a view (`slice of f32`) and `unload_wave_samples` is its release, taking the view itself.** | `LoadWaveSamples` allocates a float buffer that only `UnloadWaveSamples` frees, so the wrapper returns `ffi.slice_of_float_from_ptr` over raylib's own memory rather than copying it, and the release receives the original pointer. The same pattern as `models`' `load_animations` (its D4). Measured: the view is `frameCount * channels` floats long. |
| D9 | **Measured surprises are documented on the methods rather than smoothed over**: `LoadSoundFromWave` **resamples** (a 200-frame 44.1 kHz wave became a 218-frame sound), and `GetMusicTimeLength` on an invalid stream returns **NaN**, not `0.0`. | The first means `sound.frameCount` is the device's number and never the wave's, which a caller comparing the two would get wrong. The second means every comparison against an unguarded length is false, including `length > 0`, so the docstring points at `is_valid`. Both are the kind of thing that costs an afternoon to find. |
| D10 | `AudioStream.update` and `Sound.update` take `data as slice of byte` **plus an explicit `frame_count`**, rather than deriving the count from the slice. | The binding has both parameters because a frame's byte size depends on the channel count and sample size, so the slice's length is not the frame count. Deriving it would have meant the wrapper guessing raylib's intent; instead the docstring states the size the slice must hold and the signature stays faithful. |
| D11 | Looping a `Music` is **not** a method: the plan documents that it is the `looping` field on the value. | Measured from the binding: there is no `SetMusicLooping`; raylib 6.0 exposes `Music.looping` as a struct field, and the wrapper does not add a fake setter for it. |
| D12 | `unload_wave`, `unload_sound`, `unload_sound_alias`, `unload_music_stream` and `unload_audio_stream` are module-level, matching every other family's destructors. `Wave.copy` and `Wave.samples`, which also hand back owned or viewed memory, document their release on the method itself. | Consistency across families was the deciding argument in `textures` and `models` too: the destructor is module-level even when the constructor is a method-like loader. |
| D13 | No enchantings beyond the four types, and `Wave`, `Sound`, `Music`, `AudioStream` gain their method tables here. | No aliases are involved, so there is no `Texture2D`-style trap and no D20 cast to route around except the two `sigil of` → `void*` conversions in the update methods and the samples view. |

### ✨ Enchantings

#### `enchanting raylib.Wave` — 7 methods

| Method | Signature |
|---|---|
| `is_valid` | `into bool` |
| `copy` | `into raylib.Wave` |
| `crop` | `with init_frame as int, final_frame as int into void` |
| `to_format` | `with sample_rate as int, sample_size as int, channels as int into void` |
| `export` | `with path as string into bool` |
| `export_as_code` | `with path as string into bool` |
| `samples` | `into slice of f32` |

#### `enchanting raylib.Sound` — 10 methods

| Method | Signature |
|---|---|
| `is_valid` | `into bool` |
| `update` | `with data as slice of byte, frame_count as int into void` |
| `play` | `into void` |
| `stop` | `into void` |
| `pause` | `into void` |
| `resume` | `into void` |
| `is_playing` | `into bool` |
| `set_volume` | `with volume as f32 into void` |
| `set_pitch` | `with pitch as f32 into void` |
| `set_pan` | `with pan as f32 into void` |

#### `enchanting raylib.Music` — 13 methods

| Method | Signature |
|---|---|
| `is_valid` | `into bool` |
| `play` | `into void` |
| `is_playing` | `into bool` |
| `update` | `into void` |
| `stop` | `into void` |
| `pause` | `into void` |
| `resume` | `into void` |
| `seek` | `with position as f32 into void` |
| `set_volume` | `with volume as f32 into void` |
| `set_pitch` | `with pitch as f32 into void` |
| `set_pan` | `with pan as f32 into void` |
| `time_length` | `into f32` |
| `time_played` | `into f32` |

#### `enchanting raylib.AudioStream` — 11 methods

| Method | Signature |
|---|---|
| `is_valid` | `into bool` |
| `update` | `with data as slice of byte, frame_count as int into void` |
| `is_processed` | `into bool` |
| `play` | `into void` |
| `pause` | `into void` |
| `resume` | `into void` |
| `is_playing` | `into bool` |
| `stop` | `into void` |
| `set_volume` | `with volume as f32 into void` |
| `set_pitch` | `with pitch as f32 into void` |
| `set_pan` | `with pan as f32 into void` |

### 🔧 Module-level functions (14)

| Function | Signature |
|---|---|
| `load_wave` | `with path as string into maybe raylib.Wave` |
| `load_wave_from_memory` | `with file_type as string, data as slice of byte into maybe raylib.Wave` |
| `unload_wave` | `with wave as raylib.Wave into void` |
| `load_sound` | `with path as string into maybe raylib.Sound` |
| `load_sound_from_wave` | `with wave as raylib.Wave into maybe raylib.Sound` |
| `load_sound_alias` | `with source as raylib.Sound into maybe raylib.Sound` |
| `unload_sound` | `with sound as raylib.Sound into void` |
| `unload_sound_alias` | `with alias as raylib.Sound into void` |
| `unload_wave_samples` | `with samples as slice of f32 into void` |
| `load_music_stream` | `with path as string into maybe raylib.Music` |
| `load_music_stream_from_memory` | `with file_type as string, data as slice of byte into maybe raylib.Music` |
| `unload_music_stream` | `with music as raylib.Music into void` |
| `load_audio_stream` | `with sample_rate as int, sample_size as int, channels as int into maybe raylib.AudioStream` |
| `unload_audio_stream` | `with stream as raylib.AudioStream into void` |

### 🎁 `maybe T` wrappers

**All nine loaders**, each with its own predicate: `load_wave` and `load_wave_from_memory` with `IsWaveValid`; `load_sound`, `load_sound_from_wave` and `load_sound_alias` with `IsSoundValid`; `load_music_stream` and `load_music_stream_from_memory` with `IsMusicValid`; `load_audio_stream` with `IsAudioStreamValid`. Every one of them was measured to fail at least once (D7).

### ✂️ `slice` wrappers

| Function | Slice parameter | Kind |
|---|---|---|
| `Sound.update`, `AudioStream.update` | `data as slice of byte` | input; empty is a no-op |
| `Wave.samples` → `unload_wave_samples` | `slice of f32` | **view**; the release takes it back |
| `load_wave_from_memory`, `load_music_stream_from_memory` | `data as slice of byte` | input; empty is `maybe none` |

### 📦 Multiple returns `(T, U)`

**None apply.** `LoadWaveSamples`' `(pointer, count)` pair folds into the view's length and `LoadWaveFromMemory`'s data-size parameter is derived from the slice.

### 🌉 `std.ffi` usage

| Use | Helper | Where |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | every path, extension and export name |
| pointer → **view** | `ffi.slice_of_float_from_ptr` | `Wave.samples` |
| value → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | the two update methods |
| null check | `ffi.is_null` | the loaders, through their validity predicates |

### 💡 Compilable examples

```pengu
# Example 1 — the shortest complete audio program
import raylib
import raylibx.audio as audio

weave main into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var sound as maybe raylib.Sound is calling audio.load_sound with "shot.wav"
    if sound is present:
        var shot as raylib.Sound is calling sound.unwrap
        defer calling audio.unload_sound with shot
        calling shot.play
    return 0
```

```pengu
# Example 2 — a wave from memory, played several times at once through aliases
import raylib
import raylibx.audio as audio

weave main with encoded as slice of byte into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var wave as maybe raylib.Wave is calling audio.load_wave_from_memory with ".wav", encoded
    if wave is present:
        var w as raylib.Wave is calling wave.unwrap
        defer calling audio.unload_wave with w
        var sound as maybe raylib.Sound is calling audio.load_sound_from_wave with w
        if sound is present:
            var base as raylib.Sound is calling sound.unwrap
            defer calling audio.unload_sound with base
            var alias as maybe raylib.Sound is calling audio.load_sound_alias with base
            if alias is present:
                var copy as raylib.Sound is calling alias.unwrap
                defer calling audio.unload_sound_alias with copy
                calling copy.play
    return 0
```

```pengu
# Example 3 — an audio stream you feed yourself, and the music loop
import raylib
import raylibx.audio as audio

weave main into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var music as maybe raylib.Music is calling audio.load_music_stream with "theme.ogg"
    if music is present:
        var track as raylib.Music is calling music.unwrap
        defer calling audio.unload_music_stream with track
        calling track.play
        calling track.update
        var length as f32 is calling track.time_length
        var played as f32 is calling track.time_played
    var stream as maybe raylib.AudioStream is calling audio.load_audio_stream with 44100, 32, 1
    if stream is present:
        var out as raylib.AudioStream is calling stream.unwrap
        defer calling audio.unload_audio_stream with out
        calling out.play
    return 0
```

### 🧪 Test plan

**Eight tests, all against a real audio device**, because the device is available (D2).

- **A handmade wave is valid, copies, crops and converts** — 200 frames; the copy has the same frame count and its own buffer; `crop(0, 50)` leaves 50 frames; `to_format(44100, 16, 2)` sets `sampleSize` to 16 and `channels` to 2. All arithmetic on CPU data, so no device is needed.
- **A wave exports, reloads and exposes its samples as a view** — `export` writes a WAV that `load_wave` reads back with the same 200 frames; `export_as_code` writes its header; `samples` yields a 200-float view for a mono wave; both files and the view are released with `defer`, in the right order.
- **The wave failure paths**: `load_wave` on a missing file is `maybe none`, and `load_wave_from_memory` on eight bytes of junk is `maybe none`.
- **A sound is built from a wave and reports that it resampled** — the sound is valid, and its frame count is asserted to be non-zero rather than equal to the wave's, because D9 measured that the comparison is a trap.
- **A sound plays, pauses, resumes and stops** — `is_playing` is asserted `false`, then `true` after `play`, and the three transport calls plus the volume, pitch and pan setters and `update` are exercised.
- **A sound alias** shares the samples, is valid, and is released with `unload_sound_alias` while the source is released separately.
- **The sound and music failure paths**: `load_sound` and `load_music_stream` on missing files are `maybe none`.
- **An audio stream is created, fed and transported** — valid, `is_playing` asserted across `play` and `stop`, `update` given 128 bytes with an explicit frame count, and the setters plus the transport called. `is_processed` is **sampled but not asserted**, because whether the device has consumed the buffer yet depends on its timing and both answers are correct.

### 🚫 Not wrapped (with reason)

| C symbol | Reason |
|---|---|
| `InitAudioDevice`, `CloseAudioDevice` | one-shot global configuration, §9 row 8's shape (D4) |
| `IsAudioDeviceReady`, `GetMasterVolume`, `SetMasterVolume`, `SetAudioStreamBufferSizeDefault` | zero-argument predicate and getter, and flat global setters with no receiver and no boundary (§9 rows 1 and 8, D5) |
| `SetAudioStreamCallback`, `AttachAudioStreamProcessor`, `DetachAudioStreamProcessor`, `AttachAudioMixedProcessor`, `DetachAudioMixedProcessor` | §9 row 6: C callbacks, and PenguScript lambdas have no closures (D6) |

Coverage audit: **66 C functions, 55 wrapped, 11 not wrapped, no leftovers and no duplicates.** The method registry gains the 41 `Wave`/`Sound`/`Music`/`AudioStream` names; **no other family may add a method to any of the four types**.

## 🇪🇸 Español

### 📌 Metadatos
- Binding fuente: `pengu/raylib.d.pengu`
- Wrapper destino: `pengu/raylibx/audio.pengu`
- Dueña en el plan maestro: familia `audio` de `docs/plans/raylibx.md` (v0.1.2)
- Dependencias: `import raylib`, `import std.ffi`
- Convenciones: `docs/WRAPPER_CONVENTIONS.md` (v0.1.2)

### 🎯 Decisiones específicas del módulo

| # | Decisión | Motivo |
|---|---|---|
| D1 | Cobertura: la sección de audio tiene **66** funciones C, todas exportadas por la biblioteca instalada. **55 se envuelven** (41 métodos y 14 funciones de módulo), **5 son callbacks** y **6 son configuración global o de dispositivo de un solo uso**, y ninguno de los dos grupos se envuelve. | Enumerado desde el binding y cruzado con `tools/check_binding_symbols.py`; un script comprueba que las 66 caen exactamente en un grupo. |
| D2 | **El dispositivo de audio está disponible, así que esta familia se asegura de verdad.** Medido: `IsAudioDeviceReady()` es `1`, `SetMasterVolume`/`GetMasterVolume` hacen ida y vuelta, una `Wave` hecha a mano se convierte en un `Sound` reproducible, y `IsSoundPlaying` pasa de `false` a `true` al llamar a `play`. | El mismo paso de "medir la frontera nueva antes de prometer tests" que `window` necesitó para el display. Es la razón de que este plan reclame 8 tests en vez de una sonda de solo compilación. |
| D3 | **Cuatro tipos receptores, así que 41 de los 55 wrappers son métodos**: 7 sobre `raylib.Wave`, 10 sobre `raylib.Sound`, 13 sobre `raylib.Music` y 11 sobre `raylib.AudioStream`. | Contrato §6.1. Los cuatro tipos son cosas genuinamente distintas — datos de muestra en CPU, un búfer de reproducción que posee el dispositivo, un decodificador en streaming y un búfer donde empujas tus propias muestras — y las operaciones de cada uno van en él. Es el mayor abanico de métodos del módulo después de `images`. |
| D4 | `InitAudioDevice` y `CloseAudioDevice` **no se envuelven**, y son las únicas entradas excluidas por la *forma* de la §9 fila 8 en vez de por su texto literal. | La fila 8 nombra `InitWindow`/`CloseWindow` como configuración global de un solo uso; un dispositivo de audio tiene exactamente la misma forma, así que el mismo razonamiento aplica palabra por palabra. Los tests abren y cierran el dispositivo desde el binding, y cada docstring que necesita dispositivo lo dice. |
| D5 | `IsAudioDeviceReady`, `GetMasterVolume`, `SetMasterVolume` y `SetAudioStreamBufferSizeDefault` **tampoco se envuelven**: son un predicado sin argumentos, un getter sin argumentos y dos setters globales planos sin receptor y sin frontera. | Contrato §9 filas 1 y 8 y criterio 2. `raylib.SetMasterVolume with 0.5` ya es una llamada clara; un wrapper renombraría sin acortar. Es el mismo resultado mecánico que las 56 exclusiones de `window`, y merece decirse que la familia no es incoherente por envolver `sound.set_volume` y omitir `SetMasterVolume`: el primero tiene receptor. |
| D6 | Las **cinco entradas de callback** (`SetAudioStreamCallback`, `AttachAudioStreamProcessor`, `DetachAudioStreamProcessor`, `AttachAudioMixedProcessor`, `DetachAudioMixedProcessor`) no se envuelven. | §9 fila 6: los lambdas de PenguScript no tienen closures, y `AudioCallback` es `ref to weave with bufferData as ref to void, frames as u32 into void`. Un procesador que necesite el estado del llamador no se podría escribir, que es el mismo hallazgo que el D3 de `drawing` y el D19 del plan maestro. |
| D7 | **Los nueve cargadores devuelven `maybe`**: `load_wave`, `load_wave_from_memory`, `load_sound`, `load_sound_from_wave`, `load_sound_alias`, `load_music_stream`, `load_music_stream_from_memory`, `load_audio_stream`, y cada uno se comprueba con el predicado de su propio tipo. | Todos medidos: un fichero ausente da una onda, un sonido y una música inválidos; bytes basura y un búfer vacío dan una onda inválida; una **onda a ceros** da un sonido inválido; y **sin dispositivo alguno** `LoadAudioStream` es inválido mientras `IsAudioDeviceReady()` es `false`. El `maybe` no es decorativo en ninguno de los nueve. |
| D8 | **`Wave.samples` devuelve una vista (`slice of f32`) y `unload_wave_samples` es su liberación, que recibe la propia vista.** | `LoadWaveSamples` reserva un búfer de floats que solo `UnloadWaveSamples` libera, así que el wrapper devuelve `ffi.slice_of_float_from_ptr` sobre la memoria de raylib en vez de copiarla, y la liberación recibe el puntero original. El mismo patrón que el `load_animations` de `models` (su D4). Medido: la vista mide `frameCount * channels` floats. |
| D9 | **Las sorpresas medidas se documentan en los métodos en vez de suavizarse**: `LoadSoundFromWave` **remuestrea** (una onda de 200 frames a 44.1 kHz se convirtió en un sonido de 218), y `GetMusicTimeLength` sobre un stream inválido devuelve **NaN**, no `0.0`. | Lo primero significa que `sound.frameCount` es el número del dispositivo y nunca el de la onda, cosa que un llamador que compare los dos haría mal. Lo segundo significa que toda comparación contra una longitud sin guarda es falsa, incluida `length > 0`, así que el docstring apunta a `is_valid`. Las dos son de esas cosas que cuestan una tarde encontrar. |
| D10 | `AudioStream.update` y `Sound.update` reciben `data as slice of byte` **más un `frame_count` explícito**, en vez de derivar el recuento del slice. | El binding tiene ambos parámetros porque el tamaño en bytes de un frame depende del número de canales y del tamaño de muestra, así que la longitud del slice no es el recuento de frames. Derivarlo habría significado que el wrapper adivina la intención de raylib; en vez de eso el docstring declara el tamaño que debe tener el slice y la firma se mantiene fiel. |
| D11 | Repetir una `Music` **no** es un método: el plan documenta que es el campo `looping` del valor. | Medido desde el binding: no existe `SetMusicLooping`; raylib 6.0 expone `Music.looping` como campo del struct, y el wrapper no añade un setter falso para ello. |
| D12 | `unload_wave`, `unload_sound`, `unload_sound_alias`, `unload_music_stream` y `unload_audio_stream` son de módulo, igual que los destructores de todas las demás familias. `Wave.copy` y `Wave.samples`, que también entregan memoria con posesión o vista, documentan su liberación en el propio método. | La coherencia entre familias fue el argumento decisivo también en `textures` y `models`: el destructor es de módulo aunque el constructor sea un cargador con forma de método. |
| D13 | Sin enchantings más allá de los cuatro tipos, y `Wave`, `Sound`, `Music` y `AudioStream` ganan aquí sus tablas de métodos. | No hay alias de por medio, así que no hay trampa tipo `Texture2D` ni cast del D20 que rodear salvo las dos conversiones `sigil of` → `void*` de los métodos de actualización y la vista de muestras. |

### ✨ Enchantings

#### `enchanting raylib.Wave` — 7 métodos

| Método | Firma |
|---|---|
| `is_valid` | `into bool` |
| `copy` | `into raylib.Wave` |
| `crop` | `with init_frame as int, final_frame as int into void` |
| `to_format` | `with sample_rate as int, sample_size as int, channels as int into void` |
| `export` | `with path as string into bool` |
| `export_as_code` | `with path as string into bool` |
| `samples` | `into slice of f32` |

#### `enchanting raylib.Sound` — 10 métodos

| Método | Firma |
|---|---|
| `is_valid` | `into bool` |
| `update` | `with data as slice of byte, frame_count as int into void` |
| `play` | `into void` |
| `stop` | `into void` |
| `pause` | `into void` |
| `resume` | `into void` |
| `is_playing` | `into bool` |
| `set_volume` | `with volume as f32 into void` |
| `set_pitch` | `with pitch as f32 into void` |
| `set_pan` | `with pan as f32 into void` |

#### `enchanting raylib.Music` — 13 métodos

| Método | Firma |
|---|---|
| `is_valid` | `into bool` |
| `play` | `into void` |
| `is_playing` | `into bool` |
| `update` | `into void` |
| `stop` | `into void` |
| `pause` | `into void` |
| `resume` | `into void` |
| `seek` | `with position as f32 into void` |
| `set_volume` | `with volume as f32 into void` |
| `set_pitch` | `with pitch as f32 into void` |
| `set_pan` | `with pan as f32 into void` |
| `time_length` | `into f32` |
| `time_played` | `into f32` |

#### `enchanting raylib.AudioStream` — 11 métodos

| Método | Firma |
|---|---|
| `is_valid` | `into bool` |
| `update` | `with data as slice of byte, frame_count as int into void` |
| `is_processed` | `into bool` |
| `play` | `into void` |
| `pause` | `into void` |
| `resume` | `into void` |
| `is_playing` | `into bool` |
| `stop` | `into void` |
| `set_volume` | `with volume as f32 into void` |
| `set_pitch` | `with pitch as f32 into void` |
| `set_pan` | `with pan as f32 into void` |

### 🔧 Funciones a nivel de módulo (14)

| Función | Firma |
|---|---|
| `load_wave` | `with path as string into maybe raylib.Wave` |
| `load_wave_from_memory` | `with file_type as string, data as slice of byte into maybe raylib.Wave` |
| `unload_wave` | `with wave as raylib.Wave into void` |
| `load_sound` | `with path as string into maybe raylib.Sound` |
| `load_sound_from_wave` | `with wave as raylib.Wave into maybe raylib.Sound` |
| `load_sound_alias` | `with source as raylib.Sound into maybe raylib.Sound` |
| `unload_sound` | `with sound as raylib.Sound into void` |
| `unload_sound_alias` | `with alias as raylib.Sound into void` |
| `unload_wave_samples` | `with samples as slice of f32 into void` |
| `load_music_stream` | `with path as string into maybe raylib.Music` |
| `load_music_stream_from_memory` | `with file_type as string, data as slice of byte into maybe raylib.Music` |
| `unload_music_stream` | `with music as raylib.Music into void` |
| `load_audio_stream` | `with sample_rate as int, sample_size as int, channels as int into maybe raylib.AudioStream` |
| `unload_audio_stream` | `with stream as raylib.AudioStream into void` |

### 🎁 Wrappers `maybe T`

**Los nueve cargadores**, cada uno con su predicado: `load_wave` y `load_wave_from_memory` con `IsWaveValid`; `load_sound`, `load_sound_from_wave` y `load_sound_alias` con `IsSoundValid`; `load_music_stream` y `load_music_stream_from_memory` con `IsMusicValid`; `load_audio_stream` con `IsAudioStreamValid`. Todos y cada uno se midieron fallando al menos una vez (D7).

### ✂️ Wrappers de `slice`

| Función | Parámetro slice | Tipo |
|---|---|---|
| `Sound.update`, `AudioStream.update` | `data as slice of byte` | entrada; vacío es no-op |
| `Wave.samples` → `unload_wave_samples` | `slice of f32` | **vista**; la liberación la recupera |
| `load_wave_from_memory`, `load_music_stream_from_memory` | `data as slice of byte` | entrada; vacío es `maybe none` |

### 📦 Retornos múltiples `(T, U)`

**Ninguno aplica.** El par `(puntero, recuento)` de `LoadWaveSamples` se pliega en la longitud de la vista y el parámetro de tamaño de `LoadWaveFromMemory` se deriva del slice.

### 🌉 Uso de `std.ffi`

| Uso | Helper | Dónde |
|---|---|---|
| `string` → `const char*` | `ffi.cstr_from_string` | toda ruta, extensión y nombre de exportación |
| puntero → **vista** | `ffi.slice_of_float_from_ptr` | `Wave.samples` |
| valor → `const void*` | `transmute (sigil of …) to (ref to frozen void)` | los dos métodos de actualización |
| comprobación de nulo | `ffi.is_null` | los cargadores, a través de sus predicados de validez |

### 💡 Ejemplos compilables

```pengu
# Ejemplo 1 — el programa de audio completo más corto
import raylib
import raylibx.audio as audio

weave main into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var sound as maybe raylib.Sound is calling audio.load_sound with "shot.wav"
    if sound is present:
        var shot as raylib.Sound is calling sound.unwrap
        defer calling audio.unload_sound with shot
        calling shot.play
    return 0
```

```pengu
# Ejemplo 2 — una onda desde memoria, reproducida varias veces a la vez con alias
import raylib
import raylibx.audio as audio

weave main with encoded as slice of byte into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var wave as maybe raylib.Wave is calling audio.load_wave_from_memory with ".wav", encoded
    if wave is present:
        var w as raylib.Wave is calling wave.unwrap
        defer calling audio.unload_wave with w
        var sound as maybe raylib.Sound is calling audio.load_sound_from_wave with w
        if sound is present:
            var base as raylib.Sound is calling sound.unwrap
            defer calling audio.unload_sound with base
            var alias as maybe raylib.Sound is calling audio.load_sound_alias with base
            if alias is present:
                var copy as raylib.Sound is calling alias.unwrap
                defer calling audio.unload_sound_alias with copy
                calling copy.play
    return 0
```

```pengu
# Ejemplo 3 — un stream de audio que alimentas tú, y el bucle de la música
import raylib
import raylibx.audio as audio

weave main into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var music as maybe raylib.Music is calling audio.load_music_stream with "theme.ogg"
    if music is present:
        var track as raylib.Music is calling music.unwrap
        defer calling audio.unload_music_stream with track
        calling track.play
        calling track.update
        var length as f32 is calling track.time_length
        var played as f32 is calling track.time_played
    var stream as maybe raylib.AudioStream is calling audio.load_audio_stream with 44100, 32, 1
    if stream is present:
        var out as raylib.AudioStream is calling stream.unwrap
        defer calling audio.unload_audio_stream with out
        calling out.play
    return 0
```

### 🧪 Plan de tests

**Ocho tests, todos contra un dispositivo de audio real**, porque el dispositivo está disponible (D2).

- **Una onda hecha a mano es válida, se copia, se recorta y se convierte** — 200 frames; la copia tiene el mismo recuento y su propio búfer; `crop(0, 50)` deja 50 frames; `to_format(44100, 16, 2)` pone `sampleSize` a 16 y `channels` a 2. Todo aritmética sobre datos de CPU, así que no hace falta dispositivo.
- **Una onda se exporta, se recarga y expone sus muestras como vista** — `export` escribe un WAV que `load_wave` relee con los mismos 200 frames; `export_as_code` escribe su cabecera; `samples` da una vista de 200 floats para una onda mono; los dos ficheros y la vista se liberan con `defer`, en el orden correcto.
- **Las rutas de fallo de la onda**: `load_wave` sobre un fichero ausente es `maybe none`, y `load_wave_from_memory` sobre ocho bytes de basura es `maybe none`.
- **Un sonido se construye desde una onda y declara que remuestreó** — el sonido es válido, y su recuento de frames se asegura como distinto de cero en vez de igual al de la onda, porque el D9 midió que la comparación es una trampa.
- **Un sonido reproduce, pausa, reanuda y para** — `is_playing` se asegura `false`, luego `true` tras `play`, y se ejercitan las tres llamadas de transporte más los setters de volumen, tono y paneo y `update`.
- **Un alias de sonido** comparte las muestras, es válido, y se libera con `unload_sound_alias` mientras la fuente se libera aparte.
- **Las rutas de fallo de sonido y música**: `load_sound` y `load_music_stream` sobre ficheros ausentes son `maybe none`.
- **Un stream de audio se crea, se alimenta y se transporta** — válido, `is_playing` asegurado a través de `play` y `stop`, `update` con 128 bytes y un recuento de frames explícito, y los setters más el transporte llamados. `is_processed` se **muestrea pero no se asegura**, porque si el dispositivo ya consumió el búfer depende de su temporización y ambas respuestas son correctas.

### 🚫 NO se envuelve (con motivo)

| Símbolo C | Motivo |
|---|---|
| `InitAudioDevice`, `CloseAudioDevice` | configuración global de un solo uso, la forma de la §9 fila 8 (D4) |
| `IsAudioDeviceReady`, `GetMasterVolume`, `SetMasterVolume`, `SetAudioStreamBufferSizeDefault` | predicado y getter sin argumentos, y setters globales planos sin receptor y sin frontera (§9 filas 1 y 8, D5) |
| `SetAudioStreamCallback`, `AttachAudioStreamProcessor`, `DetachAudioStreamProcessor`, `AttachAudioMixedProcessor`, `DetachAudioMixedProcessor` | §9 fila 6: callbacks de C, y los lambdas de PenguScript no tienen closures (D6) |

Auditoría de cobertura: **66 funciones C, 55 envueltas, 11 sin envolver, sin restos y sin duplicados.** El registro de métodos gana los 41 nombres de `Wave`/`Sound`/`Music`/`AudioStream`; **ninguna otra familia puede añadir un método a ninguno de los cuatro tipos**.
