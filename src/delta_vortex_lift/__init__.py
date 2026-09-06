"""delta_vortex_lift: reduced-order aerodynamic analysis of a generic delta wing.

Milestone 1 scope only: geometry, aerodynamic conventions, and an attached-flow
lift baseline. Vortex lift is intentionally NOT implemented yet.
"""

from . import attached_flow, geometry

__all__ = ["geometry", "attached_flow"]
