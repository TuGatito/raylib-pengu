> [Reference index](../README.md) · [Notes and traps](../NOTES.md)

# audio

> Source: `pengu/raylibx/audio.pengu`

Layer-2 wrapper over the 55 audio functions of the `raylib` binding, out of the 66 in the
audio section: 5 callback entries are excluded because PenguScript lambdas have no closures
and 6 are one-shot device or global configuration.

This family has **four receiver types**, which is why almost everything is a method:

    SetSoundVolume(sound, 0.5f);     IsSoundPlaying(sound)      # binding
    calling sound.set_volume with 0.5;  calling sound.is_playing # wrapper

`Wave` is CPU sample data, `Sound` is a playback buffer the device owns, `Music` is a
streaming decoder that must be pumped every frame, and `AudioStream` is a buffer you push
your own samples into. The module-level entries are the loaders and their releases.

## The device is a precondition, not an option
`InitAudioDevice` and `CloseAudioDevice` are **not** wrapped: contract section 9 row 8's
shape (one-shot global configuration) applies exactly, so the device is opened through the
binding. Measured: with no device, `IsAudioDeviceReady()` is `false` and every loader that
needs the device returns an invalid value, which is what the `maybe` returns capture. A
**`Wave`**, on the other hand, is pure CPU data and loads with the device closed.

## Measured surprises worth knowing
* `LoadSoundFromWave` **resamples**: a 200-frame 44.1 kHz wave produced a 218-frame sound.
* `GetMusicTimeLength` on an invalid stream returns **NaN**, not zero, so every comparison
  against it is false. Guard with `is_valid`.
* Looping a `Music` is not a function call: set its `looping` field.

This is family `audio` of `raylibx`; see `docs/wrappers/raylibx-audio.md`.

## Memory
Waves own their sample buffer (`unload_wave`), sounds own a playback buffer
(`unload_sound`) unless they are aliases (`unload_sound_alias`), music streams own a decoder
(`unload_music_stream`), and `Wave.samples` returns a **view** released by
`unload_wave_samples`.

## Example
```pengu
import raylib
import raylibx_audio

weave main into int:
    calling raylib.InitAudioDevice
    defer calling raylib.CloseAudioDevice
    var sound as maybe raylib.Sound is calling raylibx_audio.load_sound with "shot.wav"
    if sound is present:
        var shot as raylib.Sound is calling sound.unwrap
        defer calling raylibx_audio.unload_sound with shot
        calling shot.play
    return 0
```

---

### `load_wave`

> **load_wave**(path: string) -> maybe Wave

_Undocumented function._


### `load_wave_from_memory`

> **load_wave_from_memory**(file_type: string, data: slice of byte) -> maybe Wave

_Undocumented function._


### `unload_wave`

> **unload_wave**(wave: Wave) -> void

_Undocumented function._


### `load_sound`

> **load_sound**(path: string) -> maybe Sound

_Undocumented function._


### `load_sound_from_wave`

> **load_sound_from_wave**(wave: Wave) -> maybe Sound

_Undocumented function._


### `load_sound_alias`

> **load_sound_alias**(source: Sound) -> maybe Sound

_Undocumented function._


### `unload_sound`

> **unload_sound**(sound: Sound) -> void

_Undocumented function._


### `unload_sound_alias`

> **unload_sound_alias**(alias: Sound) -> void

_Undocumented function._


### `unload_wave_samples`

> **unload_wave_samples**(samples: slice of f32) -> void

_Undocumented function._


### `load_music_stream`

> **load_music_stream**(path: string) -> maybe Music

_Undocumented function._


### `load_music_stream_from_memory`

> **load_music_stream_from_memory**(file_type: string, data: slice of byte) -> maybe Music

_Undocumented function._


### `unload_music_stream`

> **unload_music_stream**(music: Music) -> void

_Undocumented function._


### `load_audio_stream`

> **load_audio_stream**(sample_rate: int, sample_size: int, channels: int) -> maybe AudioStream

_Undocumented function._


### `unload_audio_stream`

> **unload_audio_stream**(stream: AudioStream) -> void

_Undocumented function._


### `make_wave`

> **make_wave**() -> Wave

A handmade wave: raylib validates waves by their buffer, so this is a real one.

