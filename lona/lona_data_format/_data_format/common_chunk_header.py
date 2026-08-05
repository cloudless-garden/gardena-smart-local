# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

# The beginning of each chunk (after length and type_id), common format for every version, do not change.
COMMON_CHUNK_HEADER = [
    ("protocol_version_major", "uint8"),
    ("protocol_version_minor", "uint8"),
]

# Extra data that may be contained in the chunk header, with varying availability and location per protocol version.
EXTRA_CHUNK_HEADER_INTERFACE = [
    ("chunk_id", "uint16"),
    ("serial_number", "uint32"),
]

COMMON_CHUNK_HEADER_MESSAGE = ("Transport", "ChunkHeader", 255, COMMON_CHUNK_HEADER)
