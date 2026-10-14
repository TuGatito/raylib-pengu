#!/usr/bin/env python3
"""Builds the native part of the `raylib-pengu` PenguScript binding.

Invoked by `pengu add <repo> --trust`, or manually with `python build.py` from
the binding's own directory. It must leave the compiled library in ./lib/ and
the header in ./include/, so the consumer's `pengu build` auto-detects both.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(HERE, "lib")
INC_DIR = os.path.join(HERE, "include")
C_DIR = os.path.join(HERE, "c")


def _cc() -> str:
    """The C compiler to use: $CC, else gcc, else clang, else cc."""
    return os.environ.get("CC") or shutil.which("gcc") or shutil.which("clang") or "cc"


def _ar() -> str:
    """The static archiver to use: $AR, else ar, else llvm-ar."""
    return os.environ.get("AR") or shutil.which("ar") or shutil.which("llvm-ar") or "ar"


def main() -> int:
    os.makedirs(LIB_DIR, exist_ok=True)
    os.makedirs(INC_DIR, exist_ok=True)
    os.makedirs(C_DIR, exist_ok=True)

    # TODO: replace this block with the real fetch/compile logic for
    # `raylib-pengu`. For example (raylib):
    #     subprocess.run(["git", "clone", "--depth", "1",
    #                     "https://github.com/raysan5/raylib.git", "vendor/raylib"],
    #                    check=True)
    #     subprocess.run(["make", "-C", "vendor/raylib/src",
    #                     "PLATFORM=PLATFORM_DESKTOP"], check=True)
    #     shutil.copy("vendor/raylib/src/libraylib.a", LIB_DIR)
    #     shutil.copy("vendor/raylib/src/raylib.h", INC_DIR)
    #
    # Keep the script idempotent: `pengu update` re-runs it.

    src = os.path.join(C_DIR, "raylib-pengu.c")
    if os.path.isfile(src):
        obj = os.path.join(LIB_DIR, "raylib-pengu.o")
        lib = os.path.join(LIB_DIR, "libraylib-pengu.a")
        print("[cbind] compiling " + src)
        subprocess.run([_cc(), "-c", "-fPIC", "-I", INC_DIR, src, "-o", obj],
                       check=True)
        print("[cbind] archiving " + lib)
        subprocess.run([_ar(), "rcs", lib, obj], check=True)

    print("[cbind] done - artifacts in " + LIB_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
