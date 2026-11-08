import math
from dataclasses import dataclass
from typing import Callable

def chamber_pressure(t: float) -> float:
    if t < 2.0:
        return 400.0 * (t / 2.0)                    # ramp up
    if t < 12.0:
        return 400.0                                 # steady burn
    return 400.0 * math.exp(-(t - 12.0) / 1.5)       # shutdown decay

def chamber_temp(t: float) -> float:
    return 300.0 + 1500.0 * (1 - math.exp(-t / 3.0))

def thrust(t: float) -> float:
    return 0.8 * chamber_pressure(t)

@dataclass(frozen=True)
class Channel:
    name: str
    unit: str
    fn: Callable[[float], float]
    noise_std: float
    dropout_prob: float = 0.0

CHANNELS = [
    Channel("chamber_pressure_psi", "psi", chamber_pressure, noise_std=2.0, dropout_prob=0.01),
    Channel("chamber_temp_k", "K", chamber_temp, noise_std=5.0),
    Channel("thrust_lbf", "lbf", thrust, noise_std=8.0, dropout_prob=0.02),
]