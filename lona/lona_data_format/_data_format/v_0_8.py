# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from .common_chunk_header import COMMON_CHUNK_HEADER, COMMON_CHUNK_HEADER_MESSAGE

CHUNK_HEADER = [
    *COMMON_CHUNK_HEADER,
    ("chunk_id", "uint16"),
    ("serial_number", "uint32"),
]

UNIX_TIME_FIELD = ("gps_unixTime", "uint32")

COMMON_DATA = [
    ("internal_clock", "uint32"),  # TODO at next breaking change: remove this field
    UNIX_TIME_FIELD,
    ("ms_since_start", "uint32"),
    ("restart_index", "uint32"),  # TODO at next breaking change: remove this field
]

# noinspection DuplicatedCode
COMMON_EVENT_DATA = [
    ("event_type", "uint32"),
    *COMMON_DATA,
]

# noinspection DuplicatedCode
NEW_LOG_META_DATA = [
    ("cs_plates_distance", "int16"),
    ("front_center_distance", "uint16"),
    ("imu", "bytes16"),
    ("serial", "uint32"),
    ("SwVersion", "bytes64"),
    *COMMON_DATA,
    ("P0_F_field", "bool"),
    ("debug_lat0", "int32"),
    ("debug_lon0", "int32"),
]

# the field 'type' is added by the converter
# the field 'name' is added by the converter

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
    ("loop_front_center_F", "int16"),
]

LOOP_EXTRA_DATA = [
    ("loop_front_center_A0_max", "int16"),
]

ODOM_DATA = [
    ("odom_x", "int32"),
    ("odom_y", "int32"),
    ("odom_heading", "int32"),
]

MOWER_APP_DATA = [
    ("mower_mode", "uint8"),
    ("mower_activity", "uint8"),
    ("mower_state", "uint8"),
    ("charger_connected", "bool"),
]

LOCAL_POSITION_DEBUG_DATA = [
    ("local_pos_x", "int32"),
    ("local_pos_y", "int32"),
    ("local_pos_heading", "int32"),
    ("local_pos_pos_sigma", "int32"),
    ("local_pos_pos_P0", "int32"),
    ("local_pos_pos_P1", "int32"),
    ("local_pos_pos_P2", "int32"),
    ("local_pos_pos_P3", "int32"),
    ("local_pos_heading_velocity", "int32"),
    ("local_pos_forward_velocity", "int32"),
    ("local_pos_traveling_distance", "int32"),
    ("local_pos_heading_variance", "int32"),
    ("local_pos_head_gnss_ok", "bool"),
    ("local_pos_head_imu_drift_rate", "int32"),
    ("local_pos_is_map_enabled", "bool"),
    ("local_pos_is_map_loaded", "bool"),
    ("local_pos_is_slipped", "bool"),
]

# noinspection DuplicatedCode
MAGNETOMETER_DATA = [
    ("mag_x", "int32"),
    ("mag_y", "int32"),
    ("mag_z", "int32"),
    ("mag_heading", "int16"),
    ("mag_calibrated", "bool"),
]

RTK_DATA = [
    ("rtk_lat", "int32"),
    ("rtk_lon", "int32"),
    ("rtk_heading", "int32"),
    ("rtk_headingAcc", "uint32"),
    ("rtk_hAcc", "uint32"),
    ("rtk_vAcc", "uint32"),
    ("rtk_sAcc", "uint32"),
    ("rtk_gSpeed", "int32"),
    ("rtk_carrierSolution", "uint8"),
]

COMMON_SENSOR_POSITION_MAPPING_FIELDS = [
    UNIX_TIME_FIELD,
    (
        "ms_since_start_16",
        "uint16",
    ),  # reduced to 16 bits, wrap-around after ~65 seconds
    ("local_pos_x", "int24"),  # reduced to 24 bits +-8.3km
    ("local_pos_y", "int24"),  # reduced to 24 bits +-8.3km
    ("local_pos_heading", "int16"),  # reduced to 16 bits +-1800
    (
        "gps_hAcc",
        "uint8",
    ),  # reduced to 8 bits mm to dm and capped at 255 (=25500mm) # TODO: rename to gps_hAcc_dm
]

SENSOR_POSITION_MAPPING_SENSOR_DATA = [
    *COMMON_SENSOR_POSITION_MAPPING_FIELDS,
    ("cut_intensity_average_current", "uint16"),
    ("rssi_and_blade_motor_running", "uint8"),  # merged with blade_motor_speed
]

RADIO_QUALITY_SENSOR_POSITION_MAPPING_SENSOR_DATA = [
    *COMMON_SENSOR_POSITION_MAPPING_FIELDS,
    ("rssi", "uint8"),  # RSSI (0 = packet loss)
    (
        "time",
        "int16",
    ),  # round-trip time (source=RM), approximate flight time (source=GW, might be negative)
    ("size", "uint16"),  # estimated packet size
    (
        "source_sequence",
        "uint8",
    ),  # source (highest bit: 0=RM, 1=GW) + sequence number (0..127)
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
DEBUG_EVENTS_DATA = COMMON_EVENT_DATA + LOCAL_POSITION_DEBUG_DATA + MAGNETOMETER_DATA
RTK_DEBUG_EVENTS_DATA = COMMON_EVENT_DATA + RTK_DATA
SENSOR_POSITION_MAPPING_EVENTS_DATA = SENSOR_POSITION_MAPPING_SENSOR_DATA
RADIO_QUALITY_SENSOR_POSITION_MAPPING_EVENTS_DATA = (
    RADIO_QUALITY_SENSOR_POSITION_MAPPING_SENSOR_DATA
)

# noinspection DuplicatedCode
MESSAGES = [
    COMMON_CHUNK_HEADER_MESSAGE[:-1] + (CHUNK_HEADER,),
    ("MetaData", "NewLog", 128, NEW_LOG_META_DATA),
    ("Event", "LoopEvent", 2, LOOP_EVENTS_DATA),
    ("Event", "CollisionEvent", 3, COLLISION_EVENTS_DATA),
    ("Event", "TimerEvent", 4, GNSS_EVENTS_DATA),
    ("Event", "StateEvent", 5, MOWER_APP_EVENTS_DATA),
    ("Event", "DebugEvent", 6, DEBUG_EVENTS_DATA),
    ("Event", "RtkDebugEvent", 7, RTK_DEBUG_EVENTS_DATA),
    ("Event", "SensorPositionMappingEvent", 8, SENSOR_POSITION_MAPPING_EVENTS_DATA),
    (
        "Event",
        "RadioQualitySensorPositionMappingEvent",
        9,
        RADIO_QUALITY_SENSOR_POSITION_MAPPING_EVENTS_DATA,
    ),
]
