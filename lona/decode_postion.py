#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import base64
import json
import os
import struct
import sys
from collections import namedtuple

Position = namedtuple(
    "Position",
    [
        "gnssLatitude",
        "gnssLongitude",
        "gnssHorizontalAccuracy",
        "realTimeLatitude",
        "realTimeLongitude",
        "realTimeHeading",
        "realTimeIsReady",
        "compassHeading",
        "compassIsCalibrated",
    ],
)


def iot_value_to_hex(value):
    decoded = base64.b64decode(value)
    return decoded.hex()


def unpack_position(value):
    if len(value) == 0:
        return None
    elif len(value) == 25:
        raw = Position(*struct.unpack(">2iI2ih?h", value), None)
    elif len(value) == 26:
        raw = Position(*struct.unpack(">2iI2ih?h?", value))
    else:
        raise ValueError(f"invalid position buffer length {len(value)}.")

    # correct decimal values
    raw = raw._replace(
        gnssLatitude=raw.gnssLatitude / 10000000,
        gnssLongitude=raw.gnssLongitude / 10000000,
        gnssHorizontalAccuracy=raw.gnssHorizontalAccuracy / 1000,
        realTimeLatitude=raw.realTimeLatitude / 10000000,
        realTimeLongitude=raw.realTimeLongitude / 10000000,
        realTimeHeading=raw.realTimeHeading / 10,
        compassHeading=raw.compassHeading / 10,
    )

    return json.dumps(raw._asdict())


def main():
    position_json = ""
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
                            and "position" in data["payload"]
                            and "vo" in data["payload"]["position"]
                        ):
                            position_data = data["payload"]["position"]["vo"]
                            if position_data is not None:
                                hexadecimal = iot_value_to_hex(position_data)
                                position_json += unpack_position(
                                    bytes.fromhex(hexadecimal)
                                )
                except (OSError, json.JSONDecodeError):
                    # skip files that aren't valid JSON or can't be read
                    continue
    print(position_json)


if __name__ == "__main__":
    main()
