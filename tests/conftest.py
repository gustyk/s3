from __future__ import annotations

import copy

import pytest

from src.configuration import load_config


@pytest.fixture
def small_params():
    params = copy.deepcopy(load_config().values)
    params["simulation_time"] = 600
    params["trigger_parameters"]["FTWB_interval"] = 30
    params["trigger_parameters"]["VTWB_threshold"] = 2
    return params


def make_order(order_id="O1", created=0.0, due=100.0, total=1, item=1):
    return {
        "Order ID": order_id,
        "Created Time": "00:00:00",
        "Created Time Seconds": created,
        "Order List": [(item, total)],
        "Total Item": total,
        "Due Time": "00:01:40",
        "Due Time Seconds": due,
    }
