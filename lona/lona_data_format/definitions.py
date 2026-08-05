# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Message definitions for the LONA data format.

The definitions are loaded and processed during import of the module. The definitions may be used for code generation
for coders in other programming languages or they may be directly used for a Python coder.
"""

__all__ = [
    "EXTRA_CHUNK_HEADER_INTERFACE_DEF",
    "LATEST_PROTOCOL_VERSION",
    "MESSAGE_FORMATS",
    "MESSAGE_HEADER_DEF_STRUCT",
]

import struct
from collections import namedtuple

from ._data_format import v_0_4, v_0_5, v_0_6, v_0_7, v_0_8
from ._data_format.common_chunk_header import (
    COMMON_CHUNK_HEADER_MESSAGE,
    EXTRA_CHUNK_HEADER_INTERFACE,
)

# Maximum message size including header LonaDataUploader can transport `sizeof(((tLonaDataUploaderTif_Write *)0)->buf)`
LONA_DATA_UPLOADER_CAPACITY = 128

DATA_FORMATS = {
    None: [COMMON_CHUNK_HEADER_MESSAGE],
    (0, 4): v_0_4.MESSAGES,
    (0, 5): v_0_5.MESSAGES,
    (0, 6): v_0_6.MESSAGES,
    (0, 7): v_0_7.MESSAGES,
    (0, 8): v_0_8.MESSAGES,
}
LATEST_PROTOCOL_VERSION = (0, 8)

assert LATEST_PROTOCOL_VERSION in DATA_FORMATS

MessageFieldTypeDef = namedtuple(
    "MessageFieldTypeDef",
    "format_char, json_decode, buffer_encode, buffer_decode, c_type_arg_l, c_type_arg_r, c_type_field_l, c_type_field_r, java_type, java_read",
)
"""Definition of a data type of a field in a message.

- `format_char` is for the Python coder, also it defines the length of the field.
- `json_decode`, `buffer_encode` and `buffer_decode` are for the Python coder.
- `c_type_arg_l`, `c_type_arg_r`,`c_type_field_l` and `c_type_field_r` are for C code generation.
- `java_type` and `java_read` are for Java code generation.
"""


def _pack_int24_le(value):
    if value < -0x800000 or value > 0x7FFFFF:
        raise ValueError("int24 format requires -0x800000 <= number <= 0x7fffff")
    return struct.pack("<HB", value & 0xFFFF, (value >> 16) & 0xFF)


def _pack_uint24_le(value):
    if value < 0 or value > 0xFFFFFF:
        raise ValueError("uint24 format requires 0 <= number <= 0xffffff")
    return struct.pack("<HB", value & 0xFFFF, (value >> 16) & 0xFF)


def _unpack_int24_le(buf):
    lo, hi = struct.unpack("<HB", buf)
    neg = 0
    if hi & 0x80:
        neg = 0x1000000
    return (lo | (hi << 16)) - neg


def _unpack_uint24_le(buf):
    lo, hi = struct.unpack("<HB", buf)
    return lo | (hi << 16)


class MessageFieldDef:
    """Definition of a single field in a message."""

    MESSAGE_FIELD_TYPES = {
        "bool": MessageFieldTypeDef(
            "?",
            bool,
            bool,
            bool,
            "bool",
            "",
            "bool",
            "",
            "Boolean",
            "{bb}.get({pos}) != 0",
        ),
        "int8": MessageFieldTypeDef(
            "b", int, int, int, "int8_t", "", "int8_t", "", "Byte", "{bb}.get({pos})"
        ),
        "uint8": MessageFieldTypeDef(
            "B",
            int,
            int,
            int,
            "uint8_t",
            "",
            "uint8_t",
            "",
            "Short",
            "(short) ({bb}.get({pos}) & 0xFF)",
        ),
        "int16": MessageFieldTypeDef(
            "h",
            int,
            int,
            int,
            "int16_t",
            "",
            "int16_t",
            "",
            "Short",
            "{bb}.getShort({pos})",
        ),
        "uint16": MessageFieldTypeDef(
            "H",
            int,
            int,
            int,
            "uint16_t",
            "",
            "uint16_t",
            "",
            "Integer",
            "{bb}.getShort({pos}) & 0xFFFF",
        ),
        "int24": MessageFieldTypeDef(
            "3s",
            int,
            _pack_int24_le,
            _unpack_int24_le,
            "int32_t",
            "",
            "uint8_t",
            "[3]",
            "Integer",
            "({bb}.getShort({pos}) & 0xFFFF) | (({bb}.get({pos} + 2) & 0xFF) << 16) | ((({bb}.get({pos} + 2) & 0x80) != 0 ? 0xFF : 0) << 24)",
        ),
        "uint24": MessageFieldTypeDef(
            "3s",
            int,
            _pack_uint24_le,
            _unpack_uint24_le,
            "uint32_t",
            "",
            "uint8_t",
            "[3]",
            "Integer",
            "({bb}.getShort({pos}) & 0xFFFF) | (({bb}.get({pos} + 2) & 0xFF) << 16)",
        ),
        "int32": MessageFieldTypeDef(
            "i",
            int,
            int,
            int,
            "int32_t",
            "",
            "int32_t",
            "",
            "Integer",
            "{bb}.getInt({pos})",
        ),
        "uint32": MessageFieldTypeDef(
            "I",
            int,
            int,
            int,
            "uint32_t",
            "",
            "uint32_t",
            "",
            "Long",
            "{bb}.getInt({pos}) & 0xFFFFFFFFL",
        ),
        "bytes16": MessageFieldTypeDef(
            "16s",
            lambda s: bytes(s, encoding="utf-8"),
            bytes,
            lambda b: b.rstrip(b"\0"),
            "const uint8_t",
            "[16]",
            "uint8_t",
            "[16]",
            "String",
            "new StringReader({bb}).read({pos}, 16)",
        ),
        "bytes64": MessageFieldTypeDef(
            "64s",
            lambda s: bytes(s, encoding="utf-8"),
            bytes,
            lambda b: b.rstrip(b"\0"),
            "const uint8_t",
            "[64]",
            "uint8_t",
            "[64]",
            "String",
            "new StringReader({bb}).read({pos}, 64)",
        ),
    }

    for type_name, field_def in MESSAGE_FIELD_TYPES.items():
        if field_def.c_type_field_r:
            if field_def.c_type_field_r.startswith(
                "["
            ) and field_def.c_type_field_r.endswith("]"):
                if field_def.c_type_field_l != "uint8_t":
                    raise ValueError(
                        f"Defined type {type_name} is an array without basic type uint8_t."
                    )
                if int(field_def.c_type_field_r[1:-1]) != struct.calcsize(
                    field_def.format_char
                ):
                    raise ValueError(
                        f"Length of defined type {type_name} does not match."
                    )
            else:
                raise ValueError(
                    f"Unknown c_type_field_r format for defined type {type_name}."
                )

    def __init__(self, name, type_):
        self.name = name
        self.type_ = self.MESSAGE_FIELD_TYPES[type_]
        self.size = struct.calcsize(self.type_.format_char)


class MessageDef:
    """Definition of a message with all fields."""

    def __init__(self, class_, name, type_id, fields):
        self.class_ = class_  # 'Transport', 'MetaData' or 'Event'
        self.name = name
        self.type_id = type_id
        self.fields = [MessageFieldDef(*f) for f in fields]
        self.fields_by_name = {f.name: f for f in self.fields}
        # little-endian byte order
        self.struct = struct.Struct(
            "<" + "".join([f.type_.format_char for f in self.fields])
        )
        self.parameters_class = namedtuple(
            self.name, ",".join([f.name for f in self.fields])
        )


def init_message_formats():
    message_formats = {}
    for version, messages in DATA_FORMATS.items():
        # verify transport header starts with common format
        if (
            messages[0][:-1] != COMMON_CHUNK_HEADER_MESSAGE[:-1]
            or messages[0][3][: len(COMMON_CHUNK_HEADER_MESSAGE[3])]
            != COMMON_CHUNK_HEADER_MESSAGE[3]
        ):
            raise RuntimeError(
                "The first defined message must start with the common chunk header structure."
            )

        # verify extra metadata in the chunk header respect the common interface
        extra_fields_by_name = dict(EXTRA_CHUNK_HEADER_INTERFACE)
        for name, type_ in messages[0][3]:
            if extra_fields_by_name.get(name, type_) != type_:
                raise RuntimeError(
                    "A chunk header field has a different type than defined in the common interface."
                )

        message_defs = [MessageDef(*m) for m in messages]
        if any(
            md.struct.size + MESSAGE_HEADER_DEF_STRUCT.size
            > LONA_DATA_UPLOADER_CAPACITY
            for md in message_defs
        ):
            raise RuntimeError("Message size exceeds LonaDataUploader capacity.")
        mf = {
            "message_defs": message_defs,
            "message_defs_by_class_and_name": {
                (m.class_, m.name): m for m in message_defs
            },
            "message_defs_by_type_id": {m.type_id: m for m in message_defs},
        }
        if len(set([len(v) for v in mf.values()])) != 1:
            raise RuntimeError(
                "Duplicate message class and names or type ids in definition."
            )
        message_formats[version] = mf
    return message_formats


MESSAGE_HEADER_DEF_STRUCT = struct.Struct("BB")
MESSAGE_FORMATS = init_message_formats()
EXTRA_CHUNK_HEADER_INTERFACE_DEF = MessageDef(
    None, "ExtraChunkHeaderInterface", None, EXTRA_CHUNK_HEADER_INTERFACE
)
