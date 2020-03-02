# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

# try:
#     from .onig import ffi, lib
# except ImportError:
from .build import builder

builder.compile()
from .onig import ffi, lib

