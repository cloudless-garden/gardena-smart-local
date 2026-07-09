# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import base64

import pytest

from gardena_smart_local_api.utils.schedules import (
    Gen1OffsetPoint,
    Gen1ScheduleCycle,
    Gen1ScheduleEntry,
    Gen1SunScheduleEntry,
    Gen1TimeOffset,
    Gen1Weekday,
    gen1_schedule_config_to_base64,
    gen1_sun_schedule_config_to_base64,
    parse_gen1_schedule_config,
    parse_gen1_sun_schedule_config,
)

# Real lemonbeat/schedule_config payload captured from a gateway.
SCHEDULE_CONFIG_B64 = "BX8GMh4ABAJ/BAoFAAQEfwYZGQABA38GABkAAAB/BAAFAAABfwQFBQAB"
# Real lemonbeat/sun_schedule_config payload captured from a gateway.
SUN_SCHEDULE_CONFIG_B64 = "YD6gWAH/P6AZoB0B/z9wEnAWAf8/AA/gDwH/PyAh4CMB/z8="


def test_schedule_entry_from_bytes():
    weekdays = Gen1Weekday.MONDAY | Gen1Weekday.WEDNESDAY | Gen1Weekday.FRIDAY
    data = bytes([1, weekdays, 6, 30, 45, 0, 0])
    entry = Gen1ScheduleEntry.from_bytes(data)
    assert entry == Gen1ScheduleEntry(
        schedule_id=1,
        weekdays=Gen1Weekday.MONDAY | Gen1Weekday.WEDNESDAY | Gen1Weekday.FRIDAY,
        start_hour=6,
        start_minute=30,
        duration_minutes=45,
        action=0,
    )


def test_schedule_entry_from_bytes_wrong_size():
    with pytest.raises(ValueError, match="7 bytes"):
        Gen1ScheduleEntry.from_bytes(bytes(6))


def test_parse_schedule_config_multiple_entries():
    entry_one = bytes([0, Gen1Weekday.SUNDAY, 8, 0, 30, 0, 0])
    entry_two = bytes([1, Gen1Weekday.SATURDAY, 18, 15, 15, 0, 1])
    entries = parse_gen1_schedule_config(entry_one + entry_two)
    assert entries == [
        Gen1ScheduleEntry(0, Gen1Weekday.SUNDAY, 8, 0, 30, 0),
        Gen1ScheduleEntry(1, Gen1Weekday.SATURDAY, 18, 15, 15, action=1),
    ]


def test_parse_schedule_config_empty():
    assert parse_gen1_schedule_config(b"") == []


def test_parse_schedule_config_invalid_length():
    with pytest.raises(ValueError, match="multiple of 7"):
        parse_gen1_schedule_config(bytes(8))


def test_parse_schedule_config_real_gateway_payload():
    config = base64.b64decode(SCHEDULE_CONFIG_B64)
    entries = parse_gen1_schedule_config(config)
    assert entries == [
        Gen1ScheduleEntry(5, Gen1Weekday(0x7F), 6, 50, 30, action=4),
        Gen1ScheduleEntry(2, Gen1Weekday(0x7F), 4, 10, 5, action=4),
        Gen1ScheduleEntry(4, Gen1Weekday(0x7F), 6, 25, 25, action=1),
        Gen1ScheduleEntry(3, Gen1Weekday(0x7F), 6, 0, 25, action=0),
        Gen1ScheduleEntry(0, Gen1Weekday(0x7F), 4, 0, 5, action=0),
        Gen1ScheduleEntry(1, Gen1Weekday(0x7F), 4, 5, 5, action=1),
    ]


def test_sun_schedule_entry_from_bytes_wrong_size():
    with pytest.raises(ValueError, match="7 bytes"):
        Gen1SunScheduleEntry.from_bytes(bytes(6))


def test_parse_sun_schedule_config_invalid_length():
    with pytest.raises(ValueError, match="multiple of 7"):
        parse_gen1_sun_schedule_config(bytes(8))


def test_parse_sun_schedule_config_real_gateway_payload():
    config = base64.b64decode(SUN_SCHEDULE_CONFIG_B64)
    entries = parse_gen1_sun_schedule_config(config)
    assert entries == [
        Gen1SunScheduleEntry(
            start=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 998),
            stop=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 1418),
            weekdays=Gen1Weekday(0x7F),
            cycle=Gen1ScheduleCycle.CYCLE_14D,
            action_id=0,
            flag=False,
        ),
        Gen1SunScheduleEntry(
            start=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 410),
            stop=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 474),
            weekdays=Gen1Weekday(0x7F),
            cycle=Gen1ScheduleCycle.CYCLE_14D,
            action_id=0,
            flag=False,
        ),
        Gen1SunScheduleEntry(
            start=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 295),
            stop=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 359),
            weekdays=Gen1Weekday(0x7F),
            cycle=Gen1ScheduleCycle.CYCLE_14D,
            action_id=0,
            flag=False,
        ),
        Gen1SunScheduleEntry(
            start=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 240),
            stop=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 254),
            weekdays=Gen1Weekday(0x7F),
            cycle=Gen1ScheduleCycle.CYCLE_14D,
            action_id=0,
            flag=False,
        ),
        Gen1SunScheduleEntry(
            start=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 530),
            stop=Gen1TimeOffset(Gen1OffsetPoint.MIDNIGHT, 574),
            weekdays=Gen1Weekday(0x7F),
            cycle=Gen1ScheduleCycle.CYCLE_14D,
            action_id=0,
            flag=False,
        ),
    ]
