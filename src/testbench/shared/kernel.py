"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

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


# ─── Measurement & Test Result ─────────────────────────────────
# These live in the shared kernel because every subsystem's test
# implementations produce them, every registry consumes them, and
# the execution engine stores them. One definition, not three copies.


@dataclass(frozen=True)
class TestMeasurement:
    """A single parameter measured during a test.

    Immutable value object containing all measurement data and metadata.
    """

    parameter_name: str
    measured_value: float
    unit: Unit
    mode: MeasurementMode = MeasurementMode.DC
    nominal_value: float | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None
    raw_data_ref: tuple[str, ...] = ()  # paths to screenshots, traces, waveforms


@dataclass(frozen=True)
class TestResult:
    """Final result of a test execution — immutable once returned."""

    passed: bool
    measurements: tuple[TestMeasurement, ...] = ()
    notes: str = ""
    error: str = ""


# ─── Repository Interfaces (Percival: domain defines, infra implements) ──


class TestDefinitionRepository(ABC):
    """Port for persisting test definitions.

    The domain defines this interface; the persistence layer implements it.
    Subsystem registries call this to seed definitions, without knowing
    whether the storage is SQLAlchemy, in-memory, or a flat file.
    """

    @abstractmethod
    def find_by_code(self, code: str) -> dict | None:
        """
        Look up a test definition using its unique code.

        Parameters:
            code (str): The test definition code to search for.

        Returns:
            dict | None: The test definition record if found, otherwise `None`.
        """
        ...

    @abstractmethod
    def find_by_scope(self, subsystem_scope: str) -> list[dict]:
        """
        Retrieve all test definition records for the given subsystem scope.

        Parameters:
            subsystem_scope (str): Subsystem scope identifier used to filter test definitions.

        Returns:
            list[dict]: List of test definition dictionaries, typically containing keys such as `code`, `name`, `description`, `scope`, `duration`, and `runnable_during_stress`.
        """
        ...

    @abstractmethod
    def save(
        self,
        code: str,
        name: str,
        description: str,
        subsystem_scope: str,
        estimated_duration_seconds: int,
        *,
        runnable_during_stress: bool = True,
    ) -> None:
        """
        Store a test definition for the given subsystem scope.
        
        Parameters:
        	code: Unique test code used as the persistent identifier.
        	name: Human-readable test name.
        	description: What the test verifies and any important details.
        	subsystem_scope: Subsystem or scope the test applies to.
        	estimated_duration_seconds: Expected execution time in seconds.
        	runnable_during_stress: Whether the test is safe to run during stress conditions (defaults to True).
        """
        ...

    @abstractmethod
    def exists(self, code: str) -> bool:
        """
        Determines whether a test definition with the given code exists.
        
        Parameters:
            code (str): The unique code identifying the test definition.
        
        Returns:
            bool: `True` if a test definition with the given code exists, `False` otherwise.
        """
        ...


class MonitorChannelRepository(ABC):
    """Port for persisting DUT monitor channels and thresholds."""

    @abstractmethod
    def find_by_dut(self, dut_id: str, channel_name: str) -> dict | None:
        """
        Retrieve a monitor channel definition for a device-under-test (DUT) by channel name.

        Parameters:
            dut_id (str): Identifier of the DUT.
            channel_name (str): Name of the monitor channel to look up.

        Returns:
            dict | None: Channel configuration dictionary if found, `None` otherwise.
        """
        ...

    @abstractmethod
    def save_channel(
        self,
        dut_id: str,
        channel_name: str,
        channel_type: str,
        unit: str,
        subsystem: str,
        nominal: tuple[float, float],
        warning: tuple[float, float],
        abort: tuple[float, float],
        context: str = "ambient",
    ) -> None:
        """
        Persist monitor channel configuration for a device under test.

        Parameters:
        dut_id (str): Identifier of the DUT that owns the channel.
        channel_name (str): Logical name of the monitor channel.
        channel_type (str): Category of the channel (e.g., "voltage", "temperature").
        unit (str): Unit symbol or identifier for measurements produced by the channel.
        subsystem (str): Subsystem or scope the channel belongs to.
        nominal (tuple[float, float]): Nominal bounds as (lower, upper).
        warning (tuple[float, float]): Warning threshold bounds as (lower, upper).
        abort (tuple[float, float]): Abort threshold bounds as (lower, upper).
        context (str): Measurement context or environment (default "ambient").
        """
        ...


# ─── Physical Quantity ──────────────────────────────────────────


@dataclass(frozen=True)
class PhysicalQuantity:
    """Immutable measured value with unit and mode."""

    value: float
    unit: Unit
    mode: MeasurementMode = MeasurementMode.DC

    def __str__(self) -> str:
        """
        Return a human-readable representation of the physical quantity including its numeric value, unit, and measurement mode.
        
        The numeric value is formatted with up to four significant digits; if the mode is not DC, the mode text is appended immediately after the unit (for example, "1.23 V" or "1.23 Vrms").
        
        Returns:
            str: The formatted string representation.
        """
        if self.mode == MeasurementMode.DC:
            return f"{self.value:.4g} {self.unit.value}"
        return f"{self.value:.4g} {self.unit.value}{self.mode.value}"


# ─── Tolerance ──────────────────────────────────────────────────


@dataclass(frozen=True)
class Tolerance:
    nominal: float
    upper: float
    lower: float
    unit: Unit

    @classmethod
    def symmetric(cls, nominal: float, delta: float, unit: Unit) -> Tolerance:
        """
        Create a Tolerance with symmetric upper and lower bounds around a nominal value.

        Parameters:
            nominal (float): Center value for the tolerance.
            delta (float): Absolute amount added to and subtracted from the nominal value to form bounds.
            unit (Unit): Unit of the nominal value and bounds.

        Returns:
            Tolerance: Instance with `upper = nominal + delta` and `lower = nominal - delta`.
        """
        if delta < 0:
            raise ValueError(f"delta must be >= 0, got {delta}")
        return cls(
            nominal=nominal, upper=nominal + delta, lower=nominal - delta, unit=unit
        )

    @classmethod
    def percentage(cls, nominal: float, pct: float, unit: Unit) -> Tolerance:
        """
        Create a Tolerance around a nominal value using a percentage of that nominal.

        Parameters:
            nominal (float): Center value for the tolerance.
            pct (float): Percentage of `nominal` to use as the half-width (e.g., 5.0 for 5%).
            unit (Unit): Unit of the nominal value and resulting bounds.

        Returns:
            Tolerance: Tolerance with `upper = nominal + nominal * pct / 100` and `lower = nominal - nominal * pct / 100`.
        """
        if pct < 0:
            raise ValueError(f"pct must be >= 0, got {pct}")
        return cls.symmetric(nominal, nominal * pct / 100.0, unit)

    def contains(self, value: float) -> bool:
        """
        Determine whether a numeric value falls within the tolerance bounds (inclusive).
        
        Returns:
            `true` if the value is greater than or equal to `lower` and less than or equal to `upper`, `false` otherwise.
        """
        return self.lower <= value <= self.upper


# ─── Base Domain Event ──────────────────────────────────────────


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: str = field(default_factory=generate_id)
    occurred_at: datetime = field(default_factory=utc_now)


# ─── Hardware Revision ──────────────────────────────────────────


@dataclass(frozen=True)
class HardwareRevision:
    serial_number: str
    revision: str
    pcb_version: Optional[str] = None
    firmware_version: Optional[str] = None