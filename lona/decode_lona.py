#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import base64
import json
import os
import sys

from lona_data_format.coder import ChunkCoder, json_encode_message


def iot_value_to_hex(value):
    decoded = base64.b64decode(value)
    return decoded.hex()


def unpack_lona(value):
    lona_json = ""
    for message in ChunkCoder.iter_unpack(value):
        if message.class_ == "Transport" or message.class_ == "MetaData":
            # print(f'header: {message.parameters}')
            continue
        lona_json += json.dumps(message, default=json_encode_message)
    return lona_json


def main():
    lona_json = ""
    for folder_path in sys.argv[1:]:
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        # check if correct payload exists in the json object
                        if (
                            "payload" in data
                            and "lona" in data["payload"]
                            and "vo" in data["payload"]["lona"]
                        ):
                            lona_data = data["payload"]["lona"]["vo"]
                            if lona_data is not None:
                                hexadecimal = iot_value_to_hex(lona_data)
                                lona_json += unpack_lona(bytes.fromhex(hexadecimal))
                except (OSError, json.JSONDecodeError):
                    # skip files that aren't valid JSON or can't be read
                    continue
    print(lona_json)


if __name__ == "__main__":
    main()
