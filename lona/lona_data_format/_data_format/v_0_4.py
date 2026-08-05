# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from .common_chunk_header import COMMON_CHUNK_HEADER, COMMON_CHUNK_HEADER_MESSAGE

CHUNK_HEADER = [
    *COMMON_CHUNK_HEADER,
    ("chunk_id", "uint16"),
    ("serial_number", "uint32"),
]

COMMON_DATA = [
    ("internal_clock", "uint32"),
    ("ms_since_start", "uint32"),
    ("restart_index", "uint32"),
]

# noinspection DuplicatedCode
COMMON_EVENT_DATA = [
    ("event_type", "uint32"),
    *COMMON_DATA,
]

NEW_LOG_META_DATA = [
    ("cs_plates_distance", "uint16"),
    ("front_center_distance", "uint16"),
    ("imu", "bytes16"),
    ("serial", "uint32"),
    ("SwVersion", "bytes64"),
    *COMMON_DATA,
    ("P0_F_field", "bool"),
]

# the field 'type' is added by the converter
# the field 'name' is added by the converter

# noinspection DuplicatedCode
GNSS_DATA = [
    ("gps_lat", "int32"),
    ("gps_lon", "int32"),
    ("gps_headMot", "int32"),
    ("gps_headAcc", "uint32"),
    ("gps_hAcc", "uint32"),
    ("gps_sAcc", "uint32"),
    ("gps_gSpeed", "int32"),
    ("gps_hDop", "uint8"),
    ("gps_numSatUsed", "uint8"),
]

IMU_DATA = [
    ("imu_pitch", "int16"),
    ("imu_roll", "int16"),
    ("imu_yaw", "int16"),
]

LOOP_DATA = [
    ("loop_front_center_A0", "int16"),
    ("loop_front_center_G1", "int16"),
    ("loop_front_center_G2", "int16"),
    ("loop_front_center_G3", "int16"),
    ("loop_front_center_F", "int16"),
]

LOOP_EXTRA_DATA = [
    ("loop_front_center_A0_max", "int16"),
]

ODOM_DATA = [
    ("odom_x", "int16"),
    ("odom_y", "int16"),
    ("odom_heading", "int32"),
]

MOWER_APP_DATA = [
    ("mower_mode", "uint8"),
    ("mower_activity", "uint8"),
    ("mower_state", "uint8"),
]

# noinspection DuplicatedCode
LOOP_EVENTS_DATA = (
    COMMON_EVENT_DATA
    + LOOP_EXTRA_DATA
    + IMU_DATA
    + LOOP_DATA
    + ODOM_DATA
    + MOWER_APP_DATA
)
COLLISION_EVENTS_DATA = (
    COMMON_EVENT_DATA
    + LOOP_EXTRA_DATA
    + IMU_DATA
    + LOOP_DATA
    + ODOM_DATA
    + MOWER_APP_DATA
)
GNSS_EVENTS_DATA = (
    COMMON_EVENT_DATA + GNSS_DATA + IMU_DATA + LOOP_DATA + ODOM_DATA + MOWER_APP_DATA
)
MOWER_APP_EVENTS_DATA = (
    COMMON_EVENT_DATA + IMU_DATA + LOOP_DATA + ODOM_DATA + MOWER_APP_DATA
)

MESSAGES = [
    COMMON_CHUNK_HEADER_MESSAGE[:-1] + (CHUNK_HEADER,),
    ("MetaData", "NewLog", 128, NEW_LOG_META_DATA),
    ("Event", "LoopEvent", 2, LOOP_EVENTS_DATA),
    ("Event", "CollisionEvent", 3, COLLISION_EVENTS_DATA),
    ("Event", "TimerEvent", 4, GNSS_EVENTS_DATA),
    ("Event", "StateEvent", 5, MOWER_APP_EVENTS_DATA),
]
