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

Milestone 4: a conceptual vortex-breakdown / high-angle validity
SENSITIVITY model (see breakdown.py) -- not a breakdown prediction -- that
multiplies the unchanged M2 vortex-lift term by a smooth effectiveness
factor above an assumed, illustrative onset angle, propagates that into the
M3 drag/L-D model, and defines a predeclared conceptual usable-AoA region.
See DESIGN.md for the source audit and the exact list of assumptions.

Milestone 5: a conceptual, reduced-order pitching-moment / center-of-
pressure model (see pitching_moment.py), built on the unchanged M1 attached
lift and M4 effective vortex lift, with explicit force-location parameters
and their own sensitivity study. Isolated-wing static pitching tendency
only -- not a complete-aircraft stability analysis. See DESIGN.md for the
source audit and exact conventions.
"""

from . import attached_flow, breakdown, drag, geometry, pitching_moment, vortex_lift

__all__ = ["geometry", "attached_flow", "vortex_lift", "drag", "breakdown", "pitching_moment"]
