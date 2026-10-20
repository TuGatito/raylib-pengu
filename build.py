#!/usr/bin/env python3
"""Deprecated shim: forwards to ``build.pengu``.

PenguScript 2.16+ discovers ``build.pengu`` first and never runs this file. It
stays so that older toolchains (which only know ``build.py``) still build the
binding, without duplicating the build logic here.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    pengu = os.environ.get("PENGU_BIN") or shutil.which("pengu")
    if not pengu:
        print(
            "[cbind] build.py is a compatibility shim for PenguScript < 2.16.\n"
            "  Install pengu on PATH or set PENGU_BIN=/path/to/pengu, then run:\n"
            "    pengu run build.pengu -- --force",
            file=sys.stderr,
        )
        return 1
    cmd = [pengu, "run", os.path.join(HERE, "build.pengu"), "--", *sys.argv[1:]]
    return subprocess.run(cmd, cwd=HERE).returncode


if __name__ == "__main__":
    raise SystemExit(main())
