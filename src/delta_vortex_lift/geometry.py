"""Generic sharp-edged, symmetric, straight-sided delta-wing planform geometry.

Convention
----------
The planform is a flat triangle with its apex at the nose and a straight
trailing edge (the root chord) spanning the full width of the wing:

    apex           = (0, 0)
    right wingtip  = (c_r, +b/2)
    left wingtip   = (c_r, -b/2)

x is the streamwise (flow) direction, y is the spanwise direction. With this
layout the *root chord* c_r is the streamwise distance from the apex to the
trailing edge along the centerline, and the leading edge is the straight line
from the apex to each wingtip.

Leading-edge sweep Λ_LE is defined, as is conventional in aircraft geometry,
as the angle between the leading edge and the spanwise (y) axis -- i.e. the
angle swept back *from* a wing of zero sweep (whose leading edge would run
straight along y). For the right-hand leading edge:

    tan(Λ_LE) = (streamwise run) / (spanwise run) = c_r / (b/2)

so Λ_LE -> 0 as the planform flattens out spanwise (c_r small relative to
span) and Λ_LE -> 90 deg as the planform becomes a thin sliver pointing
downstream (c_r large relative to span). This matches the usual aerospace
convention where a highly swept, slender delta has Λ_LE close to 90 deg.

All angles are stored/returned in radians unless a function name explicitly
says otherwise (e.g. ``sweep_LE_deg``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DeltaWingGeometry:
    """Symmetric, sharp-edged, straight-sided (true triangular) delta wing.

    The minimal independent parameter set is (root_chord, span). All other
    quantities (area, aspect ratio, sweep) are derived from these two, which
    guarantees internal consistency -- there is no way to supply an area,
    aspect ratio, and sweep that mutually contradict each other.

    Use the classmethods :meth:`from_span_and_sweep` or
    :meth:`from_root_chord_and_sweep` to construct a wing starting from a
    sweep angle instead of a root chord/span pair.
    """

    root_chord: float  # c_r [m]
    span: float  # b [m], full span (tip to tip)

    def __post_init__(self) -> None:
        if not math.isfinite(self.root_chord) or self.root_chord <= 0.0:
            raise ValueError(f"root_chord must be positive and finite, got {self.root_chord!r}")
        if not math.isfinite(self.span) or self.span <= 0.0:
            raise ValueError(f"span must be positive and finite, got {self.span!r}")

    # ------------------------------------------------------------------
    # Derived planform quantities
    # ------------------------------------------------------------------

    @property
    def semi_span(self) -> float:
        """b/2 [m]."""
        return self.span / 2.0

    @property
    def area(self) -> float:
        """Planform area S = 0.5 * b * c_r [m^2] (triangle: 0.5 * base * height)."""
        return 0.5 * self.span * self.root_chord

    @property
    def aspect_ratio(self) -> float:
        """AR = b^2 / S [-]."""
        return self.span**2 / self.area

    @property
    def sweep_LE_rad(self) -> float:
        """Leading-edge sweep Λ_LE [rad], from tan(Λ_LE) = c_r / (b/2)."""
        return math.atan2(self.root_chord, self.semi_span)

    @property
    def sweep_LE_deg(self) -> float:
        """Leading-edge sweep Λ_LE [deg]."""
        return math.degrees(self.sweep_LE_rad)

    # ------------------------------------------------------------------
    # Alternative (inverse) constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_span_and_sweep(cls, span: float, sweep_LE_rad: float) -> "DeltaWingGeometry":
        """Construct from full span and leading-edge sweep [rad].

        Inverts tan(Λ_LE) = c_r / (b/2)  =>  c_r = (b/2) * tan(Λ_LE).
        """
        if not math.isfinite(sweep_LE_rad) or not (0.0 < sweep_LE_rad < math.pi / 2.0):
            raise ValueError(
                "sweep_LE_rad must be strictly between 0 and pi/2 for a valid "
                f"triangular delta planform, got {sweep_LE_rad!r}"
            )
        if not math.isfinite(span) or span <= 0.0:
            raise ValueError(f"span must be positive and finite, got {span!r}")
        root_chord = (span / 2.0) * math.tan(sweep_LE_rad)
        return cls(root_chord=root_chord, span=span)

    @classmethod
    def from_root_chord_and_sweep(cls, root_chord: float, sweep_LE_rad: float) -> "DeltaWingGeometry":
        """Construct from root chord and leading-edge sweep [rad].

        Inverts tan(Λ_LE) = c_r / (b/2)  =>  b = 2 * c_r / tan(Λ_LE).
        """
        if not math.isfinite(sweep_LE_rad) or not (0.0 < sweep_LE_rad < math.pi / 2.0):
            raise ValueError(
                "sweep_LE_rad must be strictly between 0 and pi/2 for a valid "
                f"triangular delta planform, got {sweep_LE_rad!r}"
            )
        if not math.isfinite(root_chord) or root_chord <= 0.0:
            raise ValueError(f"root_chord must be positive and finite, got {root_chord!r}")
        span = 2.0 * root_chord / math.tan(sweep_LE_rad)
        return cls(root_chord=root_chord, span=span)


def representative_geometry() -> DeltaWingGeometry:
    """A single generic, illustrative delta-wing geometry used throughout Milestone 1.

    Chosen as (span, leading-edge sweep) = (6.0 m, 65 deg):

    - Λ_LE = 65 deg sits in the middle of the ~55-70 deg conceptual range for a
      slender supersonic-type delta planform, giving a clearly low-AR wing
      without being a degenerate sliver.
    - span = 6.0 m is a round, purely illustrative scale (no real aircraft is
      implied); it only sets the absolute size, since C_L is scale-invariant
      and depends only on AR (a dimensionless ratio).

    This is NOT a reconstruction of any specific real aircraft.
    """
    return DeltaWingGeometry.from_span_and_sweep(span=6.0, sweep_LE_rad=math.radians(65.0))
