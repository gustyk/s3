def test_setup_time_affects_predictor():
    from src.configuration import load_config, DEFAULT_CONFIG
    from src.trigger_method import _single_order_trip_seconds
    import copy

    config = load_config(DEFAULT_CONFIG)
    params1 = copy.deepcopy(config.values)
    params2 = copy.deepcopy(config.values)

    params1["setup_time"] = 180.0
    params2["setup_time"] = 30.0

    order = {
        "Order ID": 1,
        "Order List": [[1, 2], [5, 3]],
        "Total Item": 5,
        "Due Time Seconds": 3600.0,
        "Arrival Time Seconds": 100.0,
    }

    t1 = _single_order_trip_seconds(copy.deepcopy(order), "S-shape", params1)
    t2 = _single_order_trip_seconds(copy.deepcopy(order), "S-shape", params2)

    assert t1 - t2 == 150.0, f"Expected 150s difference, got {t1 - t2}"
    print("Unit test passed: predictor output changes with setup_time")

if __name__ == "__main__":
    test_setup_time_affects_predictor()
