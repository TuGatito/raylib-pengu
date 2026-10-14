#!/usr/bin/env python3
"""Builds the native part of the `raylib-pengu` PenguScript binding.

Invoked by `pengu add <repo> --trust` and re-run by `pengu update`. It must
leave the compiled library in ./lib/ so the consumer's `pengu build` finds it
(`-Llib` plus the `link "raylib"` statement in pengu/raylib.d.pengu).

The binding's own `include/*.h` are committed and authoritative: `pengu bind`
generated pengu/*.d.pengu from *those* headers, so this script never overwrites
them. It builds raylib from source and, when the source tree's headers differ
from the committed ones, says so loudly.

Where the source tree comes from (first hit wins):

    $RAYLIB_SRC          an existing raylib checkout
    vendor/raylib        a checkout left by a previous run
    extern/raylib-*      a vendored tree (e.g. the PenguScript compiler's)
    (none)               `git clone` the pinned RAYLIB_REF into vendor/raylib

If none of that is possible (no git, no network, no `make`) the script exits 0
after explaining the alternatives: a system libraylib is enough for consumers,
because the binding links with `-lraylib`.
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(HERE, "lib")
INC_DIR = os.path.join(HERE, "include")
VENDOR_DIR = os.path.join(HERE, "vendor")

RAYLIB_REPO = "https://github.com/raysan5/raylib.git"
RAYLIB_REF = os.environ.get("RAYLIB_REF", "master")

# Only raylib itself is built here; raygui is compiled from include/raygui.h by
# c/raygui_impl.c (see that file), so it is never fetched.
HEADERS = ("raylib.h", "raymath.h", "rlgl.h", "rcamera.h", "rgestures.h", "raygui.h")


def log(message: str) -> None:
    print("[cbind] " + message, flush=True)


def find_source_tree() -> str | None:
    """Returns a raylib source directory that contains src/Makefile."""
    candidates = []
    if os.environ.get("RAYLIB_SRC"):
        candidates.append(os.environ["RAYLIB_SRC"])
    candidates.append(os.path.join(VENDOR_DIR, "raylib"))
    candidates.extend(sorted(glob.glob(os.path.join(HERE, "extern", "raylib-*"))))
    for candidate in candidates:
        if candidate and os.path.isfile(os.path.join(candidate, "src", "Makefile")):
            return os.path.abspath(candidate)
    return None


def clone_source_tree() -> str | None:
    """Clones the pinned raylib ref into vendor/raylib, or returns None."""
    if shutil.which("git") is None:
        log("git is not available; cannot fetch raylib")
        return None
    target = os.path.join(VENDOR_DIR, "raylib")
    os.makedirs(VENDOR_DIR, exist_ok=True)
    log(f"cloning {RAYLIB_REPO} ({RAYLIB_REF}) into vendor/raylib")
    result = subprocess.run(["git", "clone", "--depth", "1", "--branch", RAYLIB_REF,
                             RAYLIB_REPO, target])
    if result.returncode != 0:
        log("git clone failed (offline?)")
        return None
    return target


def _same_file(a: str, b: str) -> bool:
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def header_status(source_tree: str) -> dict[str, str]:
    """Maps each committed header to same/differs/missing against the tree."""
    out = {}
    for header in HEADERS:
        local = os.path.join(INC_DIR, header)
        upstream = os.path.join(source_tree, "src", header)
        if not os.path.isfile(local):
            out[header] = "missing"
        elif os.path.isfile(upstream):
            out[header] = "same" if _same_file(local, upstream) else "differs"
        else:
            out[header] = "same"
    return out


def build(source_tree: str) -> str | None:
    """Builds libraylib.a and returns its path, or None on failure."""
    src = os.path.join(source_tree, "src")
    log(f"building raylib in {src} (make PLATFORM=PLATFORM_DESKTOP)")
    result = subprocess.run(["make", "-C", src, "PLATFORM=PLATFORM_DESKTOP", "-j"])
    if result.returncode != 0:
        log("raylib build failed")
        return None
    archive = os.path.join(src, "libraylib.a")
    if not os.path.isfile(archive):
        log(f"expected archive not found: {archive}")
        return None
    return archive


def system_raylib_available() -> bool:
    if shutil.which("pkg-config") and subprocess.run(
            ["pkg-config", "--exists", "raylib"]).returncode == 0:
        return True
    for pattern in ("/usr/lib/libraylib.so*", "/usr/local/lib/libraylib.so*",
                    "/usr/lib/libraylib.a", "/usr/local/lib/libraylib.a"):
        if glob.glob(pattern):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true",
                        help="rebuild even when lib/libraylib.a already exists")
    args = parser.parse_args()

    os.makedirs(LIB_DIR, exist_ok=True)
    os.makedirs(INC_DIR, exist_ok=True)

    archive = os.path.join(LIB_DIR, "libraylib.a")
    if os.path.isfile(archive) and not args.force:
        log(f"libraylib.a already present in {LIB_DIR} (use --force to rebuild)")
        return 0

    source_tree = find_source_tree() or clone_source_tree()
    if source_tree is None:
        if system_raylib_available():
            log("no raylib source tree; a system libraylib will be used via `-lraylib`")
            return 0
        log("no raylib source tree and no system libraylib found")
        log("set RAYLIB_SRC=/path/to/raylib, install raylib, or allow `git clone`")
        return 1

    for header, status in header_status(source_tree).items():
        if status == "differs":
            log(f"WARNING: include/{header} differs from {source_tree}/src/{header}; "
                "pengu/*.d.pengu was generated from the committed header")

    built = build(source_tree)
    if built is None:
        return 1

    shutil.copy2(built, archive)
    log(f"installed {archive}")

    # The committed headers stay authoritative; only fill in what is missing.
    for header in HEADERS:
        local = os.path.join(INC_DIR, header)
        upstream = os.path.join(source_tree, "src", header)
        if not os.path.isfile(local) and os.path.isfile(upstream):
            shutil.copy2(upstream, local)
            log(f"staged missing header include/{header}")

    log("done - artifacts in " + LIB_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
