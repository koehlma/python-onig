# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tarfile

from distutils.command.build_ext import build_ext  # type: ignore

from urllib import request

import cffi


DEPS_PATH = pathlib.Path("deps")


ONIGURUMA_VERSION = "6.9.4"

ONIGURUMA_URL = f"https://github.com/kkos/oniguruma/archive/v{ONIGURUMA_VERSION}.tar.gz"

ONIGURUMA_TAR_GZ = DEPS_PATH / "oniguruma.tar.gz"
ONIGURUMA_BUILD = DEPS_PATH / "oniguruma_build"


DEFINITIONS = (pathlib.Path("onig") / "_onig_cffi" / "definitions.c").read_text()
SOURCE = (pathlib.Path("onig") / "_onig_cffi" / "source.c").read_text()


ffi = cffi.FFI()
ffi.cdef(DEFINITIONS)
ffi.set_source("onig._onig_cffi._onig_cffi", SOURCE)

extension = ffi.distutils_extension()


def download_oniguruma():
    DEPS_PATH.mkdir(exist_ok=True)
    if not ONIGURUMA_TAR_GZ.exists():
        response = request.urlopen(ONIGURUMA_URL)
        if response.status != 200:
            raise Exception(
                "unable to download the Oniguruma regular expression library"
            )
        ONIGURUMA_TAR_GZ.write_bytes(response.read())


def build_oniguruma(environment):
    if ONIGURUMA_BUILD.exists():
        shutil.rmtree(ONIGURUMA_BUILD)
    with tarfile.open(ONIGURUMA_TAR_GZ, "r:gz") as oniguruma_tar_gz:
        oniguruma_tar_gz.extractall(path=ONIGURUMA_BUILD)
    oniguruma_path = next(ONIGURUMA_BUILD.glob("oniguruma-*"))
    extension.include_dirs.append(str(oniguruma_path / "src"))
    if sys.platform == "win32":
        subprocess.check_call(
            ["make_win.bat"], shell=True, cwd=oniguruma_path, env=environment
        )
        extension.libraries.append("onig")
        extension.library_dirs.append(str(oniguruma_path))

        shutil.copy(oniguruma_path / "onig.dll", "onig/_onig_cffi/onig.dll")
    elif sys.platform == "linux":
            subprocess.check_call(["autoreconf", "-vfi"], cwd=oniguruma_path, env=environment)
            subprocess.check_call(["./configure"], cwd=oniguruma_path, env=environment)
            subprocess.check_call(["make"], cwd=oniguruma_path, env=environment)

            extension.extra_objects.append(
                str(oniguruma_path / "src" / ".libs" / "libonig.a")
            )
    else:
        raise Exception(f"cannot build Oniguruma for platform {sys.platform!r}")


class BuildExtensions(build_ext):
    def build_extensions(self):
        DEPS_PATH.mkdir(exist_ok=True)

        download_oniguruma()

        if sys.platform == "win32":
            from distutils import _msvccompiler
            from distutils.util import get_platform

            platform_name = self.compiler.plat_name or get_platform()
            platform_spec = _msvccompiler.PLAT_TO_VCVARS[platform_name]

            vc_env = _msvccompiler._get_vc_env(platform_spec)

            
            build_oniguruma(environment=vc_env)
        elif sys.platform == "linux":
            environ = dict(os.environ)
            if 'CFLAGS' not in environ:
                environ['CFLAGS'] = ''
            environ['CFLAGS'] += ' -fPIC'
            build_oniguruma(environment=environ)
        else:
            raise Exception(f"cannot build Oniguruma for platform {sys.platform!r}")

        build_ext.build_extensions(self)


def build(setup_kwargs):
    setup_kwargs.update(
        {"ext_modules": [extension], "cmdclass": {"build_ext": BuildExtensions}}
    )
