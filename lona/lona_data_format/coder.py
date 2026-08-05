# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Python coder for the LONA data format.

This module is intended only for use in development and testing.
"""

__all__ = [
    "ChunkCoder",
    "ChunkHeaderCoder",
    "json_decode_message",
    "json_encode_message",
    "MessageCoder",
]

import itertools
import logging

from lona_data_format.definitions import MESSAGE_FORMATS, MESSAGE_HEADER_DEF_STRUCT


class MessageCoder:
    def __init__(self, definition, parameters, ignored_parameters=None):
        if not isinstance(parameters, definition.parameters_class):
            # decoding from json
            p = {
                k: (
                    None
                    if v is None
                    else definition.fields_by_name[k].type_.json_decode(v)
                )
                for k, v in parameters.items()
            }
            parameters = definition.parameters_class(**p)

        self._definition = definition
        if not isinstance(parameters, self._definition.parameters_class):
            raise TypeError("Class of argument parameters class must match definition.")
        self.parameters = parameters
        self.ignored_parameters = ignored_parameters

    @property
    def class_(self):
        return self._definition.class_

    @property
    def name(self):
        return self._definition.name

    @property
    def size(self):
        return self._definition.struct.size

    @property
    def type_id(self):
        return self._definition.type_id

    def pack(self):
        p = []
        for k, v in self.parameters._asdict().items():
            type_ = self._definition.fields_by_name[k].type_
            if v is None:
                if type_.java_type == "Boolean":
                    logging.warning(f"Missing parameter '{k}' replaced with False.")
                    v = False
                elif type_.java_type == "String":
                    logging.warning(
                        f"Missing parameter '{k}' replaced with emtpy string."
                    )
                    v = ""
                else:
                    logging.warning(f"Missing parameter '{k}' replaced with 0.")
                    v = 0
            p.append(type_.buffer_encode(v))
        return self._definition.struct.pack(*p)

    @classmethod
    def unpack(cls, version, type_id, buffer, **kwargs):
        return cls.unpack_by_def(
            MESSAGE_FORMATS[version]["message_defs_by_type_id"][type_id],
            buffer,
            **kwargs,
        )

    @classmethod
    def unpack_by_def(cls, definition, buffer, **kwargs):
        p = definition.struct.unpack(buffer)
        decoded = [definition.fields[i].type_.buffer_decode(v) for i, v in enumerate(p)]
        # noinspection PyArgumentList
        parameters = definition.parameters_class(*decoded)
        return cls(definition, parameters, **kwargs)


class MessageHeaderCoder:
    size = MESSAGE_HEADER_DEF_STRUCT.size
    LENGTH_SIZE = 1

    def __init__(self, version, length, type_id):
        self.length = length
        self.definition = MESSAGE_FORMATS[version]["message_defs_by_type_id"][type_id]

    def pack(self):
        return MESSAGE_HEADER_DEF_STRUCT.pack(self.length, self.definition.type_id)

    @classmethod
    def unpack_from(cls, version, buffer):
        return cls(version, *MESSAGE_HEADER_DEF_STRUCT.unpack_from(buffer))


class MessageContainerCoder:
    def __init__(self, version, message, message_header=None):
        self.message = message
        if message_header is not None:
            self.message_header = message_header
        else:
            self.message_header = MessageHeaderCoder(
                version,
                MessageHeaderCoder.size - MessageHeaderCoder.LENGTH_SIZE + message.size,
                message.type_id,
            )

    @property
    def size(self):
        return self.message_header.size + self.message.size

    def pack(self):
        return self.message_header.pack() + self.message.pack()

    @classmethod
    def unpack_from(cls, version, buffer, **kwargs):
        message_header = MessageHeaderCoder.unpack_from(version, buffer)
        buf = buffer[
            message_header.size : message_header.size
            + message_header.definition.struct.size
        ]
        message = MessageCoder.unpack_by_def(message_header.definition, buf, **kwargs)
        return cls(version, message, message_header)


class ChunkCoder:
    def __init__(self, chunk_header, messages):
        self.chunk_header = chunk_header
        self.messages = messages

    def pack(self):
        version = (
            self.chunk_header.parameters.protocol_version_major,
            self.chunk_header.parameters.protocol_version_minor,
        )
        return b"".join(
            MessageContainerCoder(version, m).pack()
            for m in itertools.chain([self.chunk_header], self.messages)
        )

    @staticmethod
    def iter_unpack(buffer, **kwargs):
        chunk_header = MessageContainerCoder.unpack_from(None, buffer, **kwargs).message
        version = (
            chunk_header.parameters.protocol_version_major,
            chunk_header.parameters.protocol_version_minor,
        )
        if version not in MESSAGE_FORMATS:
            raise RuntimeError("Protocol version in chunk header not understood.")

        while buffer:
            message_container = MessageContainerCoder.unpack_from(
                version, buffer, **kwargs
            )
            if (
                message_container.size
                != message_container.message_header.length
                + MessageHeaderCoder.LENGTH_SIZE
            ):
                raise RuntimeError(
                    "Unexpected message size. Backwards compatibility not implemented."
                )
            buffer = buffer[
                message_container.message_header.length
                + MessageHeaderCoder.LENGTH_SIZE :
            ]
            yield message_container.message


class ChunkHeaderCoder(MessageCoder):
    def __init__(self, version, parameters):
        definition = MESSAGE_FORMATS[version]["message_defs"][0]
        v = {"protocol_version_major": version[0], "protocol_version_minor": version[1]}
        super().__init__(definition, {**parameters, **v})


def json_encode_message(obj):
    if not isinstance(obj, MessageCoder):
        raise TypeError(f"Could not serialize {obj!r}.")
    if obj.class_ == "MetaData":
        return {
            "type": obj.name,
            **obj.parameters._asdict(),
        }
    elif obj.class_ == "Event":
        return {
            "type": "Event",
            "name": obj.name,
            **obj.parameters._asdict(),
        }
    else:
        raise TypeError(f"Invalid message class {obj.class_!s}.")


def json_decode_message(version, dct):
    try:
        class_ = dct["type"]
    except (KeyError, ValueError):
        return dct

    if class_ == "Event":
        try:
            name = dct["name"]
            emd = MESSAGE_FORMATS[version]["message_defs_by_class_and_name"][
                ("Event", name)
            ]
        except KeyError:
            return dct
        parameters = {k: v for k, v in dct.items() if k in emd.fields_by_name.keys()}
        ignored_parameters = {
            k: v
            for k, v in dct.items()
            if k not in ["type", "name"] and k not in emd.fields_by_name.keys()
        }
        for k in emd.fields_by_name.keys() - parameters.keys():
            parameters[k] = None
        return MessageCoder(emd, parameters, ignored_parameters)

    try:
        mdmd = MESSAGE_FORMATS[version]["message_defs_by_class_and_name"][
            ("MetaData", class_)
        ]
    except KeyError:
        return dct
    parameters = {k: v for k, v in dct.items() if k in mdmd.fields_by_name.keys()}
    ignored_parameters = {
        k: v
        for k, v in dct.items()
        if k != "type" and k not in mdmd.fields_by_name.keys()
    }
    for k in mdmd.fields_by_name.keys() - parameters.keys():
        parameters[k] = None
    return MessageCoder(mdmd, parameters, ignored_parameters)
