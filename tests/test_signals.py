from sim.signals import chamber_pressure, CHANNELS

def test_pressure_ramps_up():
    assert chamber_pressure(0.0) == 0.0
    assert chamber_pressure(1.0) < chamber_pressure(1.9)

def test_pressure_holds_then_decays():
    assert chamber_pressure(5.0) == 400.0
    assert chamber_pressure(20.0) < 400.0

def test_all_channels_have_unique_names():
    names = [c.name for c in CHANNELS]
    assert len(names) == len(set(names))