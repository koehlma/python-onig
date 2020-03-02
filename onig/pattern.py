# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import typing as t

import enum

from ._onig_cffi import ffi as _ffi, lib as _lib

from . import _encoding, match


class Option(enum.IntFlag):
    NONE = _lib.ONIG_OPTION_NONE

    SINGLELINE = _lib.ONIG_OPTION_SINGLELINE
    MULTILINE = _lib.ONIG_OPTION_MULTILINE

    IGNORECASE = _lib.ONIG_OPTION_IGNORECASE

    EXTEND = _lib.ONIG_OPTION_EXTEND

    FIND_LONGEST = _lib.ONIG_OPTION_FIND_LONGEST
    FIND_NOT_EMPTY = _lib.ONIG_OPTION_FIND_NOT_EMPTY

    NEGATE_SINGLELINE = _lib.ONIG_OPTION_NEGATE_SINGLELINE


class _DummyType:
    def __new__(cls, *args, **kwargs):
        raise Exception("only for typing")


_OnigRegex = t.NewType("_OnigRegex", _DummyType)


def _compile_pattern(
    pattern: _encoding.WrappedString, encoding: _encoding.Encoding, options: Option
) -> _OnigRegex:
    encoded_string = pattern.encode(encoding)
    regex = _ffi.new("OnigRegex*")
    error = _ffi.new("OnigErrorInfo*")
    code = _lib.onig_cffi_new(
        regex,
        encoded_string.byte_string,
        len(encoded_string.byte_string),
        options,
        _ffi.addressof(encoding.onig_encoding),
        error,
    )
    if code != _lib.ONIG_NORMAL:
        error_message = _ffi.new(f"OnigUChar[{_lib.ONIG_MAX_ERROR_MESSAGE_LEN}]")
        _lib.onig_error_code_to_str(error_message, code, error)
        raise Exception(_ffi.string(error_message).decode("ascii"))
    return regex


def _new_region() -> _OnigRegion:
    return _ffi.gc(_lib.onig_region_new(), _lib.onig_cffi_region_free)


class Pattern:
    _pattern: _encoding.WrappedString
    _regexes: t.Dict[_encoding.Encoding, _OnigRegex]
    _options: Option

    def __init__(self, pattern: str, *, options: Option = Option.NONE) -> None:
        self._pattern = _encoding.wrap(pattern)
        self._regexes = {}
        self._options = options
        self._compile(self._pattern.native_encoding)

    @property
    def pattern(self) -> str:
        return self._pattern.base_string

    @property
    def options(self) -> Option:
        return self._options

    def _compile(self, encoding: _encoding.Encoding) -> _OnigRegex:
        try:
            return self._regexes[encoding]
        except KeyError:
            self._regexes[encoding] = _compile_pattern(
                self._pattern, encoding, self._options
            )
            return self._regexes[encoding]

    def _get_common_encoding(
        self, wrapped_text: _encoding.WrappedString
    ) -> _encoding.Encoding:
        if wrapped_text.native_encoding.index > self._pattern.native_encoding.index:
            return wrapped_text.native_encoding
        else:
            return self._pattern.native_encoding

    def _search(
        self, encoded_text: _encoding.EncodedString, offset: int = 0
    ) -> t.Optional[match.Match]:
        region = _new_region()
        position = _lib.onig_cffi_search(
            self._compile(encoded_text.encoding),
            encoded_text.byte_string,
            len(encoded_text.byte_string),
            offset,
            region,
            _lib.ONIG_OPTION_NONE,
        )
        regions = [
            match.Region(region.beg[index], region.end[index])
            for index in range(region.num_regs)
        ]
        if position >= 0:
            return match.Match(self, encoded_text, regions)
        return None

    def _prepare(
        self, text: str, *, start: int = 0
    ) -> t.Tuple[_encoding.EncodedString, int]:
        wrapped_text = _encoding.wrap(text)
        encoding = self._get_common_encoding(wrapped_text)
        encoded_text = wrapped_text.encode(encoding)
        offset = encoded_text.char_offset_to_byte_offset(start)
        return encoded_text, offset

    def finditer(self, text: str, *, start: int = 0) -> t.Iterator[match.Match]:
        encoded_text, offset = self._prepare(text, start=start)
        while offset < len(encoded_text.byte_string):
            match = self._search(encoded_text, offset)
            if match is None:
                break
            yield match
            offset = match._byte_regions[0].end

    def findall(self, text: str, *, start: int = 0) -> t.Sequence[match.Match]:
        return list(self.finditer(text, start=start))

    def search(self, text: str, *, start: int = 0) -> t.Optional[match.Match]:
        encoded_text, offset = self._prepare(text, start=start)
        return self._search(encoded_text, offset)

    def get_group_numbers(self, name: str) -> t.Sequence[int]:
        encoding, regex = next(iter(self._regexes.items()))
        encoded_name = encoding.encode(name)
        number_list = _ffi.new("int**")
        list_length = _lib.onig_cffi_name_to_group_numbers(
            regex, encoded_name.byte_string, len(encoded_name.byte_string), number_list,
        )
        return [number_list[0][index] for index in range(list_length)]
