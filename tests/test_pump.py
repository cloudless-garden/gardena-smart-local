# SPDX-FileCopyrightText: 2026 GARDENA GmbH
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import pytest

from gardena_smart_local_api.devices.irrigation import Pump, PumpOperatingMode
from gardena_smart_local_api.model_loader import Gen1ModelDefinition


@pytest.fixture
def pump():
    return Pump(
        id="3034F8319C02BF00000033FF",
        data={},
        model_definition=Gen1ModelDefinition(model_number="22538", name="Test Pump"),
    )


def _set_operating_mode(pump, mode: PumpOperatingMode) -> None:
    pump.data.setdefault("lemonbeat", {}).setdefault("0", {})["operating_mode"] = {
        "vi": mode.value
    }


def test_build_start_obj(pump):
    request = pump.build_start_obj(120).root[0]
    assert request.op == "write"
    assert request.entity.device == pump.id
    assert request.entity.path.object_name == "lemonbeat"
    assert request.entity.path.object_instance_id == "0"
    assert request.entity.path.resource_name == "watering_timer_1"
    assert request.payload == {"vi": 120}


def test_build_stop_obj(pump):
    request = pump.build_stop_obj().root[0]
    assert request.payload == {"vi": 0}


def test_build_start_obj_raises_in_automatic_mode(pump):
    _set_operating_mode(pump, PumpOperatingMode.AUTOMATIC)
    with pytest.raises(ValueError, match="automatic mode"):
        pump.build_start_obj(120)


def test_build_stop_obj_raises_in_automatic_mode(pump):
    _set_operating_mode(pump, PumpOperatingMode.AUTOMATIC)
    with pytest.raises(ValueError, match="automatic mode"):
        pump.build_stop_obj()


def test_build_start_obj_allowed_in_scheduled_mode(pump):
    _set_operating_mode(pump, PumpOperatingMode.SCHEDULED)
    request = pump.build_start_obj(120).root[0]
    assert request.payload == {"vi": 120}


def test_build_start_obj_allowed_when_mode_unset(pump):
    request = pump.build_start_obj(120).root[0]
    assert request.payload == {"vi": 120}
