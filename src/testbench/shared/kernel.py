"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

# ─── Identifiers ───────────────────────────────────────────────


def generate_id() -> str:
    """
    Generate a UUID version 4 identifier string.

    Returns:
        A UUID v4 string (e.g., "3f8f9e2e-...").
    """
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """
    Get the current time in UTC.

    Returns:
        A timezone-aware datetime representing the current UTC time.
    """
    return datetime.now(timezone.utc)


# ─── Physical Units ────────────────────────────────────────────


class Unit(Enum):
    """Physical dimension and scale."""

    # Voltage
    VOLT = "V"
    MILLIVOLT = "mV"
    MICROVOLT = "μV"
    # Current
    AMPERE = "A"
    MILLIAMPERE = "mA"
    MICROAMPERE = "μA"
    # Power
    WATT = "W"
    MILLIWATT = "mW"
    DBM = "dBm"
    DBMV = "dBmV"
    # Ratio
    DB = "dB"
    # Resistance / Impedance
    OHM = "Ω"
    MEGAOHM = "MΩ"
    # Frequency
    HERTZ = "Hz"
    KILOHERTZ = "kHz"
    MEGAHERTZ = "MHz"
    GIGAHERTZ = "GHz"
    # Time
    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "μs"
    NANOSECOND = "ns"
    PICOSECOND = "ps"
    # Temperature
    CELSIUS = "°C"
    # Pressure
    PASCAL = "Pa"
    MILLIBAR = "mbar"
    # Data rate
    BIT_PER_SECOND = "bps"
    MEGABIT_PER_SECOND = "Mbps"
    # Other
    PERCENT = "%"
    PPM = "ppm"
    DEGREE = "°"
    DIMENSIONLESS = ""
    # EMC / Field strength
    VOLT_PER_METER = "V/m"
    DBUV_PER_METER = "dBμV/m"


class MeasurementMode(str, Enum):
    """How the value was acquired — the measurement coupling/mode."""

    DC = "dc"  # DC average (default for most measurements)
    RMS = "rms"  # True RMS (AC+DC or AC-only depending on coupling)
    PEAK = "peak"  # Single-sided peak
    PEAK_TO_PEAK = "pp"  # Peak-to-peak (Vpp, App)
    AVERAGE = "avg"  # Arithmetic mean over N samples
    MIN = "min"  # Minimum over capture window
    MAX = "max"  # Maximum over capture window
    INSTANTANEOUS = "inst"  # Single-shot sample
