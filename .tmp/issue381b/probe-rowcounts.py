"""The row's own group and its two cusp rows, as one process sees them.

A resumed process must build the same subgroup a splitting process built, or the
line row it indexes the edges against is another row.  This prints what the
process got, so two runs can be compared.
"""

import os
import sys

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key  # noqa: E402

from coble_gamma_co_2_incidence_rows import _lattice_by_name, _row_subgroup  # noqa: E402

NAME = os.environ.get("PROBE_LATTICE", "U+U(2)+<-2>")
ROW = os.environ.get("PROBE_ROW", "Otilde")

lattice = _lattice_by_name(NAME)
subgroup = _row_subgroup(lattice, ROW)
print(f"subgroup: {subgroup}", flush=True)
quotient = subgroup.finite_character_quotient()
print(f"quotient: {quotient}", flush=True)
lines = tuple(subgroup.cusps(1))
planes = tuple(subgroup.cusps(2))
print(f"line cusps {len(lines)}: {[cusp.span()[1] for cusp in lines]}", flush=True)
print(f"plane cusps {len(planes)}: {[cusp.span()[1] for cusp in planes]}", flush=True)
