# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import typing as t

import dataclasses
import functools

from . import _encoding


if t.TYPE_CHECKING:
    from .pattern import Pattern


@dataclasses.dataclass(frozen=True)
class Region:
    begin: int
    end: int


Regions = t.Sequence[Region]


class Match:
    pattern: Pattern

    _encoded_string: _encoding.EncodedString
    _byte_regions: Regions

    def __init__(
        self,
        pattern: Pattern,
        encoded_string: _encoding.EncodedString,
        byte_regions: Regions,
    ) -> None:
        self.pattern = pattern
        self._encoded_string = encoded_string
        self._byte_regions = byte_regions

    @functools.cached_property
    def start(self) -> int:
        return self._encoded_string.byte_offset_to_char_offset(
            self._byte_regions[0].begin
        )

    @functools.cached_property
    def end(self) -> int:
        return self._encoded_string.byte_offset_to_char_offset(
            self._byte_regions[0].end
        )

    @functools.cached_property
    def region(self) -> Region:
        return Region(self.start, self.end)

    @functools.cached_property
    def regions(self) -> Regions:
        return tuple(
            Region(
                self._encoded_string.byte_offset_to_char_offset(region.begin),
                self._encoded_string.byte_offset_to_char_offset(region.end),
            )
            for region in self._byte_regions
        )

    @t.overload
    def group(self, key: int) -> str:
        pass

    @t.overload
    def group(self, key: str) -> t.Sequence[str]:
        pass

    def group(self, key: t.Union[int, str]) -> t.Union[str, t.Sequence[str]]:
        if isinstance(key, int):
            return self._group_by_number(key)
        else:
            return [
                self._group_by_number(index)
                for index in self.pattern.get_group_numbers(key)
            ]

    def _group_by_number(self, index: int) -> str:
        try:
            return self._encoded_string.substring_by_byte_offset(
                self._byte_regions[index].begin, self._byte_regions[index].end
            )
        except IndexError:
            raise Exception(f"invalid group number {index}")

    def groups(self) -> t.Sequence[str]:
        return [
            self._group_by_number(index) for index in range(len(self._byte_regions))
        ]

    def __repr__(self) -> str:
        return (
            f"<onig.Match region=({self.start}, {self.end}), match={self.group(0)!r}>"
        )
