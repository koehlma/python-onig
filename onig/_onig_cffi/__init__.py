# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

try:
    from ._onig_cffi import ffi, lib
except ImportError:
    from .build import builder

    builder.compile()

    from ._onig_cffi import ffi, lib


__all__ = ["ffi", "lib"]
