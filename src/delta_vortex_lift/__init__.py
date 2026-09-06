"""delta_vortex_lift: reduced-order aerodynamic analysis of a generic delta wing.

Milestone 1: geometry, aerodynamic conventions, and an attached-flow lift
baseline.

Milestone 2: a reduced-order, Polhamus-inspired vortex-lift contribution
(see vortex_lift.py), combined with the unchanged Milestone-1 attached-flow
baseline into a total lift curve. See DESIGN.md for what is and is not
adopted from the original Polhamus (1966) theory.

Milestone 3: a reduced-order, Polhamus-inspired drag-due-to-lift and L/D
model (see drag.py), combining classical attached induced drag with a
vortex drag-due-to-lift term. See DESIGN.md for what is and is not adopted
from the original Polhamus (1968) drag-due-to-lift theory.
"""

from . import attached_flow, drag, geometry, vortex_lift

__all__ = ["geometry", "attached_flow", "vortex_lift", "drag"]
