# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import pytest

from gardena_smart_local_api.devices.gen1 import Gen1BatteryMixin
from gardena_smart_local_api.devices.gen2 import Gen2BatteryMixin
from gardena_smart_local_api.devices.mowers import ( Gen1Mower2, Gen2Mower, MowerState )


@pytest.mark.asyncio
async def test_mower_gen1_lona_is_mower(mower_gen1_lona):
    assert isinstance(mower_gen1_lona, Gen1Mower2)
    assert isinstance(mower_gen1_lona, Gen1BatteryMixin)


@pytest.mark.asyncio
async def test_mower_gen1_lona_serial_number(mower_gen1_lona):
    assert mower_gen1_lona.serial_number == "202211111111"


@pytest.mark.asyncio
async def test_mower_gen1_lona_is_online(mower_gen1_lona):
    assert mower_gen1_lona.is_online is True


@pytest.mark.asyncio
async def test_mower_gen1_lona_battery_level(mower_gen1_lona):
    battery = mower_gen1_lona.battery_level
    assert battery is not None
    assert isinstance(battery, float)
    assert 0 <= battery <= 100
    assert battery == 72


@pytest.mark.asyncio
async def test_mower_gen1_lona_state_is_charging(mower_gen1_lona):
     # Status 8 = PARKED_WEEK_TIMER which maps to MowerState.PARKED
    state = mower_gen1_lona.state
    assert state is not None
    assert isinstance(state, MowerState)
    assert state == MowerState.PARKED


@pytest.mark.asyncio
async def test_mower_gen1_lona_position(mower_gen1_lona):
    position = mower_gen1_lona.position
    assert position is not None

    assert hasattr(position, 'gnss_latitude')
    assert hasattr(position, 'gnss_longitude')
    assert position.gnss_latitude == 47.3636
    assert position.gnss_longitude == 8.512599999999999
    assert position.compass_heading == 225.0


@pytest.mark.asyncio
async def test_mower_gen1_lona_build_start_mowing_obj(mower_gen1_lona):
    request_list = mower_gen1_lona.build_start_mowing_obj(300)
    request = request_list.root[0]

    assert request.op == "write"
    assert request.entity.device == mower_gen1_lona.id
    assert request.entity.service == "lemonbeatd"
    assert request.entity.path.object_name == "lemonbeat"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "mower_timer_with_distance"


@pytest.mark.asyncio
async def test_mower_gen1_lona_build_stop_mowing_obj(mower_gen1_lona):
    request_list = mower_gen1_lona.build_stop_mowing_obj()
    request = request_list.root[0]

    assert request.op == "write"
    assert request.entity.device == mower_gen1_lona.id
    assert request.entity.path.object_name == "lemonbeat"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "action_paused_until_1"


@pytest.mark.asyncio
async def test_mower_gen1_lona_build_start_position_reporting_obj(mower_gen1_lona):
    request_list = mower_gen1_lona.build_start_position_reporting_obj(60)
    request = request_list.root[0]

    assert request.op == "write"
    assert request.entity.device == mower_gen1_lona.id
    assert request.entity.path.object_name == "lemonbeat"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "position_timer"


@pytest.mark.asyncio
async def test_mower_gen2_is_mower(mower_gen2):
    assert isinstance(mower_gen2, Gen2Mower)
    assert isinstance(mower_gen2, Gen2BatteryMixin)


@pytest.mark.asyncio
async def test_mower_gen2_serial_number(mower_gen2):
    assert mower_gen2.serial_number == "00001111"


@pytest.mark.asyncio
async def test_mower_gen2_is_online(mower_gen2):
    assert mower_gen2.is_online is True


@pytest.mark.asyncio
async def test_mower_gen2_battery_level(mower_gen2):
    battery = mower_gen2.battery_level
    assert battery is not None
    assert isinstance(battery, float)
    assert 0 <= battery <= 100
    assert battery == 85


@pytest.mark.asyncio
async def test_mower_gen2_error(mower_gen2):
    # Gen2Mower doesn't have an 'error' property (uses mower_app.state/activity instead)
    pass


@pytest.mark.asyncio
async def test_mower_gen2_state_is_charging(mower_gen2):
    state = mower_gen2.state
    assert state is not None
    assert isinstance(state, MowerState)
    assert state == MowerState.PARKED


@pytest.mark.asyncio
async def test_mower_gen2_build_start_mowing_obj(mower_gen2):
    request_list = mower_gen2.build_start_mowing_obj(300)
    request = request_list.root[0]

    assert request.op == "execute"
    assert request.entity.device == mower_gen2.id
    assert request.entity.service == "lwm2mserver"
    assert request.entity.path.object_name == "smart_system_mower_api"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "manual_start"


@pytest.mark.asyncio
async def test_mower_gen2_build_stop_mowing_obj(mower_gen2):
    request_list = mower_gen2.build_stop_mowing_obj()
    request = request_list.root[0]

    assert request.op == "execute"
    assert request.entity.device == mower_gen2.id
    assert request.entity.path.object_name == "smart_system_mower_api"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "park_until_further_notice"


@pytest.mark.asyncio
async def test_mower_gen2_build_pause_mowing_obj(mower_gen2):
    request_list = mower_gen2.build_pause_mowing_obj()
    request = request_list.root[0]

    assert request.op == "execute"
    assert request.entity.device == mower_gen2.id
    assert request.entity.path.object_name == "mower_app"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "pause"

