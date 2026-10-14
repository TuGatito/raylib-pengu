/* A toy implementation so `pengu init --template cbind` produces a binding
 * that actually compiles and runs. Delete it once build.py fetches the real
 * library. */
#include "raylib-pengu.h"
#include <stddef.h>

void raylib_pengu_init(int width, int height, const char *title) {
    (void)width; (void)height; (void)title;
}

void raylib_pengu_close(void) {}

int raylib_pengu_add(int a, int b) { return a + b; }

const char *raylib_pengu_greet(void) { return "Hello from raylib-pengu binding!"; }
