<!--
SPDX-FileCopyrightText: 2026 GARDENA GmbH

SPDX-License-Identifier: LGPL-3.0-or-later
-->

# Python scripts to decode LONA data from CBTL mowers

input file structure
```json
{
  "payload": {
    "lona": {
      "ts": 1,
      "vo": "<base64_encoded_data>"
    },
    "_urn": "urn:oma:lwm2m:x:31000"
  },
  "entity": {
    "path": "lemonbeat/0",
    "device": "<sgtin>"
  },
  "op": "update"
}
```

usage
`python3 decode_lona.py path/to/json another/path/json | jq`