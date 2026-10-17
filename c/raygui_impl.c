/* raygui is a single-header library: its implementation only exists in the
 * translation unit that defines RAYGUI_IMPLEMENTATION before including it.
 * raylib itself compiles raygui only when it is built with
 * RAYLIB_MODULE_RAYGUI=TRUE (src/Makefile), which is not the default, so the
 * Gui* functions are not in libraylib and must be compiled here.
 *
 * This file is glue: the consumer's build compiles c/*.c of every installed
 * binding into the bundle (PenguScript's own docs/BINDINGS.md §2.3, "glue C"),
 * so `import raygui` gets a working implementation with no extra archive.
 *
 * If you link a raylib that was itself built with RAYLIB_MODULE_RAYGUI=TRUE,
 * remove this file or the Gui* symbols will be defined twice.
 */
#define RAYGUI_IMPLEMENTATION
#include "raygui.h"
