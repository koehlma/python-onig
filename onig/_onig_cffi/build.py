# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import pathlib

from importlib import resources

from cffi import FFI


DEFINITIONS = resources.read_text(__package__, "definitions.c")
SOURCE = resources.read_text(__package__, "source.c")

builder = FFI()
builder.cdef(DEFINITIONS)

builder.set_source("onig._onig_cffi.onig", SOURCE, libraries=["onig"])


if __name__ == "__main__":
    builder.compile()
