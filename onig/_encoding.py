# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import typing as t

import abc
import enum
import platform
import warnings

from ._onig_cffi import ffi as _ffi, lib as _lib

try:
    from unibuf import UnicodeBuffer
except ImportError:
    if platform.python_implementation() == "CPython":
        warnings.warn(
            f"'unibuf' is not installed; 'onig' will be slow for unicode strings",
            category=ResourceWarning,
        )
    UnicodeBuffer = None


class EncodedString(abc.ABC):
    encoding: Encoding

    unicode_string: str
    encoded_string: bytes

    def __init__(
        self, encoding: Encoding, unicode_string: str, byte_string: bytes
    ) -> None:
        self.encoding = encoding
        self.unicode_string = unicode_string
        self.byte_string = byte_string

    @abc.abstractmethod
    def byte_offset_to_char_offset(self, offset: int) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def char_offset_to_byte_offset(self, offset: int) -> int:
        raise NotImplementedError()

    def substring_by_byte_offset(self, start: int, end: int) -> str:
        return self.substring_by_char_offset(
            self.byte_offset_to_char_offset(start), self.byte_offset_to_char_offset(end)
        )

    def substring_by_char_offset(self, start: int, end: int) -> str:
        return self.unicode_string[start:end]


class SingleByteString(EncodedString):
    def byte_offset_to_char_offset(self, offset: int) -> int:
        return offset

    def char_offset_to_byte_offset(self, offset: int) -> int:
        return offset


class UTF8String(EncodedString):
    def byte_offset_to_char_offset(self, offset: int) -> int:
        return len(self.byte_string[:offset].decode("utf-8"))

    def char_offset_to_byte_offset(self, offset: int) -> int:
        return len(self.unicode_string[:offset].encode("utf-8"))

    def substring_by_byte_offset(self, start: int, end: int) -> str:
        return self.byte_string[start:end].decode("utf-8")


class UTF16String(EncodedString):
    def byte_offset_to_char_offset(self, offset: int) -> int:
        return offset // 2

    def char_offset_to_byte_offset(self, offset: int) -> int:
        return offset * 2


class UTF32String(EncodedString):
    def byte_offset_to_char_offset(self, offset: int) -> int:
        return offset // 4

    def char_offset_to_byte_offset(self, offset: int) -> int:
        return offset * 4


_encoding_map: t.Dict[str, Encoding] = {}


class Encoding(enum.Enum):
    encoding_name: str

    onig_encoding: t.Any

    index: int

    string_cls: t.Type[EncodedString]

    ASCII = "ASCII", _lib.OnigEncodingASCII, 0, SingleByteString

    ISO_8859_1 = "ISO-8859-1", _lib.OnigEncodingISO_8859_1, 1, SingleByteString

    UTF_8 = "UTF-8", _lib.OnigEncodingUTF8, 2, UTF8String

    UTF_16LE = "UTF-16LE", _lib.OnigEncodingUTF16_LE, 3, UTF16String
    UTF_16BE = "UTF-16BE", _lib.OnigEncodingUTF16_BE, 3, UTF16String

    UTF_32LE = "UTF-32LE", _lib.OnigEncodingUTF32_LE, 4, UTF32String
    UTF_32BE = "UTF-32BE", _lib.OnigEncodingUTF32_BE, 4, UTF32String

    def __init__(
        self,
        encoding_name: str,
        onig_encoding: t.Any,
        index: int,
        string_cls: t.Type[EncodedString],
    ) -> None:
        _encoding_map[encoding_name] = self
        self.encoding_name = encoding_name
        self.onig_encoding = onig_encoding
        self.index = index
        self.string_cls = string_cls

    def encode(self, text: str) -> EncodedString:
        return self.string_cls(self, text, text.encode(self.encoding_name))

    @staticmethod
    def get_by_name(name: str) -> Encoding:
        try:
            return _encoding_map[name.upper()]
        except KeyError:
            raise Exception(f"unknown encoding {name}")


class WrappedString:
    base_string: str
    native_encoding: Encoding

    _encoded_strings: t.Dict[Encoding, EncodedString]

    def __init__(
        self,
        base_string: str,
        native_encoding: Encoding = Encoding.UTF_8,
        *,
        _encoded_strings: t.Optional[t.Dict[Encoding, EncodedString]] = None,
    ) -> None:
        self.base_string = base_string
        self.native_encoding = native_encoding
        self._encoded_strings = _encoded_strings or {}

    def encode(self, encoding: Encoding) -> EncodedString:
        try:
            return self._encoded_strings[encoding]
        except KeyError:
            self._encoded_strings[encoding] = encoding.encode(self.base_string)
            return self._encoded_strings[encoding]


def wrap(
    base_string: str, *, native_encoding: t.Optional[Encoding] = None
) -> WrappedString:
    if native_encoding is None and UnicodeBuffer is not None:
        buffer = UnicodeBuffer(base_string)
        native_encoding = Encoding.get_by_name(buffer.encoding)
        return WrappedString(
            base_string,
            native_encoding,
            _encoded_strings={
                native_encoding: native_encoding.string_cls(
                    native_encoding, base_string, bytes(buffer)
                )
            },
        )
    return WrappedString(base_string, native_encoding or Encoding.UTF_8)


def _onig_initialize() -> None:
    encodings = _ffi.new(
        "OnigEncoding[]",
        [_ffi.addressof(encoding.onig_encoding) for encoding in Encoding],
    )
    _lib.onig_initialize(encodings, _ffi.sizeof(encodings) // _ffi.sizeof(encodings[0]))


_onig_initialize()
