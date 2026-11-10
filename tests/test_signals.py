from sim.signals import chamber_pressure, CHANNELS

import pytest
import math

def test_pressure_ramps_up():
    assert chamber_pressure(0.0) == 0.0
    assert chamber_pressure(1.0) < chamber_pressure(1.9)

def test_pressure_holds_then_decays():
    assert chamber_pressure(5.0) == 400.0
    assert chamber_pressure(20.0) < 400.0

def test_all_channels_have_unique_names():
    names = [c.name for c in CHANNELS]
    assert len(names) == len(set(names))


# new tests here

def _sample_times(start, stop, step=0.1):
    n = round((stop - start) / step)
    return [round(start + i * step, 6) for i in range(n + 1)]


def test_pressure_never_negative():
    for t in _sample_times(0.0, 60.0):
        assert chamber_pressure(t) >= 0.0, f"negative pressure at t={t}"


def test_pressure_never_exceeds_peak():
    for t in _sample_times(0.0, 60.0):
        assert chamber_pressure(t) <= 400.0, f"overshoot at t={t}"


def test_pressure_is_finite_everywhere():
    for t in _sample_times(0.0, 60.0):
        value = chamber_pressure(t)
        assert math.isfinite(value), f"non-finite value at t={t}"


def test_ramp_is_monotonic_non_decreasing():
    times = _sample_times(0.0, 1.9)
    values = [chamber_pressure(t) for t in times]
    for earlier, later in zip(values, values[1:]):
        assert later >= earlier


def test_decay_is_monotonic_non_increasing():
    times = _sample_times(5.0, 20.0)
    values = [chamber_pressure(t) for t in times]
    for earlier, later in zip(values, values[1:]):
        assert later <= earlier


def test_pressure_returns_float():
    assert isinstance(chamber_pressure(3.0), float)


def test_pressure_is_repeatable():
    # Same time in, same value out. If signals.py adds random noise on
    # purpose, change this test to check the value stays inside a band.
    assert chamber_pressure(7.3) == chamber_pressure(7.3)


@pytest.mark.parametrize("t", [0.0, 1.0, 5.0, 10.0, 30.0])
def test_pressure_accepts_float_times(t):
    assert isinstance(chamber_pressure(float(t)), float)


def test_channels_list_is_not_empty():
    assert len(CHANNELS) > 0


def test_channel_names_are_nonempty_strings():
    for c in CHANNELS:
        assert isinstance(c.name, str)
        assert c.name.strip() != ""


def test_channel_names_have_no_spaces():
    # Spaces in names are a common cause of broken InfluxDB tags and OPC UA node IDs.
    for c in CHANNELS:
        assert " " not in c.name, f"space in channel name: {c.name!r}"