/* raylib-pengu.h - replace with the real C header of the library you bind.
 *
 * The real header must live in this binding's include/ directory: the
 * consumer's build adds lib/<name>/include/ to the compiler's -I path.
 */
#ifndef RAYLIB_PENGU_H
#define RAYLIB_PENGU_H

typedef struct raylib_pengu_color { unsigned char r, g, b, a; } raylib_pengu_color;

void raylib_pengu_init(int width, int height, const char *title);
void raylib_pengu_close(void);
int  raylib_pengu_add(int a, int b);
const char *raylib_pengu_greet(void);

#endif /* RAYLIB_PENGU_H */
