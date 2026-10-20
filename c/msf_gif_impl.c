/* msf_gif is a single-header library: its implementation only exists in the
 * translation unit that defines MSF_GIF_IMPL before including the header.
 *
 * `examples/core/core_screen_recording.pengu` includes `examples/core/msf_gif.h`
 * for the declarations and bridges the encoder through `antiquus`; this file
 * supplies the one translation unit the header asks for, so `pengu run` on that
 * example links without any extra build step.
 */
#define MSF_GIF_IMPL
#include "../examples/core/msf_gif.h"
